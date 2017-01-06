import cPickle,numpy,pyfits as py
import pymc
from pylens import *
from imageSim import SBModels,convolve,SBObjects
import indexTricks as iT
from SampleOpt import AMAOpt
import pylab as pl
import numpy as np
import myEmcee_blobs as myEmcee
from matplotlib.colors import LogNorm
from scipy import optimize
from scipy.interpolate import RectBivariateSpline
import SBBModels, SBBProfiles

'''
X=0 - TO RUN. 2 PSF components, one big one small
'''
X=0
print X

# plot things
def NotPlicely(image,im,sigma):
    ext = [0,image.shape[0],0,image.shape[1]]
    #vmin,vmax = numpy.amin(image), numpy.amax(image)
    pl.figure()
    pl.subplot(221)
    pl.imshow(image,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=0,vmax=2) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('data')
    pl.subplot(222)
    pl.imshow(im,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=0,vmax=2) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('model')
    pl.subplot(223)
    pl.imshow(image-im,origin='lower',interpolation='nearest',extent=ext,vmin=-0.25,vmax=0.25,cmap='afmhot',aspect='auto')
    pl.colorbar()
    pl.title('data-model')
    pl.subplot(224)
    pl.imshow((image-im)/sigma,origin='lower',interpolation='nearest',extent=ext,vmin=-5,vmax=5,cmap='afmhot',aspect='auto')
    pl.title('signal-to-noise residuals')
    pl.colorbar()

image = py.open('/data/ljo31/Lens/J1218/J1218_med.fits')[0].data.copy()[640:820,460:640]
sigma = np.ones(image.shape) 

result = np.load('/data/ljo31/Lens/LensModels/J1218_211')
lp= result[0]
a2=0
a1,a3 = numpy.unravel_index(lp[:,0].argmax(),lp[:,0].shape)
trace = result[1]
dic = result[2]

OVRS = 1
yc,xc = iT.overSample(image.shape,OVRS)
yo,xo = iT.overSample(image.shape,1)
#xc,xo,yc,yo = xc-60,xo-60,yc-40,yo-40

xc,xo,yc,yo = xc+250,xo+250,yc+200,yo+200
xc,xo,yc,yo=xc*0.6,xo*0.6,yc*0.6,yo*0.6
xc,xo,yc,yo = xc-140,xo-140,yc-120,yo-120

mask = np.zeros(image.shape)
tck = RectBivariateSpline(yo[:,0],xo[0],mask)
mask2 = tck.ev(xc,yc)
mask2[mask2<0.5] = 0
mask2[mask2>0.5] = 1
mask2 = mask2==0
mask = mask==0



pars = []
cov = []
### first parameters need to be the offsets
pars.append(pymc.Uniform('xoffset',-40.,40.,value=5))
pars.append(pymc.Uniform('yoffset',-40.,40.,value=5))
cov += [0.4,0.4]
pars.append(pymc.Uniform('sigma 1',0,8,value=4))
cov += [5]
pars.append(pymc.Uniform('q 1',0,1,value=0.7))
cov += [1]
pars.append(pymc.Uniform('pa 1',-180,180,value= 90 ))
cov += [50]
pars.append(pymc.Uniform('amp 1',0,1,value=0.25))
cov += [4]
pars.append(pymc.Uniform('sigma 2',10,60,value= 20 )) 
cov += [40]
pars.append(pymc.Uniform('q 2',0,1,value=0.9))
cov += [1]
pars.append(pymc.Uniform('pa 2',-180,180,value= 90 ))
cov += [50]
pars.append(pymc.Uniform('amp 2',0,1,value=0.25))
cov += [4]
pars.append(pymc.Uniform('sigma 3',1,60,value= 10 )) 
cov += [40]
pars.append(pymc.Uniform('q 3',0,1,value=0.9))
cov += [1]
pars.append(pymc.Uniform('pa 3',-180,180,value= 90 ))
cov += [50]
pars.append(pymc.Uniform('amp 3',0,1,value=0.25))
cov += [4]
# psf4
'''pars.append(pymc.Uniform('sigma 4',10,100,value= 50 )) 
cov += [40]
pars.append(pymc.Uniform('q 4',0,1,value=0.9))
cov += [1]
pars.append(pymc.Uniform('pa 4',-180,180,value= 90 ))
cov += [50]'''

xpsf,ypsf = iT.coords((201,201))-100

gals = []
for name in ['Galaxy 1', 'Galaxy 2']:
    p = {}
    if name == 'Galaxy 1':
        for key in 'x','y','q','pa','re','n':
            p[key] = dic[name+' '+key][a1,a2,a3]
    elif name == 'Galaxy 2':
        for key in 'x','y','q','pa','re','n':
            p[key] = dic[name+' '+key][a1,a2,a3]
    gals.append(SBModels.Sersic(name,p))

