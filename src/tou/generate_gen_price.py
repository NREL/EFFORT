'''
Use this module to generate 'gen_price.csv' used in optimization based on merit order
'''

# Internal libraries
import os

# Third-party libraries
import pandas as pd


plant_data_path = r'C:\Users\KDUWADI\Desktop\BRPL\merit_order_excel_sheets'
merit_order_data = pd.read_excel(os.path.join(plant_data_path, 'merit_order_dispatch_data_cleaned.xlsx'),index_col=0)


gen_price_dict = {'row':[],'col':[], 'gen_price':[]}

summer_month_dict = {
    'Apr' : [0, 720],
    'May' :[720, 1464],
    'Jun' : [1464,2184],
    'Jul': [2184, 2928],
    'Aug' : [2928, 3672],
    'Sep' : [3672, 4392],
    'Oct' : [4392, 5136],
}
winter_month_dict = {
    'Nov' : [0, 720],
    'Dec' : [720, 1464],
    'Jan' : [1464, 2208],
    'Feb' : [2208, 2880 ],
    'Mar': [2880, 3624],
}

year_dict = {
    'Apr' : [0, 720],
    'May' :[720, 1464],
    'Jun' : [1464,2184],
    'Jul': [2184, 2928],
    'Aug' : [2928, 3672],
    'Sep' : [3672, 4392],
    'Oct' : [4392, 5136],
    'Nov' : [5136, 5856],
    'Dec' : [5856, 6600],
    'Jan' : [6600, 7344],
    'Feb' : [7344, 8016],
    'Mar': [8016, 8760],
}
TIME_LENGTH = 5136+3624
# generate gen_price.csv for a day
for t in range(TIME_LENGTH):
    gen_price_dict['row'].extend([t]*len(merit_order_data))
    gen_price_dict['col'].extend(list(range(len(merit_order_data))))

    for keys, array in year_dict.items():
        if array[0] <= t < array[1]:
            price_array = merit_order_data[keys].tolist()
            price_array = [el*1000 for el in price_array]
            gen_price_dict['gen_price'].extend(price_array)
            

export_path = r'C:\Users\KDUWADI\Desktop\BRPL\data_year'
df = pd.DataFrame(gen_price_dict)
df.to_csv(os.path.join(export_path, 'gen_price_matrix.csv'),index=False)


# # generate gen_price.csv for a day
# for t in range(TIME_LENGTH):
#     gen_price_dict['row'].extend([t]*len(merit_order_data))
#     gen_price_dict['col'].extend(list(range(len(merit_order_data))))

#     for keys, array in summer_month_dict.items():
#         if array[0] <= t < array[1]:
#             price_array = merit_order_data[keys].tolist()
#             price_array = [el*1000 for el in price_array]
#             gen_price_dict['gen_price'].extend(price_array)
            

# export_path = r'C:\Users\KDUWADI\Desktop\BRPL\data_summer'
# df = pd.DataFrame(gen_price_dict)
# df.to_csv(os.path.join(export_path, 'gen_price_matrix.csv'),index=False)


# TIME_LENGTH = 3624

# gen_price_dict = {'row':[],'col':[], 'gen_price':[]}

# # generate gen_price.csv for a day
# for t in range(TIME_LENGTH):
#     gen_price_dict['row'].extend([t]*len(merit_order_data))
#     gen_price_dict['col'].extend(list(range(len(merit_order_data))))

#     for keys, array in winter_month_dict.items():
#         if array[0] <= t < array[1]:
#             price_array = merit_order_data[keys].tolist()
#             price_array = [el*1000 for el in price_array]
#             gen_price_dict['gen_price'].extend(price_array)
            

# export_path = r'C:\Users\KDUWADI\Desktop\BRPL\data_winter'
# df = pd.DataFrame(gen_price_dict)
# df.to_csv(os.path.join(export_path, 'gen_price_matrix.csv'),index=False)