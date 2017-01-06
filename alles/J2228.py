import pyfits as py, numpy as np, pylab as pl

name = 'J2228-0018'


# load V-band science data, cut out the lens system and plot it
V = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F555W_sci.fits')[0].data.copy()
header = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F555W_sci.fits')[0].header.copy()

Vcut=V[2920:3410,1581:1930] # this is ENORMOUS and is going to take FOREVER
print Vcut.shape

#Vcut[Vcut<-1] = 0
pl.figure()
pl.imshow(np.log10(Vcut),origin='lower',interpolation='nearest')

# load V-band weight data, cut it and plot it
V_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F555W_wht.fits')[0].data.copy()
header_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F555W_wht.fits')[0].header.copy()
V_wht_cut = V_wht[2920:3410,1581:1930]

#Vcut[Vcut<-1] = 0
pl.figure()
pl.imshow(np.log10(V_wht_cut),origin='lower',interpolation='nearest')

# save both
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F555W_sci_cutout.fits',Vcut,header,clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F555W_wht_cutout.fits',V_wht_cut,header_wht,clobber=True)

'''psfs'''
psf1 = V[3010.5-14.5:3010.5+14.5,3453-14:3453+14]
psf1=psf1[:-1]
psf2 = V[3939-14:3939+14,4978-14:4978+14]
psf2 = psf2[:-1,:-1]
psf3 = V[2714-14:2714+14,3081-14:3081+14]
psf3 = psf3[:-1,:-1]
psf4 = V[2456.5-14.5:2456.5+14.5,4660.5-14.5:4660.5+14.5]
psf4=psf4[:-1,:-1]
psf1 = psf1/np.sum(psf1)
psf2 = psf2/np.sum(psf2)
psf3 = psf3/np.sum(psf3)
psf4 = psf4/np.sum(psf4)

pl.figure()
pl.imshow((psf1),interpolation='nearest')
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
I = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F814W_sci.fits')[0].data.copy()
header = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F814W_sci.fits')[0].header.copy()
Icut = I[2920:3410,1581:1930]

pl.figure()
pl.imshow(np.log10(Icut),origin='lower',interpolation='nearest')

# load I-band weight data, cut it and plot it
I_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F814W_wht.fits')[0].data.copy()
header_wht = py.open('/data/ljo31/Lens/'+str(name[:5])+'/F814W_wht.fits')[0].header.copy()
I_wht_cut = I_wht[2920:3410,1581:1930]

pl.figure()
pl.imshow(np.log10(Icut),origin='lower',interpolation='nearest')
print Icut.shape# - this is probably ok for gui but probably not for pymc

# save both
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_sci_cutout.fits',Icut,header,clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_wht_cutout.fits',I_wht_cut,header_wht,clobber=True)



'''psfs! how dull they are '''
psf1 = I[4854-14:4854+14,2355-14:2355+14]
psf1 = psf1[:-1,:-1]
psf2 = I[2714-14:2714+14,3081-14:3081+14]
psf2 = psf2[:-1,:-1]
psf3 = I[1151-14:1151+14,3586.5-14.5:3586.5+14.5]
psf3 = psf3[:-1,:-1]
psf4 = I[4006.5-14.5:4006.5+14.5,3631.5-14.5:3631.5+14.5]
psf4 = psf4[:-1,:-1]
psf1 = psf1/np.sum(psf1)
psf2 = psf2/np.sum(psf2)
psf3 = psf3/np.sum(psf3)
psf4 = psf4/np.sum(psf4)

pl.figure()
pl.imshow((psf1),interpolation='nearest')
pl.figure()
pl.imshow((psf2),interpolation='nearest')
pl.figure()
pl.imshow((psf3),interpolation='nearest')
pl.figure()
pl.imshow(psf4,interpolation='nearest')

py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_psf1.fits', psf1, clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_psf2.fits', psf2, clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_psf3.fits', psf3, clobber=True)
py.writeto('/data/ljo31/Lens/'+str(name[:5])+'/F814W_psf4.fits', psf4, clobber=True)
