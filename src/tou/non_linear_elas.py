'''
Use this formulation if you want to optimize based on merit order.
Merit order data below is provided by BRPL
'''

# Standard libraries
import os

# Third-party libraries
import pandas as pd
from pyomo.environ import *
import pyomo


'''
Obtained from DERC website (http://www.derc.gov.in/ordersPetitions/orders/Tariff/Tariff%20Order/FY%202019-20/Tariff%20Order%20FY%202019-20/Tariff%20Orders%202019-20/BRPL.pdf
, page 321, SECI solar rajasthan : Rs. 5.5/kWh, SECI wind : Rs. 2.52/kWh
average renewable price: (6.75*5.5+10.25*2.52)/(6.75+10.25) = Rs. 3.7/kWh)
'''
RENEWABLE_PRICE = 3700 

'''
Network avoidance cost obtained from BRPL per MW is Rs 2 crore
'''
CAPACITY_UPGRADE_COST = 200000


'''Initiliallize a Pyomo Model'''
model = AbstractModel()

''' Three set of indices are defined: time, tier, generators'''
model.time = Set(dimen=1)
model.tier = Set(dimen=1)
model.genindex = Set(dimen=1)

'''
Constants for optimization. 
    - pem : price elasticity matrix, two dimenstional matrix defined in pem.csv file
    - Load : load profile spefied in load.csv file
    - netLoad: net load after subtracting RPO from original profile
    - baseprice: flat electricity price in Rs/kWh (default 8 defined in data.dat file)- 
    - tier_time_on_peak: on peak time indicator, 1 if hour is onpeak otherwise 0
    - tier_time_off_peak: off peak time indicator, 1 if hour is offpeak otherwise 0
    - gen_capacity: capacity BRPL contracted for each generators
    - gen_price: electricity price for 'i' generator in 't' time
'''
model.pem = Param(model.time, model.time)
model.Load = Param(model.time)
model.netLoad = Param(model.time)
model.baseprice = Param()
model.tier_time_on_peak = Param(model.time)
model.tier_time_off_peak = Param(model.time)
model.gen_capacity = Param(model.genindex)
model.gen_price = Param(model.time, model.genindex)
model.window_pre = Param(model.time)
model.window_post = Param(model.time)


''' Initiallizes baseprice in model'''
def init_price_rule(model):
    return model.baseprice

''' Define variables for optimization
    - price_on_peak: on-peak price (initiallzed to base price)
    - price_off_peak: off-peak price (initiallized to base price)
    - Peak_Load: peak load of load profile ()
    - gen_output: output of each generators at each time
'''

model.price_on_peak = Var(initialize=init_price_rule,domain=NonNegativeReals)
model.price_off_peak = Var(initialize=init_price_rule, domain=NonNegativeReals)
model.window = Var(model.time, domain=NonNegativeReals)
# check this
model.gen_output = Var(model.time, model.genindex, domain=NonNegativeReals)
model.Peak_Load = Var(domain=NonNegativeReals)

'''
Price elasticity matric constraint
'''
model.self_elasticity=-0.3
model.W_e=13 #Window length including self timestamp, e.g. +/-6 hours would be 6*2+1=13

def price_delta_expression(model,t):
    return(-0.01*model.tier_time_off_peak[t]
        + 0.01*model.tier_time_on_peak[t])
model.price_delta_ind=Expression(model.time, rule=price_delta_expression)

def price_ind_expression(model, t): # Just a function of time
    return log((model.price_off_peak*model.tier_time_off_peak[t]
        + model.price_on_peak*model.tier_time_on_peak[t])/(model.baseprice))/log(1.0+model.price_delta_ind[t])
model.price_ind=Expression(model.time, rule=price_ind_expression)
  
def self_elas_expression(model, t):
    return model.Load[t]*(-1+((1+model.self_elasticity*model.price_delta_ind[t])**( model.price_ind[t] )))
model.Load_self_elas=Expression(model.time, rule=self_elas_expression)

def cross_elas_expression(model, t):
    return 0 + sum(model.Load[t]*(-1+((1+(-( (( ( 
            (-1+((1+model.self_elasticity*model.price_delta_ind[k])**model.price_ind[k]))/(model.W_e-1) )
        +1)**(1/model.price_ind[k])) -1)/model.price_delta_ind[k] )*model.price_delta_ind[k])**( model.price_ind[k] )))  
        for k in range(t-model.window_pre[t],t+model.window_post[t]+1,1) if k!=t) 
model.Load_cross_elas=Expression(model.time, rule=cross_elas_expression)

def load_response_expression(model, t):
    return model.Load_self_elas[t]+model.Load_cross_elas[t]+model.Load[t]
    #return model.Load_self_elas[t]+model.Load[t]
model.Load_Response=Expression(model.time, rule=load_response_expression)

'''
On peak price should be greater than off-peak price
'''

def price_constraint(model):
    return model.price_on_peak >= model.price_off_peak
model.price_constraint = Constraint(rule=price_constraint)

''' Peak load is maximum of loads in all time period'''
def Peak_Load_Constraint_Expr(model,t):
    return model.Peak_Load >= model.Load_Response[t]
model.Peak_Load_Constraint = Constraint(model.time,rule=Peak_Load_Constraint_Expr)


''' Expression for computing electricity bill under time of use tariff - new bill'''
def new_bill_expr(model):
    return sum(model.Load_Response[t]*(
        model.price_off_peak*model.tier_time_off_peak[t]
        +model.price_on_peak*model.tier_time_on_peak[t]) 
        for t in model.time)
model.new_bill=Expression(rule=new_bill_expr)

''' At each time step sum of power outputs from all generators must be equal to new load'''

def gen_output(model,t):
    return (model.Load_Response[t] - model.Load[t] + model.netLoad[t]) == sum(model.gen_output[t,j] for j in model.genindex)
model.gen_output_constraint = Constraint(model.time, rule=gen_output)

''' Constraint for upper bound for each plants'''
def upper_generator_bound(model,t,j):
    return model.gen_output[t,j] <= model.gen_capacity[j]
model.gen_upper_bound = Constraint(model.time, model.genindex, rule=upper_generator_bound)

# ''' Constraint for lower bound for each plants'''
# def lower_generator_bound(model,t,j):
#     return model.gen_output[t,j] >= 0.55*model.gen_capacity[j]
# model.gen_lower_bound = Constraint(model.time, model.genindex, rule=lower_generator_bound)

''' Expression for total cost of generation from all plants '''
def cost_of_generation(model):
    return sum(model.gen_output[t,j]*(model.gen_price[t,j]+4000) for t in model.time for j in model.genindex)
model.generation_cost = Expression(rule=cost_of_generation)

'''  New bill '''
def levelized_cost(model):
    return model.new_bill == sum((model.Load[t]-model.netLoad[t])*RENEWABLE_PRICE for t in model.time) \
            + (model.Peak_Load-max(model.Load[t] for t in model.time))*CAPACITY_UPGRADE_COST + model.generation_cost
model.levlized_cost  = Constraint(rule=levelized_cost)


''' Minimize cost of power purchase '''
def obj_expression(model):
    return sum((model.Load[t]-model.netLoad[t])*RENEWABLE_PRICE for t in model.time) \
            + (model.Peak_Load-max(model.Load[t] for t in model.time))*CAPACITY_UPGRADE_COST + model.generation_cost

model.obj = Objective(rule=obj_expression,sense=minimize)
