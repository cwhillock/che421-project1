from math import pow,pi
R = 8.20573660809596e-5 * 1.013 #m3*bar/mol/K

class Liquid:
    def __init__(self,density,viscosity):
        self.density = density #mol/m3
        self.viscosity = viscosity #Pa*s

class Gas:
    def __init__(self,Tc,Pc,w,avg_bubble_diameter=100e-6):
        self.Tc = Tc
        self.Pc = Pc
        self.w = w
        self.avg_bubble_diameter = avg_bubble_diameter #m
        self.avg_bubble_vol = 4/3* pi *(avg_bubble_diameter/2)**3 #average bubble volume
        self.avg_bubble_sa = 4 * pi * (avg_bubble_diameter/2)**2 #average bubble surface area

def calcZ(gas,T,P):
    Tr = T/gas.Tc
    Pr = P/gas.Pc
    B0 = 0.083 - 0.422/pow(Tr,1.6)
    B1 = 0.139 - 0.172/pow(Tr,4.2)
    Bhat = B0 + gas.w * B1
    B = Bhat * R * gas.Tc / gas.Pc
    Z = 1 + B * P / (R*T)
    return Z

def calcP(gas,T,V):
    #V = SPECIFIC molar volume m3/mol
    Tr = T/gas.Tc
    B0 = 0.083 - 0.422/pow(Tr,1.6)
    B1 = 0.139 - 0.172/pow(Tr,4.2)
    Bhat = B0 + gas.w * B1
    B = Bhat * R * gas.Tc / gas.Pc
    return -R * T / (B-V)

