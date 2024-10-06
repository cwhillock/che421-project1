import numpy as np
from tabulate import tabulate
from componentPropsAndEOS import Liquid,Gas,calcZ,calcP,R
#units of R: m3*bar/mol/K

class Tank:
    def __init__(self,area,height,temp,liquid,gas,liq_holdup,gas_holdup,bubbler_flow_vol,bubbler_pressure):
        #static geometry parameters
        self.area = area
        self.height = height
        self.liquid = liquid
        self.gas = gas
        self.liq_holdup = liq_holdup #mol
        self.temp = temp
        self.liq_vol = liq_holdup / liquid.density
        self.liq_height = self.liq_vol / area
        self.head_height = height - self.liq_height
        self.head_vol = self.head_height * area
        self.Dab = calc_Dab(liquid,gas)

        #static bubbler parameters
        self.bubbler_flow_vol = bubbler_flow_vol #m3/s
        self.bubbler_flow_mol = calc_ngas(self.gas,bubbler_flow_vol,bubbler_pressure,temp) #mol/s

        #dynamic vars
        self.gas_holdup = gas_holdup #mol
        self.head_pressure = calcP(self.gas,temp,self.head_vol/gas_holdup)
        self.dissolved_gas = 0
        self.liq_conc = self.dissolved_gas / self.liq_vol

        #dynamic bubble vars
        self.free_gas_mol = 0 #mol
        self.num_bubbles = calc_vgas(self.free_gas_mol,self.head_pressure,self.temp) / gas.avg_bubble_vol
        self.total_bubble_sa = self.num_bubbles * gas.avg_bubble_sa #total surface area of bubbles

    def calc_bubble_flux(self):
        #calculate flux from bubbles to liquid
        pass

    def calc_head_flux(self):
        #calculate flux from head pressure to liquid
        pass

    def update_state(self,dt):
        #calculates fluxes from head and bubbles
        flowfromhead = self.calc_head_flux(self) * self.area * dt #calculates dissolution from headspace to liquid
        flowfrombubbles = self.calc_bubble_flux(self)*self.total_bubble_sa * dt #calculates dissolution from bubbles to liquid
        #bubbles not dissolved go to head space
        leftover_free_gas = self.free_gas_mol - flowfrombubbles
        #add fluxes to amount of dissolved gas
        self.dissolved_gas += flowfromhead + flowfrombubbles
        #update amount of gas in head space
        self.gas_holdup = max(0,self.gas_holdup - flowfromhead + leftover_free_gas)
        #update liquid concentration
        self.liq_conc = self.dissolved_gas / self.liq_vol
        #update head pressure
        self.head_pressure = calcP(self.gas,self.temp,self.head_vol/self.gas_holdup)
        #update amount of free gas, bubbles, and total bubble surface area (may not be necessary)
        self.free_gas_mol = self.bubbler_flow_mol * dt
        self.num_bubbles = calc_vgas(self.free_gas_mol,self.head_pressure,self.temp) / self.gas.avg_bubble_vol
        self.total_bubble_sa = self.num_bubbles * self.gas.avg_bubble_sa

def calc_Dab(liquid,gas):
    #calculate Dab of gas in liquid
    pass

def calc_ngas(gas,v,p,t):
    #calculate number of moles of gas from volume, pressure, and temperature
    z = calcZ(gas,t,p)
    return p*v/(z*R*t)

def calc_vgas(gas,n,p,t):
    #calculate volume of gas from pressure and temperature
    z = calcZ(gas,t,p)
    return n*R*t*z/p