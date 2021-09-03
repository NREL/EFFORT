
import pandas as pd
import math
import matplotlib.pyplot as plt
import random


residential_survey_data_path = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\survey_data\Residential Consumer Survey Response_09072020.xlsx'
res_sur_data = pd.read_excel(residential_survey_data_path, skiprows=1)

months = ['January', 'February','March','April','May','June','July','August','September','October','November','December']

cust_heating_cooling_month = {'ca_number': [], 'heating_start_month': [],'heating_end_month': [], 'cooling_start_month': [], 'cooling_end_month': [] }
for i in range(len(res_sur_data)):
    row_data = res_sur_data.loc[i]
    cust_heating_cooling_month['ca_number'].append(row_data['Consumer Account (CA) Number'])
    cust_heating_cooling_month['heating_start_month'].append(row_data['what month of the year do you typically Start using air heater home heating (choose one)?'])
    cust_heating_cooling_month['heating_end_month'].append(row_data['what month of the year do you typically stop using air heater for home heating (choose one)?'])
    cust_heating_cooling_month['cooling_start_month'].append(row_data['If any air cooling (i.e. portable air cooler/air conditioning) is used at your residence, what month of the year do you typically start using home cooling (choose one)?'])
    cust_heating_cooling_month['cooling_end_month'].append(row_data['If any air cooling (i.e. portable air cooler/air conditioning) is used at your residence, what month of the year do you typically stop using home cooling (choose one)?'])


for key, values in cust_heating_cooling_month.items():
    if key != 'ca_number':
        common_months = list(set(months)&set(values))
        new_values = [el if el in common_months else random.choice(common_months) for el in values]
        cust_heating_cooling_month[key] = new_values

df = pd.DataFrame(cust_heating_cooling_month)
df.to_csv('Heating_cooling_month_for_customers.csv')

"""
Script to export number of customers csv file
"""


column_mapping_dict = {
    'ca_number':  'Consumer Account (CA) Number',
    'num_of_equipments':
        {
            'fans': 'Number of Fans in your house including ceiling fans and/or portable fans',
            'coolers': 'How many coolers (i.e. portable plug cooling appliances) do you own at your home ?',
            'air_heater': 'No. of air heaters (i.e. portable plug heating appliances) do you own at your home?',
            'ac_unit': 'Number of Air Conditioners',
            'incandescent_bulb':  'Out of all light bulbs installed approximately how many are incandescent or halogen light bulbs? (see picture below for an example)',
            'cfl_bulb' :  'Out of all light bulbs installed approximately how many are CFL light bulbs? (see picture below for an example)',
            'led_bulb': 'Out of all light bulbs installed approximately how many are LED light bulbs? (see picture below for an example)',
            'tubelights': 'Out of those light bulbs approximately how many are tube lights? (see picture below for an example)',
            'refrigerator_l300': 'Which of the following appliances do you have at your residence and how many of each? [Number of Refrigerators (<300litres)]',
            'refrigerator_g300' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Refrigerators (>300 Litres)]',
            'washing_machine' : 'Which of the following appliances do you have at your residence and how many of each? [No.of Washing Machines]',
            'dishwashers' : 'Which of the following appliances do you have at your residence and how many of each? [No.of Dish Washers]',
            'washer_dryer' : 'Which of the following appliances do you have at your residence and how many of each? [No. of Washer Dryer/Tumble Dryers]',
            'water_pump' : 'Which of the following appliances do you have at your residence and how many of each? [No.of Water Pumps]',
            'geyser_electric': 'Electric Water Heater (Geyser)  ',
            'hair_dryer' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Hair Dryers]',
            'toaster' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Electric Toasters]',
            'coffe_maker': 'Which of the following appliances do you have at your residence and how many of each? [Number of Coffee Makers]',
            'laptops' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Laptops]',
            'televisions' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Televisions]',
            'routers' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Wi-Fi Routers]',
            'clothing_iron' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Electric Clothing Irons]',
            'batteries' : 'Which of the following appliances do you have at your residence and how many of each? [Number of Battery Systems]',

            }
}

equipment_dataframe_dict = {key: [] for key in column_mapping_dict['num_of_equipments'].keys()}
for i in range(len(res_sur_data)):
    row_data = res_sur_data.loc[i]
    for key in equipment_dataframe_dict.keys():
        num = row_data[column_mapping_dict['num_of_equipments'][key]]
        if num == 'None': num = 0
        if num == 'Do not know/Unsure' or num == 'Do not know': num = math.nan
        if '-' in str(num):
            num = int((int(num.split('-')[0]) + int(num.split('-')[1]))/2)
        if 'more' in str(num):
            num = int(num.split(' ')[0])
        equipment_dataframe_dict[key].append(num)

equipment_dataframe = pd.DataFrame(equipment_dataframe_dict)
equipment_dataframe.index = res_sur_data[column_mapping_dict['ca_number']]
equipment_dataframe.to_csv('number_of_equipments.csv')

# fig, ax = plt.subplots(nrows=int(len(column_mapping_dict['num_of_equipments'].keys())/4+1), ncols=4)
# counter = 0
# for keys, array in equipment_dataframe_dict.items():
#     row = int(counter/4)
#     col = counter%4
#     ax[row,col].plot(range(len(array)),array)
#     ax[row,col].set_title(keys)
#     counter += 1
# plt.show()