lenses = []
p = {}
for key in 'x','y','q','pa','b','eta':
    p[key] = dic['Lens 1 '+key][a1,a2,a3]
lenses.append(MassModels.PowerLaw('Lens 1',p))
p = {}
p['x'] = lenses[0].pars['x']
p['y'] = lenses[0].pars['y']
p['b'] = dic['extShear'][a1,a2,a3]
p['pa'] = dic['extShear PA'][a1,a2,a3]
lenses.append(MassModels.ExtShear('shear',p))

srcs = []
for name in ['Source 1']:
    p = {}
    if name == 'Source 2':
        print name
        for key in 'q','re','n','pa':
           p[key] = dic[name+' '+key][a1,a2,a3]
        for key in 'x','y': # subtract lens potition - to be added back on later in each likelihood iteration!
            p[key] = dic[name+' '+key][a1,a2,a3]+lenses[0].pars[key]
    elif name == 'Source 1':
        print name
        for key in 'q','re','n','pa':
           p[key] = dic[name+' '+key][a1,a2,a3]
        for key in 'x','y': # subtract lens potition - to be added back on later in each likelihood iteration!
            p[key] = dic[name+' '+key][a1,a2,a3]+lenses[0].pars[key]
            #p[key] = srcs[0].pars[key]
    srcs.append(SBBModels.Sersic(name,p))

npars = []
for i in range(len(npars)):
    pars[i].value = npars[i]


@pymc.deterministic
def logP(value=0.,p=pars):
    lp = 0.
    models = []
    dx = pars[0].value
    dy = pars[1].value 
    xp,yp = xc+dx,yc+dy
    sig1 = pars[2].value.item()
    q1 = pars[3].value.item()
    pa1 = pars[4].value.item()
    amp1 = pars[5].value.item()
    sig2 = pars[6].value.item()
    q2 = pars[7].value.item()
    pa2 = pars[8].value.item()
    amp2 = pars[9].value.item()
    sig3 = pars[10].value.item()
    q3 = pars[11].value.item()
    pa3 = pars[12].value.item()
    '''amp3 = pars[13].value.item()
    sig4 = pars[14].value.item()
    q4 = pars[15].value.item()
    pa4 = pars[16].value.item()'''
    amp3=1.-amp1-amp2#-amp3
    if amp3<0:
        return -1e10
    #print dx,dy,sig1,sig2,sig3,q1,q2,q3,pa1,pa2,pa3,amp1,amp2,amp3
    psfObj1 = SBObjects.Gauss('psf 1',{'x':0,'y':0,'sigma':sig1,'q':q1,'pa':pa1,'amp':10})
    psfObj2 = SBObjects.Gauss('psf 2',{'x':0,'y':0,'sigma':sig2,'q':q2,'pa':pa2,'amp':10})
    psfObj3 = SBObjects.Gauss('psf 3',{'x':0,'y':0,'sigma':sig3,'q':q3,'pa':pa3,'amp':10})
    #psfObj4 = SBObjects.Gauss('psf 4',{'x':0,'y':0,'sigma':sig4,'q':q4,'pa':pa4,'amp':10})

    psf1 = psfObj1.pixeval(xpsf,ypsf) * amp1 / (np.pi*2.*sig1**2.)
    psf2 = psfObj2.pixeval(xpsf,ypsf) * amp2 / (np.pi*2.*sig2**2.)
    psf3 = psfObj3.pixeval(xpsf,ypsf) * amp3 / (np.pi*2.*sig3**2.)
    #psf4 = psfObj4.pixeval(xpsf,ypsf) * amp4 / (np.pi*2.*sig4**2.)

    psf = psf1 + psf2 + psf3 #+ psf4
    psf /= psf.sum()
    psf = convolve.convolve(image,psf)[1]
    imin,sigin,xin,yin = image[mask], sigma[mask],xp[mask2],yp[mask2]
    n = 0
    model = np.empty(((len(gals) + len(srcs)+1),imin.size))
    for gal in gals:
        gal.setPars()
        tmp = xc*0.
        tmp[mask2] = gal.pixeval(xin,yin,1./OVRS,csub=1) # evaulate on the oversampled grid. OVRS = number of new pixels per old pixel.
        tmp = iT.resamp(tmp,OVRS,True) # convert it back to original size
        tmp = convolve.convolve(tmp,psf,False)[0]
        model[n] = tmp[mask].ravel()
        n +=1
    for lens in lenses:
        lens.setPars()
    x0,y0 = pylens.lens_images(lenses,srcs,[xin,yin],1./OVRS,getPix=True)
    kk=0
    for src in srcs:
        src.setPars()
        tmp = xc*0.
        tmp[mask2] = src.pixeval(x0,y0,1./OVRS,csub=1)
        tmp = iT.resamp(tmp,OVRS,True)
        tmp = convolve.convolve(tmp,psf,False)[0]
        model[n] = tmp[mask].ravel()
        n +=1
    model[n] = np.ones(model[n-1].shape)
    rhs = (imin/sigin) # data
    op = (model/sigin).T # model matrix
    fit, chi = optimize.nnls(op,rhs)
    model = (model.T*fit).sum(1)
    resid = (model-imin)/sigin
    lp = -0.5*(resid**2.).sum()
    return lp 
 
  
