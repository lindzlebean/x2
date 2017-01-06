import numpy as np, pylab as pl, pyfits as py, cPickle
from astLib import astCalc
import pymc
import myEmcee_blobs as myEmcee
from tools.EllipsePlot import *

table = py.open('/data/ljo31/Lens/LensParams/Phot_1src_huge_new.fits')[1].data
names = table['name']
re,dre = table['re v'], np.min((table['re v lo'],table['re v hi']),axis=0)
sz = np.load('/data/ljo31/Lens/LensParams/SourceRedshiftsUpdated.npy')[()]
ages = re*0.
dages=re*0.

for n in range(names.size):
    name = names[n]
    try:
        lo,med,hi=np.load('/data/ljo31b/EELs/inference/new/212_params_'+name+'.npy').T
    except:
        lo,med,hi=np.load('/data/ljo31b/EELs/inference/new/211_params_'+name+'.npy').T
    z = sz[name][0]
    age = med[3] + astCalc.tl(z)
    print name, '%.2f'%age
    ages[n] = age
    dages[n] = np.mean((med[3]-lo[3],hi[3]-med[3]))
    print '%.2f'%(med[3]-lo[3]), '%.2f'%(hi[3]-med[3])

print dages/ages

fp = np.load('/data/ljo31b/EELs/esi/kinematics/inference/results.npy')
l,m,u = fp
d = np.mean((l,u),axis=0)
dvl,dvs,dsigmal,dsigmas = d.T
vl,vs,sigmal,sigmas = m.T
sigmas,sigmal,dsigmas,dsigmal = np.delete(sigmas,6), np.delete(sigmal,6),np.delete(dsigmas,6),np.delete(dsigmal,6)
G = 4.3e-6
apcorr = np.load('/data/ljo31b/EELs/esi/kinematics/aperture_corrections.npy')
sigmas /= apcorr
Mvir = 5.*sigmas**2.*re/G
logMvir = np.log10(Mvir)

# fit log sigma = a log Mstar + b
x,y = np.log10(ages),logMvir-10. # units: 10^11 solar masses for both axes.
sxx, syy = dages/ages/np.log(10.), 0.03*y # made up error for now - really need to go through chain
sxx2, syy2 = sxx**2., syy**2.
sxy,syx = 0.*sxx*syy, 0.*syy*sxx

pl.figure()
pl.scatter(x,y,s=30,c='CornflowerBlue')
pl.errorbar(x,y,xerr=sxx,yerr=syy,fmt='o',color='CornflowerBlue')
pl.show()


pars, cov = [], []
pars.append(pymc.Uniform('alpha',-20,20))
pars.append(pymc.Uniform('beta',-20,20 ))
pars.append(pymc.Uniform('sigma',0,0.9,value=0.1))
pars.append(pymc.Uniform('tau',0.001,10,value=0.1))
pars.append(pymc.Uniform('mu',0.,2.,value=1.))
cov += [0.5,0.5,0.1,0.1,0.5]
optCov = np.array(cov)

@pymc.deterministic
def logP(value=0.,p=pars):
    lp=0.
    alpha,beta,sigma,tau,mu = pars[0].value, pars[1].value,pars[2].value, pars[3].value,pars[4].value
    tau2,sigma2,beta2 = tau**2., sigma**2.,beta**2.
    X = x-mu
    Y = y - alpha - beta*mu
    Sxx = sxx + tau2
    Syy = syy + sigma2 + beta2*tau2
    Sxy = sxy + beta*tau2
    Syx = syx + beta*tau2
    Delta = Syy*X**2. + Sxx*Y**2. - X*Y*(Sxy+Syx)
    Sigma =  Sxx*Syy - Sxy*Syx
    pdf = -0.5*Delta/Sigma- 0.5*np.log(Sigma)
    lp = pdf.sum()
    return lp

@pymc.observed
def likelihood(value=0.,lp=logP):
    return lp

S = myEmcee.Emcee(pars+[likelihood],cov=optCov,nthreads=1,nwalkers=20)
S.sample(4000)
outFile = '/data/ljo31/Lens/Analysis/MT'
f = open(outFile,'wb')
cPickle.dump(S.result(),f,2)
f.close()
result = S.result()
result = np.load('/data/ljo31/Lens/Analysis/MT')
lp,trace,dic,_ = result
a1,a2 = np.unravel_index(lp.argmax(),lp.shape)
ftrace=trace[1000:].reshape((trace[1000:].shape[0]*trace[1000:].shape[1],trace[1000:].shape[2]))
for i in range(len(pars)):
    pars[i].value = np.percentile(ftrace[:,i],50,axis=0)
    print "%18s  %8.5f"%(pars[i].__name__,pars[i].value)

