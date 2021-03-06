import pylab as pl, numpy as np
import pyfits as py

### eels
b = np.load('/data/ljo31/Lens/LensParams/V_redshift0_model_ABSMAG.npy')
phot = py.open('/data/ljo31/Lens/LensParams/Phot_2src_huge_new_new.fits')[1].data
names = phot['name']
re = phot['Re v']

### macsj0717
cat = np.load('/data/ljo31b/MACSJ0717/data/MLM_macs_newmasked_FINALCMD_doubles_rhos_dMs.npy')
ii = np.where(cat[:,0]!=31.)
name,M,ML,dM,dML,RE,dre,sigma,dsigma,mu,dmu,vel,dvel,rho_remu,rho_mml,rho_mre,dM,dML = cat[ii].T
B = np.load('/data/ljo31b/MACSJ0717/data/B.npy')[:-1]

pl.figure()
pl.scatter(RE,B,c='SteelBlue',s=40,label='cluster')
pl.scatter(re,b,c='Crimson',s=40,label='nugget')
pl.legend(loc='upper left')
pl.xlabel('$R_e$ (kpc)')
pl.ylabel('B (mag)')
pl.show()
