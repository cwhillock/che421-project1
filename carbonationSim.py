import numpy as np
from tabulate import tabulate

class liquid:
    def __init__(self,density):
        self.density = density #mol/m3

class gas:
    def __init__(self,avg_bubble_diameter):
        self.avg_bubble_diameter = avg_bubble_diameter #m
        self.avg_bubble_size = 4/3*3.14156*(avg_bubble_diameter/2)**3

class tank:
    def __init__(self,area,height,liquid,gas,liq_holdup,gas_holdup,bubbler_flow,temp):
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

        #static bubble vars
        self.bubbler_flow = bubbler_flow #m3/s
        self.num_new_bubbles = bubbler_flow / gas.avg_bubble_size

        #dynamic vars
        self.gas_holdup = gas_holdup #mol
        self.head_pressure = calc_Pgas(self.gas_holdup,self.liq_vol,temp)
        self.dissolved_gas = 0
        self.liq_conc = self.dissolved_gas / self.liq_vol

def calc_Pgas(n,v,t):
    #calculate pressure of gas from holdup,volume, and temperature
    #in the future should use cubic eos
    #ideal gas law for now
    R = 8.31446261815324 #m3*Pa/K/mol
    return n*R*t/v


