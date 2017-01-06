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

#X=0
X=1 # lowering prior on sig2 as it hit it!
X=2 # lowering prior on sig4...
X=3 # adding two more components
X=4 # putting each component in a certain size window
X = 5 # starting walkers off in good places
print X

# plot things
def NotPlicely(image,im,sigma):
    ext = [0,image.shape[0],0,image.shape[1]]
    #vmin,vmax = numpy.amin(image), numpy.amax(image)
    pl.figure()
    pl.subplot(221)
    pl.imshow(image,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=0) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('data')
    pl.subplot(222)
    pl.imshow(im,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=0) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('model')
    pl.subplot(223)
    pl.imshow(image-im,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=-5)
    pl.colorbar()
    pl.title('data-model')
    pl.subplot(224)
    pl.imshow((image-im)/sigma,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=-10)
    pl.title('signal-to-noise residuals')
    pl.colorbar()

image = py.open('/data/ljo31/Lens/J1605/J1605_Kp_narrow_med.fits')[0].data.copy()[535:740,590:835]
sigma = np.ones(image.shape) 

result = np.load('/data/ljo31/Lens/LensModels/J1605_211')
lp= result[0]
a2=0
a1,a3 = numpy.unravel_index(lp[:,0].argmax(),lp[:,0].shape)
trace = result[1]
dic = result[2]

kresult = np.load('/data/ljo31/Lens/J1605/KeckPSF_4')
klp= kresult[0]
ka2=0
ka1,ka3 = numpy.unravel_index(klp[:,0].argmax(),klp[:,0].shape)
ktrace = kresult[1]
kdic = kresult[2]
xoffset,yoffset,sig1,q1,pa1,amp1,sig2,q2,pa2,amp2,sig3,q3,pa3,amp3,sig4,q4,pa4,amp4,sig5,q5,pa5,amp5,sig6,q6,pa6 = ktrace[ka1,ka2,ka3]

OVRS = 1
yc,xc = iT.overSample(image.shape,OVRS)
yo,xo = iT.overSample(image.shape,1)
xc,xo,yc,yo=xc*0.2,xo*0.2,yc*0.2,yo*0.2
xc,xo,yc,yo = xc+4,xo+4,yc+5,yo+5
mask = np.zeros(image.shape)
tck = RectBivariateSpline(yo[:,0],xo[0],mask)
mask2 = tck.ev(xc,yc)
mask2[mask2<0.5] = 0
mask2[mask2>0.5] = 1
mask2 = mask2==0
mask = mask==0

pars = []
cov = []
### four PSF components
pars.append(pymc.Normal('xoffset',mu=xoffset,tau=1,value=xoffset))
pars.append(pymc.Normal('yoffset',mu=yoffset,tau=1,value=yoffset))
cov += [0.4,0.4]
#psf1
pars.append(pymc.TruncatedNormal('sigma 1',mu=sig1,tau=2.,value=sig1,a=0))
pars.append(pymc.TruncatedNormal('q 1',mu=q1,tau=2.,value=q1,a=0))
pars.append(pymc.TruncatedNormal('pa 1',mu=pa1,tau=5.,value=pa1,a=-180,b=180))
pars.append(pymc.TruncatedNormal('amp 1',mu=amp1,tau=0.2,value=amp1,a=0))
cov +=[1,0.5,50,0.5]
# psf2
pars.append(pymc.TruncatedNormal('sigma 2',mu=sig2,tau=2.,value=sig2,a=0))
pars.append(pymc.TruncatedNormal('q 2',mu=q2,tau=2.,value=q2,a=0))
pars.append(pymc.TruncatedNormal('pa 2',mu=pa2,tau=5.,value=pa2,a=-180,b=180))
pars.append(pymc.TruncatedNormal('amp 2',mu=amp2,tau=0.2,value=amp2,a=0))
cov +=[2,0.5,50,0.5]
# psf3
pars.append(pymc.TruncatedNormal('sigma 3',mu=sig3,tau=2.,value=sig3,a=0))
pars.append(pymc.TruncatedNormal('q 3',mu=q3,tau=2.,value=q3,a=0))
pars.append(pymc.TruncatedNormal('pa 3',mu=pa3,tau=5.,value=pa3,a=-180,b=180))
pars.append(pymc.TruncatedNormal('amp 3',mu=amp3,tau=0.2,value=amp3,a=0))
cov +=[2,0.5,50,0.5]
# psf4
pars.append(pymc.TruncatedNormal('sigma 4',mu=sig4,tau=2.,value=sig4,a=0))
pars.append(pymc.TruncatedNormal('q 4',mu=q4,tau=2.,value=q4,a=0))
pars.append(pymc.TruncatedNormal('pa 4',mu=pa4,tau=5.,value=pa4,a=-180,b=180))
pars.append(pymc.TruncatedNormal('amp 4',mu=amp4,tau=0.2,value=amp4,a=0))
cov +=[2,0.5,50,0.5]
# psf5
pars.append(pymc.TruncatedNormal('sigma 5',mu=sig5,tau=2.,value=sig5,a=0))
pars.append(pymc.TruncatedNormal('q 5',mu=q5,tau=2.,value=q5,a=0))
pars.append(pymc.TruncatedNormal('pa 5',mu=pa5,tau=5.,value=pa5,a=-180,b=180))
pars.append(pymc.TruncatedNormal('amp 5',mu=amp5,tau=0.2,value=amp5,a=0))
cov +=[2,0.5,50,0.5]
# psf6
pars.append(pymc.TruncatedNormal('sigma 6',mu=sig6,tau=2.,value=sig6,a=0))
pars.append(pymc.TruncatedNormal('q 6',mu=q6,tau=2.,value=q6,a=0))
pars.append(pymc.TruncatedNormal('pa 6',mu=pa6,tau=5.,value=pa6,a=-180,b=180))
cov +=[2,0.5,50]