@pymc.observed
def likelihood(value=0.,lp=logP):
    return lp #[0]

def resid(p):
    lp = -2*logP.value
    return self.imgs[0].ravel()*0 + lp

optCov = None
if optCov is None:
    optCov = numpy.array(cov)

print len(cov), len(pars)

S = myEmcee.PTEmcee(pars+[likelihood],cov=optCov,nthreads=20,nwalkers=28,ntemps=3)
S.sample(500)
outFile = '/data/ljo31/Lens/J1218/KeckPSF_'+str(X)
f = open(outFile,'wb')
cPickle.dump(S.result(),f,2)
f.close()
result = S.result()
lp = result[0]
trace = numpy.array(result[1])
a1,a3 = numpy.unravel_index(lp[:,0].argmax(),lp[:,0].shape)
a2=0
for i in range(len(pars)):
    pars[i].value = trace[a1,a2,a3,i]
    print "%18s  %8.3f"%(pars[i].__name__,pars[i].value)

jj=0
for jj in range(10):
    S = myEmcee.PTEmcee(pars+[likelihood],cov=optCov,nthreads=20,nwalkers=28,ntemps=3,initialPars=trace[a1])
    S.sample(500)

    outFile = '/data/ljo31/Lens/J1218/KeckPSF_'+str(X)
    f = open(outFile,'wb')
    cPickle.dump(S.result(),f,2)
    f.close()

    result = S.result()
    lp = result[0]

    trace = numpy.array(result[1])
    a1,a3 = numpy.unravel_index(lp[:,0].argmax(),lp[:,0].shape)
    for i in range(len(pars)):
        pars[i].value = trace[a1,a2,a3,i]
    print jj
    jj+=1



dx = pars[0].value
dy = pars[1].value 
xp,yp = xc+dx,yc+dy
sig1 = pars[2].value.item()
q1 = pars[3].value.item()
pa1 = pars[4].value.item()
amp1 = pars[5].value.item()
sig2 = pars[6].value.item()
q2 = pars[7].value.item()
pa2 = pars[8].value.item()
amp2 = 1.-amp1
psfObj1 = SBObjects.Gauss('psf 1',{'x':0,'y':0,'sigma':sig1,'q':q1,'pa':pa1,'amp':10})
psfObj2 = SBObjects.Gauss('psf 2',{'x':0,'y':0,'sigma':sig2,'q':q2,'pa':pa2,'amp':10})
psf1 = psfObj1.pixeval(xpsf,ypsf) * amp1 / (np.pi*2.*sig1**2.)
psf2 = psfObj2.pixeval(xpsf,ypsf) * amp2 / (np.pi*2.*sig2**2.)
psf = psf1 + psf2
psf /= psf.sum()
psf = convolve.convolve(image,psf)[1]
dx = pars[0].value 
dy = pars[1].value 
xp,yp = xc+dx,yc+dy
xop,yop = xo+dy,yo+dy
imin,sigin,xin,yin = image.flatten(), sigma.flatten(),xp.flatten(),yp.flatten()
n = 0
model = np.empty(((len(gals) + len(srcs)),imin.size))
for gal in gals:
    gal.setPars()
    tmp = xc*0.
    tmp = gal.pixeval(xp,yp,1./OVRS,csub=1) # evaulate on the oversampled grid. OVRS = number of new pixels per old pixel.
    tmp = iT.resamp(tmp,OVRS,True) # convert it back to original size
    tmp = convolve.convolve(tmp,psf,False)[0]
    model[n] = tmp.ravel()
    n +=1
for lens in lenses:
    lens.setPars()
x0,y0 = pylens.lens_images(lenses,srcs,[xp,yp],1./OVRS,getPix=True)
for src in srcs:
    src.setPars()
    tmp = xc*0.
    tmp = src.pixeval(x0,y0,1./OVRS,csub=1)
    tmp = iT.resamp(tmp,OVRS,True)
    tmp = convolve.convolve(tmp,psf,False)[0]
    model[n] = tmp.ravel()
    n +=1
rhs = (imin/sigin) # data
op = (model/sigin).T # model matrix
fit, chi = optimize.nnls(op,rhs)
print fit
components = (model.T*fit).T.reshape((n,image.shape[0],image.shape[1]))
model = components.sum(0)
NotPlicely(image,model,sigma)
pl.show()
