# %%
import datetime
import glob
import os

import numpy as np
import pandas as pd
import seaborn as sb
import xarray as xr
from tqdm import tqdm
from packaging import version

import joanne
from joanne.Level_2 import fn_2 as f2
from joanne.Level_2 import dicts

Platform = 'HALO'
data_dir='extra/Sample_Data/20200122/HALO/'
save_dir = 'extra/Sample_Data/20200122/HALO/Level_2/'

if os.path.exists(save_dir):
    pass
else:
    os.makedirs(save_dir)

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

varname_L1 = ["height", "time", "wspd", "wdir", "tdry", "pres", "rh", "lat", "lon"]
varname_L2 = ["alt", "time", "wspd", "wdir", "ta", "p", "rh", "lat", "lon"]

# for Platform in ["HALO", "P3"]:

(
    sonde_ds,
    directory,
    a_dir,
    qc_directory,
    a_files,
    file_time,
    sonde_paths,
) = get_all_sondes_list(data_dir)

# look for status file with same major and minor version-bit
# (patch number and modifiers can be different)

status_filename = glob.glob(
    f"{qc_directory}Status_of_sondes_v{joanne.__version__[:3]}*.nc"
)

vers = [None] * len(status_filename)

for n, i in enumerate(status_filename):
    vers[n] = version.parse(i)

status_ds = xr.open_dataset(str(max(vers)))

a_filepaths = []

for i in a_files:
    a_filepaths.append(sorted(glob.glob(a_dir + i + "*")))

file_time_str = [None] * len(sonde_paths)

for i in range(len(sonde_paths)):
    # file_time_str[i] = sonde_paths[i][-22:-7]
    lt_pd = pd.to_datetime(min(sonde_ds[i].time.values))

    file_time_str[
        i
    ] = f"{(lt_pd.year)}{(lt_pd.month):02}{(lt_pd.day):02}_{(lt_pd.hour):02}{(lt_pd.minute):02}{(lt_pd.second):02}"

for i in tqdm(range(len(sonde_ds))):

    if (
        status_ds.swap_dims({"sonde_id": "launch_time"})
        .sel(
            launch_time=sonde_ds[i].launch_time.values,
            # method="nearest",
            # tolerance="1s",
        )
        .qc_flag
        == "GOOD"
    ):

        # ht_indices = ~np.isnan(sonde_ds[i].alt)
        ht_indices = (
            ~np.isnan(sonde_ds[i].alt)
            & ~np.isnan(sonde_ds[i].lat)
            & ~np.isnan(sonde_ds[i].lon)
        )
        # retrieving non-NaN indices of geopotential height (sonde_ds[i].alt)
        # only time values at these indices will be used in Level-2 trajectory data;
        # this means that only alternate u,v values are included in the Level-2 data
        # PTU has 2 Hz measurement frequency, while GPS has a 4 Hz measurement frequency

        ###----- Dimensions -----###

        obs = np.arange(1, ht_indices.sum() + 1, 1)
        # creating the observations dimension of the NC file

        ###----- Variables -----###

        height = np.float32(sonde_ds[i].alt[ht_indices].values)
        # Variable array: geopotential height

        time = sonde_ds[i].time[ht_indices].values  # .astype("float").values / 1e9
        # Variable array: time

        variables = {}

        variables["time"] = time
        variables["alt"] = height

        ###--------- Unit Conversions --------###

        if Platform == "HALO":
            variables["rh"] = np.float32(
                sonde_ds[i]["rh"][ht_indices].values * 1.06 / 100
            )
        elif Platform == "P3":
            variables["rh"] = np.float32(sonde_ds[i]["rh"][ht_indices].values / 100)
        variables["lat"] = np.float32(sonde_ds[i]["lat"][ht_indices].values)
        variables["lon"] = np.float32(sonde_ds[i]["lon"][ht_indices].values)
        variables["p"] = np.float32(sonde_ds[i]["pres"][ht_indices].values * 100)
        variables["ta"] = np.float32(
            sonde_ds[i]["tdry"][ht_indices].values + 273.15
        )

        for var1, var2 in zip(varname_L1, varname_L2):
            if var2 not in variables.keys():
                variables[var2] = np.float32(sonde_ds[i][var1][ht_indices].values)

        ###--------- Creating and populating dataset --------###

        to_save_ds = xr.Dataset(coords={"time": obs})

        for var in dicts.nc_meta.keys():
            # v = var
            f2.create_variable(to_save_ds, var, variables[var])

        ### ---------- adding the sonde_id var to the dataset --------- #####
        sonde_id = (
            status_ds.swap_dims({"sonde_id": "launch_time"})
            .sel(launch_time=sonde_ds[i].launch_time.values)
            .sonde_id.values
        )
        attrs = {
            "descripion": "unique sonde ID",
            "long_name": "sonde identifier",
            "cf_role": "trajectory_id",
        }
        sonde_id_var = xr.Variable([], sonde_id, attrs=attrs)
        to_save_ds["sonde_id"] = sonde_id_var

        # file name
        file_name = (
            "EUREC4A_JOANNE"
            # + str(Platform)
            + "_Dropsonde-RD41_"
            + str(sonde_id)
            + "_Level_2"
            + "_v"
            + str(joanne.__version__)
            + ".nc"
        )

        comp = dict(
            zlib=True,
            complevel=4,
            fletcher32=True,
            _FillValue=np.finfo("float32").max,
        )

        encoding = {var: comp for var in to_save_ds.data_vars if var != "sonde_id"}
        encoding["time"] = {"units": "seconds since 2020-01-01", "dtype": "float"}

        nc_global_attrs = dicts.get_global_attrs(
            Platform, file_time[i], sonde_ds[i]
        )

        for key in nc_global_attrs.keys():
            to_save_ds.attrs[key] = nc_global_attrs[key]

        flight_attrs = dicts.get_flight_attrs(a_filepaths[i][0])

        for key in flight_attrs:
            to_save_ds.attrs[key] = flight_attrs[key]

        ###--------- Saving dataset to NetCDF file --------###
        
        if os.path.exists(save_dir + file_name):

            print(f"Level-2 file of the current version exists.")

#             to_save_ds = xr.open_dataset(to_save_ds_filename)
            
        else :

            to_save_ds.to_netcdf(
                save_dir + file_name,
                mode="w",
                format="NETCDF4",
                encoding=encoding,
            )