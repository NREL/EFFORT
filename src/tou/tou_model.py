
from pyomo.environ import *
import pyomo


'''Initiliallize a Pyomo Model'''
model = AbstractModel()

'''There will be two set of indexes 'time' and 'tier'.
time and tier parameters are specified time.csv and tier.csv file inside 'data' folder
'''
model.time = Set(dimen=1)
model.tier = Set(dimen=1)


'''
Constants for optimization. 
    - pem : price elasticity matrix, two dimenstional matrix defined in pem.csv file
    - Load : load profile spefied in load.csv file
    - baseprice: flat electricity price in Rs/kWh (default 8 defined in data.dat file)- 
    - tier_time_on_peak: on peak time indicator, 1 if hour is onpeak otherwise 0
    - tier_time_off_peak: off peak time indicator, 1 if hour is offpeak otherwise 0
'''
model.pem = Param(model.time, model.time)
model.Load = Param(model.time)
model.baseprice = Param()
model.tier_time_on_peak = Param(model.time)
model.tier_time_off_peak = Param(model.time)

''' Initiallizes baseprice in model'''
def init_price_rule(model):
    return model.baseprice

''' Define variables for optimization
    - price_on_peak: on-peak price (initiallzed to base price)
    - price_off_peak: off-peak price (initiallized to base price)
    - Peak_Load: peak load of load profile ()
'''
model.price_on_peak = Var(initialize=init_price_rule)
model.price_off_peak = Var(initialize=init_price_rule)
model.Peak_Load = Var(domain=NonNegativeReals)


'''
Expression of new load profile. Customers behaviour is dictated by price elasticity matrix
as well as on peak and off peak price.
'''

def pricetime_expression(model, t):
    return model.Load[t] + sum(model.pem[t%24,k%24]*(
        model.price_off_peak*model.tier_time_off_peak[k]
        +model.price_on_peak*model.tier_time_on_peak[k] 
        - model.baseprice)*model.Load[t]/model.baseprice 
        for k in model.time) 
model.Load_Response=Expression(model.time, rule=pricetime_expression)


''' Peak load is maximum of loads in all time period'''

def Peak_Load_Constraint_Expr(model,t):
    return model.Peak_Load >= model.Load_Response[t]
model.Peak_Load_Constraint = Constraint(model.time,rule=Peak_Load_Constraint_Expr)


''' on peak price must be greater than off peak price'''
def price_constraint2(model):
    return model.price_on_peak >= model.price_off_peak
model.UpperTier2 = Constraint(rule=price_constraint2)


''' Expression for computing electricity bill under flat rate tariff scheme - original bill'''
def original_bill_expr(model):
    return sum(model.Load[t]*model.baseprice for t in model.time)
model.original_bill=Expression(rule=original_bill_expr)


''' Expression for computing electricity bill under time of use tariff - new bill'''
def new_bill_expr(model):
    return sum(model.Load_Response[t]*(
        model.price_off_peak*model.tier_time_off_peak[t]
        +model.price_on_peak*model.tier_time_on_peak[t]) 
        for t in model.time)
model.new_bill=Expression(rule=new_bill_expr)

''' New bill must be less than or equal to original bill'''
def bill_constraint(model):
    return 1.1*model.original_bill >= model.new_bill >= 0.9*model.original_bill
model.bill_constraint  = Constraint(rule=bill_constraint)


''' Minimize the peak load '''
def obj_expression(model):
    return model.Peak_Load


model.obj = Objective(rule=obj_expression,sense=minimize)
