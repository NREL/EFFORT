from setuptools import setup, find_packages

with open("README.md","r") as fh:
    long_description = fh.read()

# Net lOad wiTh DERs
setup(
    name='DSMTOOL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='v1.0-alpha',
    description='Net load evolution with DERs',
    author='Kapil Duwadi',
    author_email='kapil.duwadi@nrel.gov',
    packages=find_packages("src"),
    url="https://github.com/NREL/DSMTOOL",
    keywords="Energy Storage, PV, Electric Vehicle, Net load, Distribution System",
    install_requires=[
        "Click==7.0",
        "pyfiglet==0.8.post1",
        "termcolor==1.1.0",
        "colorama==0.4.1"],
    entry_points={
        "console_scripts": [
            "pydsm=main:run"
        ]
    },
    package_dir={"": "src"},   
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent"
    ]
)