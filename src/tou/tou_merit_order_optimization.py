# Standard imports
import os
import logging
import json

# Third-party imports
from pyomo.environ import SolverFactory
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Internal imports
#from tou_model import model
#from tou.non_linear_elas import model
from tou.tou_merit_order import model
from generate_profile.constants import LOG_FORMAT

'''
Obtained from DERC website (http://www.derc.gov.in/ordersPetitions/orders/Tariff/Tariff%20Order/FY%202019-20/Tariff%20Order%20FY%202019-20/Tariff%20Orders%202019-20/BRPL.pdf
, page 321, SECI solar rajasthan : Rs. 5.5/kWh, SECI wind : Rs. 2.52/kWh
avrage renewable price: (6.75*5.5+10.25*2.52)/(6.75+10.25) = Rs. 3.7/kWh)
'''
RENEWABLE_PRICE = 3700

'''
Network avoidance cost obtained from BRPL per MW is Rs 2 crore
'''
CAPACITY_UPGRADE_COST =   9627550.70 #14094540.73 #93705.09  #20000000    9627550.70
class RunModel:

  def __init__(self, **kwargs):

    # setup logger
    self.logger = logging.getLogger()
    logging.getLogger('matplotlib.font_manager').disabled = True
    logging.basicConfig(format=LOG_FORMAT,level='DEBUG')
    self.logger.info(f'optimization initiallized with dictionary {kwargs}')

    self.config = kwargs

    self.prepare_input()

    instance, results = self.run(self.modified_dat_filepath, self.solver_name, model)

    col_headers=['time','Net load MW','Original Load MW','New Load MW',
                'Original Price Rs/MWh','Fixed price Rs/Mwh','On Price Rs/MWh','Off peak Rs/MWh' ,'On Peak', 'Off Peak']

    
    self.generators = ['GT-CC','Bawana-CC','PPCL-CC','Jhajjar','Dadri-I','Dadri-Gas','Dadri-II','Auraiya-Gas','Anta-Gas',\
                  'Mezia#6','Unchahar-I','Unchahar-II','Unchahar-III','Kahalgaon-I','Farakka','kahalgaon-II', 'CTPS 7&8', 'Rihand-III',\
                  'Rihand-I','Rihand-II','Singrauli','Sasan']

    self.outputs=pd.DataFrame(data=[],columns=col_headers)
    self.gen_outputs = pd.DataFrame(data=[], columns=self.generators)

    for t in instance.time:
        outputs_temp=pd.DataFrame([list([
                t,
                instance.netLoad[t],
                instance.Load[t],
                instance.Load_Response[t].expr(),
                instance.baseprice.value + instance.fixedprice.value,
                instance.fixedprice.value,
                instance.price_on_peak.value,
                instance.price_off_peak.value,
                instance.tier_time_on_peak[t],
                instance.tier_time_off_peak[t] #instance.price_on_peak.value #instance.price_var[t].expr()
                ])], columns=col_headers)
        self.outputs=self.outputs.append(outputs_temp)
 
    
    for t in instance.time:
      output_temp = pd.DataFrame([
        list([
          instance.gen_output[t,j].value for j in instance.genindex
        ])
      ], columns=self.generators)
      self.gen_outputs = self.gen_outputs.append(output_temp)


    self.instance = instance
        
    if 'export_path' not in self.config:
      self.outputs.to_csv('output.csv')
      self.gen_outputs.to_csv('gen_output.csv')
    else:
        self.outputs.to_csv(os.path.join(self.config['export_path'],'output.csv'))
        self.gen_outputs.to_csv(os.path.join(self.config['export_path'],'gen_output.csv'))

    self.logger.info(f"Peak reduced (MW): {-max(self.outputs['New Load MW'].tolist())+max(self.outputs['Original Load MW'].tolist())}")
    self.logger.info(f"""Base price: {self.outputs['Original Price Rs/MWh'].tolist()[0]}, On peak price: {self.outputs['On Price Rs/MWh'].tolist()[0]},
    Off peak price: {self.outputs['Off peak Rs/MWh'].tolist()[0]}""")
    self.logger.info(f"Price difference (Rs.): {self.outputs['On Price Rs/MWh'].tolist()[0]-self.outputs['Off peak Rs/MWh'].tolist()[0]}")

    self.get_result()

    if 'plot_result' in self.config:
      if self.config['plot_result']:
        self.plot_loadprofile()
        self.plot_genoutput()


  def prepare_input(self):

    if 'data_path' not in self.config:
        ''' Read the data.dat file from directoy of currently running file'''
        main_dir = os.path.join(os.path.dirname(__file__)) 
        dat_filepath =   main_dir+r'/data_price.dat' #main_dir+r'/data.dat'
        main_dir = main_dir + '\data'
    else:
        main_dir = self.config['data_path']
        dat_filepath = os.path.join(self.config['data_path'],'data.dat')
        if not os.path.exists(dat_filepath):
          self.logger.error(f"{dat_filepath} does not exist!!")


    with open(dat_filepath, 'r') as file:
      filedata = file.read()

    ''' Replace DIRECTORY placeholder with current directory'''
    filedata = filedata.replace('DIRECTORY', main_dir)

    ''' Write modified dat file'''
    with open(os.path.join(main_dir,'data_mod.dat'), 'w') as file:
      file.write(filedata)
    self.logger.info(f"Modified datfile successfully written - {os.path.join(main_dir,'data_mod.dat')}")
    
    self.modified_dat_filepath = os.path.join(main_dir,'data_mod.dat')
    
    if 'solver' in self.config:
        self.solver_name = self.config['solver']
    else:
        self.solver_name = 'ipopt' #'glpk'
    self.logger.info(SolverFactory(self.solver_name).available())

    ''' Update on-peak and off peak time csv files'''
    if 'on_time_list' in self.config:
      on_peak_time = [0]*self.config['num_of_hours']
      off_peak_time = [1]*self.config['num_of_hours']

      for index in range(self.config['num_of_hours']):

        hour_index = index%24
        if hour_index in self.config['on_time_list']:
          on_peak_time[index] = 1
          off_peak_time[index] = 0
      
      df1 = pd.DataFrame({'time': list(range(self.config['num_of_hours'])),'tier_time_on_peak':on_peak_time})
      df2 = pd.DataFrame({'time': list(range(self.config['num_of_hours'])),'tier_time_off_peak':off_peak_time})

      df1.to_csv(os.path.join(main_dir,'tier_time_on_peak.csv'),index=False)
      df2.to_csv(os.path.join(main_dir,'tier_time_off_peak.csv'),index=False)


  def run(self,dat_filename, solver_name, model):
        instance = model.create_instance(dat_filename)
        #SolverFactory(solver_name).options['max_iter'] = 1000
        print('kapil--> ',SolverFactory(solver_name).options['max_iter'])
        results = SolverFactory(solver_name).solve(instance, tee=False)
        #results.write()
        instance.solutions.store_to(results)

        return (instance, results)

  def get_output_dataframe(self):
    return self.outputs

  def get_result(self):

    on_peak_price = self.outputs['On Price Rs/MWh'].tolist()[0]
    off_peak_price = self.outputs['Off peak Rs/MWh'].tolist()[0]
    original_price = self.outputs['Original Price Rs/MWh'].tolist()[0]
    fixed_price = self.outputs['Fixed price Rs/Mwh'].tolist()[0]
    new_load_profile = self.outputs['New Load MW'].tolist()
    net_load_profile = self.outputs['Net load MW'].tolist()
    original_profile = self.outputs['Original Load MW'].tolist()
    on_peak = self.outputs['On Peak'].tolist()
    off_peak = self.outputs['Off Peak'].tolist()
    renewable_obligation = [x[0]-x[1] for x in zip(original_profile,net_load_profile)]

    self.logger.info(f'New energy consumption: {sum(new_load_profile)}')
    self.logger.info(f'Original energy consumption: {sum(original_profile)}')    
    peak_reduced =   max(self.outputs['Original Load MW'].tolist()) - max(self.outputs['New Load MW'].tolist())
    price_diff = on_peak_price - off_peak_price
    
    if off_peak_price!=0:
      price_ratio = on_peak_price/off_peak_price
    else:
      price_ratio = None

    non_renwable_purchase_cost = 0
    for t in self.instance.time:
        non_renwable_purchase_cost +=  sum([self.instance.gen_output[t,j].value*self.instance.gen_price[t,j] for j in self.instance.genindex])

    self.generators_energy = {
      plant: sum([self.instance.gen_output[t,id].value for t in self.instance.time]) for id, plant in enumerate(self.generators)
    }
    self.generators_cost = {
      plant: sum([self.instance.gen_output[t,id].value*self.instance.gen_price[t,id]/1000000 for t in self.instance.time]) for id, plant in enumerate(self.generators)
    }
    renewable_energy_cost = sum([x*RENEWABLE_PRICE for x in renewable_obligation])
    utility_new_energy_cost = non_renwable_purchase_cost + renewable_energy_cost
    utility_original_energy_cost = sum((original_price-fixed_price)*x for x in original_profile)
    utility_new_fixed_cost = max(new_load_profile)*CAPACITY_UPGRADE_COST/1 #(365*24/len(new_load_profile))
    utility_original_fixed_cost = max(original_profile)*CAPACITY_UPGRADE_COST/1 #(365*24/len(original_profile))
    utility_fixed_cost_saving = utility_original_fixed_cost - utility_new_fixed_cost

    customer_price_series = [on_peak_price*x[0] + off_peak_price*x[1] for x in zip(on_peak,off_peak)]
    customers_original_bill = sum(x*original_price for x in original_profile) 
    customers_new_bill = sum([x[0]*x[1] for x in zip(new_load_profile,customer_price_series)])
    customers_saving = customers_original_bill - customers_new_bill
 
    self.singleoutput = {
      'Customers original cost (Rs in Million)': customers_original_bill/1000000,
      'Customers New cost (Rs in Million)': customers_new_bill/1000000,
      'Customers Saving (Rs in Million)': customers_saving/1000000,
      'Utility original variable (energy) cost (Rs in Million)': utility_original_energy_cost/1000000,
      'Utility new variable (energy) cost (Rs in Million)': utility_new_energy_cost/1000000,
      'Utility variable cost saving (Rs in Million)' : (utility_original_energy_cost-utility_new_energy_cost)/1000000,
      'Utility original fixed cost (Rs in Million)' : utility_original_fixed_cost/1000000,
      'Utility new fixed cost (Rs in Million)' : utility_new_fixed_cost/1000000,
      'Utility fixed cost saving (Rs in Million)': utility_fixed_cost_saving/1000000,
      'Peak load reduction (MW)': peak_reduced,
      'On-peak price (Rs./MWh)': self.outputs['On Price Rs/MWh'].tolist()[0],
      'Off-peak price (Rs./MWh)':self.outputs['Off peak Rs/MWh'].tolist()[0],
      'On-peak off peak difference': price_diff,
      'On-peak off peak ratio': price_ratio
    }
    self.logger.info(f"{self.singleoutput}")
    file_name = os.path.join(self.config['export_path'],'output.json')
    with open(file_name,'w') as json_file:
      json.dump(self.singleoutput,json_file)

    return self.singleoutput


  def plot_loadprofile(self):

    new_load_profile = self.outputs['New Load MW'].tolist()
    original_profile = self.outputs['Original Load MW'].tolist()
    plt.plot(range(len(new_load_profile)),new_load_profile,'--or',label='new')
    plt.plot(range(len(original_profile)),original_profile,'--og',label='old')
    plt.ylabel('load (MW)')
    plt.xlabel('time index')
    plt.legend()
    plt.show()

  def plot_genoutput(self):

    # stacked bar plot
    generator_names = list(self.gen_outputs.columns)
    fig = plt.figure(figsize=(7,6))
    for id, gen in enumerate(generator_names):
      gen_profile = self.gen_outputs[gen].tolist()
      if id==0:
        bottom_profile = gen_profile
        plt.bar(range(len(gen_profile)),gen_profile,label=gen)
      else:
        plt.bar(range(len(gen_profile)),gen_profile,bottom=bottom_profile,label=gen)
        bottom_profile = [sum(x) for x in zip(bottom_profile,gen_profile)]

    plt.ylabel('generation (MW)')
    plt.xlabel('time index')
    plt.legend(bbox_to_anchor=(1.02, 1))
    plt.subplots_adjust(right=0.72)
    plt.show()

    # line plot
    generator_names = list(self.gen_outputs.columns)
    
    fig = plt.figure(figsize=(7,6))
    for id, gen in enumerate(generator_names):
      gen_profile = self.gen_outputs[gen].tolist()
      plt.plot(range(len(gen_profile)),gen_profile,'--o',label=gen)

    plt.ylabel('generation (MW)')
    plt.xlabel('time index')
    plt.legend(bbox_to_anchor=(1.02, 1))
    plt.subplots_adjust(right=0.72)
    plt.show()

    # area plot
    self.gen_outputs.index  = list(range(len(self.gen_outputs)))
    fig = plt.figure(figsize=(15,10))
    sns.heatmap(self.gen_outputs,linewidths=.5,annot=True, fmt=".1f",cmap="YlGnBu",cbar_kws={"orientation": "horizontal"})
    plt.show()
    
    # gen_output
    plt.bar(list(self.generators_energy.keys()), self.generators_energy.values())
    plt.ylabel('Energy generated (MWh)')
    plt.xticks(rotation=70)
    plt.show()

    plt.bar(list(self.generators_cost.keys()), self.generators_cost.values())
    plt.ylabel('Purchase cost \n (Million Rupees)')
    plt.xticks(rotation=70)
    plt.show()


if __name__ == '__main__':

    opt_config_dict = {
            'export_path': r'C:\Users\KDUWADI\Desktop\BRPL',
            'plot_result': True,
            'on_time_list': [19,20,21,22],
            'data_path': r'C:\Users\KDUWADI\Desktop\BRPL\data_merit_order',
            'num_of_hours': 24,#3624,
            'solver': 'ipopt'
        }
    instance = RunModel(**opt_config_dict)