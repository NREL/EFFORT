
import pandas as pd
import os
import math
import numpy as np
from sklearn.linear_model import LinearRegression



DATA_FOLDER = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\survey_data'
num_of_equips = 'number_of_equipments.csv'
customer_energy = 'Energy consumption and sanctioned load.csv'
heating_cooling_months = 'Heating_cooling_month_for_customers.csv'
out_folder = r'C:\Users\KDUWADI\Desktop\BRPL\survey_data'


def check_within(start_month, end_month, check_month):

    month_converter = {'Jan': 'January',
                        'Feb': 'February',
                        'Mar' : 'March',
                        'Apr' : 'April',
                        'May' : 'May',
                        'Jun' : 'June',
                        'Jul' : 'July',
                        'Aug' : 'August',
                        'Sep' : 'September',
                        'Oct' : 'October',
                        'Nov' : 'November',
                        'Dec' : 'December'}
    
    month_dict = {
        'January': 1,
        'February': 2,
        'March' : 3,
        'April' : 4,
        'May' : 5,
        'June' : 6,
        'July' : 7,
        'August' : 8,
        'September': 9,
        'October' : 10,
        'November' : 11,
        'December' : 12
    }

    check_month = month_converter[check_month]

    within_list = []
    if month_dict[start_month] <= month_dict[end_month]:

        within_list = list(range(month_dict[start_month], month_dict[end_month]+1,1))
    else:
        within_list = list(range(month_dict[start_month], 13,1)) + list(range(1, month_dict[end_month]+1 ,1))

    return month_dict[check_month] in within_list
 
