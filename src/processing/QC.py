# Python file to run QC over ASPEN-processed files and output "good" sondes for input to Level-3

import datetime
import glob
import os
import sys
import warnings

import numpy as np
import pandas as pd
import xarray as xr

import joanne
from joanne.Level_2 import fn_2 as f2

Platform = 'HALO'

def get_all_sondes_list(data_dir='../extra/Sample_Data/20200122/HALO/'):

    directory = f"{data_dir}Level_1/"
    # directory where all sonde files are present

    a_dir = f"{data_dir}Level_0/"
    # directory where all the A files are present

    qc_directory = f"{data_dir}QC/"
    # directory to store logs and stats

    sonde_paths = sorted(glob.glob(directory + "*QC.nc"))
    # paths to the individual sonde files

    file_time_str = [None] * len(sonde_paths)
    file_time = [None] * len(sonde_paths)
    # list to store extracted sonde time from file name as string and as time

    a_files = [None] * len(sonde_paths)
    # list to store file names for the log files starting with A.

    sonde_ds = [None] * len(sonde_paths)
    # list to store individual datasets of all sondes from PQC files

    for i in range(len(sonde_paths)):
        file_time_str[i] = sonde_paths[i][-20:-5]
        file_time[i] = np.datetime64(
            pd.to_datetime(file_time_str[i], format="%Y%m%d_%H%M%S"), "s"
        )
        a_files[i] = "A" + file_time_str[i]
        sonde_ds[i] = xr.open_dataset(sonde_paths[i])

    return sonde_ds, directory, a_dir, qc_directory, a_files, file_time, sonde_paths


data_dir = 'extra/Sample_Data/20200122/HALO/'
qc_directory = f"{data_dir}QC/"
a_dir = f"{data_dir}Level_0/"

(sonde_ds,
    directory,
    a_dir,
    qc_directory,
    a_files,
    file_time,
    sonde_paths,
) = get_all_sondes_list(data_dir)

if os.path.exists(qc_directory):
    pass
else:
    os.makedirs(qc_directory)
    
to_save_ds_filename = (
        f"{qc_directory}Status_of_sondes_v{joanne.__version__}.nc"
    )

if os.path.exists(to_save_ds_filename):

    print(f"Status file of the current version exists.")

    to_save_ds = xr.open_dataset(to_save_ds_filename)

else:

    # Retrieving all non NaN index sums in to a list for all sondes
    list_nc = list(map(f2.get_total_non_nan_indices, sonde_ds))

    launch_time = [None] * len(sonde_ds)

    for i in range(len(sonde_ds)):
        launch_time[i] = sonde_ds[i].launch_time.values
    
    print('Running QC tests...')
    
    (
        list_of_variables,
        s_time,
        s_t,
        s_rh,
        s_p,
        s_z,
        s_u,
        s_v,
        s_alt,
    ) = f2.get_var_count_sums(list_nc)

    ld_FLAG = f2.get_ld_flag_from_a_files(a_dir, a_files, qc_directory, Platform, logs=True)

    status_ds = f2.init_status_ds(
        list_of_variables,
        s_time,
        s_t,
        s_rh,
        s_p,
        s_z,
        s_u,
        s_v,
        s_alt,
        ld_FLAG,
        file_time,
    )

    status_ds, ind_flag_vars = f2.add_ind_flags_to_statusds(
        status_ds, list_of_variables
    )
    status_ds, srf_flag_vars = f2.add_srf_flags_to_statusds(status_ds, sonde_paths)
    status_ds, ind_FLAG = f2.get_the_ind_FLAG_to_statusds(status_ds, ind_flag_vars)
    status_ds, srf_FLAG = f2.get_the_srf_FLAG_to_statusds(status_ds, srf_flag_vars)
    status_ds = f2.get_the_FLAG(status_ds, ind_FLAG, srf_FLAG)
    status_ds["launch_time"] = (["time"], pd.DatetimeIndex(launch_time))
    status_ds = f2.add_sonde_id_to_status_ds(Platform, sonde_ds, status_ds)
    
    print('Saving QC status file...')
    
    to_save_ds = (
        status_ds.swap_dims({"time": "sonde_id"}).reset_coords("time", drop=True)
        # .sortby("launch_time")
    )

    to_save_ds = f2.rename_vars(to_save_ds)
    
    to_save_ds.to_netcdf(
        f"{qc_directory}Status_of_sondes_v{joanne.__version__}.nc"
    )