'''
Find out appliance energy for all months
'''
# Standard imports
import os

# Internal imports
from run_appliance_opt import RunAppModel
from model import generate_csvs
import pandas as pd
import numpy as np

NUM_OF_MONTE_CARLO_RUN = 100

appliance_with_constant_mc = ['lighting', 'water_pump','washing_machine', 'dishwashers', 'washer_dryer', \
                    'hair_dryer', 'toaster', 'coffe_maker', 'laptops', 'televisions', 'routers','clothing_iron', 'refrigerator_l300', 'refrigerator_g300' ]
# appliance_with_variable_mc = ['fans', 'coolers', 'air_heater', 'ac_unit', 'incandescent_bulb', \
#             'cfl_bulb', 'led_bulb', 'tubelights', \
#                'water_pump', 'geyser_electric' ]

appliance_with_variable_mc = ['fans', 'coolers', 'air_heater', 'ac_unit', 'geyser_electric' ]

constant_mc_result_mean = {'Appliances': appliance_with_constant_mc, 'mean_energy': []}
constant_mc_result_sd = {'Appliances': appliance_with_constant_mc, 'std_energy': []}


constant_mc_result = []
variable_mc_result = []

obj_values = []
for num in range(NUM_OF_MONTE_CARLO_RUN):
    print(f'Running for {num} iteration --------------------------------------------------->')

    # update csvs
    customers = generate_csvs(num_of_customers=30)
    
    # Run optimization
    instance = RunAppModel(data_path = r'C:\\Users\\KDUWADI\\Desktop\\BRPL\\survey_data',
        export_path = r'C:\Users\KDUWADI\Desktop\BRPL\survey_result',
        solver = 'ipopt')

    # Get result
    constant_mc_result.append(instance.get_result_constant_mc())
    variable_mc_result.append(instance.get_result_variable_mc())
    obj_values.append(instance.get_objective_func())


energy_consumption = []

for subdict in constant_mc_result:
    values = [el if el!=None else 0 for el in list(subdict.values())]
    energy_consumption.append(values)

mean_energy_consumption = [sum(x)/len(x) for x in zip(*energy_consumption)]
sd_energy_consumption = [np.std(x) for x in zip(*energy_consumption)]


constant_mc_result_mean['mean_energy'] = mean_energy_consumption
constant_mc_result_sd['std_energy'] = sd_energy_consumption

months = ['Jan', 'Feb','Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
appliance_month_dict = {appliance: {month: [] for month in months} for appliance in appliance_with_variable_mc}
appliance_month_dict_mean = {appliance: {month: [] for month in months} for appliance in appliance_with_variable_mc}
appliance_month_dict_sd = {appliance: {month: [] for month in months} for appliance in appliance_with_variable_mc}

for df in variable_mc_result:
    for appliance in df.columns:
        for month in months:
            appliance_month_dict[appliance][month].append(df[appliance][month])


for appliance, energydict in appliance_month_dict.items():
    for month, values in energydict.items():
        appliance_month_dict_mean[appliance][month] = sum(values)/len(values)
        appliance_month_dict_sd[appliance][month] = np.std(values)



df = pd.DataFrame(constant_mc_result_mean)
df.to_csv(os.path.join(r'C:\Users\KDUWADI\Desktop\BRPL\survey_result', 'constant_mc_mean.csv'))

df = pd.DataFrame(constant_mc_result_sd)
df.to_csv(os.path.join(r'C:\Users\KDUWADI\Desktop\BRPL\survey_result', 'constant_mc_sd.csv'))

df = pd.DataFrame(appliance_month_dict_mean)
df.to_csv(os.path.join(r'C:\Users\KDUWADI\Desktop\BRPL\survey_result', 'variable_mc_mean.csv'))

df = pd.DataFrame(appliance_month_dict_sd)
df.to_csv(os.path.join(r'C:\Users\KDUWADI\Desktop\BRPL\survey_result', 'variable_mc_sd.csv'))