psfObj1 = SBObjects.Gauss('psf 1',{'x':0,'y':0,'sigma':pars[2],'q':pars[3],'pa':pars[4],'amp':pars[5]})
psfObj2 = SBObjects.Gauss('psf 2',{'x':0,'y':0,'sigma':pars[6],'q':pars[7],'pa':pars[8],'amp':pars[9]})
psfObj3 = SBObjects.Gauss('psf 3',{'x':0,'y':0,'sigma':pars[10],'q':pars[11],'pa':pars[12],'amp':pars[13]})
psfObj4 = SBObjects.Gauss('psf 4',{'x':0,'y':0,'sigma':pars[14],'q':pars[15],'pa':pars[16],'amp':pars[17]})
psfObj5 = SBObjects.Gauss('psf 4',{'x':0,'y':0,'sigma':pars[18],'q':pars[19],'pa':pars[20],'amp':pars[21]})
psfObj6 = SBObjects.Gauss('psf 4',{'x':0,'y':0,'sigma':pars[22],'q':pars[23],'pa':pars[24],'amp':1.-pars[5]-pars[9]-pars[13]-pars[17]-pars[21]})

psfObjs = [psfObj1,psfObj2,psfObj3,psfObj4,psfObj5,psfObj6]

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
        for key in 'q','re','n','pa':
           p[key] = dic[name+' '+key][a1,a2,a3]
        for key in 'x','y': # subtract lens potition - to be added back on later in each likelihood iteration!
            p[key] = dic[name+' '+key][a1,a2,a3]+lenses[0].pars[key]
    elif name == 'Source 1':
        for key in 'q','re','n','pa':
           p[key] = dic[name+' '+key][a1,a2,a3]
        for key in 'x','y': # subtract lens potition - to be added back on later in each likelihood iteration!
            p[key] = dic[name+' '+key][a1,a2,a3]+lenses[0].pars[key]
            #p[key] = srcs[0].pars[key]
    srcs.append(SBBModels.Sersic(name,p))

xpsf,ypsf = iT.coords((221,221))-110

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
    psf = xpsf*0.
    for obj in psfObjs:
        obj.setPars()
        psf += obj.pixeval(xpsf,ypsf) / (np.pi*2.*obj.pars['sigma'].value**2.)
    if obj.pars['amp'].value<0:
        return -1e10
    psf = psf/np.sum(psf)
    #print obj.pars['q'].value, obj.pars['amp'].value
    psf = convolve.convolve(image,psf)[1]
    imin,sigin,xin,yin = image[mask], sigma[mask],xp[mask2],yp[mask2]
    n = 0
    model = np.empty(((len(gals) + len(srcs)+1),imin.size))
    for gal in gals:
        gal.setPars()
        tmp = xc*0.
        tmp[mask2] = gal.pixeval(xin,yin,1./OVRS,csub=11) # evaulate on the oversampled grid. OVRS = number of new pixels per old pixel.
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
        tmp[mask2] = src.pixeval(x0,y0,1./OVRS,csub=11)
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

S = myEmcee.PTEmcee(pars+[likelihood],cov=optCov,nthreads=20,nwalkers=50,ntemps=3)
print 'set up sampler'
S.sample(500)
outFile = '/data/ljo31/Lens/J1605/KeckPSF_'+str(X)
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
for jj in range(20):
    S = myEmcee.PTEmcee(pars+[likelihood],cov=optCov,nthreads=20,nwalkers=50,ntemps=3,initialPars=trace[a1])
    S.sample(500)

    outFile = '/data/ljo31/Lens/J1605/KeckPSF_'+str(X)
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
psf = xpsf*0.
for obj in psfObjs:
    obj.setPars()
    psf += obj.pixeval(xpsf,ypsf) / (np.pi*2.*obj.pars['sigma'].value**2.)
psf = psf/np.sum(psf)
print 'ici',obj.pars['q'].value
psf = convolve.convolve(image,psf)[1]
xp,yp = xc+dx,yc+dy
xop,yop = xo+dy,yo+dy
imin,sigin,xin,yin = image.flatten(), sigma.flatten(),xp.flatten(),yp.flatten()
n = 0
model = np.empty(((len(gals) + len(srcs)),imin.size))
for gal in gals:
    gal.setPars()
    tmp = xc*0.
    tmp = gal.pixeval(xp,yp,1./OVRS,csub=11) # evaulate on the oversampled grid. OVRS = number of new pixels per old pixel.
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
    tmp = src.pixeval(x0,y0,1./OVRS,csub=11)
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
