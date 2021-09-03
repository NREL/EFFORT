
'''
Use this module to generate net-load after subtracting 
RPO obligation. Inputs used are solar and non-solar obligation as a percentage
of energy that needs to be purchased. India RPO 2018-2019 from
'https://rpo.gov.in/'
for non-solar wind is being used.
'''

import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime as dt
from datetime import timedelta
import calendar
import numpy as np
import matplotlib.dates as mdates
from calendar import monthrange

solar_target = 6.75
non_solar_target = 10.25
solar_energy = 752000
wind_energy = 1142000

export_path = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\brpl_data'


base_load_path = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\brpl_data\brpl_transformerdata.csv'

output_resolution_min = 60
time_data = pd.read_csv(base_load_path,parse_dates=['TimeStamps'])['TimeStamps'].to_list()[::2] 
base_load_data = pd.read_csv(base_load_path)['PeakLoad'].to_list()[::2]

folder_path = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\nrel_data\wind_and_solar_data_from_marty'
solar_profiles = [
    (os.path.join(folder_path,'Badla_PV_2014_8760.csv'),50000),
    (os.path.join(folder_path,'Jodhpur_PV_2014_8760.csv'),100000),
    (os.path.join(folder_path,'Nokh_PV_2014_8760.csv'),50000),
    (os.path.join(folder_path,'Pokharan_PV_2014_8760.csv'),100000)
]

wind_profiles = [
    (os.path.join(folder_path,'Coimbatore_Wind_2014_8760.csv'),100000),
    (os.path.join(folder_path,'Lakhpat_Wind_2014_8760.csv'),100000),
    (os.path.join(folder_path,'Kutch_Wind_2014_8760.csv'),50000)
]

# find average solar profile
solar_average_profile = []
for solar_profile in solar_profiles:
    solar_profile_data = pd.read_csv(solar_profile[0])
    solar_profile_data.columns = list(range(len(solar_profile_data.columns)))
    solar_data = solar_profile_data[1].tolist()
    resolution = int(len(solar_data)/8760)
    if resolution <1: 
        raise Exception('resolution not matching !!!')
    solar_data = solar_data[::resolution]
    solar_data_pu = [el/solar_profile[1] for el in solar_data]
    if solar_average_profile == []:
        solar_average_profile = solar_data_pu
    else:
        solar_average_profile = (sum(x) for x in zip(solar_average_profile,solar_data_pu))

solar_average_profile = [x/len(solar_profiles) for x in solar_average_profile]
solar_avergae_profile = solar_average_profile[2160:] + solar_average_profile[:2160]

# find average wind profile

wind_average_profile = []
for wind_profile in wind_profiles:
    wind_profile_data = pd.read_csv(wind_profile[0])
    wind_profile_data.columns = list(range(len(wind_profile_data.columns)))
    wind_data = wind_profile_data[1].tolist()
    resolution = int(len(wind_data)/8760)
    if resolution <1: 
        raise Exception('resolution not matching !!!')
    wind_data = wind_data[::resolution]
    wind_data_pu = [el/wind_profile[1] for el in wind_data]
    if wind_average_profile == []:
        wind_average_profile = wind_data_pu
    else:
        wind_average_profile = (sum(x) for x in zip(wind_average_profile,wind_data_pu))

wind_average_profile = [x/len(wind_profiles) for x in wind_average_profile]
wind_average_profile = wind_average_profile[2160:] + wind_average_profile[:2160]


# let's generate net load profile
total_energy_consumption = sum(base_load_data)
solar_energy = solar_target*total_energy_consumption/100
wind_energy = non_solar_target*total_energy_consumption/100
print(total_energy_consumption,solar_energy,wind_energy)

solar_target_profile = [el*solar_energy/sum(solar_average_profile) for el in solar_average_profile]
wind_target_profile = [el*wind_energy/sum(solar_average_profile) for el in wind_average_profile]
net_load_profile = [x[2]-x[0]-x[1] for x in zip(solar_target_profile,wind_target_profile,base_load_data)]

df = pd.DataFrame(
    {
        'Original Load (MW)': base_load_data,
        'Solar target (MW)': solar_target_profile,
        'Wind target (MW)': wind_target_profile,
        'Net load (MW)': net_load_profile,
        'Solar profile (pu)': solar_average_profile,
        'Wind profile (pu)': wind_average_profile
    }
)

df.to_csv(os.path.join(export_path,'brpl_load_profile_wind_solar_adjusted.csv'))


fig, ax = plt.subplots()
ax.plot(time_data,solar_average_profile,label='solar')
ax.plot(time_data,wind_average_profile,label='wind')
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_ylabel('output (pu)')
ax.legend()
plt.show()

