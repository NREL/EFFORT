import os
import pandas as pd
from pemv1 import GeneratePEM
import matplotlib.pyplot as plt
import json
import datetime
import numpy as np

"""
Used to plot results of all scenarios
"""
DATA_PATH = r'C:\Users\KDUWADI\Desktop\BRPL\all_results'


peak_power_reduction = {}
price_ratio = {}
saving_percentage = {}
new_load_profile = {}
season  = 'summer'

for folder in os.listdir(DATA_PATH):
    
    if season in folder:
        elasticity = folder.split('_')[0] 
        window = folder.split('_')[1]
        if elasticity not in peak_power_reduction:
            peak_power_reduction[elasticity] = {'x': [], 'y': []}
            price_ratio[elasticity] = {'x': [], 'y': []}
            saving_percentage[elasticity] = {'x': [], 'y': []}

        peak_power_reduction[elasticity]['x'].append(window)
        price_ratio[elasticity]['x'].append(window)
        saving_percentage[elasticity]['x'].append(window)

        with open(os.path.join(DATA_PATH, folder, 'output.json'),'r') as infile:
            output_dict = json.load(infile)

        output_df = pd.read_csv(os.path.join(DATA_PATH, folder,'output.csv'))
        if season == 'winter':
            time_list = [datetime.datetime(2018,11,1,0,0,0) + datetime.timedelta(minutes=60)*i for i in range(len(output_df))]
        else:
            time_list = [datetime.datetime(2018,4,1,0,0,0) + datetime.timedelta(minutes=60)*i for i in range(len(output_df))]

        
        original_profile = output_df['Original Load MW'].tolist()
        peak_load = max(original_profile)
        new_load_profile[folder] = output_df['New Load MW'].tolist()

        peak_power_reduction[elasticity]['y'].append(output_dict['Peak load reduction (MW)']*100/peak_load)
        #price_ratio[elasticity]['y'].append(output_dict['On-peak off peak ratio'])
        pr = (output_dict['On-peak price (Rs./MWh)']-4418)/(output_dict['Off-peak price (Rs./MWh)']-4418)
        price_ratio[elasticity]['y'].append(pr)

        saving_percentage[elasticity]['y'].append(output_dict['Customers Saving (Rs in Million)']*100/output_dict['Customers original cost (Rs in Million)'])


print(peak_power_reduction)
print(price_ratio)
grouped_width = 1
grouped_space = 0.2
ind_width = (grouped_width-grouped_space)/len(peak_power_reduction)
counter = 0
el_t  = {
    '0.2': 'low',
    '0.4': 'medium',
    '0.6': 'high'
}

cw_t = {
    '3' : 'low',
    '5' : 'medium',
    '8': 'high'
}
for keys, items in peak_power_reduction.items():
    x_data_ = [(id+1)*grouped_width for id, val in enumerate(items['x'])]
    x_data = [id-(grouped_width-grouped_space)/2+ ind_width/2 +ind_width*counter for id in x_data_]
    plt.bar(x_data,items['y'],ind_width,label= 'self elasticity: '+ el_t[keys])
    counter+=1

x_, labels_ = [], []
for key, value in cw_t.items():
    if key in items['x']:
        labels_.append(value)
        x_.append(x_data_[items['x'].index(key)])

plt.xticks(x_, labels_)
plt.xlabel('Customer response window \n (in hours both forward and backward)')
plt.ylabel('Peak Reduction (%)')
plt.title('Summer result: on peak hours [0,1,15,16,17,22,23] \n linear gradient cross elasticity')
plt.legend()
plt.show()

counter = 0
for keys, items in price_ratio.items():
    x_data_ = [(id+1)*grouped_width for id, val in enumerate(items['x'])]
    x_data = [id-(grouped_width-grouped_space)/2+ ind_width/2 +ind_width*counter for id in x_data_]
    plt.bar(x_data,items['y'],ind_width,label= 'self elasticity: '+ el_t[keys])
    counter+=1