def generate_csvs(shuffle=True, num_of_customers=50):
    
    num_of_equips_data = pd.read_csv(os.path.join(DATA_FOLDER, num_of_equips), na_filter=False)
    cust_energy_data = pd.read_csv(os.path.join(DATA_FOLDER, customer_energy))
    heat_cool_month_data = pd.read_csv(os.path.join(DATA_FOLDER, heating_cooling_months))

    num_of_equips_data = num_of_equips_data.set_index(['Consumer Account (CA) Number'])
    cust_energy_data = cust_energy_data.set_index(['Consumer Account (CA) Number'])
    heat_cool_month_data = heat_cool_month_data.set_index(['ca_number'])

    appliances = list(num_of_equips_data.columns)
    appliances = appliances[:-1] # removing batteries

    coeffmatrix_app = {'consumer':[], 'appliance': [], 'coeffmatrix_app': []}
    coeffmatrix_app_timeseries = {'consumer':[], 'appliance': [], 'coeffmatrix_app_timeseries': []}
    usagematrix_app_timeseries = {'consumer' : [], 'month': [], 'appliance': [], 'usagematrix_app_timeseries': []}
    energy = {'consumer':[], 'month': [], 'energy': []}
    
    
    row = 0

    appliance_list = ['fans', 'coolers', 'air_heater', 'ac_unit', 'incandescent_bulb', \
                'cfl_bulb', 'led_bulb', 'tubelights', 'refrigerator_l300', 'refrigerator_g300', \
                'washing_machine', 'dishwashers', 'washer_dryer', 'water_pump', 'geyser_electric',\
                'hair_dryer', 'toaster', 'coffe_maker', 'laptops', 'televisions', 'routers', \
                'clothing_iron']

    appliance_with_constant_mc = ['lighting', 'water_pump','washing_machine', 'dishwashers', 'washer_dryer', \
                    'hair_dryer', 'toaster', 'coffe_maker', 'laptops', 'televisions', 'routers','clothing_iron', 'refrigerator_l300', 'refrigerator_g300' ]
    # appliance_with_variable_mc = ['fans', 'coolers', 'air_heater', 'ac_unit', 'incandescent_bulb', \
    #         'cfl_bulb', 'led_bulb', 'tubelights', \
    #            'water_pump', 'geyser_electric' ]

    appliance_with_variable_mc =  ['fans', 'coolers', 'air_heater', 'ac_unit', 'geyser_electric' ]

    
    ca_numbers = list(num_of_equips_data.index)
    if shuffle: np.random.shuffle(ca_numbers)

    if num_of_customers > len(ca_numbers):
        num_of_customers = len(ca_numbers)

    if num_of_customers <=0:
        num_of_customers = 1

    customers = []
    for ca in ca_numbers:
        
        row_data = num_of_equips_data.loc[ca]
        
        try:
            row_data = row_data.tolist()
        except Exception as e:
            row_data = row_data[:1].loc[ca].tolist()


        if '' not in row_data:
            row_data = [float(el) for el in row_data]
            if ca in list(cust_energy_data.index):
                
                
                row_coeff = cust_energy_data.loc[ca]  

                try:
                    energy_list = row_coeff.tolist()
                except Exception as e:
                    energy_list = row_coeff[:1].loc[ca].tolist()

                energy_list = [energy_list[id] for id in [11,12,13,2,3,4,5,6,7,8,9,10]]
                
                check_outside = [True if el<=0 or el>500 else False for el in energy_list] 
                check_between = [True if el>=350 and el<500 else False for el in energy_list] 
                
                #if True not in flags:
                if True not in check_outside and True in check_between:
                    for month in range(12):
                        energy['consumer'].append(row)
                        energy['month'].append(month)
                        energy['energy'].append(energy_list[month])
                
                row_month = heat_cool_month_data.loc[ca]

                try:
                    row_month = row_month.tolist()
                except Exception as e:
                    row_month = row_month[:1].loc[ca].tolist()

                if True not in check_outside and True in check_between:
                    for col in range(len(appliance_with_constant_mc)):
                        coeffmatrix_app['consumer'].append(row)
                        coeffmatrix_app['appliance'].append(col)

                        if appliance_with_constant_mc[col] == 'lighting':
                            app_indexes = [4,5,6,7]
                            coeffmatrix_app['coeffmatrix_app'].append(sum(row_data[app_index] for app_index in app_indexes)) 
                        else:
                            app_index = appliance_list.index(appliance_with_constant_mc[col])
                            coeffmatrix_app['coeffmatrix_app'].append(row_data[app_index])

                    
                    for col in range(len(appliance_with_variable_mc)):

                        coeffmatrix_app_timeseries['consumer'].append(row)
                        coeffmatrix_app_timeseries['appliance'].append(col)

                        if appliance_with_variable_mc[col] == 'lighting':
                            app_indexes = [4,5,6,7]
                            coeffmatrix_app_timeseries['coeffmatrix_app_timeseries'].append(sum(row_data[app_index] for app_index in app_indexes)) 

                        else:
                            app_index = appliance_list.index(appliance_with_variable_mc[col])
                            coeffmatrix_app_timeseries['coeffmatrix_app_timeseries'].append(row_data[app_index]) 

                        
                        for id, month in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                            usagematrix_app_timeseries['consumer'].append(row)
                            usagematrix_app_timeseries['appliance'].append(col)
                            usagematrix_app_timeseries['month'].append(id)


                            if appliance_with_variable_mc[col] in ['fans', 'coolers','ac_unit']:
                                if check_within(row_month[3], row_month[4], month): 
                                    usagematrix_app_timeseries['usagematrix_app_timeseries'].append(1)
                                else:
                                    usagematrix_app_timeseries['usagematrix_app_timeseries'].append(0)
                            
                            elif appliance_with_variable_mc[col] in ['air_heater', 'geyser_electric' ]: 
                                if check_within(row_month[1], row_month[2], month): 
                                    usagematrix_app_timeseries['usagematrix_app_timeseries'].append(1)
                                else:
                                    usagematrix_app_timeseries['usagematrix_app_timeseries'].append(0)

                            else:
                                usagematrix_app_timeseries['usagematrix_app_timeseries'].append(1)

                    row+=1
                    customers.append(ca)
                    if row >=num_of_customers:
                        break;
                    


    # Write appliance.csv file
    df = pd.DataFrame({'appliance':list(range(len(appliance_with_constant_mc)))})
    df.to_csv(os.path.join(out_folder, 'appliance.csv'), index=False)

    df = pd.DataFrame({'appliance_timeseries':list(range(len(appliance_with_variable_mc)))})
    df.to_csv(os.path.join(out_folder, 'appliance_timeseries.csv'), index=False)

    # Write consumer.csv file
    df = pd.DataFrame({'consumer':list(range(len(customers)))})
    df.to_csv(os.path.join(out_folder, 'consumer.csv'),index=False)

    # Write month.csv file
    df = pd.DataFrame({'month':list(range(12))})
    df.to_csv(os.path.join(out_folder, 'month.csv'), index=False)

    # Write coeff_matrix.csv file
    df = pd.DataFrame(coeffmatrix_app)
    df.to_csv(os.path.join(out_folder, 'coeffmatrix_app.csv'),index=False)
    df = pd.DataFrame(coeffmatrix_app_timeseries)
    df.to_csv(os.path.join(out_folder, 'coeffmatrix_app_timeseries.csv'),index=False)

    # Write energy.csv file
    df = pd.DataFrame(energy)
    df.to_csv(os.path.join(out_folder, 'energy.csv'),index=False)


    df = pd.DataFrame(usagematrix_app_timeseries)
    df.to_csv(os.path.join(out_folder, 'usagematrix_app_timeseries.csv'),index=False)

    return customers


generate_csvs()
        