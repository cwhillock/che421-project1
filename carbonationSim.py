import numpy as np

#necessary properties (fill as we go)
liq_dens = 1 #liquid density 

class tank:
    def __init__(self,area,height,temp,liq_mol_HU,num_sections,gas_mol_HU):
        #static vars
        self.area = area #tank cross sectional area
        self.height = height #tank height
        self.temp = temp
        self.liq_mol_HU = liq_mol_HU #holdup (molar/mass TBD) of liquid in tank
        self.num_sections = num_sections
        self.liq_vol = liq_mol_HU / liq_dens #volume of liquid in tank
        self.liq_height = self.liq_vol / self.area #height of liquid in tank
        self.head_vol = (height - self.liq_height)*area #volume of head in top of tank
        self.liq_disc_height = self.liq_height / num_sections #height of one discretization
        self.liq_disc_vol = self.liq_disc_height * area
        self.liq_disc_pos = [0] #position of each discretized layer of liquid (going down)
        for i in range(num_sections):
            self.liq_disc_pos.append(self.liq_disc_pos[-1] + self.liq_disc_height)
        
        #changing vars
        self.gas_mol_HU = gas_mol_HU #moles of gas in head space
        self.head_pressure = calc_P_from_moles_in_V(gas_mol_HU,self.head_vol) #pressure in head space
        self.dissolved_gas = np.zeros(num_sections) #moles of dissolved gas in each liquid section
        self.concentrations = np.zeros(num_sections) #concentration of gas in each section
        self.flow_to_head = 0 #flow to head space (can be negative)
        self.flow_to_section = np.zeros(num_sections) #flow to each section (can be negative)

    def calculate_flows(self):
        #calculate the flowrates to the head and each liquid discretization
        #based on current tank concentration gradient
        #updates to the flow arrays
        self.flow_to_head = calc_vapor_to_liq_flux(self.head_pressure,self.concentrations[0]) * self.area
        self.flow_to_section[0] =  self.flow_to_head + calc_liq_to_liq_flux(self.concentrations[0],self.concentrations[1]) * self.area
        for i in range(1,self.num_sections - 1):
            self.flow_to_section[i] = calc_liq_to_liq_flux(self.concentrations[i-1],self.concentrations[i]) * self.area + calc_liq_to_liq_flux(self.concentrations[i],self.concentrations[i+1]) * self.area
        self.flow_to_section[-1] = calc_liq_to_liq_flux(self.concentrations[-2],self.concentrations[-1]) * self.area

    def update_system_state(self, dt):
        self.gas_mol_HU += self.flow_to_head * dt
        for i in range(self.num_sections):
            self.dissolved_gas[i] += self.flow_to_section[i] * dt
            self.concentrations[i] = calc_conc_from_moles(self.dissolved_gas[i],self.liq_disc_vol)
        


#necessary functions (create later)
def calc_P_from_moles_in_V(T,B,D):
    # calculate the pressure of a gas given the volume of the container and the amount of moles in that volume
    pass

def calc_vapor_to_liq_flux(T,B,D):
    #calculate the flux from the head space to the liquid
    pass

def calc_liq_to_liq_flux(T,B,D):
    #calculate the flux from one liquid layer to the other based on concentration difference
    pass

def calc_conc_from_moles(T,B,D):
    #calculate the concentration of gas in liquid layer from amount of moles dissovled
    pass

def run_simulation(tank,dt,final_t):
    #simulate the tank with time step dt
    #might want to switch this out for an implementation in Pygame - for drawing and stuff
    pass


        