def plot_monthly_average(**kwargs):
       
       
       if 'multiplier' not in kwargs: kwargs['multiplier'] = 1
       if 'start_date' not in kwargs: kwargs['start_date'] = dt(2018,4,1,0,0,0)
       if 'resolution_in_min' not in kwargs: kwargs['resolution_in_min'] = 30
       if 'data1' not in kwargs: kwargs['data1'] = [random.random() for _ in range(365*48)]
       if 'data2' not in kwargs: kwargs['data2'] = [random.random() for _ in range(365*48)]
       if 'ylabel' not in kwargs: kwargs['ylabel'] = 'Average GW'
       if 'grid' not in kwargs: kwargs['grid'] = False
       if 'xticks_num' not in kwargs: kwargs['xticks_num'] = 6
       if 'xticks_format' not in kwargs: kwargs['xticks_format'] = '%H:%M'

       year_long_data_1 = kwargs['data1']
       year_long_data_2 = kwargs['data2']
       datelist = [kwargs['start_date'] + timedelta(minutes=kwargs['resolution_in_min'])*i for i in range(len(kwargs['data1']))]

       fig,ax = plt.subplots() if not kwargs['grid'] else plt.subplots(3,4)
       for month in range(1,13,1):
              row = int((month-1)/4)
              col = int((month-1)%4)
              
              month_data_1 = [float(d)*kwargs['multiplier'] for date,d in zip(datelist,year_long_data_1) if date.month==month]
              month_data_2 = [float(d)*kwargs['multiplier'] for date,d in zip(datelist,year_long_data_2) if date.month==month]
              dlist = [date for date in datelist if date.month==month]
              dlist = [date for date in datelist if date.month==month]
              num_of_days=calendar.monthrange(datelist[0].year,dlist[0].month)[1]

              month_data_splitted_1 = np.split(np.array(month_data_1),num_of_days)
              month_data_splitted_2 = np.split(np.array(month_data_2),num_of_days)
              dlist_splitted = np.split(np.array(dlist),num_of_days)
              average_data_1 = [sum(x)/(1000*len(x)) for x in zip(*month_data_splitted_1)]
              average_data_2 = [sum(x)/(1000*len(x)) for x in zip(*month_data_splitted_2)]
              time_range = [dt(2018,1,1,0,0,0) + timedelta(minutes=kwargs['resolution_in_min'])*i \
                     for i in range(len(dlist_splitted[0]))]
              hours = mdates.HourLocator(interval = kwargs['xticks_num'])
              h_fmt = mdates.DateFormatter(kwargs['xticks_format'])

              if kwargs['grid']:
                     ax[row,col].plot(time_range,list(average_data_1),label='base')
                     ax[row,col].plot(time_range,list(average_data_2),label='net')
                     ax[row,col].xaxis.set_major_locator(hours)
                     ax[row,col].xaxis.set_major_formatter(h_fmt)
                     ax[row,col].set_ylabel(kwargs['ylabel'])
                     ax[row,col].legend()
                     ax[row,col].set_title(dlist[0].strftime('%b')+'-'+ str(dlist[0].year))
              else:
                     ax.plot(time_range,list(average_data_1),label=dlist[0].strftime('%b'))
                     ax.xaxis.set_major_locator(hours)
                     ax.xaxis.set_major_formatter(h_fmt)
                     ax.set_ylabel(kwargs['ylabel'])
                     ax.legend()
       if not kwargs['grid']: plt.legend()
       plt.show()

plot_monthly_average(data2=net_load_profile,data1=base_load_data,resolution_in_min=60,xticks_num=8,grid=True,xticks_format='%H')
#plot_monthly_average(data=base_load_data,resolution_in_min=60,xticks_num=8,grid=True,xticks_format='%H')


plt.plot(time_data,solar_target_profile,label='solar')
plt.plot(time_data,wind_target_profile,label='wind')
plt.plot(time_data,base_load_data,label='base')
plt.plot(time_data,net_load_profile,label='net')
plt.ylabel('load (MW)')
plt.legend()
plt.show()



# fig,ax = plt.subplots(3,4)

# for id, month in enumerate([4,5,6,7,8,9,10,11,12,1,2,3]):
#        row = int((id)/4)
#        col = int((id)%4)
#        year = 2018 if month >= 4 else 2019
#        datelist = [dt(year,month,1,0,0,0) +  timedelta(minutes=60)*i \
#               for i in range(monthrange(year,month)[1]*24)]
       
#        month_data = [x[1] for x in zip(time_data,base_load_data) if x[0] in datelist]
       
#        sorted_month_data, sorted_date_list = zip(*sorted(zip(month_data,datelist),key=lambda x: x[0],reverse=True))

#        load_hour = {i: 0 for i in range(24) }
#        num_of_hours= int(0.01*len(sorted_month_data))
#     #    for id, value in enumerate(sorted_month_data[-num_of_hours:]):
#     #           load_hour[sorted_date_list[-id].hour] += 1
#        for id, value in enumerate(sorted_month_data[:num_of_hours]):
#                 load_hour[sorted_date_list[id].hour] += 1


#        for keys, values in load_hour.items():
#               load_hour[keys] = values*100/num_of_hours
#        ax[row,col].bar(range(24),list(load_hour.values()))
#        ax[row,col].set_ylabel('% top-hours')
#        ax[row,col].set_title(datelist[0].strftime('%b'))
# plt.show()