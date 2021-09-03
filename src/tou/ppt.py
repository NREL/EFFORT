import plotly.graph_objects as go
import numpy as np
import pandas as pd
import squarify
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib
from scipy.stats import pearsonr 
import numpy as np
from sklearn.linear_model import LinearRegression 
import seaborn as sns
import datetime 
from collections import Counter


"""Daily energy consumption pattern (for both summer and winter)"""

summer_consumption = [2825,2723,2619,2542,2424,2330,2171,2049,2011,2086,2271,2402,2496,2572,2631,2824,2910,2747,2535,2323,2395,2663,2874,2972]
winter_consumption = [864,712,646,619,623,673,858,1197,1550,1728,1813,1823,1727,1616,1387,1341,1296,1302,1418,1470,1423,1361,1249,1088]
plt.plot(range(len(summer_consumption)), summer_consumption, '--or', label='summer day (July 9)' )
plt.plot(range(len(winter_consumption)), winter_consumption, '--ob', label='winter day (Jan 4)' )
plt.ylabel('Load (MW)')
plt.legend()
plt.xticks([0,5,10,15,20], ['12 AM', '5 AM', '10 AM', '3 PM', '8 PM'])
plt.grid(color='k', linestyle='--', linewidth=0.2, alpha=0.5)
plt.show()

""" Load duration curve """

load_data = pd.read_csv(r'C:\Users\KDUWADI\Desktop\BRPL\data_year\load.csv')['Load'].tolist()
load_data.sort(reverse=True)
x_points = [el*100/len(load_data) for el in range(len(load_data))]
fig, ax= plt.subplots()
plt.plot(x_points, load_data)
plt.ylabel('Load (MW)')
plt.xlabel('Percentage of time of year')
plt.title('Load duration curve')
plt.grid(color='k', linestyle='--', linewidth=0.2, alpha=0.5)
xmin, xmax, ymin, ymax = plt.axis()

knee_points = [10,20,50]
face_alpha = [0.7, 0.4, 0.2]
colors = ['red', 'green', 'blue']


plt.plot([0,100], [max(load_data), max(load_data)], ls='--', color='k')

counter = 0
previous_y = load_data[0]
for point, al, cl in zip(knee_points, face_alpha, colors):
    sliced_load = [el for el in load_data if el> (100-point)*load_data[0]/100]
    pa = matplotlib.patches.Rectangle((0,0), len(sliced_load)*100/len(load_data),ymax, facecolor= 'red', alpha=al)
    ax.add_collection(PatchCollection([pa], facecolor= cl, alpha=al))
    plt.plot([len(sliced_load)*100/len(load_data),60+counter*10], [min(sliced_load), min(sliced_load)], ls='--', color=cl)
    middle_x, middle_y = len(sliced_load)*100/len(load_data)+ (100-len(sliced_load)*100/len(load_data))/4, min(sliced_load) + (previous_y - min(sliced_load))/6
    previous_y = min(sliced_load)
    if point>40:
        plt.annotate(f'{point}% ({round(point*(max(load_data))/100,2)}) of peak \n loads occurs {round(len(sliced_load)*100/len(load_data),2)}% of time', (middle_x,middle_y))
    else:
        plt.annotate(f'{point}% ({round(point*(max(load_data))/100,2)}) of peak loads occurs {round(len(sliced_load)*100/len(load_data),2)}% of time', (middle_x,middle_y))
    counter +=1


plt.show()

