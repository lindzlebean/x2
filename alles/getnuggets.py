import numpy as np, pylab as pl, pyfits as py
from scipy.interpolate import splrep, splint, splev
import pymc
import cPickle
from tools.EllipsePlot import *

''' select as RNs any objects that are more compact than van Dokkum's criterion (the most stringent) for both 1- and 2-component models. '''
logR,logM,dlogR,dlogM,rho = np.load('/data/ljo31/Lens/LensParams/ReMass_2src.npy').T
logR1,logM1,dlogR1,dlogM1,rho = np.load('/data/ljo31/Lens/LensParams/ReMass_1src.npy').T
xfit,yfit,lo,up = np.load('/data/ljo31/Lens/Analysis/sizemass_2src_fit.npy').T
xfit,yfit1,lo1,up1 = np.load('/data/ljo31/Lens/Analysis/sizemass_1src_fit.npy').T
vdWfit1 = 0.42 - 0.71*(10.+np.log10(5.)) + 0.71*xfit
vdWfit2 = 0.60 - 0.75*(10.+np.log10(5.)) + 0.75*xfit
shenfit = np.log10(3.47e-6) + 0.56*xfit

def vD(x,y):
    return x-10.7

def select(logM,logR,logM1,logR1):
    line = vD(logM,logR)
    line1 = vD(logM1,logR1)
    nuggets = np.where((logR<line) & (logR1<line1))
    return nuggets

nuggets = select(logM,logR,logM1,logR1)
logR,logM,dlogR,dlogM,rho = logR[nuggets],logM[nuggets],dlogR[nuggets],dlogM[nuggets],rho[nuggets]
logR1,logM1,dlogR1,dlogM1 = logR1[nuggets],logM1[nuggets],dlogR1[nuggets],dlogM1[nuggets]
name = py.open('/data/ljo31/Lens/LensParams/Phot_1src.fits')[1].data['name'][nuggets]

pl.figure()
pl.plot(xfit,yfit,'Crimson')
pl.fill_between(xfit,yfit,lo,color='LightPink',alpha=0.5)
pl.fill_between(xfit,yfit,up,color='LightPink',alpha=0.5)
pl.plot(xfit,yfit1,'SteelBlue')
pl.fill_between(xfit,yfit1,lo1,color='LightBlue',alpha=0.5)
pl.fill_between(xfit,yfit1,up1,color='LightBlue',alpha=0.5)
pl.scatter(logM,logR,color='Crimson')
plot_ellipses(logM,logR,dlogM,dlogR,rho,'Crimson')
pl.scatter(logM1,logR1,color='SteelBlue')
plot_ellipses(logM1,logR1,dlogM1,dlogR1,rho,'SteelBlue')
#pl.plot(xfit,vdWfit1,'k:',label='van der Wel+14, z=0.75')
#pl.plot(xfit,vdWfit2,'k-.',label='van der Wel+14, z=0.25')
#pl.plot(xfit,shenfit,'k-',lw=0.5,label='Shen+03, z= 0')

pl.xlabel(r'$\log(M_{\star}/M_{\odot})$')
pl.ylabel(r'$\log(R_e/kpc)$')
pl.xlim([10.5,12.5])
pl.ylim([-0.4,1.9])

## red nugget criteria
vD15 = xfit - 10.7
B13 = (xfit - 10.3)/1.5
vdW14 = 0.75*xfit - 8.25+np.log10(2.5)
pl.plot(xfit,vD15,'k--',label = 'van Dokkum+15')
pl.plot(xfit,B13,'k-.',label='Barro+13')
pl.plot(xfit,vdW14,'k:',label='van der Wel+14')
pl.legend(loc='upper left')