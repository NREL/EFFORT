'''
Use this module to find out the on-peak hours for a given load profile
'''

# Standard libraries
from datetime import datetime as dt
from datetime import timedelta
import os

# Third-party libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Onpeak:

    def __init__(self, 
            load_profile: list = [], 
            start_date: dt.date = dt(2018,3,1,0,0,0), 
            resolution_min: int = 60):

        self.load_profile = load_profile
        self.start_date = start_date
        self.resolution_min = resolution_min

        self.time_list = [self.start_date + timedelta(minutes=self.resolution_min*i) for i in range(len(self.load_profile)) ]
        self.sorted_time, self.sorted_load = zip(*sorted(zip(self.time_list,self.load_profile),key=lambda x: x[1], reverse=True))
        

    def find_on_peak_hours(self, percen_top_load_hr=0.01):

        top_load_hours = []
        for time in self.sorted_time[:int(percen_top_load_hr*len(self.load_profile))]:
            if time.hour not in top_load_hours:
                top_load_hours.append(time.hour)

        return top_load_hours

    def plot_on_peak_hours(self):

        
        percen_top_load_hrs = list(range(1,5,1))
        self.top_load_hr_dict = {
            'Hours of day': [],
            'Pecentage of top load hours': [],
            'On peak or not' : []
        }
        for percen_top_load_hr in percen_top_load_hrs:

            on_peak_hrs = self.find_on_peak_hours(percen_top_load_hr=percen_top_load_hr/100)
            print(on_peak_hrs, percen_top_load_hr)
            self.top_load_hr_dict['Hours of day'].extend(list(range(24)))
            self.top_load_hr_dict['Pecentage of top load hours'].extend([percen_top_load_hr]*24)
            on_peak_or_not = [0]*24
            for hr in on_peak_hrs:
                on_peak_or_not[hr] = 1
            self.top_load_hr_dict['On peak or not'].extend(on_peak_or_not)
        
        self.on_peak_dataframe = pd.DataFrame(self.top_load_hr_dict)

        self.on_peak_dataframe = self.on_peak_dataframe.pivot('Pecentage of top load hours','Hours of day','On peak or not')
        sns.heatmap(self.on_peak_dataframe,annot=True, fmt="d",cbar_kws={"orientation": "horizontal"}, cbar=False)
        plt.show()

        # fig, ax = plt.subplots()
        # l1 = ax.plot(range(len(self.load_profile)),self.load_profile,'--or',label='load profile')
        # ax.plot([0,24], [1277,1277],'--r')
        # ax1 = ax.twiny()
        # percen_load_hours = [el*100/len(self.load_profile) for el in range(len(self.load_profile))]
        # l2 = ax1.plot(percen_load_hours, self.sorted_load,'--g',label='load duration curve')
        # ax1.plot([20,20], [1000,1400],'--g')
        # ax1.set_xlabel('% load hours', color='green')
        # ax1.tick_params(axis='x', colors='green')
        # ax1.spines['top'].set_color('green')
        # ax.set_xlabel('hour index',color='red')
        # ax.tick_params(axis='x', colors='red')
        # ax.spines['top'].set_color('red')
        # ax.set_ylabel('load (MW)')

        # lns = l1+l2
        # labs = [l.get_label() for l in lns]
        # ax.legend(lns, labs,loc=8)
        # plt.show()


if __name__ == "__main__":
    
    data_path = r'C:\Users\KDUWADI\Desktop\BRPL\data_summer'
    load_data = pd.read_csv(os.path.join(data_path,'load.csv'))['Load'].tolist()

    instance = Onpeak(load_profile=load_data)
    instance.plot_on_peak_hours()




