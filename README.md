# MolCondMeasurements
Data acquisition and analysis in the context of molecule evaporation and conductivity measurements.

This is a toolbox consisting of several programs developed during my master thesis in nanoscience. Most are targeted towards very specific problems encountered while working with partly lab-made devices. 

- The program `QuartzMicrobalance.py` is written for automization and remote data recording from a tectra Quartz Microbalance. The connection is established via an intellemetrics<sup>TM</sup> IL150 Quartz Crystal Rate Monitor using a serial port. 
- The program `Breakjunction.py` is written for automization and remote data recording on a lab-made setup to measure the conductance of metal nanowires and molecular break junctions. Voltage measurements where done on an Agilent Technologies InfiniiVision digital storage oscilloscope (DSO7014B) which is controled using the given program.
- The program `I_of_t_DataReview.py` is an example of a program to get a quick overview of a data set that is to be evaluated in the form of a histogram. The contribution of individual curves can be accessed and a basic option for sorting the curves is provided by remembering relevant entries in the data set by index. 50 random current-time curves (I(t)-) from a data set are provided as sample data for testing purposes.