burnin=200
xfit = np.linspace(0,2.5,20)
f = trace[burnin:].reshape((trace[burnin:].shape[0]*trace[burnin:].shape[1],trace[burnin:].shape[2]))
fits=np.zeros((len(f),xfit.size))
for j in range(0,len(f)):
    alpha,beta,sigma,tau,mu = f[j]
    fits[j] = beta*xfit+alpha

los,meds,ups = np.percentile(f,[16,50,84],axis=0)
los,ups=meds-los,ups-meds
'''print r'\begin{table}[H]'
print r'\centering'
print r'\begin{tabular}{|ccccccc|}\hline'
print r'Sersic model & age model & $\alpha$ & $\beta$ & $\sigma$ & $\tau$ & $\mu$ \\\hline'
print 'one-component & from photometry & ', '$','%.2f'%meds[0], '_{-','%.2f'%los[0], '}^{+','%.2f'%ups[0],'}$ & $', '%.2f'%meds[1], '_{-','%.2f'%los[1], '}^{+','%.2f'%ups[1],'}$ & $','%.2f'%meds[2], '_{-','%.2f'%los[2], '}^{+','%.2f'%ups[2],'}$ & $','%.2f'%meds[3], '_{-','%.2f'%los[3], '}^{+','%.2f'%ups[3],'}$ & $','%.2f'%meds[4], '_{-','%.2f'%los[4], '}^{+','%.2f'%ups[4],'}$', r'\\'
print r'\end{tabular}'
print r'\end{table}'
'''

# make plots with uncertainties
yfit=meds[1]*xfit+meds[0]
lo,med,up = xfit*0.,xfit*0.,xfit*0.
for j in range(xfit.size):
    lo[j],med[j],up[j] = np.percentile(fits[:,j],[16,50,84],axis=0)

da, db = np.percentile(dic['alpha'][1000:].ravel(),50) - np.percentile(dic['alpha'][1000:].ravel(),16),np.percentile(dic['beta'][1000:].ravel(),50) -np.percentile(dic['beta'][1000:].ravel(),16)
a,b = np.percentile(dic['alpha'][1000:].ravel(),50), np.percentile(dic['beta'][1000:].ravel(),50)

#pl.figure()
pl.plot(xfit,yfit,'Crimson')
pl.fill_between(xfit,yfit,lo,color='LightPink',alpha=0.5)
pl.fill_between(xfit,yfit,up,color='LightPink',alpha=0.5)
pl.scatter(x,y,color='Crimson')
#pl.errorbar(x,y,xerr=sxx,yerr=syy,fmt='o',color='Crimson')
plot_ellipses(x,y,sxx,syy,0.1*np.ones(sxx.size),'Crimson')
pl.xlabel(r'$\log T$')
pl.ylabel(r'$M_{vir}$')
pl.figtext(0.2,0.8,'$a = '+'%.2f'%a+'\pm'+'%.2f'%da+'$')
pl.figtext(0.2,0.75,'$b = '+'%.2f'%b+'\pm'+'%.2f'%db+'$')
#pl.xlim([10,12])
#pl.ylim([-0.4,1.9])


pl.figure()
pl.plot(lp)
pl.show()
# run loads of realisations of the EELs models to get covariance






####################
'''pl.figure()
pl.scatter(logM,logMstarL,s=30,color='SteelBlue')

# nb. we can also get virial masses!
fp = np.load('/data/ljo31b/EELs/esi/kinematics/inference/results.npy')
l,m,u = fp
d = np.mean((l,u),axis=0)
dvl,dvs,dsigmal,dsigmas = d.T
vl,vs,sigmal,sigmas = m.T
sigmas,sigmal,dsigmas,dsigmal = np.delete(sigmas,6), np.delete(sigmal,6),np.delete(dsigmas,6),np.delete(dsigmal,6)
G = 4.3e-6

struct = np.load('/data/ljo31/Lens/LensParams/Structure_1src.npy')[0]
Mvir = magv*0.
for ii in range(magv.size):
    name = names[ii]
    n = struct[name]['Source 1 n']
    beta = 8.87 - 0.831*n + 0.0241*n**2.
    Mvir[ii] = beta*sigmas[ii]**2.*re[ii]/G
    print beta

logMvir = np.log10(Mvir)

pl.figure()
pl.scatter(logMvir, logM,s=30,color='SteelBlue')
pl.xlabel('$\log M_{vir}$')
pl.ylabel('$\log M_{\star}$')
xline = np.linspace(10,12,10)
pl.plot(xline,xline)

pl.figure()
pl.scatter(logM,np.log10(sigmas/100.),s=30,color='SteelBlue')
pl.xlabel('$\log M_{\star}$')
pl.ylabel('$\log \sigma$')

pl.figure()
pl.scatter(logMvir,np.log10(sigmas/100.),s=30,color='SteelBlue')
pl.xlabel('$\log M_{vir}$')
pl.ylabel('$\log \sigma$')

'''
