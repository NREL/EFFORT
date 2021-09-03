"""
Use this module to find base price - priority order method
"""

import pandas as pd
import os

data_path = r'C:\Users\KDUWADI\Desktop\BRPL\merit_order_excel_sheets'
plant_capacity_data = pd.read_excel(os.path.join(data_path, 'plant_capacity.xlsx'))
plant_price_data = pd.read_excel(os.path.join(data_path,'merit_order_dispatch_data_cleaned.xlsx'), index_col=0)

plant_capacity_dict = dict(zip(plant_capacity_data['Plant'],plant_capacity_data['BRPL share MW']))
month_days = {'Apr': 30,'May': 31, 'Jun': 30, 'Jul': 31, 'Aug' : 31, 'Sep' : 30, 'Oct' : 31, 'Nov' : 30, 'Dec' : 31, 'Jan' : 31, 'Feb' : 28, 'Mar': 31}
plant_price_data_dict  = {plant_name: [] for plant_name in plant_price_data.index}

# ['Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar']
for month_name in ['Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar']:#['Nov','Dec','Jan','Feb','Mar']:
    month_day = month_days[month_name]
    for plant in plant_price_data_dict.keys():
        price = plant_price_data[month_name][plant]
        plant_price_data_dict[plant].extend([price]*month_day*24)


load_data = pd.read_csv(r'C:\Users\KDUWADI\Desktop\BRPL\data_year\load.csv')['Load'].tolist()
net_load = pd.read_csv(r'C:\Users\KDUWADI\Desktop\BRPL\data_year\netload.csv')['netLoad'].tolist()
renewable_load = [x[0]-x[1] for x in zip(load_data,net_load)]

RENEWABLE_PRICE = 3700


def find_base_price(
                load_data: list=[],
                plant_capacity: dict={},
                plant_price: dict={},
                renewable_load: list=[],
            ):
    

    # load_data = [10,20,40,35,30,25,15]
    # plant_capacity = {
    #     'plantA': 20,
    #     'plantB': 50
    # }

    # plant_price = {
    #     'plantA': [4,5,6,7,1,3,4],
    #     'plantB': [1,4,5,8,9, 2,5]
    # }

    purchase_price = 0
    for id, load in enumerate(load_data):
        
        plants_name = list(plant_price.keys())
        price = [price_array[id] for plants, price_array in plant_price.items()]
        sorted_plant, sorted_price = zip(*sorted(zip(plants_name,price), key=lambda x: x[1]))
       
        for plant, price in zip(sorted_plant, sorted_price):
            if load > plant_capacity[plant]:
                purchase_price += price*1000*plant_capacity[plant]
            else:
                purchase_price += price*1000*load

            load = load - plant_capacity[plant]
            if load <=0:
                break
    
    renewable_purchase = sum(renewable_load)*RENEWABLE_PRICE
    base_price = (purchase_price+renewable_purchase)/(sum(load_data)+sum(renewable_load))
    print(base_price)

    return base_price
        
base_price = find_base_price(load_data=net_load,
                plant_capacity=plant_capacity_dict,
                plant_price=plant_price_data_dict,
                renewable_load=renewable_load)