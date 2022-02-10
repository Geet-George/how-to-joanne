import joanne
import os
import QC

data_directory = 'extra/Sample_Data/20200122/HALO/'
jo_version = joanne.__version__

####### QC
print('Starting QC...')
qc_dir = os.path.join(data_directory, "QC/")

status_file = f"{qc_dir}Status_of_sondes_v{joanne.__version__}.nc"

if os.path.exists(status_file):
    print("QC Status file of the current version found. Not running tests again...")
else:
    print("QC Status files of the current version not found. Running tests...")
    QC.run_qc(data_directory)
print('QC finished')

####### Level-2
print('Starting Level-2...')
import generate_Level_2
print("Level-2 finished")

####### Level-3
l3_filelist = [x for x in os.listdir(f'{data_directory}/Level_3') if x[-8:] == f"{jo_version}.nc"]

if len(l3_filelist) > 0:
    print(
        "Level-3 file found with the current JOANNE version. Therefore not running Level-3 script again."
    )
else:
    print("Starting Level-3")
    import generate_Level_3

print("Level-3 finished")