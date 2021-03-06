import pyfits as py, numpy as np, pylab as pl
import indexTricks as iT
from scipy import ndimage

name = 'J010127'

''' part one: Poisson noise '''
# g band
sci = py.open('/data/ljo31b/lenses/chip5/imgg.fits')[0].data#[460:-460,430:-490]
wht = py.open('/data/ljo31b/lenses/chip5/expmapg.fits')[0].data#[460:-460,430:-490]


cut1 = sci[527:543,435:455]
cut2 = sci[490:505,495:515]
#cut1 -= np.median(cut1)
#cut2 -=np.median(cut2)
wht1 = wht[527:543,435:455]
wht2 = wht[490:505,495:515]

pl.figure()
pl.imshow(cut1)
pl.colorbar()
pl.figure()
pl.imshow(cut2)
pl.colorbar()


counts1 = cut1*wht1
var1 = np.var(counts1)/np.median(wht1)**2.

counts2 = cut2*wht2
var2 = np.var(counts2)/np.median(wht2)**2.


print var1,var2
poisson = np.mean((var1,var2))

sigma = poisson**0.5

from scipy import ndimage

im = sci[450:-450,420:-480]
wht = wht[450:-450,420:-480]

smooth = ndimage.gaussian_filter(im,0.7)
noisemap = np.where((smooth>0.7*sigma)&(im>0),im/wht+poisson, poisson)**0.5

## get rid of nans
ii = np.where(np.isnan(noisemap)==True)
noisemap[ii] = np.amax(noisemap[np.isnan(noisemap)==False])


py.writeto('/data/ljo31b/lenses/chip5/noisemap_g_big.fits',noisemap,clobber=True)
pl.figure()
pl.imshow(noisemap,origin='lower',interpolation='nearest')
pl.colorbar()

###################
###################
###################
# r band
sci = py.open('/data/ljo31b/lenses/chip5/imgr.fits')[0].data#[460:-460,430:-490]
wht = py.open('/data/ljo31b/lenses/chip5/expmapr.fits')[0].data#[460:-460,430:-490]


cut1 = sci[527:543,435:455]
cut2 = sci[490:505,495:515]
#cut1 -= np.median(cut1)
#cut2 -=np.median(cut2)
wht1 = wht[527:543,435:455]
wht2 = wht[490:505,495:515]

pl.figure()
pl.imshow(cut1)
pl.colorbar()
pl.figure()
pl.imshow(cut2)
pl.colorbar()


counts1 = cut1*wht1
var1 = np.var(counts1)/np.median(wht1)**2.

counts2 = cut2*wht2
var2 = np.var(counts2)/np.median(wht2)**2.


print var1,var2
poisson = np.mean((var1,var2))

sigma = poisson**0.5

from scipy import ndimage

im = sci[450:-450,420:-480]#[460:-460,430:-490]
wht = wht[450:-450,420:-480]#[460:-460,430:-490]

smooth = ndimage.gaussian_filter(im,0.7)
noisemap = np.where((smooth>0.7*sigma)&(im>0),im/wht+poisson, poisson)**0.5

## get rid of nans
ii = np.where(np.isnan(noisemap)==True)
noisemap[ii] = np.amax(noisemap[np.isnan(noisemap)==False])


py.writeto('/data/ljo31b/lenses/chip5/noisemap_r_big.fits',noisemap,clobber=True)
pl.figure()
pl.imshow(noisemap,origin='lower',interpolation='nearest')
pl.colorbar()


###################
###################
###################
# i band
sci = py.open('/data/ljo31b/lenses/chip5/imgi.fits')[0].data#[460:-460,430:-490]
wht = py.open('/data/ljo31b/lenses/chip5/expmapi.fits')[0].data#[460:-460,430:-490]


cut1 = sci[527:543,435:455]
cut2 = sci[490:505,495:515]
#cut1 -= np.median(cut1)
#cut2 -=np.median(cut2)
wht1 = wht[527:543,435:455]
wht2 = wht[490:505,495:515]

pl.figure()
pl.imshow(cut1)
pl.colorbar()
pl.figure()
pl.imshow(cut2)
pl.colorbar()


counts1 = cut1*wht1
var1 = np.var(counts1)/np.median(wht1)**2.

counts2 = cut2*wht2
var2 = np.var(counts2)/np.median(wht2)**2.


print var1,var2
poisson = np.mean((var1,var2))

sigma = poisson**0.5

from scipy import ndimage

im = sci[450:-450,420:-480]#[460:-460,430:-490]
wht = wht[450:-450,420:-480]#[460:-460,430:-490]

smooth = ndimage.gaussian_filter(im,0.7)
noisemap = np.where((smooth>0.7*sigma)&(im>0),im/wht+poisson, poisson)**0.5

## get rid of nans
ii = np.where(np.isnan(noisemap)==True)
noisemap[ii] = np.amax(noisemap[np.isnan(noisemap)==False])


py.writeto('/data/ljo31b/lenses/chip5/noisemap_i_big.fits',noisemap,clobber=True)
pl.figure()
pl.imshow(noisemap,origin='lower',interpolation='nearest')
pl.colorbar()

