"""
Use this script to run scenarios for TOU optimization 
involving merit order plants for summer and winter months.
Generates input data necessary for optimization in each scenario
and runs optimization.

"""


import os
from tou_merit_order_optimization import RunModel
from pemv1 import GeneratePEM
import pandas as pd
import time


summer_data_path = r'C:\Users\KDUWADI\Desktop\BRPL\data_summer'
winter_data_path = r'C:\Users\KDUWADI\Desktop\BRPL\data_winter'
export_path = r'C:\Users\KDUWADI\Desktop\BRPL\all_results'

scenarios = ['high_high','high_medium','high_low', 'medium_high',\
     'medium_medium', 'medium_low','low_high', 'low_medium', 'low_low']


price_elasticity = {'high': 0.6, 'medium': 0.42, 'low': 0.2}
response_window = {'high': 8, 'medium': 4, 'low': 2}


def generate_windows_csv(size, export_path):

    window_pre = {'time': [], 'window_pre': []}
    window_post = {'time': [], 'window_post': []}
    for i in range(size):
        window_post['time'].append(i)
        window_pre['time'].append(i)
        if i<12:
            window_pre['window_pre'].append(i)
            window_post['window_post'].append(23-i)
        elif i>=(size-12):
            window_pre['window_pre'].append(23-size+i+1)
            window_post['window_post'].append(size-i-1)
        else:
            window_pre['window_pre'].append(11)
            window_post['window_post'].append(12)
    
    window_pre_df = pd.DataFrame(window_pre)
    window_post_df = pd.DataFrame(window_post)

    window_pre_df.to_csv(os.path.join(export_path,'window_pre.csv'), index=False)
    window_post_df.to_csv(os.path.join(export_path,'window_post.csv'), index=False)


# generate_windows_csv(24, r'C:\Users\KDUWADI\Desktop\BRPL\data_merit_order')
# generate_windows_csv(8760, r'C:\Users\KDUWADI\Desktop\BRPL\data_year')

#for scen in scenarios:

for elas in [0.2,0.4,0.6]:
    for window in [3,4,5,6]:
        
        # print(f'Working on {elas, window} for summer months')
        scen = str(elas)+'_'+str(window)
        
        # # work on summer month

        # start_time = time.time()
        # result_folder = os.path.join(export_path, scen + '_summer')
        # if not os.path.exists(result_folder):
        #     os.mkdir(result_folder)
                    
        # pem = GeneratePEM(price_elasticity= elas, 
        #             response_window= window, 
        #             non_responsive_hours=[2,3,4,5], 
        #             size = 24,
        #             cross_elasticity_method='gradient',
        #             export_path = os.path.join(summer_data_path, 'pem.csv'))
        # #print(pem.get_pem_matrix())

        # # Generate window length csv file
        # generate_windows_csv(5136, summer_data_path)

        
        # print('Generated PEM successfully.')
        # opt_config_dict = {
        #         'export_path': result_folder,
        #         'plot_result': False,
        #         'on_time_list': [0,1,15,16,17,22,23],
        #         'data_path': summer_data_path,
        #         'num_of_hours': 5136,
        #         'solver': 'ipopt'
        #     }
        # instance = RunModel(**opt_config_dict)
        # end_time = time.time()
        # print(f'Elapsed time is : {end_time-start_time} seconds')

        print(f'Working on {scen} for winter months')

        result_folder = os.path.join(export_path, scen + '_winter')
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)

        GeneratePEM(price_elasticity= elas, 
                    response_window= window, 
                    non_responsive_hours=[2,3,4,5],
                    size=24,
                    cross_elasticity_method='gradient',
                    export_path = os.path.join(winter_data_path, 'pem.csv'))

         # Generate window length csv file
        generate_windows_csv(3624, winter_data_path)

        opt_config_dict = {
                'export_path': result_folder,
                'plot_result': False,
                'on_time_list': [9,10,11,12],
                'data_path': winter_data_path,
                'num_of_hours': 3624,
                'solver': 'ipopt'
            }
        instance = RunModel(**opt_config_dict)