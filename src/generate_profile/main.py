# Standard libraries
import logging
import os
import json
import datetime 
import math
import copy

# External libraries
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# Internal libraries
from constants import LOG_FORMAT, DATE_FORMAT

class LinearModel:

    """ A class to develop a linear regression model to predict 
    transformer power profile bases on exogenous parameters mainly 
    weatherdata.
    """

    def __init__(self,config_json_path="BRPL-NREL-II\\generate_profile\\config.json"):

        """ Constructor """

        # setup logger
        self.logger = logging.getLogger()
        logging.basicConfig(format=LOG_FORMAT,level='DEBUG')

        # read settings 
        with open(config_json_path,'r') as json_file:
            self.config = json.load(json_file)
        
        # TODO: validate settings

        self.logger.info('Reading data .......')

        # Read all data
        self.data = {
            'weatherdata': pd.read_csv(self.config["weatherdatapath"],parse_dates=True,index_col='TimeStamps'),
            'dtprofile':pd.read_csv(self.config["dtprofilepath"],parse_dates=True,index_col='TimeStamps'),
            'datedata':pd.read_csv(self.config["datedatapath"],parse_dates=True,index_col='TimeStamps'),
        }

        self.start_date = datetime.datetime.strptime(self.config["start_date"],DATE_FORMAT)
        self.end_date = datetime.datetime.strptime(self.config["end_date"],DATE_FORMAT)

        self.timelist = [date for date in self.data['dtprofile'].index \
                            if date>=self.start_date and date <=self.end_date]

        self.logger.info('Imported data successfully.')


    def create_dataframe(self):
        
        self.dataformodel = pd.concat([
                self.data['weatherdata'].loc[self.timelist],
                self.data['datedata'].loc[self.timelist],
            ],axis=1,sort=False)
        self.dataformodel['TransformerPower'] = self.data['dtprofile']['PeakLoad'] \
                                                    .loc[self.timelist]
        
        self.normalizedtprofile()
        self.dataformodel['TransformerPower'] = [el if not math.isnan(el) else 0.01 \
                                                for el in self.dataformodel['TransformerPower']]
        
        self.logger.info('Created dataframe successfully')
    
    def normalizedtprofile(self):

        self.trans_power = self.dataformodel['TransformerPower'].tolist()
        self.dataformodel['TransformerPower'] = [x/max(self.trans_power) for x in self.trans_power]
        self.logger.info('Transformer power is normalized')
    
    
    def get_dataformodel(self):
        """ returns data for model """
        return self.dataformodel

    def summary_totext(self):
        """ returns a text file of model summary"""

        textfile = open('texts.txt','w')
        textfile.write(self.result.summary().as_text())
        textfile.close()

    def lm_model(self,group_name, model):

        # Normalize transformer power profile
        
        self.group_name = group_name

        # develop a statistical model
        self.model = smf.ols(model,data=self.dataformodel)

        self.logger.info(f'Model developed --> "{model}"')

        # fit and predict model
        self.result = self.model.fit()

        # export summary
        self.summary_totext()
        self.trans_prediction = self.result.predict(self.dataformodel)
        self.trans_prediction = [np.exp(el) for el in self.trans_prediction]

        # predict for group 
        self.copydata = self.dataformodel

        temp_dict = {'Temperature':0,'Humidity':0,'DewPoint':0,'WindSpeed':0}
        #temp_dict[self.group_name] = self.dataformodel[self.group_name]

        for key,value in temp_dict.items():
            if key != self.group_name:
                self.copydata[key] = [value]*len(self.copydata)
        self.prediction = self.result.predict(self.copydata)
        self.prediction = [np.exp(el) for el in self.prediction]
        self.prediction_normalized = [x/max(self.prediction) for x in self.prediction]

        self.logger.info(f'Model used for predictiong "{group_name}" group')
         
        
    def get_normalized_prediction(self):
        
        return self.prediction_normalized

    def get_transformer_prediction(self):

        return self.trans_prediction

    def get_tempmodel(self):

        return  'np.log(TransformerPower) ~  Temperature*C(Hhindex)*C(Month)\
                                  + Temperature*C(Hhindex) + Humidity*C(Hhindex) + Humidity + Humidity*C(Hhindex)*C(Month)*C(Hday) + \
                                  Temperature + Temperature*C(Hhindex)*C(Month)*C(Hday)'
        # 'np.log(TransformerPower) ~  C(Month)+ C(Hhindex)+ C(Hhindex)*C(Month) + C(Hday)*C(Hhindex)\
        #                          + Humidity*C(Hhindex) + Temperature*C(Hhindex)\
        #                          + WindSpeed*C(Hhindex) + DewPoint*C(Hhindex) + Temperature +\
        #                          Humidity + DewPoint + WindSpeed'
        # 'np.log(TransformerPower) ~  C(Month)+C(Hhindex)+ C(Hhindex)*C(Month) + C(Hday)*C(Hhindex)\
        #                          +Temperature*Humidity*C(Hhindex) + Temperature*C(Hhindex) + Temperature*C(Month)\
        #                          + Temperature*WindSpeed*C(Hhindex) + Temperature*DewPoint*C(Hhindex)'

    def execute_all_lm(self):

        # TODO  different parameters might have different model

        model_dict = {
            'Temperature': self.get_tempmodel(),
            'Humidity': self.get_tempmodel(),
            'DewPoint': self.get_tempmodel(),
            'WindSpeed': self.get_tempmodel(),
        }

        self.prediction_result = {}

        # for now let's find out temperature dependent profile
        self.lm_model('Temperature',model_dict['Temperature'])
        self.prediction_result['Temperature'] = self.get_normalized_prediction()
        self.prediction_result['TransformerPrediction'] = self.get_transformer_prediction()

        # Reduced temperature by 5 degree celcius
        self.copydata = copy.deepcopy(self.dataformodel)
        self.copydata['Temperature'] = [el-5 for el in self.copydata['Temperature'].tolist()]

        trans_pred = self.result.predict(self.copydata)
        self.prediction_result['TemperatureReduced'] = [np.exp(el) for el in trans_pred]

        # Increase temperature by 5 degree celcius
        self.copydata = copy.deepcopy(self.dataformodel)
        self.copydata['Temperature'] = [el+5 for el in self.dataformodel['Temperature'].tolist()]

        trans_pred = self.result.predict(self.copydata)
        self.prediction_result['TemperatureIncreased'] = [np.exp(el) for el in trans_pred]
        self.prediction_result['Temperature'] = self.dataformodel['Temperature']

    def predict_using_external_data(self, external_data):

        self.ext_pred = self.result.predict(external_data)
        self.ext_pred = [np.exp(el)*max(self.trans_power) \
            for el in self.ext_pred]

        df = pd.DataFrame({'Original': external_data['TransformerPower'], 
        'Prediction': self.ext_pred })
        df.to_csv('external.csv')


    def export_all(self):

        df = pd.DataFrame({'TransformerOriginal':self.dataformodel['TransformerPower']})
        for group, result in self.prediction_result.items():
            df[group] = result
        df.index = self.dataformodel.index
        df.to_csv(os.path.join(self.config['export_folder'],'result.csv'))

        self.logger.info(f'exported all prediction for transformer')


if __name__ == '__main__':

    model_instance = LinearModel(config_json_path="BRPL-NREL-II\\src\\generate_profile\\config.json")
    model_instance.create_dataframe()
    model_instance.execute_all_lm()
    model_instance.export_all() 

    # read data
    df = pd.read_csv('test_lm_data.csv')
    model_instance.predict_using_external_data(df)   