""" prices vs load curve """
summer_price = [3190.04, 2942.99, 2654.43, 2405.4, 2511.24, 2367.87, 2529.71, 2479.48, 2257.08, 2176.97, 2219.74, 2219.56, 2179.28, 2029.94, 2544.92, 2649.65, 3353.61, 4237.84, 4987.86, 5240.4, 4244.68, 3212.45 ]
winter_price = [2164.69, 1972.07, 1830.82, 1896.57, 1947.75, 2519.78,3659.97,4905.62,5405.24,5982.49,5688.27,5083.6,4546.46,3480.5,3400.49,3868.52,4213.52,4720.58,5274.8,5310.2,4214.06,3370.07,2489.3,2246.7]
summer_consumption_norm = [el/max(summer_consumption) for el in summer_consumption]
winter_consumption_norm = [el/max(summer_consumption) for el in winter_consumption]
fig, ax = plt.subplots()
ax.plot(range(len(summer_consumption)), summer_consumption_norm, 'k')
ax.set_ylabel('Normalized load')
ax1 = ax.twinx()
ax1.plot(range(len(summer_price)), summer_price, '--b')
ax1.set_ylabel('Price (Rs/MWh)')
ax1.tick_params(axis='y', colors='b')
ax1.yaxis.label.set_color('b')
plt.xticks([0,5,10,15,20], ['12 AM', '5 AM', '10 AM', '3 PM', '8 PM'])
plt.grid(color='k', linestyle='--', linewidth=0.2, alpha=0.5)
plt.title('Summer load vs price (July 9)')
plt.show()

fig, ax = plt.subplots()
ax.plot(range(len(winter_consumption)), winter_consumption_norm, 'k')
ax.set_ylabel('Normalized load')
ax1 = ax.twinx()
ax1.plot(range(len(winter_price)), winter_price, '--b')
ax1.set_ylabel('Price (Rs/MWh)')
ax1.tick_params(axis='y', colors='b')
ax1.yaxis.label.set_color('b')
plt.xticks([0,5,10,15,20], ['12 AM', '5 AM', '10 AM', '3 PM', '8 PM'])
plt.grid(color='k', linestyle='--', linewidth=0.2, alpha=0.5)
plt.title('Winter load vs price (Jan 4)')
plt.show()

""" Average price over block of loads """

load_data = pd.read_csv(r'C:\Users\KDUWADI\Desktop\BRPL\data_year\load.csv')['Load'].tolist()
price_data = pd.read_csv(r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\nrel_data\price data\wholesale_price.csv')['Price (Rs/MWh)'].tolist()

load_data_sorted, price_data_sorted = zip(*sorted(zip(load_data, price_data), key = lambda x: x[0]))
avg_price, price_std, blocked_load = [], [], []
for i in range(600,3100,100):
    load_id_sliced = [(id,el) for id, el in enumerate(load_data) if el > i-100 and el <=i]
    id_sliced, load_sliced = [x[0] for x in load_id_sliced], [x[1] for x in load_id_sliced]
    price_sliced = [price_data[id] for id in id_sliced]
    avg_price.append(np.mean(price_sliced))
    price_std.append(np.std(price_sliced))
    blocked_load.append(i)

fig, ax = plt.subplots()
ax.plot(blocked_load, avg_price, 'k')
ax.set_xlabel('Load (MW)')
ax.set_ylabel('Average price (Rs/MWh)')
ax1 =ax.twinx()
ax1.plot(blocked_load, price_std, 'b')
ax1.set_ylabel('Standard deviation')
ax1.tick_params(axis='y', colors='b')
ax1.yaxis.label.set_color('b')
plt.show()

""" Perform linear regression to find Rs/MW"""
x_ = np.array(blocked_load).reshape((-1, 1))
y_ = np.array(avg_price)
model = LinearRegression()
model.fit(x_, y_)
print('r_squared_error:',  model.score(x_, y_))
print('intercept:', model.intercept_)
print('slope:', model.coef_)




""" Donut plot for customers """

num_of_cust = [86.48, 13.3, 0.22]
energy_con = [67, 31, 3]
labels = ['domestic', 'commercial', 'industrial']

def func(pct, allvals):
    return f"{round(pct,1)}%"

fig, ax = plt.subplots(1,2)
wedges, texts, autotexts = ax[0].pie(num_of_cust, 
        autopct = lambda pct: func(pct, num_of_cust), 
                        textprops=dict(color="w", fontsize=18))

ax[0].legend(wedges, labels,
          title="group",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))

wedges, texts, autotexts = ax[1].pie(energy_con, 
        autopct = lambda pct: func(pct, energy_con), 
                        textprops=dict(color="w",fontsize=18))

plt.show()

