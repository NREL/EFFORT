## Demand side management toolbox

This tool currently has three features.

* Optimizing time of use tariff: This module uses pyomo to solve linear optimization problem setup to find on peak and off peak price. The objective is to minimize power purchase cost as  well as future upgrade cost. Day ahead price is used to compute power purchase cost and capacity deferral cost (Rs./MW) is used to compute economic benefit of peak reduction. 
* Generate price elasticity marix: This module allows user to compute price elasticity matrix. 
* Linear regression model for predicting load proifile: Historical weather profiles (windspeed, temperature, humidity, dewpoint), consumers electicity consumption contribution for diffeerent groups, type of months, holidays are used to model statistical model to predict load profile profile for different consumer's group.

### Instructions to install the software:

Follow these steps to install the package

* Clone the repository
* Create a virtual environment using Anaconda: .. conda create -n <name_of_env> python=3.8
* Activate the environemnt and cd to a directory where you have cloned the repository
* Install the repository locally: `pip install -e .`
* Install solver from conda channel: `conda install -c conda-forge ipopt`

Now you can start using the tool.

### How to use the tool ?

There are two ways you can use this tool. One way is to use code-editor to import modules and running script. Other way is to use command line.

#### Using command line:

First step is to open up a command line and activate the environemnt.

Getting  general help

```shell
    pydsm --help
```

Getting  command help

```shell
    pydsm optimizetou --help
```

Generating price elasticity matrix with high price elasticity and low responsive consumers scenario and export in current folder

```shell
    pydsm generatepem --pe high --cr low --ex . 
```


