'''
Script to run appliance optimization model and gather results
'''

# Stnadard library imports
import os
import logging
import json

# Third-party imports
import pandas as pd
from pyomo.environ import *

# Internal imports
from appliance_opt_model import model
import matplotlib.pyplot as plt

LOG_FORMAT =  '%(asctime)s: %(levelname)s: %(message)s'


class RunAppModel:

    def __init__(self,**kwargs):

        # setup logger
        self.logger = logging.getLogger()
        logging.basicConfig(format=LOG_FORMAT, level='DEBUG')
        logging.getLogger('matplotlib.font_manager').disabled = True

        self.config = kwargs
        self.prepare_input()

        instance, results = self.run(self.datfilepath, self.solver, model)


        self.appliance_with_constant_mc = ['lighting', 'water_pump','washing_machine', 'dishwashers', 'washer_dryer', \
                    'hair_dryer', 'toaster', 'coffe_maker', 'laptops', 'televisions', 'routers','clothing_iron', 'refrigerator_l300', 'refrigerator_g300']
        
        # self.appliance_with_variable_mc = ['fans', 'coolers', 'air_heater', 'ac_unit', 'incandescent_bulb', \
        #     'cfl_bulb', 'led_bulb', 'tubelights', \
        #        'water_pump', 'geyser_electric' ]

        self.appliance_with_variable_mc = ['fans', 'coolers', 'air_heater', 'ac_unit', 'geyser_electric']
        self.appliance_energy_constant_mc = []

        for a in instance.appliance:
            self.appliance_energy_constant_mc.append(instance.appliance_energy[a].value)

        self.appliance_energy_constant_mc_dict = dict(zip(self.appliance_with_constant_mc, self.appliance_energy_constant_mc))

        self.appliance_energy_variable_mc_df = pd.DataFrame(data=[], columns=self.appliance_with_variable_mc)
        for m in instance.month:
            output_temp = pd.DataFrame(
                [list(instance.appliance_timeseries_energy[a,m].value for a in instance.appliance_timeseries)], 
                columns = self.appliance_with_variable_mc
            )
            self.appliance_energy_variable_mc_df = self.appliance_energy_variable_mc_df.append(output_temp)

        self.appliance_energy_variable_mc_df.index = ['Jan', 'Feb','Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        self.obj_value = instance.obj.value()


        if 'export_path' in self.config:
            with open(os.path.join(self.config['export_path'],'appliance_energy_constant_mc.json'), 'w') as outfile:
                outfile.write(json.dumps(self.appliance_energy_constant_mc_dict, indent=4))
            
            self.appliance_energy_variable_mc_df.to_csv(os.path.join(self.config['export_path'],'appliance_energy_cvariable_mc.csv'))

    def plot_result(self):
        
        self.appliance_energy = [el if el != None else 0 for el in self.appliance_energy_constant_mc]
        plt.bar(self.appliance_with_constant_mc, self.appliance_energy)
        plt.xticks(rotation=90)
        plt.ylabel('Monthly Energy (kWh) per customer')
        plt.show()

        self.appliance_energy_variable_mc_df.plot()
        plt.show()

        

    def prepare_input(self):

        try:
            dat_filepath = os.path.join(self.config['data_path'], 'data.dat')
            
            with open(dat_filepath, 'r') as file:
                filedata = file.read()
            self.logger.info('data.dat file read successfully')
        except Exception as err:
            self.logger.error(f'Cannot read .dat file >> {str(err)}')


        # Create a new dat file with updated directory
        filedata = filedata.replace('DIRECTORY', self.config['data_path'])

        with open(os.path.join(self.config['data_path'],'data_mod.dat'),'w') as infile:
            infile.write(filedata)

        self.logger.info(f"new .dat file created successfully >> {os.path.join(self.config['data_path'],'data_mod.dat')}")

        self.datfilepath = os.path.join(self.config['data_path'],'data_mod.dat')

        self.solver = self.config.get('solver', 'ipopt')
        
        # check solver availability
        self.logger.info(SolverFactory(self.solver).available())

    
    def run(self, dat_file, solver, model):

        instance = model.create_instance(dat_file)
        results = SolverFactory(solver).solve(instance)
        results.write()
        instance.solutions.store_to(results)

        return (instance, results)

    def get_result_constant_mc(self):

        return self.appliance_energy_constant_mc_dict

    def get_result_variable_mc(self):

        return self.appliance_energy_variable_mc_df

    def get_objective_func(self):

        return self.obj_value


if __name__ == '__main__':

    instance1 = RunAppModel(
        data_path = r'C:\\Users\\KDUWADI\\Desktop\\BRPL\\survey_data',
        export_path = r'C:\Users\KDUWADI\Desktop\BRPL\survey_result',
        solver = 'ipopt'
    )
    instance1.plot_result()

    #print(instance1.get_objective_func())