""" Finding average contribution"""
data_source  = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\brpl_data\Energy Consumption Details_22.05.2020.xlsx'
df = pd.read_excel(data_source)
column_names = list(df.columns)
grouped_df = df.groupby(['Day'])
season_df = grouped_df.get_group(279)
peak_contri = []
for i in range(20,24,1):
    max_load = max(df[column_names[i]].tolist())
    profile = [el/max_load for el in season_df[column_names[i]].tolist()[::2]]
    peak_contri.append(profile[11])

print(peak_contri)
print(sum(peak_contri)/len(peak_contri))
    


""" plotting loads of different groups """
data_source  = r'C:\Users\KDUWADI\Box\BRPL Demand Side Management\Data\brpl_data\Energy Consumption Details_22.05.2020.xlsx'
df = pd.read_excel(data_source)
domestic_peak = 58.2#99.4 #max(df['DT-1: Appartment\n (in KWH)'].tolist())
commercial_peak = 92.64 #max(df['DT-9: Market Complex\n (in KWH)'].tolist())
industrial_peak = 215.04 #max(df['DT-17: Industrial Consumer-1\n(in KWH)'].tolist())
grouped_df = df.groupby(['Day'])
season_df = grouped_df.get_group(279) # 279 # 100
fig, ax = plt.subplots()
domestic_profile = [el/domestic_peak for el in season_df['DT-1: Appartment\n (in KWH)'].tolist()[::2]]
commercial_profile = [el/commercial_peak for el in season_df['DT-9: Market Complex\n (in KWH)'].tolist()[::2]]
industrial_profile = [el/industrial_peak for el in season_df['DT-17: Industrial Consumer-1\n(in KWH)'].tolist()[::2]]
ax.plot( range(len(domestic_profile)), domestic_profile, 'r', label='domestic')
ax.plot( range(len(commercial_profile)), commercial_profile , 'g',  label='commercial')
ax.plot( range(len(industrial_profile)), industrial_profile , 'b', label='industrial')
plt.legend()
xmin, xmax, ymin, ymax = plt.axis()
pa = matplotlib.patches.Rectangle((11,ymin), 1 , ymax)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('peak time', (11, 0.3), rotation='vertical')

plt.ylabel('Normalized load')
plt.xticks([0,5,10,15,20], ['12 AM', '5 AM', '10 AM', '3 PM', '8 PM'])
plt.grid(color='k', linestyle='--', linewidth=0.2, alpha=0.5)
plt.title('Winter (Jan 4)')
plt.show()

daily_peak_hour = {}
year_long_data = pd.read_csv(r'C:\Users\KDUWADI\Desktop\BRPL\data_year\load.csv')
hr_res_dates = [datetime.datetime(2018,4,1,0,0,0)+datetime.timedelta(minutes=60*i) for i in range(8760)]
year_long_data.index = hr_res_dates


for date in year_long_data.index:
    if date.timetuple().tm_yday not in daily_peak_hour:
        daily_peak_hour[date.timetuple().tm_yday] = []
    daily_peak_hour[date.timetuple().tm_yday].append(year_long_data['Load'][date])

for key, values in daily_peak_hour.items():
    daily_peak_hour[key] = values.index(max(values))

#print(set(daily_peak_hour.values()))

sorted_date, sorted_load = zip(*sorted(zip(hr_res_dates, year_long_data['Load'].tolist()), key=lambda x: x[1], reverse=True))
sorted_date_5_percen = sorted_date[:438]
print('load', sorted_load[:10])

# Get average load
hr_load_profiles = {}
day_load = {}
for date, load in zip(hr_res_dates, year_long_data['Load'].tolist()):
    if date.hour not in hr_load_profiles:
        hr_load_profiles[date.hour] = []
    
    if date.timetuple().tm_yday not in day_load:
        day_load[date.timetuple().tm_yday] = []
    
    hr_load_profiles[date.hour].append(load)
    day_load[date.timetuple().tm_yday].append((date.hour, load))

mean_hr_profiles = []
for i in range(24):
    mean_hr_profiles.append(np.nanmean(hr_load_profiles[i]))

