# Python file to grid all Level-2 files and output single NC for input to Level-4

# %%
import datetime
import os
import subprocess
import warnings
from tqdm import tqdm 

import numpy as np
import xarray as xr

# import dicts
from joanne.Level_3 import fn_3 as f3
from joanne.Level_3 import dicts as dicts
import joanne

warnings.filterwarnings(
    "ignore", module="metpy.calc.thermo", message="invalid value encountered"
)

#### Defining functions - update these on JOANNE for general use #####

def substitute_T_and_RH_for_interpolated_dataset(dataset):

    """
    Input :
        dataset : Dataset interpolated along height
    Output :
        dataset : Original dataset with new T and RH
    Function to remove interoplated values of T and RH in the original dataset and 
    replace with new values of T and RH,
    calculated from values of interpolated theta and q, respetively
    """
    T = f3.calc_T_from_theta(dataset)
    rh = f3.calc_rh_from_q(dataset, T=T)

    dataset["ta"] = (dataset.p.dims, T)
    dataset["rh"] = (dataset.p.dims, rh.values)

    return dataset

def substitute_wdir_for_interpolated_dataset(dataset):

    """
    Input :
        dataset : Dataset interpolated along height
    Output :
        dataset : Original dataset with new wind direction and wind speed
    Function to remove interoplated values of wdir in the original dataset and 
    replace with new values of wdir computed from u and v
    """

    w_dir, w_spd = f3.compute_wdir_from_u_and_v(dataset.u, dataset.v)

    dataset["w_dir"] = (dataset.p.dims, w_dir.values)
    dataset["w_spd"] = (dataset.p.dims, w_spd.values)

    return dataset


def interpolate_for_level_3(
    file_path_OR_dataset,
    height_limit=10000,
    vertical_spacing=10,
    pressure_log_interp=True,
):

    """
    Input :
        file_path_OR_dataset : string or  dataset
                               if file path to Level-2 NC file is provided as string, 
                               dataset will be created using the ready_to_interpolate() function,
                               if dataset is provided, it will be used directly
    Output :
        interpolated_dataset : xarray dataset
                               interpolated dataset
    Function to interpolate a dataset with Level-2 data, in the format 
    for Level-3 gridding
    """

    if type(file_path_OR_dataset) is str:
        dataset = f3.ready_to_interpolate(file_path_OR_dataset)
    else:
        dataset = file_path_OR_dataset

    interpolated_dataset = f3.interp_along_height(
        dataset, height_limit=height_limit, vertical_spacing=vertical_spacing
    )

    interpolated_dataset = f3.get_N_and_m_values(
        interpolated_dataset, dataset, bin_length=vertical_spacing
    )

    if pressure_log_interp is True:
        interpolated_dataset = f3.add_log_interp_pressure_to_dataset(
            dataset, interpolated_dataset
        )

    interpolated_dataset = substitute_T_and_RH_for_interpolated_dataset(
        interpolated_dataset
    )

    interpolated_dataset = substitute_wdir_for_interpolated_dataset(
        interpolated_dataset
    )

    dataset = f3.add_platform_details_as_var(dataset)

    for var in [
        "platform_id",
        "flight_altitude",
        "flight_lat",
        "flight_lon",
        "launch_time",
        "low_height_flag",
        "sonde_id",
    ]:
        interpolated_dataset[var] = dataset[var]

    # interpolated_dataset = add_cloud_flag(interpolated_dataset)
    # interpolated_dataset = adding_static_stability_to_dataset(interpolated_dataset)

    return interpolated_dataset

