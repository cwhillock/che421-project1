from math import pow
from classesAndEOS import Liquid,Gas,calcZ,calcP,R
#units of R: m3*bar/mol/K

class Tank: #OBSOLETE
    def __init__(self,area,height,temp,liquid,gas,liq_holdup,gas_holdup,bubbler_flow_vol,bubbler_pressure,vent_pressure):
        #static geometry parameters
        self.area = area
        self.height = height
        self.liquid = liquid
        self.gas = gas
        self.liq_holdup = liq_holdup #mol
        self.temp = temp
        self.liq_vol = liq_holdup / liquid.density
        self.liq_height = self.liq_vol / area
        if self.liq_height >= self.height:
            raise Exception("too much liquid") 
        self.head_height = height - self.liq_height
        self.head_vol = self.head_height * area

        #static bubbler parameters
        self.bubbler_flow_vol = bubbler_flow_vol #m3/s
        self.bubbler_flow_mol = calc_ngas(self.gas,bubbler_flow_vol,bubbler_pressure,temp) #mol/s
        self.vent_pressure = vent_pressure
        self.max_gas_holdup = calc_ngas(self.gas,self.head_vol,vent_pressure,temp)

        #dynamic vars
        self.gas_holdup = gas_holdup #mol
        self.head_pressure = calcP(self.gas,temp,self.head_vol/gas_holdup)
        self.dissolved_gas = 0
        self.gas_conc = self.dissolved_gas / self.liq_vol
        self.percent_sol = self.gas_conc / self.calc_Sol()

        #dynamic bubble vars
        self.free_gas_mol = 0 #mol
        self.num_bubbles = calc_vgas(self.gas,self.free_gas_mol,self.head_pressure,self.temp) / gas.avg_bubble_vol
        self.total_bubble_sa = self.num_bubbles * gas.avg_bubble_sa #total surface area of bubbles
    
    def calc_Dab(self):
        #calculate Dab of gas in liquid
        return 3.24e-9 #m2/s

    def calc_Sol(self):
        #calculate solubility of gas in liquid henrys law
        H = 34 #mol/m3/bar
        return self.head_pressure*H

    def calc_bubble_flux(self):
        #calculate flux from bubbles to liquid
        Sc = self.liquid.viscosity / self.liquid.density / self.calc_Dab()
        rhog = 1/calc_vgas(self.gas,1,self.head_pressure,self.temp) #returns molar density of gas (mol/m3)
        deltarho = abs(rhog - self.liquid.density)
        klprime = 2*self.calc_Dab()/self.gas.avg_bubble_diameter + 0.31 * pow(Sc,-2/3) * pow(deltarho*self.liquid.viscosity*9.81/(self.liquid.density)**2,1/3)
        flux = klprime * (self.calc_Sol() - self.gas_conc)
        return flux

    def calc_head_flux(self):
        #calculate flux from head pressure to liquid
        deltaZ = abs(self.liq_height/2)
        deltaC = self.calc_Sol() - self.gas_conc
        return self.calc_Dab() * deltaC / deltaZ

    def update_state(self,dt):
        #calculates fluxes from head and bubbles
        flowfromhead = self.calc_head_flux() * self.area * dt #calculates dissolution from headspace to liquid
        flowfrombubbles = min(self.free_gas_mol,self.calc_bubble_flux()*self.total_bubble_sa * dt) #calculates dissolution from bubbles to liquid
        #bubbles not dissolved go to head space
        leftover_free_gas = self.free_gas_mol - flowfrombubbles
        #add fluxes to amount of dissolved gas
        self.dissolved_gas += flowfromhead + flowfrombubbles
        #update amount of gas in head space
        self.gas_holdup = max(0, min(self.max_gas_holdup,self.gas_holdup - flowfromhead + leftover_free_gas))
        #update liquid concentration
        self.gas_conc = self.dissolved_gas / self.liq_vol
        #update head pressure
        self.head_pressure = calcP(self.gas,self.temp,self.head_vol/self.gas_holdup)
        #update amount of free gas, bubbles, and total bubble surface area (may not be necessary)
        self.free_gas_mol = self.bubbler_flow_mol * dt
        self.num_bubbles = calc_vgas(self.gas,self.free_gas_mol,self.head_pressure,self.temp) / self.gas.avg_bubble_vol
        self.total_bubble_sa = self.num_bubbles * self.gas.avg_bubble_sa
        self.percent_sol = self.gas_conc / self.calc_Sol()

