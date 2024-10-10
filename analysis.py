import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from classesAndEOS import Liquid,Gas
from carbonationSim import TankV2,runSimulationTime,runSimulationSol
from matplotlib.ticker import ScalarFormatter

beer = Liquid(density=54.788e3,viscosity=0.001691,MW=19.122)
co2 = Gas(Tc=304.21,Pc=73.83,w=0.224,MW=44.01,avg_bubble_diameter=5e-4)

#General simulation run
#"""
Tank1 = TankV2(area=0.043355,height=0.59055,temp=277.59,liquid=beer,gas=co2,liq_holdup=1036.866,gas_pressure=5,bubbler_flow_vol=1.67e-5,bubbler_pressure=2.7)
#Tank1 = TankV2(area=0.043355,height=0.59055,temp=277.5,liquid=beer,gas=co2,liq_holdup=1036.866,gas_pressure=2.068,bubbler_flow_vol=1.67e-5,bubbler_pressure=2.7)
print(f'Tank Volume={Tank1.liq_vol+Tank1.head_vol}')
print(f'Liquid Volume={Tank1.liq_vol}')
print(f'Residence Time={Tank1.gas_residence_time}')
print(f'Molar bubbler flow={Tank1.bubbler_flow_mol}')
print(f'Number of bubbles={Tank1.num_bubbles}')
print(f'Total bubble surface area={Tank1.total_bubble_sa}')
print(f'Solubility Limit={Tank1.Sol}')
headers,data = runSimulationSol(Tank1,dt=0.001,eval_time=5)
print(tabulate(data,headers=headers))
time = [row[0] for row in data]
conc = [row[2] for row in data]
plt.plot(time,conc)
plt.xlabel('Time (s)')
plt.ylabel(f'Concentration of Carbon Dioxide (mol/m\N{SUPERSCRIPT THREE})')
plt.show()
#"""

#time step analysis
"""
time_test = np.linspace(10,0.1,10)
print(time_test)
final_time_data = []
for dt in time_test:
    testTank = TankV2(area=0.043355,height=0.59055,temp=277.59,liquid=beer,gas=co2,liq_holdup=1036.866,gas_pressure=5,bubbler_flow_vol=1.67e-5,bubbler_pressure=2.7)
    blah,data = runSimulationSol(Tank=testTank,final_percent_sol=0.99,dt=dt/1000,eval_time=500)
    final_time_data.append(data[-1][0])
plt.plot(time_test,final_time_data,'o')
plt.xlabel('Time Step (ms)')
plt.ylabel('Time to reach 99% Solubility (s)')
plt.show()
"""

#particle diameter sensitivity test
"""
dp_arr = np.linspace(1e-4,1e-3,5)
for dp in dp_arr:
    co2 = Gas(Tc=304.21,Pc=73.83,w=0.224,MW=44.01,avg_bubble_diameter=dp)
    Tank1=TankV2(area=0.043355,height=0.59055,temp=277.59,liquid=beer,gas=co2,liq_holdup=1036.866,gas_pressure=5,bubbler_flow_vol=1.67e-5,bubbler_pressure=2.7)
    blah,data = runSimulationTime(Tank=Tank1,total_time=600,dt=0.01,eval_time=1)
    time = [row[0] for row in data]
    sol_percent = [row[3]*100 for row in data]
    plt.plot(time,sol_percent,label=f"Dp={dp:.2e}")
plt.xlabel('Time (s)')
plt.ylabel('Percent of Solubility')
plt.legend()
plt.show()
"""

#temperature sensitivity test
"""
T_arr = np.arange(270,320,5)
T_results = []
for T in T_arr:
    testTank = TankV2(area=0.043355,height=0.59055,temp=T,liquid=beer,gas=co2,liq_holdup=1036.866,gas_pressure=5,bubbler_flow_vol=1.67e-5,bubbler_pressure=2.7)
    blah,data = runSimulationSol(Tank=testTank,final_percent_sol=0.99,dt=0.01,eval_time=500)
    T_results.append((data[-1][0]))
plt.plot(T_arr,T_results,'o')
plt.xlabel('System Temperature (K)')
plt.ylabel('Time to reach 99% Solubility (s)')
plt.show()
"""