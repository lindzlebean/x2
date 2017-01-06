import cPickle,numpy,pyfits as py
import pymc
from pylens import *
from imageSim import SBModels,convolve,SBObjects
import indexTricks as iT
import pylab as pl
import numpy as np
import myEmcee_blobs as myEmcee
from scipy import optimize
from scipy.interpolate import RectBivariateSpline
import SBBModels, SBBProfiles

X = 5
print X

# plot things
def NotPlicely(image,im,sigma):
    ext = [0,image.shape[0],0,image.shape[1]]
    #vmin,vmax = numpy.amin(image), numpy.amax(image)
    pl.figure()
    pl.subplot(221)
    pl.imshow(image,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=0,vmax=np.amax(image)*0.99) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('data')
    pl.subplot(222)
    pl.imshow(im,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',vmin=0,vmax=np.amax(image)*0.99) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('model')
    pl.subplot(223)
    pl.imshow(image-im,origin='lower',interpolation='nearest',extent=ext,vmin=-50,vmax=50,cmap='afmhot',aspect='auto')
    pl.colorbar()
    pl.title('data-model')
    pl.subplot(224)
    pl.imshow((image-im)/sigma,origin='lower',interpolation='nearest',extent=ext,vmin=-75,vmax=75,cmap='afmhot',aspect='auto')
    pl.title('signal-to-noise residuals')
    pl.colorbar()



img = py.open('/data/ljo31b/lenses/J010127-334319_r_osj.fits')[0].data[460:-460,430:-490]/10.
bg=np.median(img[-10:,0:10])
img-=bg
sig = np.ones(img.shape)
sig[50:79,25:85] = 1e4
sig[10:30,0:15] = 1e4
psf = py.open('/data/ljo31b/lenses/r_psf1.fits')[0].data

psf /= psf.sum()
psf = convolve.convolve(img,psf)[1]

y,x = iT.overSample(img.shape,1)

rhs = (img/sig).ravel()
sflt = sig.ravel()
xflt = x.ravel()
yflt = y.ravel()

result = np.load('/data/ljo31b/lenses/model_3')
lp,trace,dic,_= result
a2=0
a1,a3 = numpy.unravel_index(lp[:,0].argmax(),lp[:,0].shape)

pars = []
cov = []

GX = pymc.Uniform('GX',dic['Galaxy 1 x'][a1,a2,a3]-10.,dic['Galaxy 1 x'][a1,a2,a3]+10.,dic['Galaxy 1 x'][a1,a2,a3])
GY = pymc.Uniform('GY',dic['Galaxy 1 y'][a1,a2,a3]-10.,dic['Galaxy 1 y'][a1,a2,a3]+10.,dic['Galaxy 1 y'][a1,a2,a3])
GR = pymc.Uniform('GR',0.5,100.,dic['Galaxy 1 re'][a1,a2,a3])
GN = pymc.Uniform('GN',0.5,12.,dic['Galaxy 1 n'][a1,a2,a3])
GP = pymc.Uniform('GP',-180,180.,dic['Galaxy 1 pa'][a1,a2,a3])
GQ = pymc.Uniform('GQ',0.1,1.,dic['Galaxy 1 q'][a1,a2,a3])

LB = pymc.Uniform('LB',0.5,100,dic['Lens 1 b'][a1,a2,a3])
LQ = pymc.Uniform('LQ',0.1,1.,dic['Lens 1 q'][a1,a2,a3])
LP = pymc.Uniform('LP',-180,180.,dic['Lens 1 pa'][a1,a2,a3])
#LETA = pymc.Uniform('LETA',0.5,1.7,dic['Lens 1 eta'][a1,a2,a3])

SX = pymc.Uniform('SX',dic['Galaxy 1 x'][a1,a2,a3]-15,dic['Galaxy 1 x'][a1,a2,a3]+15,dic['Source 1 x'][a1,a2,a3]+dic['Lens 1 x'][a1,a2,a3])
SY = pymc.Uniform('SY',dic['Galaxy 1 y'][a1,a2,a3]-15,dic['Galaxy 1 y'][a1,a2,a3]+15,dic['Source 1 y'][a1,a2,a3]+dic['Lens 1 y'][a1,a2,a3])
SR = pymc.Uniform('SR',0.5,100,dic['Source 1 re'][a1,a2,a3])
SN = pymc.Uniform('SN',0.5,8,dic['Source 1 n'][a1,a2,a3])
SP = pymc.Uniform('SP',-180,180,dic['Source 1 pa'][a1,a2,a3])
SQ = pymc.Uniform('SQ',0.2,1.,dic['Source 1 q'][a1,a2,a3])

LB2 = pymc.Uniform('LB2',0.5,100,dic['Lens 1 b'][a1,a2,a3])
BETA = pymc.Uniform('beta',1.2,3,value=2.3)

SX2 = pymc.Uniform('SX2',dic['Galaxy 1 x'][a1,a2,a3]-10.,dic['Galaxy 1 x'][a1,a2,a3]+10.,dic['Source 1 x'][a1,a2,a3]+dic['Lens 1 x'][a1,a2,a3])
SY2 = pymc.Uniform('SY2',dic['Galaxy 1 y'][a1,a2,a3]-10.,dic['Galaxy 1 y'][a1,a2,a3]+10.,dic['Source 1 y'][a1,a2,a3]+dic['Lens 1 y'][a1,a2,a3])
SR2 = pymc.Uniform('SR2',0.5,100,3.)

pars = [GX,GY,GR,GQ,GP,GN,LB,LQ,LP,SX,SY,SR,SN,SP,SQ,LB2,BETA,SX2,SY2,SR2]
cov = [0.1,0.1,0.5,0.05,1.,0.5,0.2,0.05,1.,0.1,0.1,0.5,0.2,1.,0.05,0.5,0.1,0.1,0.1,0.5]

print len(pars), len(cov)

result = np.load('/data/ljo31b/lenses/model_twolens_2')
lp,trace,dic,_= result
a2=0
a1,a3 = numpy.unravel_index(lp[:,0].argmax(),lp[:,0].shape)

#for i in range(len(pars)):
#    pars[i].value = trace[a1,a2,a3,i]
#    print "%18s  %8.3f"%(pars[i].__name__,pars[i].value)

gal = SBObjects.Sersic('G1',{'x':GX,'y':GY,'re':GR,'q':GQ,'pa':GP,'n':GN})
src = SBObjects.Sersic('S1',{'x':SX,'y':SY,'re':SR,'q':SQ,'pa':SP,'n':SN})
src2 = SBObjects.Sersic('S2',{'x':SX2,'y':SY2,'re':SR2,'q':1.,'pa':0.,'n':1.})

lens = MassModels.PowerLaw('L1',{'x':GX,'y':GY,'b':LB,'q':LQ,'pa':LP,'eta':1.})
lens2 = MassModels.PowerLaw('L2',{'x':SX,'y':SY,'b':LB2,'q':1.,'pa':0.,'eta':1.})

def getModel(getResid=False):
    gal.setPars()
    src.setPars()
    src2.setPars()
    lens.setPars()
    lens2.setPars()

    #xl,yl = pylens.getDeflections([lens],[x,y])
    ax,ay = lens.deflections(x,y)

    lx = x-ax
    ly = y-ay

    ax2,ay2 = lens2.deflections(lx,ly)

    lx2 = x-BETA.value*ax-ax2
    ly2 = y-BETA.value*ay-ay2

    model = numpy.empty((sflt.size,4))
    model[:,0] = convolve.convolve(gal.pixeval(x,y),psf,False)[0].ravel()/sflt
    model[:,1] = convolve.convolve(src.pixeval(lx,ly),psf,False)[0].ravel()/sflt
    model[:,2] = convolve.convolve(src2.pixeval(lx2,ly2),psf,False)[0].ravel()/sflt
    model[:,3] = np.ones(model[:,3].shape)

    fit,chi = optimize.nnls(model,rhs)
    if getResid is True:
        print fit
        fit[2] = 10.
        return (model.T*sflt).T*fit
    return chi

@pymc.observed
def logl(value=0.,tmp=pars):
    return -0.5*getModel()**2

'''result = np.load('/data/ljo31b/lenses/model_twolens_0')
lp = result[0]
trace = numpy.array(result[1])
a1,a3 = numpy.unravel_index(lp[:,0].argmax(),lp[:,0].shape)
a2=0
for i in range(len(pars)):
    pars[i].value = trace[a1,a2,a3,i]
    print "%18s  %8.3f"%(pars[i].__name__,pars[i].value)
'''


S = myEmcee.PTEmcee(pars+[logl],cov=np.array(cov),nthreads=8,nwalkers=40,ntemps=3)
S.sample(500)
outFile = '/data/ljo31b/lenses/model_twolens_'+str(X)
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
for jj in range(30):
    S.p0 = trace[-1]
    print 'sampling'
    S.sample(1000)

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

# now need to work out how to evaluate this and plot something...
def plotModel(getResid=False):
    gal.setPars()
    src.setPars()
    src2.setPars()
    lens.setPars()
    lens2.setPars()

    ax,ay = lens.deflections(x,y)

    lx = x-ax
    ly = y-ay

    ax2,ay2 = lens2.deflections(lx,ly)

    lx2 = x-BETA.value*ax-ax2
    ly2 = y-BETA.value*ay-ay2

    model = numpy.empty((sflt.size,4))
    model[:,0] = convolve.convolve(gal.pixeval(x,y),psf,False)[0].ravel()/sflt
    model[:,1] = convolve.convolve(src.pixeval(lx,ly),psf,False)[0].ravel()/sflt
    model[:,2] = convolve.convolve(src2.pixeval(lx2,ly2),psf,False)[0].ravel()/sflt
    model[:,3] = np.ones(model[:,3].shape)

    fit,chi = optimize.nnls(model,rhs)

    components = (model*fit).T.reshape((4,img.shape[0],img.shape[1]))
    model = components.sum(0)
    NotPlicely(img,model,sig)
    pl.show()


plotModel()
