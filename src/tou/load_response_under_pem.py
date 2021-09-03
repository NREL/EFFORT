

# Third_party imports
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from collections import deque
import matplotlib
import numpy as np
import pandas as pd


# Internal imports
from tou.pemv1 import GeneratePEM


class LoadResponse:

    def __init__(self, 
        elasticity: list,
        windows: list,
        load_profile: list,
        method = 'gradient',
        on_peak_price =   3000,
        off_peak_price = 2000,
        base_price = 2500,
        non_responsive_hours = [2,3,4,5],
        on_peak_hours = [0,1,15,16,17,22,23]#[0,1,2,3,23,14,15,16,17,18,21,22,23]
        ):

        self.load_profile = load_profile
        self.elasticity = elasticity
        self.windows = windows
        self.on_peak_price = on_peak_price
        self.off_peak_price = off_peak_price
        self.base_price = base_price
        self.on_peak_hours = on_peak_hours
        self.method = method
        self.new_load = []
        #print(len(load_profile),sum(load_profile))
        
        for elas, window, meth in zip(elasticity, windows, method):
            """ Generate pem matrix """
            pem = GeneratePEM(price_elasticity= elas, 
                        response_window= window, 
                        non_responsive_hours=non_responsive_hours, 
                        size = 24,
                        cross_elasticity_method=meth,
                    )
            self.pem_matrix = pem.get_pem_matrix()
            #print(self.pem_matrix)
            self.new_load.append(self.simulate())

    
    def simulate(self):

        self.generate_window_dict(len(self.load_profile))
        
        new_load = []
        for id, val in enumerate(self.load_profile):

            base_load = val

            #for  t in range(len(self.load_profile)): 
            for t in range(id-self.window_dict[id]['window_pre'],id+self.window_dict[id]['window_post'],1):
            
                if (t%24) in self.on_peak_hours:

                    val = val + self.pem_matrix[id%24][t%24]*(self.on_peak_price-self.base_price)*base_load/self.base_price 

                else:

                    val = val + self.pem_matrix[id%24][t%24]*(self.off_peak_price-self.base_price)*base_load/self.base_price 
            new_load.append(val)

        #print(sum(new_load))

        self.new_peak = max(new_load)

        return new_load

    def generate_window_dict(self,size):

        self.window_dict = {}
        for i in range(size):
            self.window_dict[i] = {}
            if i<12:
                self.window_dict[i]['window_pre'] = i
                self.window_dict[i]['window_post'] = 23-i
            
            elif i>=(size-12):
                self.window_dict[i]['window_pre'] = 23-size+i+1
                self.window_dict[i]['window_post'] = size-i-1
            else:
                self.window_dict[i]['window_pre'] = 11
                self.window_dict[i]['window_post'] =12
              
            

    def plot_response(self):

        fig, ax = plt.subplots()

        ax.plot(range(len(self.load_profile)), self.load_profile, label='original_profile')
        for id, arr in enumerate(self.new_load):
            label_name = f'elas: {self.elasticity[id]}, window: {self.windows[id]}, method: {self.method[id]}'
            elas_dict = {0.2: 'low', 0.4: 'medium', 0.6: 'high'}
            window_dict = {2: 'short', 4: 'medium', 8: 'long'}
            #label_name = f'level of response: {elas_dict[self.elasticity[id]]} ({self.elasticity[id]})'
            label_name = f'Response window: {window_dict[self.windows[id]]} ({self.windows[id]})'
            ax.plot(range(len(arr)), arr, '--o',label= label_name)

        ax.legend()
        ax.set_ylabel('Load (MW)')

        # ax1 = ax.twinx()
        # prices = [self.on_peak_price if el%24 in self.on_peak_hours else self.off_peak_price for el in range(len(self.load_profile))]
        # ax1.plot(range(len(self.load_profile)), prices, '--b')
        on_time_list = self.on_peak_hours
        on_time_list_deque = deque(on_time_list)
        on_time_list_deque.rotate(1)
        diff_vector = [x-y for x, y in zip(on_time_list_deque, on_time_list)]
        split_indexes = [id for id, el in enumerate(diff_vector) if el !=-1]
        split_array = [list(el) for el in np.array_split(on_time_list, split_indexes)]
        

        plt.xticks([0,5,10,15,20], ['12 AM', '5 AM', '10 AM', '3 PM', '8 PM'])
        plt.grid(color='k', linestyle='--', linewidth=0.2, alpha=0.5)

        xmin, xmax, ymin, ymax = plt.axis()

        for arr in split_array:
            if arr !=[]:
                pa = matplotlib.patches.Rectangle((min(arr), ymin), max(arr)- min(arr),ymax)
                ax.add_collection(PatchCollection([pa], facecolor= 'k', alpha= 0.2))
        
        plt.title('Load responses under TOU')
        # ax1.tick_params(axis='y', colors='b')
        # ax1.yaxis.label.set_color('b')
        # ax1.set_ylabel('Price (Rs/MWh)')
        plt.show()

if __name__ == '__main__':
    
    
    # [2825,2723, 2619,2542,2424,2330,2171,2049,2011,2086,2271,2402,2496,2572,2631,2824,2910,2747,2535,2323,2395,2663,2874,2972]
    load_profile = pd.read_csv(r'C:\Users\KDUWADI\Desktop\BRPL\data_summer\load.csv')['Load'].tolist()
    res_ins = LoadResponse(
        elasticity = [0.2,0.2],
        windows= [2, 4],
        method = ['uniform', 'uniform'],
        non_responsive_hours = [],
        load_profile = [2825,2723, 2619,2542,2424,2330,2171,2049,2011,2086,2271,2402,2496,2572,2631,2824,2910,2747,2535,2323,2395,2663,2874,2972]
    )
    res_ins.plot_response()

    #on_peak_hours = (23, 16, 22, 0, 15, 17, 1, 21, 14, 2, 13, 3, 18, 12, 4, 11, 20, 5, 19, 10, 6, 9, 7, 8)
    hours_ = [id%24 for id,el in enumerate(load_profile)]
    sorted_hours, sorted_load = zip(*sorted(zip(hours_,load_profile), key=lambda x:x[1], reverse=True))
    on_peak_hours = []
    a = [on_peak_hours.append(x) for x in sorted_hours if x not in on_peak_hours]
    print(on_peak_hours)
    
    peak_reduction = {}
    for el, p1, p2 in zip([4, 4], [3000, 3500], [2000, 1500]):
        peak_reduction[round(p1/p2,2)] = []
        for i in range(20):

            res_ins = LoadResponse(
            elasticity = [0.1],
            windows= [el],
            method = ['uniform'],
            on_peak_price= p1,
            off_peak_price= p2,
            non_responsive_hours = [],
            on_peak_hours= on_peak_hours[:i+1],
            load_profile = load_profile
            )

            peak_reduction[round(p1/p2,2)].append(res_ins.new_peak)

    for keys, items in peak_reduction.items():
        #plt.plot(range(1, len(items)+1), items,'--o', label = f'windows= {keys}')
        plt.plot(range(1, len(items)+1), items,'--o', label=f'on peak off peak ratio = {keys}')

    plt.xticks([2,4,6,8,10,12,14,16,18], [2,4,6,8,10,12,14,16,18])
    plt.legend()
    plt.xlabel('Number of on peak hours')
    plt.ylabel('New Peak (MW)')
    plt.show()

    
