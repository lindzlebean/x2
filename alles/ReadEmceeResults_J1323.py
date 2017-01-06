import cPickle,numpy,pyfits
import pymc
from pylens import *
from imageSim import SBModels,convolve
import indexTricks as iT
import pylab as pl
import numpy as np
import lensModel2
from matplotlib.colors import LogNorm

def NotPlicely(image,im,sigma):
    ext = [0,image.shape[0],0,image.shape[1]]
    #vmin,vmax = numpy.amin(image), numpy.amax(image)
    pl.figure()
    pl.subplot(221)
    pl.imshow(image,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',norm=LogNorm(),vmin=1e-3,vmax=1e2) #,vmin=0,vmax=1) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('data')
    pl.subplot(222)
    pl.imshow(im,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',aspect='auto',norm=LogNorm(),vmin=1e-3,vmax=1e2) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('model')
    pl.subplot(223)
    #pl.imshow((image-im)/sigma,origin='lower',interpolation='nearest',extent=ext,vmin=-3,vmax=3,cmap='afmhot',aspect='auto')
    #pl.colorbar()
    #pl.title('signal-to-noise residuals 1')
    pl.imshow((image-im),origin='lower',interpolation='nearest',extent=ext,vmin=-0.3,vmax=0.3,cmap='afmhot',aspect='auto')
    pl.colorbar()
    pl.title('data-model')
    #pl.colorbar()
    #pl.title('signal-to-noise residuals 1')
    pl.subplot(224)
    pl.imshow((image-im)/sigma,origin='lower',interpolation='nearest',extent=ext,vmin=-5,vmax=5,cmap='afmhot',aspect='auto')
    pl.title('signal-to-noise residuals 2')
    pl.colorbar()

def SotPleparately(image,im,sigma,col):
    ext = [0,image.shape[0],0,image.shape[1]]
    pl.figure()
    pl.imshow(image,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',vmin=0) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('data - '+str(col))
    pl.figure()
    pl.imshow(im,origin='lower',interpolation='nearest',extent=ext,cmap='afmhot',vmin=0) #,vmin=vmin,vmax=vmax)
    pl.colorbar()
    pl.title('model - '+str(col))
    pl.figure()
    pl.imshow((image-im)/sigma,origin='lower',interpolation='nearest',extent=ext,vmin=-5,vmax=5,cmap='afmhot')
    pl.title('signal-to-noise residuals - '+str(col))
    pl.colorbar()

result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee3'))
#result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee4'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee5'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee12'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee13'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee14'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee16'))
#result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee18'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee23'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee24'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee25'))
#result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee28'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee26'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee32'))
#result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee25'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee37'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee32'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee45'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee48'))
#result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee47'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee49'))
result = cPickle.load(open('/data/ljo31/Lens/J1323/emcee53'))



lp= result[0]

a1,a2 = numpy.unravel_index(lp.argmax(),lp.shape)
trace = result[1]
dic = result[2]
dx,dy = dic['xoffset'][a1,a2], dic['yoffset'][a1,a2]
x1,y1,re1,n1,pa1,q1 = dic['Source 2 x'][a1,a2], dic['Source 2 y'][a1,a2], dic['Source 1 re'][a1,a2], dic['Source 1 n'][a1,a2], dic['Source 1 pa'][a1,a2], dic['Source 1 q'][a1,a2]
re5,n5,pa5,q5 = dic['Source 2 re'][a1,a2], dic['Source 2 n'][a1,a2], dic['Source 2 pa'][a1,a2], dic['Source 2 q'][a1,a2]
x2,y2,re2,n2,pa2,q2 = dic['Galaxy 1 x'][a1,a2], dic['Galaxy 1 y'][a1,a2], dic['Galaxy 1 re'][a1,a2], dic['Galaxy 1 n'][a1,a2], dic['Galaxy 1 pa'][a1,a2], dic['Galaxy 1 q'][a1,a2]
re3,n3,pa3,q3 = dic['Galaxy 2 re'][a1,a2], dic['Galaxy 2 n'][a1,a2], dic['Galaxy 2 pa'][a1,a2], dic['Galaxy 2 q'][a1,a2]
#re6,n6,pa6,q6 = dic['Galaxy 3 re'][a1,a2], dic['Galaxy 3 n'][a1,a2], dic['Galaxy 3 pa'][a1,a2], dic['Galaxy 3 q'][a1,a2]
x4,y4,b,eta,pa4,q4 = dic['Lens 1 x'][a1,a2], dic['Lens 1 y'][a1,a2], dic['Lens 1 b'][a1,a2], dic['Lens 1 eta'][a1,a2], dic['Lens 1 pa'][a1,a2], dic['Lens 1 q'][a1,a2]
shear,shearpa = dic['extShear'][a1,a2], dic['extShear PA'][a1,a2]

'''
# single-source
if trace.shape[-1] == 25:
    dx,dy,x1,y1,q1,re1,n1,pa1,x2,y2,q2,pa2,re2,n2,q3,pa3,re3,n3,x4,y4,q4,pa4,b,shear,shearpa = trace[a1,a2,:]

# double-source
elif trace.shape[-1] == 30:
    dx,dy,x1,y1,q1,re1,n1,pa1,q5,re5,n5,pa5,x2,y2,q2,pa2,re2,n2,q3,pa3,re3,n3,x4,y4,q4,pa4,b,eta,shear,shearpa = trace[a1,a2,:]
    print 'q',q5,'pa',pa5,'re',re5,'n',n5,'eta',eta,'b',b

## triple-galaxy, double source
elif trace.shape[-1] == 34:
    dx,dy,x1,y1,q1,re1,n1,pa1,q5,re5,n5,pa5,x2,y2,q2,pa2,re2,n2,q3,pa3,re3,n3,q6,pa6,re6,n6,x4,y4,q4,pa4,b,eta,shear,shearpa = trace[a1,a2,:]
'''
srcs,gals,lenses = [],[],[]
print dx,dy,x1,y1,q1,re1,n1,pa1,x2,y2,q2,re2,n2,pa2,q3,pa3,re3,n3,x4,y4,q4,pa4,b,shear,shearpa
srcs.append(SBModels.Sersic('Source 1', {'x':x1,'y':y1,'q':q1,'pa':pa1,'re':re1,'n':n1}))
srcs.append(SBModels.Sersic('Source 2', {'x':x1,'y':y1,'q':q5,'pa':pa5,'re':re5,'n':n5}))
gals.append(SBModels.Sersic('Galaxy 1', {'x':x2,'y':y2,'q':q2,'pa':pa2,'re':re2,'n':n2}))
gals.append(SBModels.Sersic('Galaxy 2', {'x':x2,'y':y2,'q':q3,'pa':pa3,'re':re3,'n':n3}))
if trace.shape[-1] == 34:
    gals.append(SBModels.Sersic('Galaxy 3', {'x':x2,'y':y2,'q':q6,'pa':pa6,'re':re6,'n':n6}))
lenses.append(MassModels.PowerLaw('Lens 1', {'x':x4,'y':y4,'q':q4,'pa':pa4,'b':b,'eta':eta}))
lenses.append(MassModels.ExtShear('shear',{'x':x4,'y':y4,'b':shear, 'pa':shearpa}))



img1 = pyfits.open('/data/ljo31/Lens/J1323/SDSSJ1323+3946_F555W_sci_cutout.fits')[0].data.copy()
sig1 = pyfits.open('/data/ljo31/Lens/J1323/SDSSJ1323+3946_F555W_noisemap.fits')[0].data.copy()
psf1 = pyfits.open('/data/ljo31/Lens/J1323/SDSSJ1323+3946_F555W_psf2.fits')[0].data.copy()
psf1 = psf1[10:-10,11:-10] # possibly this is too small? See how it goes
psf1 = psf1/np.sum(psf1)

img2 = pyfits.open('/data/ljo31/Lens/J1323/SDSSJ1323+3946_F814W_sci_cutout.fits')[0].data.copy()
sig2 = pyfits.open('/data/ljo31/Lens/J1323/SDSSJ1323+3946_F814W_noisemap.fits')[0].data.copy()
psf2 = pyfits.open('/data/ljo31/Lens/J1323/SDSSJ1323+3946_F814W_psf2.fits')[0].data.copy()
psf2 = pyfits.open('/data/ljo31/Lens/J1323/SDSSJ1323+3946_F814W_psf3.fits')[0].data.copy()

psf2 = psf2[8:-8,9:-8]
psf2 /= psf2.sum()

imgs = [img1,img2]
sigs = [sig1,sig2]
psfs = [psf1,psf2]

PSFs = []
OVRS = 3
yc,xc = iT.overSample(img1.shape,OVRS)
yc,xc = yc,xc
for i in range(len(imgs)):
    psf = psfs[i]
    image = imgs[i]
    psf /= psf.sum()
    psf = convolve.convolve(image,psf)[1]
    PSFs.append(psf)

lp = 0.
for i in range(len(imgs)):
        if i == 0:
            x0,y0 = 0,0
        else:
            x0 = dx
            y0 = dy
            print x0,y0
        image = imgs[i]
        sigma = sigs[i]
        psf = PSFs[i]
        lp += lensModel.lensFit(None,image,sigma,gals,lenses,srcs,xc+x0,yc+y0,OVRS,verbose=False,psf=psf,csub=1)

print 'lp = ', lp
# lp = -8686

# plot figures
logp,coeffs,dic,vals = result
ii = np.where(logp==np.amax(logp))
coeff = coeffs[ii][0]

ims = []
models = []
for i in range(len(imgs)):
    image = imgs[i]
    sigma = sigs[i]
    psf = PSFs[i]
    print psf.shape, sigma.shape,image.shape
    if i == 0:
        x0,y0 = 0,0
    else:
        x0,y0 = dic['xoffset'][ii][0], dic['yoffset'][ii][0]
    im = lensModel.lensFit(None,image,sigma,gals,lenses,srcs,xc+x0,yc+y0,OVRS,psf=psf,verbose=True)
    im = lensModel.lensFit(coeff,image,sigma,gals,lenses,srcs,xc+x0,yc+y0,OVRS,noResid=True,psf=psf,verbose=True) # return model
    model = lensModel.lensFit(coeff,image,sigma,gals,lenses,srcs,xc+x0,yc+y0,OVRS,noResid=True,psf=psf,verbose=True,getModel=True,showAmps=True) # return the model decomposed into the separate galaxy and source components
    print lensModel2.lensFit(coeff,image,sigma,gals,lenses,srcs,xc+x0,yc+y0,OVRS,noResid=True,psf=psf,verbose=True,getModel=True,showAmps=True)
    ims.append(im)
    models.append(model)

colours = ['F606W', 'F814W']
for i in range(len(imgs)):
    image = imgs[i]
    im = ims[i]
    model = models[i]
    sigma = sigs[i]
    #pyfits.PrimaryHDU(model).writeto('/data/ljo31/Lens/J1347/components_uniform'+str(colours[i])+str(X)+'.fits',clobber=True)
    #pyfits.PrimaryHDU(im).writeto('/data/ljo31/Lens/J1347/model_uniform'+str(colours[i])+str(X)+'.fits',clobber=True)
    #pyfits.PrimaryHDU(image-im).writeto('/data/ljo31/Lens/J1347/resid_uniform'+str(colours[i])+str(X)+'.fits',clobber=True)
    #f = open('/data/ljo31/Lens/J1347/coeff'+str(X),'wb')
    #cPickle.dump(coeff,f,2)
    #f.close()
    SotPleparately(image,im,sigma,colours[i])
    pl.suptitle(str(colours[i]))
    pl.show()

print 'source 1 ', '&', '%.2f'%x1, '&',  '%.2f'%y1, '&', '%.2f'%n1, '&', '%.2f'%re1, '&', '%.2f'%q1, '&','%.2f'%pa1,  r'\\'

print 'source 2 ', '&', '%.2f'%x1, '&',  '%.2f'%y1, '&', '%.2f'%n5, '&', '%.2f'%re5, '&', '%.2f'%q5, '&','%.2f'%pa5,  r'\\'

print 'galaxy 1 ', '&', '%.2f'%x2, '&',  '%.2f'%y2, '&', '%.2f'%n2, '&', '%.2f'%re2, '&', '%.2f'%q2, '&','%.2f'%pa2,  r'\\'

print 'galaxy 2 ', '&', '%.2f'%x2, '&',  '%.2f'%y2, '&', '%.2f'%n3, '&', '%.2f'%re3, '&', '%.2f'%q3, '&','%.2f'%pa3,  r'\\'

if trace.shape[-1] == 34:
    print 'galaxy 3 ', '&', '%.2f'%x2, '&',  '%.2f'%y2, '&', '%.2f'%n6, '&', '%.2f'%re6, '&', '%.2f'%q6, '&','%.2f'%pa6,  r'\\'


print 'lens 1 ', '&', '%.2f'%x4, '&',  '%.2f'%y4, '&', '%.2f'%eta, '&', '%.2f'%b, '&', '%.2f'%q4, '&','%.2f'%pa4,  r'\\\hline'

print 'shear = ', '%.4f'%shear, 'shear pa = ', '%.2f'%shearpa, 'dx = ', '%.2f'%dx, 'dy = ', '%.2f'%dy

