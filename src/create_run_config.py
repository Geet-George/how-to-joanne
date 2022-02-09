import configparser

config = configparser.ConfigParser()

config['DEFAULT'] = {'directory': '../extra/Sample_Data/20200122/',
                     'aspen_suffix': '*QC.nc',
                     'run_levels': '4',
                     'flight_segmentation_available': False,
                    }

config['flight_segmentation'] = {}

fs = config['flight_segmentation']
fs['directory'] = ''

config['quicklooks'] = {'mode': 'on'}

with open('../run_config.cfg', 'w') as configfile:
    config.write(configfile)