plt.xticks(x_, labels_)
plt.xlabel('Customer response window \n (in hours both forward and backward)')
plt.ylabel('On peak to Off peak price ratio')
plt.title('Summer result: on peak hours [0,1,15,16,17,22,23]\n linear gradient cross elasticity')
plt.legend()
plt.show()

for keys, items in saving_percentage.items():
    plt.plot(items['x'],items['y'],'--o',label= 'self elasticity: '+ str(keys))
plt.xlabel('Customer response window \n (in hours both forward and backward)')
plt.ylabel('Saving (%)')
plt.title('Summer result: on peak hours [0,1,15,16,17,22,23]\n linear gradient cross elasticity')
plt.legend()
plt.show()

# plot day worth profile
(month, day) = (1, 30) if season == 'winter' else (7,9)

for key, values in new_load_profile.items():
    if '_6' in key:
        val_indexes = [id for id, d in enumerate(time_list) if d.month == month and d.day == day]
        plt.plot(range(len(val_indexes)), np.array(values)[val_indexes], label=f"self elasticity : {key.split('_')[0]}")
plt.plot(range(len(val_indexes)), np.array(original_profile)[val_indexes], label=f'original profile')
plt.plot()
plt.legend()
plt.ylabel('Load (MW)')
plt.title('New profile for peak load day compared across \n multiple self elasticities for 6 hour window')
plt.show()

DATA_PATH = r'C:\Users\KDUWADI\Desktop\BRPL\all_results'


folders = ['high_high_summer', 'high_medium_summer', 'high_low_summer',
            'medium_high_summer', 'medium_medium_summer', 'medium_low_summer',
            'low_high_summer', 'low_medium_summer', 'low_low_summer']

# folders = ['high_high_winter', 'high_medium_winter','high_low_winter',
#             'medium_high_winter', 'medium_medium_winter', 'medium_low_winter',
#             'low_high_winter', 'low_medium_winter', 'low_low_winter']


# for scen in folders:
#     instance = GeneratePEM(price_elasticity=scen.split('_')[0], 
#                 consumers_response=scen.split('_')[1], 
#                 external_dict={},
#                  export_path = 'pem.csv')
#     instance.plot_pem()


peak_reduced = []
x_ticks = []

for folder in folders:

    load_data = pd.read_csv(os.path.join(DATA_PATH, folder, 'output.csv'))
    original_load = sorted(load_data['Original Load MW'].tolist(), reverse=True)
    new_load = sorted(load_data['New Load MW'].tolist(), reverse=True)
    peak_reduced.append(original_load[0]-new_load[0])
    x_ticks.append(folder.replace('_summer',''))

plt.bar(x_ticks, peak_reduced)
plt.ylabel('Peak Reduced (MW)')
plt.xticks(rotation=45)
plt.grid('off')
plt.show()


fixed_cost_saving = []
variable_cost_saving = []
on_peak_price, off_peak_price = [], []
for folder in folders:
    with open(os.path.join(DATA_PATH, folder, 'output.json'),'r') as infile:
        output_dict = json.load(infile)

    off_peak_price.append(output_dict['Off-peak price (Rs./MWh)'])
    on_peak_price.append(output_dict['On-peak price (Rs./MWh)'])
    variable_cost_saving.append(output_dict['Utility variable cost saving (Rs in Million)'])
    fixed_cost_saving.append(output_dict['Utility fixed cost saving (Rs in Million)'])

plt.plot(range(len(off_peak_price)),off_peak_price,'--ro',label='off peak price')
plt.plot(range(len(off_peak_price)),on_peak_price,'--go',label='on peak price')
plt.xticks(list(range(len(off_peak_price))), x_ticks,rotation=45)
plt.grid('off')
plt.ylabel('Rs/MWh')
plt.legend()
plt.show()

x1 = [el-0.2 for el in range(len(fixed_cost_saving))]
x2 = [el+0.2 for el in range(len(fixed_cost_saving))]
barwidth = 0.25
# plt.bar(x1, fixed_cost_saving, width=barwidth, label='Fixed cost saving')
# plt.bar(x2, variable_cost_saving, width=barwidth, label='Variable cost saving')

