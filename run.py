#!/usr/bin/env python3

import os
import configparser

config = configparser.ConfigParser()
config.read('run_config.cfg')

# set in and out dir
in_dir = config.get('DEFAULT','directory')

if config.getboolean('output_directory','same_as_input') == True:
    out_dir = in_dir
else:
    out_dir = config['output_directory']['output_directory']
    
if os.path.isdir(out_dir + 'Plots') == False: os.mkdir(out_dir + 'Plots')
if os.path.isdir(out_dir + 'Level_2') == False: os.mkdir(out_dir + 'Level_2')
if os.path.isdir(out_dir + 'Level_3') == False: os.mkdir(out_dir + 'Level_3')
if os.path.isdir(out_dir + 'Level_4') == False: os.mkdir(out_dir + 'Level_4')

### only for this test, put in output dir of Level_3 or level 4 data in the end

if config.getboolean('quicklooks','mode') == True:
    plot_data_dir = in_dir
    import src.plotting.quicklooks