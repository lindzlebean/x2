import pyfits as py, numpy as np, pylab as pl

V = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F555W_sci.fits')[0].data.copy()
header = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F555W_sci.fits')[0].header.copy()

Vcut = V[2150-146:2150+146,2264-146:2264+146]#

Vcut[Vcut<-1] = 0
pl.figure()
pl.imshow(np.log10(Vcut),origin='lower',interpolation='nearest')

V_wht = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F555W_wht.fits')[0].data.copy()
header_wht = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F555W_wht.fits')[0].header.copy()

V_wht_cut = V_wht[2150-146:2150+146,2264-146:2264+146]#[2150-46:2150+46,2264-46:2264+46]

py.writeto('/data/ljo31/Lens/J1605/F555W_wht_cutout_huge.fits',V_wht_cut,header_wht,clobber=True)
py.writeto('/data/ljo31/Lens/J1605/F555W_sci_cutout_huge.fits',Vcut,header,clobber=True)


### I band

I = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F814W_sci.fits')[0].data.copy()
header = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F814W_sci.fits')[0].header.copy()

Icut = I[2150-146:2150+146,2264-146:2264+146]#[2150-46:2150+46,2264-46:2264+46]

Icut[Icut<-1] = 0
pl.figure()
pl.imshow(np.log10(Icut),origin='lower',interpolation='nearest')

I_wht = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F814W_wht.fits')[0].data.copy()
header_wht = py.open('/data/ljo31/Lens/J1605/SDSSJ1605+3811_F814W_wht.fits')[0].header.copy()

I_wht_cut = I_wht[2150-146:2150+146,2264-146:2264+146]#[2150-46:2150+46,2264-46:2264+46]

py.writeto('/data/ljo31/Lens/J1605/F814W_wht_cutout_huge.fits',I_wht_cut,header_wht,clobber=True)
py.writeto('/data/ljo31/Lens/J1605/F814W_sci_cutout_huge.fits',Icut,header,clobber=True)

