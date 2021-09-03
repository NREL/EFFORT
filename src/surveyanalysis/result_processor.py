
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


energy_data = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\survey_data\Energy consumption and sanctioned load.csv'
energy_data =pd.read_csv(energy_data)
energy_data = energy_data.fillna(0)
customers_energy_consumption, ca_nums = [], []
for cust in range(len(energy_data)):
    row_data = energy_data.loc[cust]
    energy = 0
    flag, flag1 = 0, 0
    for col in energy_data.columns:
        if '-' in col:
            if row_data[col] <0 or row_data[col] >500: 
                flag=1
            if row_data[col] >= 350 and row_data[col] <500:
                flag1= 1
            energy += row_data[col]
    if flag==0 and flag1==1:
        ca_nums.append(row_data['Consumer Account (CA) Number'])
        customers_energy_consumption.append(energy)

plt.hist(customers_energy_consumption)
plt.xlabel('Energy consumption (kWh)')
plt.ylabel('Occurences')
plt.show()


result_path = r'C:\Users\KDUWADI\Desktop\BRPL\survey_result'
constant_mc = os.path.join(result_path,'constant_mc_mean.csv')
variable_mc = os.path.join(result_path,'variable_mc_mean.csv')

num_of_customers = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\survey_data\number_of_equipments.csv'

constant_mc_data = pd.read_csv(constant_mc, index_col='Appliances')
variable_mc_data = pd.read_csv(variable_mc)
variable_mc_data = variable_mc_data.fillna(0)
num_of_customer_data = pd.read_csv(num_of_customers)

customers_energy_consumption = []

appliance_with_constant_mc = ['lighting', 'water_pump','washing_machine', 'dishwashers', 'washer_dryer', \
                    'hair_dryer', 'toaster', 'coffe_maker', 'laptops', 'televisions', 'routers','clothing_iron', 'refrigerator_l300', 'refrigerator_g300' ]

appliance_with_variable_mc = ['fans', 'coolers', 'air_heater', 'ac_unit', 'geyser_electric' ]

energy_consumption_dict = {i: {} for i in range(1,13,1)}
appliance_count_dict = {}

for cust in range(len(num_of_customer_data)):

    energy = 0
    row_data = num_of_customer_data.loc[cust]
    for app in appliance_with_constant_mc:
        if app != 'lighting':
            num_of_app = row_data[app] if not np.isnan(row_data[app]) else 0
            en = num_of_app*constant_mc_data['mean_energy'][app]*12
            if not np.isnan(en): energy += en
        else:
            num_of_app = np.nansum([row_data['incandescent_bulb'],row_data['cfl_bulb'],row_data['led_bulb']])
            en = num_of_app*constant_mc_data['mean_energy'][app]*12
            if not np.isnan(en): energy += en
        
        if row_data['Consumer Account (CA) Number'] in ca_nums:
            for key, subdict in energy_consumption_dict.items():
                if app not in subdict:
                    energy_consumption_dict[key][app] = 0
                else:
                    energy_consumption_dict[key][app] += en if not np.isnan(en) else 0
            
        if app not in appliance_count_dict:
            appliance_count_dict[app] = 0
        else:
            appliance_count_dict[app] += num_of_app

    for app in appliance_with_variable_mc:
        if app != 'lighting':
            num_of_app = row_data[app] if not np.isnan(row_data[app]) else 0
            var_row_data = variable_mc_data[app].tolist()
            en = np.nansum(var_row_data)*num_of_app
            if not np.isnan(en): energy += en
        else:
            num_of_app = np.nansum([row_data['incandescent_bulb'],row_data['cfl_bulb'],row_data['led_bulb']])
            var_row_data = variable_mc_data[app].tolist()
            en = num_of_app*np.nansum(var_row_data)
            if not np.isnan(en): energy += en

        if row_data['Consumer Account (CA) Number'] in ca_nums:
            for key, subdict in energy_consumption_dict.items():
                if app not in subdict:
                    energy_consumption_dict[key][app] = 0
                    appliance_count_dict[app] = 0
                else:
                    energy_consumption_dict[key][app] += var_row_data[key-1] if not np.isnan(var_row_data[key-1]) else 0
        
        if app not in appliance_count_dict:
                appliance_count_dict[app] = 0
        else:
            appliance_count_dict[app] += num_of_app

    if row_data['Consumer Account (CA) Number'] in ca_nums:
        customers_energy_consumption.append(energy)

print(appliance_count_dict)

#print(customers_energy_consumption)
plt.hist(customers_energy_consumption)
plt.xlabel('Energy consumption (kWh)')
plt.ylabel('Occurences')
plt.show()

labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] + \
     ['fans', 'coolers', 'air_heater', 'ac_unit', 'geyser_electric' ]

colors = ['#C5D1EB', '#92AFD7', '#5A7684', '#395B50', '#1F2F16' , '#A6C48A', '#89043D', '#18F2B2', '#FF8A5B', '#EA526f', '#7D1D3F' ,'#FED766','#FE4A49', '#0000FF', '#7CEA9C','#E2C044', '#D3D0CB']

sources, targets, values, linecolors = [], [], [], []
for month, energydict in energy_consumption_dict.items():
    for app, energy in energydict.items():
        if app in labels:
            sources.append(month-1)
            targets.append(labels.index(app))
            values.append(energy)
            linecolors.append(colors[labels.index(app)])

import plotly.graph_objects as go

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels, 
      color= colors
    ),
    link = dict(
      source = sources,
      target = targets,
      value = values, 
      color = linecolors
  ))])

fig.update_layout(title_text="Variable Energy Consumption Appliances", font_size=10)
fig.show()

const_app_dict = {'app': [], 'energy': []}
for month, energydict in energy_consumption_dict.items():
    for app, energy in energydict.items():
        if app not in ['fans', 'coolers', 'air_heater', 'ac_unit', 'geyser_electric' ]:
            if app not in const_app_dict['app']:
                const_app_dict['app'].append(app)
                const_app_dict['energy'].append(energy)

import plotly.express as px
df = pd.DataFrame(const_app_dict)
fig = px.pie(df, values='energy', names='app', title='Constant energy appliances')
fig.show()


