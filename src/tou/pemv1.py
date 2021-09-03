"""
Generates price elasticity matrix (24x24 matrix).
Exports in the format pyomo is able to read.
Inputs:
    1. price_elasticity: self price elasticity, same value used for all hours
    2. response_window: number of hours to shift consumption because of price change
    used both in forward and backward direction
    3. non_responsive_hours: list of hours in which consumer demand does not change
    4. cross_elasticity_method: method to compute cross-elasticities
    only `gradient` and `uniform` methods are available.
    5. lossy_factor: value between 0 and 1 indicating energy consumption loss
    5. export_path: path to csv file to store pem_matrix
"""


import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from generate_profile.constants import LOG_FORMAT
import logging
import seaborn as sns
import os


class GeneratePEM:

    def __init__(self,
                price_elasticity=0.6, 
                response_window=8, 
                non_responsive_hours=[], 
                cross_elasticity_method='gradient',
                lossy_factor = 1.0,
                size=24,
                export_path = r'BRPL-NREL-II//src//tou//data//pem.csv'):

        self.logger = logging.getLogger()
        logging.getLogger('matplotlib.font_manager').disabled = True
        logging.basicConfig(format=LOG_FORMAT,level='DEBUG')

        self.price_elasiticity = price_elasticity
        self.response_window = response_window
        self.non_responsive_hours = non_responsive_hours
        self.lossy_factor = lossy_factor
        self.size = size

        self.pem_dict = {'row':[],'col':[],'pem':[]}
        self.pem_matrix = []
        
        if cross_elasticity_method == 'gradient':
            self.gradient_pem()
        
        elif cross_elasticity_method == 'uniform':
            self.uniform_pem()

        else:
            self.logger.error('Cross elasticities method available : gradient, uniform')
        
        for i, array in enumerate(self.pem_matrix):
            for j, val in enumerate(array):
                self.pem_dict['col'].append(i)
                self.pem_dict['row'].append(j)
                self.pem_dict['pem'].append(val)
        self.logger.info('Generated PEM successfully.')
        
        self.export(export_path)

    def uniform_pem(self):

        for row in range(self.size):
            array = []
            
            for col in range(self.size):

                if col%24 in self.non_responsive_hours or row%24 in self.non_responsive_hours:
                    array.append(0)

                else:
                    if row == col:
                        array.append(-self.price_elasiticity)
                    
                    else:
                        # find hours for responding
                        hours = list(range(self.size))

                        res_hours_index = list(range(row - self.response_window,row + self.response_window+1,1))
                        res_hours = [hours[id] if id < self.size else hours[id-self.size] for id in res_hours_index]
                        res_hours_ = list(set(res_hours)-set(self.non_responsive_hours)) 
                        if row in res_hours_: res_hours_.remove(row)

                        if col in res_hours_:
                            array.append(self.price_elasiticity*self.lossy_factor/len(res_hours_))
                        
                        else:
                            array.append(0)
            self.pem_matrix.append(array)

    def arange_in_order(self,row, array):

        dist_array = []
        for el in array:
            dist_array.append(min(abs(row-el),abs(24+row-el)))

        sorted_array, sorted_dist = zip(*sorted(zip(array, dist_array),key = lambda x: x[1]))
        return sorted_array

           
    def gradient_pem(self):
        

        for row in range(self.size):
            array= []
            
            for col in range(self.size):

                if col%24 in self.non_responsive_hours or row%24 in self.non_responsive_hours:
                    array.append(0)

                else:
                
                    if row == col:
                        array.append(-self.price_elasiticity)
                    
                    else:

                        # find hours for responding
                        hours = list(range(self.size))

                        pre_hours_index = list(range(row - self.response_window,row,1))
                        pre_hours = [hours[id] for id in pre_hours_index]
                        pre_hours_ = list(set(pre_hours)-set(self.non_responsive_hours))
                        # arrange in order
                        if len(pre_hours_) !=0: pre_hours_ = self.arange_in_order(row, pre_hours_)

                        post_hours_index = list(range(row+1,row + self.response_window+1,1))
                        post_hours = [hours[id] if id < self.size else hours[id-self.size] for id in post_hours_index]
                        post_hours_ = list(set(post_hours)-set(self.non_responsive_hours))
                        if len(post_hours_) !=0: post_hours_ = self.arange_in_order(row, post_hours_)


                        pre_hour_elasticity = self.price_elasiticity*self.lossy_factor*len(pre_hours_)/(len(pre_hours_)+len(post_hours_))
                        post_hour_elasticity = self.price_elasiticity*self.lossy_factor - pre_hour_elasticity

                        
                       
                        if col in pre_hours_:
                            col_index = pre_hours_.index(col)+1
                            array.append(self.linear_gradient(pre_hour_elasticity,len(pre_hours_),col_index))
                        elif col in post_hours_:
                            col_index = post_hours_.index(col)+1
                            array.append(self.linear_gradient(post_hour_elasticity,len(post_hours_),col_index))
                        else:
                            array.append(0)
                    
            self.pem_matrix.append(array)


    def export(self,export_path):
        df = pd.DataFrame(self.pem_dict)
        if os.path.exists(export_path):
            df.to_csv(export_path,index=False)
            self.logger.info('Exported PEM successfully.')

    
    def plot_pem(self):  
        self.pem_df  = pd.DataFrame({
            i: self.pem_matrix[i] for i in range(len(self.pem_matrix))
        })
        self.pem_df =self.pem_df.T
        self.pem_df.to_csv('C:\\Users\\KDUWADI\\Desktop\\\pem_mat.csv')
        sns.heatmap(self.pem_df, linewidths=.5, vmin=-0.25, vmax = 0.05)
        plt.show()

    def get_pem_matrix(self):
        return self.pem_matrix

    def linear_gradient(self,length, span, index):

        return (span+1-index)*length/sum(list(range(1,span+1)))

if __name__ == '__main__':

    instance = GeneratePEM(price_elasticity=0.4, 
                response_window=4, 
                non_responsive_hours=[2,3,4,5],
                size=24,
                cross_elasticity_method='gradient'
                )
    instance.plot_pem()

    mat = instance.get_pem_matrix()
    
    df = pd.DataFrame({i: mat[i] for i in range(24)})
    df.to_csv('matrix_pem.csv')
    print(mat)

    for arr in mat:
        print(sum(arr))
   