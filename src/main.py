from pyfiglet import Figlet
from colorama import init
from termcolor import colored
import click
from tou.tou_optimization import RunModel
from tou.pem import GeneratePEM
import os

TEXT_COLOR = 'green'
click.style("stdout", fg="blue")

@click.group()
def run():
    f= Figlet(font='slant')
    click.echo(colored(f.renderText('PYDSM'),TEXT_COLOR))

@run.command()
@click.option('--ex', default='.', help='result export path')
@click.option('--n', default='output.csv', help='csv output file name')
@click.option('--pl', default=False, type=bool, help='plot new and old load profile')
@click.option('--pt', default='18,19,20,21,22,23', help='list of time indexes for peak time')
@click.option('--l', default=24, type=int, help="number of hours in load e.g. 24 for a day")
@click.option('--s', default='ipopt', help="pick a solver either 'ipopt' or 'glpk'")
@click.argument('datapath')
def optimizetou(ex,n,pl,pt,l,s,datapath):
    """Helps you optimize time of use tariff 

        Arguments:

            datapath: provide a folder path containing all input .csv files
    """
    pt = pt.split(',')
    print(pt)
    config_dict = {
        'export_path': os.path.join(ex,n),
        'plot_result': pl,
        'on_time_list': [int(el) for el in pt],
        'data_path': datapath,
        'num_of_hours':l,
        'solver': s
    }

    instance = RunModel(**config_dict)


@run.command()
@click.option('--pe', default='high', help="price elasticity choose from ('high','medium','low')")
@click.option('--cr', default='high', help="consumer response choose from ('high','medium','low')")
@click.option('--ex', default='.', help='result export path')
@click.option('--pl', default=True, type=bool, help='plot price elasticity matrix')
def generatepem(pe,cr,ex,pl):

    """Generates price elasticity matrix based on level of elasticity and responsiveness of customer"""

    instance = GeneratePEM(price_elasticity=pe, 
                consumers_response=cr, 
                external_dict={}, 
                export_path = os.path.join(ex,'pem.csv'))
    if pl:
        instance.plot_pem()