class TankV2:
    def __init__(self,area,height,temp,liquid,gas,liq_holdup,gas_pressure,bubbler_flow_vol,bubbler_pressure):
        #static geometry parameters
        self.area = area
        self.height = height
        self.liquid = liquid
        self.gas = gas
        self.liq_holdup = liq_holdup #mol
        self.temp = temp
        self.liq_vol = liq_holdup / liquid.density
        self.liq_height = self.liq_vol / area
        if self.liq_height >= self.height:
            raise Exception("too much liquid") 
        self.head_height = height - self.liq_height
        self.head_vol = self.head_height * area
        self.gas_pressure = gas_pressure
        self.gas_holdup = calc_ngas(gas,self.head_vol,gas_pressure,temp) #mol
        self.Sol = self.calc_Sol()

        #static bubbler parameters
        self.bubbler_flow_vol = bubbler_flow_vol #m3/s
        self.bubbler_flow_mol = calc_ngas(self.gas,bubbler_flow_vol,bubbler_pressure,temp) #mol/s
        self.gas_residence_time = self.liq_height / 90e-3 #s
        self.free_gas_mol = self.bubbler_flow_mol * self.gas_residence_time #mol
        self.num_bubbles = calc_vgas(self.gas,self.free_gas_mol,gas_pressure,self.temp) / gas.avg_bubble_vol
        self.total_bubble_sa = self.num_bubbles * gas.avg_bubble_sa #total surface area of bubbles

        #dynamic vars
        self.dissolved_gas = 0
        self.gas_conc = self.dissolved_gas / self.liq_vol
        self.percent_sol = self.gas_conc / self.Sol
    
    def calc_Dab(self):
        #calculate Dab of gas in liquid
        return 3.24e-9 #m2/s

    def calc_Sol(self):
        #calculate solubility of gas in liquid henrys law
        H = 34 #mol/m3/bar
        return self.gas_pressure*H

    def calc_bubble_flux(self):
        liquid_mass_density = self.liquid.density * self.liquid.MW / 1000 #kg/m3
        #calculate flux from bubbles to liquid
        Sc = self.liquid.viscosity / liquid_mass_density / self.calc_Dab()
        rhog = (self.free_gas_mol*self.gas.MW/1000/self.num_bubbles)/self.gas.avg_bubble_vol #mass density of gas (kg/m3)
        deltarho = abs(rhog - liquid_mass_density)
        klprime = 2*self.calc_Dab()/self.gas.avg_bubble_diameter + 0.31 * pow(Sc,-2/3) * pow(deltarho*self.liquid.viscosity*9.81/(liquid_mass_density)**2,1/3)
        flux = klprime * (self.Sol - self.gas_conc)
        return flux

    def calc_head_flux(self):
        #calculate flux from head pressure to liquid
        return 0

    def update_state(self,dt):
        #calculates fluxes from head and bubbles
        flowfromhead = self.calc_head_flux() * self.area * dt #calculates dissolution from headspace to liquid
        flowfrombubbles = min(self.free_gas_mol,self.calc_bubble_flux()*self.total_bubble_sa * dt) #calculates dissolution from bubbles to liquid
        #add fluxes to amount of dissolved gas
        self.dissolved_gas += flowfromhead + flowfrombubbles
        #update liquid concentration
        self.gas_conc = self.dissolved_gas / self.liq_vol
        self.percent_sol = self.gas_conc / self.Sol

def calc_ngas(gas,v,p,t):
    #calculate number of moles of gas from volume, pressure, and temperature
    z = calcZ(gas,t,p)
    return p*v/(z*R*t)

def calc_vgas(gas,n,p,t):
    #calculate volume of gas from pressure and temperature
    z = calcZ(gas,t,p)
    return n*R*t*z/p

def runSimulationTime(Tank,total_time,dt=0.01,eval_time=10):
    time = 0
    i = eval_time/dt
    headers = ['time (s)','dissolved gas (mol)','concentration (mol/m3)','% Solubility']
    data = []
    while time < total_time:
        if i >= eval_time/dt:
            data.append([time,Tank.dissolved_gas,Tank.gas_conc,Tank.percent_sol])
            i = 0
        Tank.update_state(dt)
        i += 1
        time += dt
    data.append([time,Tank.dissolved_gas,Tank.gas_conc,Tank.percent_sol])
    return headers,data

def runSimulationSol(Tank,final_percent_sol=0.99,dt=0.01,eval_time=10,max_time=100000):
    time = 0
    i = eval_time/dt
    headers = ['time (s)','dissolved gas (mol)','concentration (mol/m3)','% Solubility']
    data = []
    while Tank.percent_sol < final_percent_sol:
        if i >= eval_time/dt:
            data.append([time,Tank.dissolved_gas,Tank.gas_conc,Tank.percent_sol])
            i = 0
        Tank.update_state(dt)
        i += 1
        time += dt
        if time > max_time:
            print('broke, max time reached')
            return headers,data
    data.append([time,Tank.dissolved_gas,Tank.gas_conc,Tank.percent_sol])
    return headers,data