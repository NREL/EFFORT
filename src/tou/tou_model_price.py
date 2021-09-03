
from pyomo.environ import *
import pyomo

'''
Obtained from DERC website (http://www.derc.gov.in/ordersPetitions/orders/Tariff/Tariff%20Order/FY%202019-20/Tariff%20Order%20FY%202019-20/Tariff%20Orders%202019-20/BRPL.pdf
, page 321, SECI solar rajasthan : Rs. 5.5/kWh, SECI wind : Rs. 2.52/kWh
avrage renewable price: (6.75*5.5+10.25*2.52)/(6.75+10.25) = Rs. 3.7/kWh)
'''
RENEWABLE_PRICE = 3700 

'''
Network avoidance cost obtained from BRPL per MW is Rs 2 crore
'''
CAPACITY_UPGRADE_COST = 20000000

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
model.netLoad = Param(model.time)
model.baseprice = Param()
model.tier_time_on_peak = Param(model.time)
model.tier_time_off_peak = Param(model.time)
model.energy_price = Param(model.time)
model.Peak_Load = Var(domain=NonNegativeReals)

''' Initiallizes baseprice in model'''
def init_price_rule(model):
    return model.baseprice

''' Define variables for optimization
    - price_on_peak: on-peak price (initiallzed to base price)
    - price_off_peak: off-peak price (initiallized to base price)
    - Peak_Load: peak load of load profile ()
'''
model.price_on_peak = Var(initialize=init_price_rule,domain=NonNegativeReals)
model.price_off_peak = Var(initialize=init_price_rule, domain=NonNegativeReals)

'''
Expression of new load profile. Customers behaviour is dictated by price elasticity matrix
as well as on peak and off peak price.
'''
def pricetime_expression(model, t):
    return model.Load[t] + sum(model.pem[k%24,t%24]*(
        model.price_off_peak*model.tier_time_off_peak[k]
        +model.price_on_peak*model.tier_time_on_peak[k] 
        - model.baseprice)*model.Load[k]/model.baseprice  
        for k in model.time) 
model.Load_Response=Expression(model.time, rule=pricetime_expression)

''' on peak price must be greater than off peak price'''
def price_constraint2(model):
    return model.price_on_peak >= model.price_off_peak
model.UpperTier2 = Constraint(rule=price_constraint2)


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


'''  New bill '''
def levelized_cost(model):
    return model.new_bill == sum((model.Load_Response[t]-model.netLoad[t]+model.Load[t])*model.energy_price[t] + \
         (model.Load[t]-model.netLoad[t])*RENEWABLE_PRICE for t in model.time) \
            + (model.Peak_Load-max(model.Load[t] for t in model.time))*CAPACITY_UPGRADE_COST
model.levlized_cost  = Constraint(rule=levelized_cost)


''' Minimize cost of power purchase '''
def obj_expression(model):
    return sum((model.Load_Response[t]-model.netLoad[t]+model.Load[t])*model.energy_price[t] for t in model.time) \
            + (model.Peak_Load-max(model.Load[t] for t in model.time))*CAPACITY_UPGRADE_COST

model.obj = Objective(rule=obj_expression,sense=minimize)



# ''' Expression for computing original energy consumption'''
# def original_energy_expr(model):
#     return sum(model.Load[t] for t in model.time)
# model.original_energy=Expression(rule=original_energy_expr)

# ''' Expression for new energy consumption'''
# def new_energy_expr(model):
#     return sum(model.Load_Response[t] for t in model.time)
# model.new_energy=Expression(rule=new_energy_expr)

# ''' New energy consumption must be less tha 105% of original consumption'''
# def energy_upper_constraint(model):
#     return 1.05*model.original_energy >= model.new_energy
# model.energy_upper_constraint  = Constraint(rule=energy_upper_constraint)

# ''' New energy consumption should be greater than 95% of original '''
# def energy_lower_constraint(model):
#     return model.new_energy >= 0.95*model.original_energy
# model.energy_lower_constraint  = Constraint(rule=energy_lower_constraint)


# ''' New customer bill must be less than original bill'''
# def customer_bill(model):
#     return model.new_bill <= model.original_bill 
# model.customer_bill = Constraint(rule=customer_bill)

# ''' Expression for computing electricity bill under flat rate tariff scheme - original bill'''
# def original_bill_expr(model):
#     return sum(model.Load[t]*model.baseprice for t in model.time)
# model.original_bill=Expression(rule=original_bill_expr)

# def off_peak_floor(model):
#     return model.price_off_peak >= 2.0
# model.off_peak_floor_contraint = Constraint(rule=off_peak_floor)