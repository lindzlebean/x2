import numpy as np, pylab as pl, pyfits as py
from imageSim import SBObjects, convolve
from astropy.io import fits
from astropy.wcs import WCS
import indexTricks as iT
import pymc
from scipy import optimize, ndimage
import myEmcee_blobs as myEmcee
import cPickle
from linslens import Plotter, EELsModels as L

### use our best models for each source
# nb. if there are two components at very different pas, we might have to use the single source model.
results = ['J0837_211','J0901_211','J0913_212','/dump/J1125_212_nonconcentric','J1144_212_allparams','J1218_211','J1323_212','J1347_112','J1446_212','J1605_212_final','J1606_112','J2228_212']
names = py.open('/data/ljo31/Lens/LensParams/Phot_1src.fits')[1].data['name']

# 3 is good
# 4 is with Gaussian noise added and realistic noise maps!
# 5 again with arbitrary weighting/gain -- need to get this from weight image though!

for i in range(3,names.size):
    name=names[i]
    print name
    result = np.load('/data/ljo31/Lens/LensModels/'+results[i])
    model = L.EELs(result,name)
    model.Initialise()
    V,I = model.unlensedeval()
    whtV,whtI = model.AddWeightImages()
    #Dx,Dy = model.Dx, model.Dy
    #PSFs = model.PSFs
    psf1,psf2 = model.psf1,model.psf2
    psfs=[psf1,psf2]
    ## add noise to image abd create noisemaps
    sigmaV,sigmaI = np.mean(model.sig1[:10,:10]),np.mean(model.sig2[:10,:10])
    V, I = V + np.random.randn(V.shape[0],V.shape[1])*sigmaV, I + np.random.randn(I.shape[0],I.shape[1])*sigmaI
    smoothV, smoothI = ndimage.gaussian_filter(V,0.7),ndimage.gaussian_filter(I,0.7) 
    sig1 = np.where((smoothV>0.7*sigmaV)&(V>0),V/whtV+sigmaV**2., sigmaV**2)**0.5
    sig2 = np.where((smoothI>0.7*sigmaI)&(I>0),I/whtI+sigmaI**2., sigmaI**2)**0.5
    sig1[np.isnan(sig1)] = 1
    sig2[np.isnan(sig2)] = 1
    sig1[~np.isfinite(sig1)] = 1
    sig2[~np.isfinite(sig2)] = 1
    imgs = [V,I]
    sigs = [sig1,sig2]
    yo,xo = iT.overSample(V.shape,1)
    x0,y0 = 0.5*np.amax(xo),0.5*np.amax(yo)
    PSFs = []
    for i in range(len(imgs)):
        psf = psfs[i]
        image = imgs[i]
        psf /= psf.sum()
        psf = convolve.convolve(image,psf)[1]
        PSFs.append(psf)
    pars,cov = [],[]
    pars.append(pymc.Uniform('x',0,100,value=50.1))
    pars.append(pymc.Uniform('y',0,100,value=50.1))
    pars.append(pymc.Uniform('pa',-180,180,value=0))
    pars.append(pymc.Uniform('q',0.05,1.,value=0.9))
    pars.append(pymc.Uniform('re',0.5,100,value=10.1))
    pars.append(pymc.Uniform('n',0.5,12,value=4.))
    #pars.append(pymc.Uniform('amp',1e-3,1,value=0.01))
    pars.append(pymc.Uniform('xoffset',-5.,5.,value=1.))
    pars.append(pymc.Uniform('yoffset',-5.,5.,value=1.))
    cov += [2.,2.,50.,0.1,10.,1.,0.5,0.5]
    optCov=np.array(cov)
    gal = SBObjects.Sersic('Galaxy',{'x':pars[0],'y':pars[1],'pa':pars[2],'q':pars[3],'re':pars[4],'n':pars[5]})
    gal.setPars()
    npars = []
    for j in range(len(npars)):
        pars[j].value = npars[j]
    
    @pymc.deterministic
    def logP(value=0.,p=pars):
        lp = 0
        gal.setPars()
        for i in range(2):
            if i == 0:
                dx,dy = 0,0
            else:
                dx = pars[-2].value
                dy = pars[-1].value
            #xp,yp = xo+dx+Dx,yo+dy+Dy
            xp,yp = xo+dx,yo+dy
            image,sigma,psf = imgs[i],sigs[i],PSFs[i]
            imin,sigin,xin,yin = image.flatten(), sigma.flatten(),xp.flatten(),yp.flatten()
            model = np.zeros((1,imin.size))
            tmp = xp*0.
            tmp = gal.pixeval(xin,yin,csub=23).reshape(xp.shape)
            tmp = convolve.convolve(tmp,psf,False)[0]
            model[0] = tmp.ravel()
            rhs = (imin/sigin) # data
            op = (model/sigin).T # model matrix
            fit, chi = optimize.nnls(op,rhs)
            model = (model.T*fit).sum(1)
            resid = (model-imin)/sigin
            lp += -0.5*(resid**2.).sum()
        return lp

    @pymc.observed
    def likelihood(value=0.,lp=logP):
        return lp 


    S = myEmcee.PTEmcee(pars+[likelihood],cov=optCov,nthreads=20,nwalkers=26,ntemps=3)
    S.sample(20000)
    outFile = '/data/ljo31/Lens/Analysis/fit_unlensed_src_5_'+str(name)
    f = open(outFile,'wb')
    cPickle.dump(S.result(),f,2)
    f.close()
    
    result = S.result()
    lp,trace,dic,_ = result
    a1,a3 = np.unravel_index(lp[:,0].argmax(),lp[:,0].shape)
    a2=0
    for i in range(len(pars)):
        pars[i].value = trace[a1,a2,a3,i]
        print "%18s  %8.3f"%(pars[i].__name__,pars[i].value)

    pl.figure()
    pl.plot(lp[:,0])

    gal.setPars()
    for i in range(2):
        if i == 0:
            dx,dy = 0,0
        else:
            dx = pars[-2].value
            dy = pars[-1].value 
        xp,yp = xo+dx,yo+dy
        image,sigma,psf = imgs[i],sigs[i],PSFs[i]
        imin,sigin,xin,yin = image.flatten(), sigma.flatten(),xp.flatten(),yp.flatten()
        model = np.zeros((1,imin.size))
        tmp = xp*0.
        tmp = gal.pixeval(xin,yin,csub=23).reshape(xp.shape)
        tmp = convolve.convolve(tmp,psf,False)[0]
        model[0] = tmp.ravel()
        rhs = (imin/sigin) 
        op = (model/sigin).T
        fit, chi = optimize.nnls(op,rhs)
        components = (model.T*fit).T.reshape((1,image.shape[0],image.shape[1]))
        model = components.sum(0)
        Plotter.SotPleparately(image,model,sigma,name,vmin=-2.5,vmax=2.5)

        pl.show()
'''
 outFile = '/data/ljo31b/MACSJ0717/models/model_'+str(name)+'_'+str(i)+'.fits'
 f = open(outFile,'wb')
 cPickle.dump(model,f,2)
    f.close()
    outFile = '/data/ljo31b/MACSJ0717/models/fit_'+str(name)+'_'+str(i)
    f = open(outFile,'wb')
    cPickle.dump(fit,f,2)
    f.close()
'''
