import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt

class Sail(object):

    def __init__(self, type, area, vce, up=True):
        self.type = type
        self.area = area
        self.vce  = vce
        # get sails coefficients
        self._build_interp_func(self.type+'.dat')
        self.bk = 1. # always valid for main, only AWA<135 for jib
        self.up = up # is that an upwind sail?


    def cl(self, awa):
        awa = max(0, min(awa, 180))
        return self.interp_cl(awa)


    def cd(self, awa):
        awa = max(0, min(awa, 180))
        return self.interp_cd(awa)


    def _build_interp_func(self, fname):
        '''
        build interpolation function and returns it in a list
        '''
        a = np.genfromtxt('dat/'+fname,delimiter=',',skip_header=1)
        self.kp = a[0,0]
        # linear for now, this is not good, might need to polish data outside
        self.interp_cd = interpolate.interp1d(a[1,:],a[2,:],kind='linear')
        self.interp_cl = interpolate.interp1d(a[1,:],a[3,:],kind='linear')


    def debbug_coeffs(self, N=256):
        awa = np.linspace(0,180,N)
        coeffs = np.empty((N,2)) 
        for i,a in enumerate(awa):
            coeffs[i,0]=self.cd(a)
            coeffs[i,1]=self.cl(a)
        plt.plot(awa,coeffs[:,0],awa,coeffs[:,1])
        plt.title(self.type+str(self.kp)); plt.legend(['CD','CL'])
        plt.show()


class Main(Sail):
    def __init__(self, area, vce, P=0):
        self.type = 'main'
        self.area = area
        self.roach = 0.
        self.vce =  vce + 0.024*P # (5.7)
        super().__init__(self.type, self.area, self.vce)


class Jib(Sail):
    def __init__(self, area, vce):
        self.type = 'jib'
        self.area = area
        self.vce = vce
        super().__init__(self.type, self.area, self.vce)


class Kite(Sail):
    def __init__(self, SLU, SLE, SFL, SHW, ISP, J, SPL):
        self.type = 'kite'
        area_d = 1.14*np.sqrt(ISP**2+J**2)*max(SPL,J) # only for symm kite
        self.area = max(area_d, 0.5*(SLU+SLE)*(SFL+4*SHW)/6.)
        self.vce = 0.565*ISP # above base of I
        super().__init__(self.type, self.area, self.vce, up=False)