plt.bar(range(len(fixed_cost_saving)), variable_cost_saving, label='Variable cost saving')
plt.bar(range(len(fixed_cost_saving)), fixed_cost_saving, bottom=variable_cost_saving, label='Fixed cost saving', alpha=0.4)
plt.xticks(list(range(len(x1))), x_ticks,rotation=45)
plt.ylabel('Rs. (in Million)')
plt.grid('off')
plt.legend()
plt.show()

# Compare what generators are producing before and after 
gen_energy_before = {}
gen_energy_after = {}

gen_data = pd.read_csv(os.path.join(DATA_PATH, 'high_medium_summer', 'gen_output.csv'))
for col in gen_data.columns:
    if col != 'Unnamed: 0':
        gen_energy_after[col] = sum(gen_data[col].tolist())/1000

net_load_prof = pd.read_csv(r'C:\Users\KDUWADI\Desktop\BRPL\data_summer\netload.csv')['netLoad'].tolist()
data_path = r'C:\Users\KDUWADI\Desktop\BRPL\merit_order_excel_sheets'
plant_capacity_data = pd.read_excel(os.path.join(data_path, 'plant_capacity.xlsx'))
plant_price_data = pd.read_excel(os.path.join(data_path,'merit_order_dispatch_data_cleaned.xlsx'), index_col=0)


plant_capacity = dict(zip(plant_capacity_data['Plant'],plant_capacity_data['BRPL share MW']))
month_days = {'Apr': 30,'May': 31, 'Jun': 30, 'Jul': 31, 'Aug' : 31, 'Sep' : 30, 'Oct' : 31, 'Nov' : 30, 'Dec' : 31, 'Jan' : 31, 'Feb' : 28, 'Mar': 31}
plant_price  = {plant_name: [] for plant_name in plant_price_data.index}

# ['Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar']
# ['Nov','Dec','Jan','Feb','Mar']
for month_name in ['Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar']:
    month_day = month_days[month_name]
    for plant in plant_price.keys():
        price = plant_price_data[month_name][plant]
        plant_price[plant].extend([price]*month_day*24)

gen_energy_before = {plant: 0 for plant in plant_price.keys()}
for id, load in enumerate(net_load_prof):
        
    plants_name = list(plant_price.keys())
    price = [price_array[id] for plants, price_array in plant_price.items()]
    sorted_plant, sorted_price = zip(*sorted(zip(plants_name,price), key=lambda x: x[1]))
       
    for plant, price in zip(sorted_plant, sorted_price):
        if load > plant_capacity[plant]:
            if plant not in gen_energy_before: 
                gen_energy_before[plant] = plant_capacity[plant]/1000
            else:
                gen_energy_before[plant] += plant_capacity[plant]/1000
        else:
            if plant not in gen_energy_before: 
                gen_energy_before[plant] = load/1000
            else:
                gen_energy_before[plant] += load/1000

        load = load - plant_capacity[plant]
        
        if load <=0:
            break


before_energy = [gen_energy_before[plant] for plant in plant_price.keys()]
after_energy = [gen_energy_after[plant] for plant in plant_price.keys()]

x1 = [el-0.2 for el in range(len(before_energy))]
x2 = [el+0.2 for el in range(len(before_energy))]
barwidth = 0.25
plt.bar(x1, before_energy, width=barwidth, label='Before')
plt.bar(x2, after_energy, width=barwidth, label='After')
plt.xticks(list(range(len(x1))),list(plant_price.keys()),  rotation=90)
plt.ylabel('Energy purchased (GWh)')
plt.legend()
plt.show()


diff_energy = [x[1]-x[0] for x in zip(after_energy,before_energy)]
plt.bar(list(plant_price.keys()), diff_energy)
plt.ylabel('Difference (Before-After) \n in energy generation (GWh)')
plt.xticks(rotation=90)
plt.grid('off')
plt.show()

