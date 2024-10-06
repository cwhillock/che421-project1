import numpy as np
from tabulate import tabulate

class Liquid:
    def __init__(self,density):
        self.density = density #mol/m3

class Gas:
    def __init__(self,avg_bubble_diameter):
        self.avg_bubble_diameter = avg_bubble_diameter #m
        self.avg_bubble_vol = 4/3*np.pi*(avg_bubble_diameter/2)**3 #average bubble volume
        self.avg_bubble_sa = 4 * np.pi * (avg_bubble_diameter/2)**2 #average bubble surface area

class Tank:
    def __init__(self,area,height,temp,liquid,gas,liq_holdup,gas_holdup,bubbler_flow_vol,bubbler_pressure):
        #static geometry vars
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

        #static bubbler parameters
        self.bubbler_flow_vol = bubbler_flow_vol #m3/s
        self.bubbler_flow_mol = calc_ngas(bubbler_flow_vol,bubbler_pressure,temp)

        #dynamic vars
        self.gas_holdup = gas_holdup #mol
        self.head_pressure = calc_Pgas(self.gas_holdup,self.head_vol,temp)
        self.dissolved_gas = 0
        self.liq_conc = self.dissolved_gas / self.liq_vol

        #dynamic bubble vars
        self.free_gas_mol = 0 #mol
        self.num_bubbles = self.bubbler_flow_vol / gas.avg_bubble_vol
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
        self.gas_holdup = max(0,self.gas_holdup - flowfromhead + self.leftover_free_gas)
        #update liquid concentration
        self.liq_conc = self.dissolved_gas / self.liq_vol
        #update head pressure
        self.head_pressure = calc_Pgas(self.gas_holdup,self.head_vol,self.temp)
        #update amount of free gas, bubbles, and total bubble surface area (may not be necessary)
        self.free_gas_mol = self.bubbler_flow_mol * dt
        self.num_bubbles = self.bubbler_flow_vol / self.gas.avg_bubble_vol
        self.total_bubble_sa = self.num_bubbles * self.gas.avg_bubble_sa


def calc_Pgas(n,v,t):
    #calculate pressure of gas from holdup,volume, and temperature
    #in the future should use cubic eos to calculate z
    R = 8.31446261815324 #m3*Pa/K/mol
    z = 1
    return n*R*t*z/v

def calc_ngas(v,p,t):
    #calculate number of moles of gas from volume, pressure, and temperature
    R = 8.31446261815324 #m3*Pa/K/mol
    z = 1
    return p*v/(z*R*t)

def calc_vgas(n,p,t):
    #calculate volume of gas from pressure and temperature
    R = 8.31446261815324 #m3*Pa/K/mol
    z = 1
    return n*R*t*z/p