def lv3_structure_from_lv2(
    directory,
    height_limit=10000,
    vertical_spacing=10,
    pressure_log_interp=True,
):
    """
    Input :
        directory : string or list
                                     if directory where NC files are stored is provided as a string,
                                     a list of file paths for all NC files in the directory is created,
                                     otherwise a list of file paths needed to be gridded can also be 
                                     provided directly
    Output :
        dataset : xarray dataset
                  dataset with Level-3 structure
                  
    Function to create Level-3 gridded dataset from Level-2 files
    """
    
    list_of_files = f3.retrieve_all_files(directory+'Level_2/', file_ext="*.nc")

    interp_list = [None] * len(list_of_files)

    save_directory = f"{directory}Level_3/Interim_files/"
    
    if os.path.exists(save_directory):
        pass
    else:
        os.makedirs(save_directory)

    for id_, file_path in enumerate(tqdm(list_of_files)):

        file_name = (
            "EUREC4A_JOANNE_Dropsonde-RD41_"
            + str(file_path[file_path.find("RD41_") + 3 : file_path.find("RD41_") + 19])
            + "Level_3_v"
            + str(joanne.__version__)
            + ".nc"
        )

        if os.path.exists(save_directory + file_name):

            interp_list[id_] = xr.open_dataset(save_directory + file_name)

        else:

            interp_list[id_] = interpolate_for_level_3(
                file_path,
                height_limit=height_limit,
                vertical_spacing=vertical_spacing,
                pressure_log_interp=pressure_log_interp,
            )

            interp_list[id_].to_netcdf(save_directory + file_name)

    concat_list = []
    for i in interp_list:

        if "ta" in i.variables:
            concat_list.append(i)

    dataset = f3.concatenate_soundings(concat_list)

    return dataset

######## Generating Level-3 ######

data_directory = (
    "extra/Sample_Data/20200122/HALO/"  # Level_2/"  # code_testing_data/"
)

print("Creating / checking for interim files...")

lv3_dataset = lv3_structure_from_lv2(data_directory,pressure_log_interp=False)

# # %%
nc_data = {}

for var in dicts.list_of_vars:
    if lv3_dataset[var].values.dtype == "float64":
        nc_data[var] = np.float32(lv3_dataset[var].values)
    else:
        nc_data[var] = lv3_dataset[var].values
# %%

obs = np.arange(0, len(lv3_dataset.alt) * 10, 10, dtype="short")
sonde_id = lv3_dataset.sonde_id.values

to_save_ds = xr.Dataset(coords={"alt": obs, "sonde_id": sonde_id})

for dim in dicts.dim_attrs:
    to_save_ds[dim] = to_save_ds[dim].assign_attrs(dicts.dim_attrs[dim])

for var in dicts.list_of_vars:
    f3.create_variable(
        to_save_ds, var, data=nc_data, dims=dicts.nc_dims, attrs=dicts.nc_attrs
    )

to_save_ds["alt_bnds"] = (
    ["alt", "nv"],
    np.array([f3.interpolation_bins[:-1], f3.interpolation_bins[1:]]).T.astype("int32"),
)
to_save_ds["alt_bnds"] = to_save_ds["alt_bnds"].assign_attrs(
    {
        # "long_name": "cell altitude_bounds",
        "description": "cell interval bounds for altitude",
        "_FillValue": False,
        "comment": "(lower bound, upper bound]",
        "units": "m",
    }
)

print('Saving Level-3 file...')

file_name = (
    "EUREC4A_JOANNE_Dropsonde-RD41_" + "Level_3_v" + str(joanne.__version__) + ".nc"
)

save_directory = f"{data_directory}Level_3/"  # Test_data/" #Level_3/"

comp = dict(zlib=True, complevel=4, fletcher32=True, _FillValue=np.finfo("float32").max)

encoding = {
    var: comp
    for var in to_save_ds.data_vars
    if var not in ["platform_id", "sonde_id", "alt_bnds"]
}
encoding["launch_time"] = {"units": "seconds since 2020-01-01", "dtype": "int32"}
encoding["interpolated_time"] = {
    "units": "seconds since 2020-01-01",
    "dtype": "int32",
    "_FillValue": np.iinfo("int32").max,
}

for key in dicts.nc_global_attrs.keys():
    to_save_ds.attrs[key] = dicts.nc_global_attrs[key]

to_save_ds.to_netcdf(
    save_directory + file_name, mode="w", format="NETCDF4", encoding=encoding
)