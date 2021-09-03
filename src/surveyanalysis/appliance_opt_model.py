'''
Optimization model to find out the energy consumption of each
of the electric appliances from survey data.
'''

# Standard library imports
import os

# Third-party imports
from pyomo.environ import *
import pyomo

# Initialize abstract pyomo model
model = AbstractModel()

# Define indices
model.appliance = Set(dimen=1)
model.appliance_timeseries = Set(dimen=1)
model.consumer = Set(dimen=1)
model.month = Set(dimen=1)

# constants for model
model.coeffmatrix_app = Param(model.consumer, model.appliance)
model.coeffmatrix_app_timeseries = Param(model.consumer, model.appliance_timeseries)
model.energy = Param(model.consumer, model.month)
model.usagematrix_app_timeseries = Param(model.consumer, model.month, model.appliance_timeseries)

# Define varibales
model.appliance_energy = Var(model.appliance, domain=NonNegativeReals)
model.appliance_timeseries_energy = Var(model.appliance_timeseries, model.month, domain=NonNegativeReals)
#model.intercept = Var(domain=NonNegativeReals)


# Expression for energy consumption
def energy_consumption_expression(model, c, m):
    return sum(model.coeffmatrix_app[c,a]*model.appliance_energy[a] for a in model.appliance) + \
            sum(model.coeffmatrix_app_timeseries[c,a]*model.appliance_timeseries_energy[a,m]*model.usagematrix_app_timeseries[c,m,a] for a in model.appliance_timeseries)
model.con_monthly_energy_consumption = Expression(model.consumer, model.month, rule=energy_consumption_expression)

def obj_expression(model):
    return sum((model.con_monthly_energy_consumption[c,m]-model.energy[c,m])*(model.con_monthly_energy_consumption[c,m]-model.energy[c,m]) for c in model.consumer for m in model.month)

model.obj = Objective(rule=obj_expression)

