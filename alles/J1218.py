import pyfits as py, numpy as np, pylab as pl

name = 'J1218+5648'


# load V-band science data, cut out the lens system and plot it
V = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F606W_sci.fits')[0].data.copy()
header = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F606W_sci.fits')[0].header.copy()

Vcut=V[3660:3890,3240:3490] # but could use [15:-15,15:-15]
print Vcut.shape

#Vcut[Vcut<-1] = 0
pl.figure()
pl.imshow(np.log10(Vcut),origin='lower',interpolation='nearest')

# load V-band weight data, cut it and plot it
V_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F606W_wht.fits')[0].data.copy()
header_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F606W_wht.fits')[0].header.copy()
V_wht_cut = V_wht[3660:3890,3240:3490]

#Vcut[Vcut<-1] = 0
pl.figure()
pl.imshow(np.log10(V_wht_cut),origin='lower',interpolation='nearest')

# save both
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F606W_sci_cutout.fits',Vcut,header,clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F606W_wht_cutout.fits',V_wht_cut,header_wht,clobber=True)

'''psfs'''
psf1=V[4011-14:4011+14,2380-14:2380+14]
psf1=psf1[:-1,:-2]
psf2 = V[2054-14:2054+14,1425-14:1425+14]
psf2=psf2[:-1,:-1]
psf3 = V[1892-14:1892+14,622-14:622+14]
psf3=psf3[:-1]
psf4=V[1520-14:1520+14,4094-14:4094+14]
psf4=psf4[:,:-1]

psf1 = psf1/np.sum(psf1)
psf2 = psf2/np.sum(psf2)
psf3 = psf3/np.sum(psf3)
psf4 = psf4/np.sum(psf4)

pl.figure()
pl.imshow((psf1),interpolation='nearest',cmap='hot_r')
pl.figure()
pl.imshow((psf2),interpolation='nearest')
pl.figure()
pl.imshow((psf3),interpolation='nearest')
pl.figure()
pl.imshow((psf4),interpolation='nearest')

py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F606W_psf1.fits', psf1, clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F606W_psf2.fits', psf2, clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F606W_psf3.fits', psf3, clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F606W_psf4.fits', psf4, clobber=True)


''' I BAND '''
# load V-band science data, cut out the lens system and plot it
I = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F814W_sci.fits')[0].data.copy()
header = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F814W_sci.fits')[0].header.copy()
Icut = I[3660:3890,3240:3490]

pl.figure()
pl.imshow(np.log10(Icut),origin='lower',interpolation='nearest')

# load I-band weight data, cut it and plot it
I_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F814W_wht.fits')[0].data.copy()
header_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/SDSS'+str(name)+'_F814W_wht.fits')[0].header.copy()
I_wht_cut = I_wht[3660:3890,3240:3490]

pl.figure()
pl.imshow(np.log10(I_wht_cut),origin='lower',interpolation='nearest')

# save both
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_sci_cutout.fits',Icut,header,clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_wht_cutout.fits',I_wht_cut,header_wht,clobber=True)



'''psfs! how dull they are '''
psf1=I[2054-14:2054+14,1425-14:1425+14]
psf1 = psf1[:-2]

psf2 = I[4011-14:4011+14,2380-14:2380+14]
psf2 = psf2[:-3,:-1]

psf1 = psf1/np.sum(psf1)
psf2 = psf2/np.sum(psf2)

pl.figure()
pl.imshow((psf1),interpolation='nearest')
pl.figure()
pl.imshow((psf2),interpolation='nearest')

py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_psf1.fits', psf1, clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_psf2.fits', psf2, clobber=True)