daily_peak_hours = []
for d, arr in day_load.items():
    hours_ = [el[0] for el in arr]
    loads_ = [el[1] for el in arr]
    sorted_loads_, sorted_hours_ = zip(*sorted(zip(loads_, hours_), key= lambda x: x[0], reverse=True))
    daily_peak_hours.append(sorted_hours_[0])

print(dict(Counter(daily_peak_hours)))

sorted_date_tuple = [(date.timetuple().tm_yday, date.hour) for date in sorted_date_5_percen]
sorted_data_tuple_mod = []
for el in sorted_date_tuple:
    if el[0]>=91:
        sorted_data_tuple_mod.append((el[0]-91, el[1]))
    else:
        sorted_data_tuple_mod.append((el[0]+274, el[1])) 
sorted_date_tuple = sorted_data_tuple_mod


#print(set([date.hour for date in sorted_date_5_percen if ]))
#print(sorted_date_tuple)
#print(sorted_date_5_percen)

# h = [date.hour for date in sorted_date_5_percen]
# from collections import Counter
# print(h)
# print(dict(Counter(h)))
# print(a)


summer_dict = {'Hours': [], 'Load (pu)': [], 'Cust type': []}
winter_dict = {'Hours': [], 'Load (pu)': [], 'Cust type': []}
ds_, cs_, is_, dw_, cw_, iw_ = [], [], [], [], [], []
s,w = set(), set()
d_e_s, c_e_s, i_e_s = [], [], []
d_e_w, c_e_w, i_e_w = [], [], []

for i in range(1,366,1):
    #print(i)
    day_df = grouped_df.get_group(i)
    domestic_profile = [el/domestic_peak for el in day_df['DT-2: Appartment\n (in KWH)'].tolist()[1::2]]
    commercial_profile = [el/commercial_peak for el in day_df['DT-9: Market Complex\n (in KWH)'].tolist()[1::2]]
    industrial_profile = [el/industrial_peak for el in day_df['DT-17: Industrial Consumer-1\n(in KWH)'].tolist()[1::2]]

    if i <= 214:
        for hour, value in enumerate(domestic_profile):
            summer_dict['Hours'].append(hour)
            summer_dict['Load (pu)'].append(value)
            summer_dict['Cust type'].append('domestic')
            if hour in [0, 9, 10, 11, 14, 16, 20, 23]:
                ds_.append(value)
                s.add(hour)
            if (i,hour) in sorted_date_tuple:
                d_e_s.append(value)
        for hour, value in enumerate(commercial_profile):
            summer_dict['Hours'].append(hour)
            summer_dict['Load (pu)'].append(value)
            summer_dict['Cust type'].append('commercial')
            if hour in [0, 9, 10, 11, 14, 16, 20, 23]:
                cs_.append(value)
                s.add(hour)
            if (i,hour) in sorted_date_tuple:
                c_e_s.append(value)
        for hour, value in enumerate(industrial_profile):
            summer_dict['Hours'].append(hour)
            summer_dict['Load (pu)'].append(value)
            summer_dict['Cust type'].append('industrial')
            if hour in [0, 9, 10, 11, 14, 16, 20, 23]:
                is_.append(value)
                s.add(hour)
            if (i,hour) in sorted_date_tuple:
                i_e_s.append(value)
        

    else:
        for hour, value in enumerate(domestic_profile):
            winter_dict['Hours'].append(hour)
            winter_dict['Load (pu)'].append(value)
            winter_dict['Cust type'].append('domestic')
            if hour in [0, 10, 11, 12, 15, 16, 19, 20, 23]:
                dw_.append(value)
                w.add(hour)
            if (i,hour) in sorted_date_tuple:
                d_e_w.append(value)
        for hour, value in enumerate(commercial_profile):
            winter_dict['Hours'].append(hour)
            winter_dict['Load (pu)'].append(value)
            winter_dict['Cust type'].append('commercial')
            if hour in [0, 10, 11, 12, 15, 16, 19, 20, 23]:
                cw_.append(value)
                w.add(hour)
            if (i,hour) in sorted_date_tuple:
                c_e_w.append(value)
        for hour, value in enumerate(industrial_profile):
            winter_dict['Hours'].append(hour)
            winter_dict['Load (pu)'].append(value)
            winter_dict['Cust type'].append('industrial')
            if hour in [[0, 10, 11, 12, 15, 16, 19, 20, 23]]:
                iw_.append(value)
                w.add(hour)
            if (i,hour) in sorted_date_tuple:
                i_e_w.append(value)

