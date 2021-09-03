from pem import GeneratePEM
from tou_optimization import RunModel
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# off_peak_time = [1]*18 + [0]*5 + [1]
# on_peak_time = [0]*18 + [1]*5 + [0]

# 3624
fig1, ax1 = plt.subplots(3,3)
fig2, ax2 = plt.subplots(3,3)
row, col, counter = 0, 0, 0

data_path = r'C:\Users\KDUWADI\Desktop\BRPL\data'
export_path = r'C:\Users\KDUWADI\Desktop\BRPL\day_result'
opt_config_dict = {
        'export_path': '.',
        'plot_result': False,
        'on_time_list': [18,19,20,21,22,23],
        'data_path': data_path,
        'num_of_hours':24,#3624,
        'solver': 'ipopt'
    }


result_dict = {'Scenario':[], 'Parameter': [], 'Value':[]}

for price_elasticity in ['low','medium','high']:
    for consumers_response in ['low','medium','high']:

        row, col = int(counter/3), counter%3
        scenario_name = f"elasticity_{price_elasticity}\nwindow_{consumers_response}"
        pem_instance = GeneratePEM(
                    price_elasticity=price_elasticity,
                    consumers_response=consumers_response,
                    external_dict={},
                    export_path = os.path.join(data_path,'pem.csv')
                    )

        pem_matrix = pem_instance.get_pem_matrix()
        im = ax2[row,col].imshow(np.array(pem_matrix),cmap='jet',vmin=-0.6, vmax=0.3)
        fig2.colorbar(im, ax= ax2[row,col])
        ax2[row,col].set_xlabel('hour index')
        ax2[row,col].set_ylabel('hour index')
        ax2[row,col].set_title(scenario_name)

        opt_config_dict['export_path'] = os.path.join(export_path,f"{price_elasticity}_{consumers_response}.csv")
        instance = RunModel(**opt_config_dict)
        outputs = instance.get_output_dataframe()
        json_result = instance.get_result()
        new_load = outputs['New Load MW'].tolist()
        old_load = outputs['Original Load MW'].tolist()
        for key, value in json_result.items():
            result_dict['Scenario'].append('price_'+price_elasticity+'responsewindow_'+consumers_response)
            result_dict['Parameter'].append(key)
            result_dict['Value'].append(value)
        

        ax1[row,col].plot(range(len(new_load)),new_load,'--r',label='new')
        ax1[row,col].plot(range(len(new_load)),old_load,'--b',label='old')
        ax1[row,col].set_xlabel('Time index for a day')
        ax1[row,col].set_ylabel('Load (MW)')
        ax1[row,col].set_title(scenario_name)
        ax1[row,col].legend()


        counter +=1

df = pd.DataFrame(result_dict)
df.to_csv(os.path.join(export_path,'aggregated_result.csv'))
plt.show()

# base_price = 8
# new_bill = sum((on_peak_price*on_peak_time[j] + off_peak_price*off_peak_time[j])*new_load[j] for j in range(24))
# old_bill = sum(8*old_load[j] for j in range(24))