print('kapil', np.nanmean(d_e_s), np.nanmean(c_e_s), np.nanmean(i_e_s), np.nanmean(d_e_w), np.nanmean(c_e_w), np.nanmean(i_e_w))
#print('kapil', d_e_s, c_e_s, i_e_s, d_e_w, c_e_w, i_e_w)

#print(s, w)
print(summer_dict['Hours'])
summer_df = pd.DataFrame(summer_dict)
winter_df = pd.DataFrame(winter_dict)

print( 'hi', np.nanmean(ds_), np.nanmean(cs_), np.nanmean(is_), np.nanmean(dw_), np.nanmean(cw_), np.nanmean(iw_))
#print('kapil', d_e_s, c_e_s, i_e_s, d_e_w, c_e_w, i_e_w)

ax = sns.boxplot(x='Hours', y='Load (pu)', hue="Cust type", data=summer_df)
ax1 = ax.twinx()
ax1.plot(range(24), summer_consumption, '--r', label='summer peak day consumption')
ax1.plot(range(24), mean_hr_profiles, '--b', label='average consumption')
plt.legend()
ax1.set_ylabel('summer peak day \n consumption (MW)')

plt.show()

ax = sns.boxplot(x='Hours', y='Load (pu)', hue="Cust type", data=winter_df)
ax1 = ax.twinx()
ax1.plot(range(24), winter_consumption, '--r', label='winter peak day consumption')
ax1.set_ylabel('winter peak day \n consumption (MW)')
ax1.plot(range(24), mean_hr_profiles, '--b', label='average consumption')
plt.legend(loc=1)
plt.show()


""" plotting appliance ownership """

lightings = ['Incandescent bulbs', 'CFL bulbs', 'LED bulbs', 'Tubelights']
plug_loads = ['Toaster','Coffe makers', 'Routers' , 'TVs', 'Hair dryers', 'Clothing irons']
wet_appliances = ['Washing machine', 'Dishwashers', 'Washer dryers']
space_heating_cooling = ['Coolers', 'Air Heater', 'AC unit', 'Fans']
refrigeration = ['Refrigerator(<300L)', 'Refrigerator(>300L)']
water_heating = ['Geyser (electric)']
pv_and_battery = ['Batteries']

labels = lightings + plug_loads + wet_appliances + space_heating_cooling + refrigeration + water_heating + pv_and_battery
num_of_customers =  [83, 243, 367, 337 ] + [214, 31, 306, 387, 171, 332] + \
                [370,14,28] + [189,203,359,413] + [173, 265 ] + [341] + [154]

fig, ax = plt.subplots()
plt.bar(labels, [el*100/414 for el in num_of_customers])
plt.ylabel('Percentage customers')
plt.grid(color='k', linestyle='--', linewidth=0.2, alpha=0.5)
plt.xticks(rotation=90)

pa = matplotlib.patches.Rectangle((-0.4,0), 3.8, 100)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('lighting', (0, 60), rotation='vertical')

pa = matplotlib.patches.Rectangle((3.6,0), 5.8, 100)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('plug loads', (4, 60), rotation='vertical')

pa = matplotlib.patches.Rectangle((9.6,0), 2.8, 100)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('wet appliances', (10, 60), rotation='vertical')

pa = matplotlib.patches.Rectangle((12.6,0), 3.8, 100)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('space heating \n and cooling', (13, 60), rotation='vertical')

pa = matplotlib.patches.Rectangle((16.6,0), 1.8, 100)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('refrigeration', (17, 60), rotation='vertical')

pa = matplotlib.patches.Rectangle((18.6,0), 0.8, 100)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('water heating', (19, 60), rotation='vertical')

pa = matplotlib.patches.Rectangle((19.6,0), 0.8, 100)
ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.4))
plt.annotate('pv and battery', (20, 60), rotation='vertical')

plt.show()


""