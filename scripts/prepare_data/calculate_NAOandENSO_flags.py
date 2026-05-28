import xarray as xr
import numpy as np
import pandas as pd
import glob
from datetime import datetime, timedelta
time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

def calculate_tercile_flags(data, var):
    # calculate terciles to cluster indices into 3 categories: -1 (negative/cold), 0 (netural), 1 (positive/warm state)
    df = data[var].to_dataframe()
    df = df.reset_index()
    df = df.set_index('time')
    tertiles = df[var].quantile([1/3, 2/3]).to_list()
    tertiles = [-float('inf')] + tertiles + [float('inf')]

    df['tercile'] = pd.cut(df[var], bins=tertiles, labels=[-1,0,1])
    return df['tercile']

def calculate_index(path, var, time_coder=time_coder, sel_time=None):
    # calculate index and tercile flags for a given variable and path (ENSO: var='tos', NAO: var='zg')
    data = xr.open_dataset(path, decode_times=time_coder)
    if sel_time is not None:
        data = data.isel(time=sel_time)
    index = (data - data.mean('time'))/ np.sqrt(data.var('time'))   
    index['tercile'] = calculate_tercile_flags(index, var)
    return index


# prepare dataframe
df_all = []
outfilename = "/home/kperny/VolMIP_stratosphere/tab/nao_enso_flags.csv"

###########
# CanESM5 #
###########
path = "/sto4/data/Intermediate/VolMIP/pinatubo-full/CanESM5/raw/ta*"

# path_nao = "/sto4/data/Intermediate/VolMIP/piControl/CanESM5/wrong_piControl_CanESM5_NAO_djf_5550-6600_wrong.nc"
# path_enso = "/sto4/data/Intermediate/VolMIP/piControl/CanESM5/wrong_piControl_CanESM5_Nino34_djf_5550-6600_wrong.nc"
path_nao = "/sto4/data/Intermediate/VolMIP/piControl/CanESM5/piControl_CanESM5_NAO_djf_5550-6600.nc"
path_enso = "/sto4/data/Intermediate/VolMIP/piControl/CanESM5/piControl_CanESM5_Nino34_djf_5550-6600.nc"

nao = calculate_index(path_nao, 'zg')
enso = calculate_index(path_enso, 'tos')

realization_can = []
nao_can = []
nao_flag_can = []
enso_can = []
enso_flag_can = []
year_can = []
for i in range(len(glob.glob(path))):
    file = glob.glob(path + 'r' + str(i + 1) + 'i*.nc')[0]
    realization_can.append(file.split('/')[-1].split('_')[4])
    data_can = xr.open_dataset(file)
    year_post_eruption = str(int(data_can.attrs['YMDH_branch_time_in_parent'].split(':')[0]) + 1)
    year_can.append(str(year_post_eruption) + '-02-01')

    nao_can.append(nao.sel(time=year_post_eruption).zg.values[0])
    enso_can.append(enso.sel(time=year_post_eruption).tos.values[0])
    nao_flag_can.append(nao.sel(time=year_post_eruption).tercile.values[0])
    enso_flag_can.append(enso.sel(time=year_post_eruption).tercile.values[0])
df = pd.DataFrame({'realization': realization_can, 'nao': nao_can, 'enso': enso_can, 'nao_flag': nao_flag_can, 'enso_flag': enso_flag_can, 'year': year_can})
df['model'] = 'CanESM5'
df_all.append(df)

###############
# GISS-E2-1-G #
###############
path = "/sto4/data/Intermediate/VolMIP/pinatubo-full/GISS-E2-1-G/raw/ta*"
# path_nao = "/sto4/data/Intermediate/VolMIP/piControl/GISS-E2-1-G/wrong_piControl_GISS-E2-1-G_NAO_djf_7550-8400_wrong.nc"
# path_enso = "/sto4/data/Intermediate/VolMIP/piControl/GISS-E2-1-G/wronf_piControl_GISS-E2-1-G_Nino34_djf_7550-8400_wrong.nc"

path_nao = "/sto4/data/Intermediate/VolMIP/piControl/GISS-E2-1-G/piControl_GISS-E2-1-G_NAO_djf_7550-8400.nc"
path_enso = "/sto4/data/Intermediate/VolMIP/piControl/GISS-E2-1-G/piControl_GISS-E2-1-G_Nino34_djf_7550-8400.nc"

nao = calculate_index(path_nao, 'zg')
enso = calculate_index(path_enso, 'tos')

realization_giss = []
nao_giss =[]
enso_giss = []
nao_flag_giss = []
enso_flag_giss = []
year_giss  = []
for file in sorted(glob.glob(path)):
    # file = glob.glob(path + 'r' + str(i + 1) + 'i*.nc')[0]
    realization_giss.append(file.split('/')[-1].split('_')[4])
    data_giss = xr.open_dataset(file, decode_times=time_coder)
    year_post_eruption = str(int(str(data_giss.time[0].values).split('-')[0]) + 1)
    year_giss.append(str(year_post_eruption) + '-02-01')

    nao_giss.append(nao.sel(time=year_post_eruption).zg.values[0])
    enso_giss.append(enso.sel(time=year_post_eruption).tos.values[0])

    nao_flag_giss.append(nao.sel(time=year_post_eruption).tercile.values[0])
    enso_flag_giss.append(enso.sel(time=year_post_eruption).tercile.values[0])
df = pd.DataFrame({'realization': realization_giss, 'nao': nao_giss, 'enso': enso_giss, 'nao_flag': nao_flag_giss, 'enso_flag': enso_flag_giss, 'year': year_giss})
df['model'] = 'GISS-E2-1-G'
df_all.append(df)

##############
# MIROC-ES2L #
##############
path = "/sto4/data/Intermediate/VolMIP/pinatubo-full/MIROC-ES2L/raw/ta*"
# path_nao = "/sto4/data/Intermediate/VolMIP/piControl/MIROC-ES2L/wrong_piControl_MIROC-ES2L_NAO_djf_1850-2349_wrong.nc"
# path_enso = "/sto4/data/Intermediate/VolMIP/piControl/MIROC-ES2L/wrong_piControl_MIROC-ES2L_Nino34_djf_1850-2349_wrong.nc"  
path_nao = "/sto4/data/Intermediate/VolMIP/piControl/MIROC-ES2L/piControl_MIROC-ES2L_NAO_djf_1850-2349.nc"
path_enso = "/sto4/data/Intermediate/VolMIP/piControl/MIROC-ES2L/piControl_MIROC-ES2L_Nino34_djf_1850-2349.nc"  

nao = calculate_index(path_nao, 'zg')
enso = calculate_index(path_enso, 'tos')

realization_miroc = []
nao_miroc = []
enso_miroc = []
nao_flag_miroc = []
enso_flag_miroc = []
year_miroc = []
for i in range(len(glob.glob(path))):
    file = glob.glob(path + 'r' + str(i + 1) + 'i*.nc')[0]
    realization_miroc.append(file.split('/')[-1].split('_')[4])
    data_miroc = xr.open_dataset(file, decode_times=time_coder)
    start = datetime.strptime(data_miroc.attrs['parent_time_units'].split(' ')[2], '%Y-%m-%d') 
    year_post_eruption = str((start + timedelta(days=data_miroc.attrs['branch_time_in_parent'])).year + 1)
    year_miroc.append(str(year_post_eruption) + '-02-01')

    nao_miroc.append(nao.sel(time=year_post_eruption).zg.values[0])
    enso_miroc.append(enso.sel(time=year_post_eruption).tos.values[0])

    nao_flag_miroc.append(nao.sel(time=year_post_eruption).tercile.values[0])
    enso_flag_miroc.append(enso.sel(time=year_post_eruption).tercile.values[0])
df = pd.DataFrame({'realization': realization_miroc, 'nao': nao_miroc, 'enso': enso_miroc, 'nao_flag': nao_flag_miroc, 'enso_flag': enso_flag_miroc, 'year': year_miroc})
df['model'] = 'MIROC-ES2L'
df_all.append(df)

#################
# MPI-ESM1-2-LR #
#################
path = "/sto4/data/Intermediate/VolMIP/pinatubo-full/MPI-ESM1-2-LR/raw/ta*"
# path_nao = "/sto4/data/Intermediate/VolMIP/piControl/MPI-ESM1-2-LR/wrong_piControl_MPI-ESM1-2-LR_NAO_djf_1850-2849_wrong.nc"
# path_enso = "/sto4/data/Intermediate/VolMIP/piControl/MPI-ESM1-2-LR/wrong_piControl_MPI-ESM1-2-LR_Nino34_djf_1850-2849_wrong.nc"
path_nao = "/sto4/data/Intermediate/VolMIP/piControl/MPI-ESM1-2-LR/piControl_MPI-ESM1-2-LR_NAO_djf_1850-2849.nc"
path_enso = "/sto4/data/Intermediate/VolMIP/piControl/MPI-ESM1-2-LR/piControl_MPI-ESM1-2-LR_Nino34_djf_1850-2849.nc"

nao = calculate_index(path_nao, 'zg')
enso = calculate_index(path_enso, 'tos')

realization_mpi = []
nao_mpi = []
enso_mpi = []
nao_flag_mpi = []
enso_flag_mpi = []
year_mpi = []
for i in range(len(glob.glob(path))):
    file = glob.glob(path + 'r' + str(i + 1) + 'i*.nc')[0]
    realization_mpi.append(file.split('/')[-1].split('_')[4])
    data_mpi = xr.open_dataset(file, decode_times=time_coder)
    start = datetime.strptime(data_mpi.attrs['parent_time_units'].split(' ')[2], '%Y-%m-%d') 
    year_post_eruption = str((start + timedelta(days=data_mpi.attrs['branch_time_in_parent'])).year + 1)
    year_mpi.append(str(year_post_eruption) + '-02-01')
    
    nao_mpi.append(nao.sel(time=year_post_eruption).zg.values[0])
    enso_mpi.append(enso.sel(time=year_post_eruption).tos.values[0])
    
    nao_flag_mpi.append(nao.sel(time=year_post_eruption).tercile.values[0])
    enso_flag_mpi.append(enso.sel(time=year_post_eruption).tercile.values[0])
df = pd.DataFrame({'realization': realization_mpi, 'nao': nao_mpi, 'enso': enso_mpi, 'nao_flag': nao_flag_mpi, 'enso_flag': enso_flag_mpi, 'year': year_mpi})
df['model'] = 'MPI-ESM1-2-LR'
df_all.append(df)

###############
# UKESM1-0-LL #
###############
path = "/sto4/data/Intermediate/VolMIP/pinatubo-full/UKESM1-0-LL/ta_A*"
# path_nao = "/sto4/data/Intermediate/VolMIP/piControl/UKESM1-0-LL/wrong_piControl_UKESM1-0-LL_NAO_djf_1960-3839_wrong.nc"
# path_enso = "/sto4/data/Intermediate/VolMIP/piControl/UKESM1-0-LL/wrong_piControl_UKESM1-0-LL_Nino34_djf_1960-3839_wrong.nc"
path_nao = "/sto4/data/Intermediate/VolMIP/piControl/UKESM1-0-LL/piControl_UKESM1-0-LL_NAO_djf_1960-3839.nc"
path_enso = "/sto4/data/Intermediate/VolMIP/piControl/UKESM1-0-LL/piControl_UKESM1-0-LL_Nino34_djf_1960-3839.nc"

# hard-coded years from Zanchettin et al 2022, Table S1, as the branch time in parent and child attributes are not correct for UKESM1-0-LL
years = [3174, 3064, 3067, 3128, 3116, 3171, 3138, 3153, 3052, 3135, 3141, 3193, 3058, 3055, 3061, 3085, 3094, 3049, 3177, 3165, 3122, 3073, 3103, 3076, 3180]

# nao = calculate_index(path_nao, 'zg')
# enso = calculate_index(path_enso, 'tos')
nao = calculate_index(path_nao, 'zg', sel_time=np.arange(2600-1960,3199-1960+1))
enso = calculate_index(path_enso, 'tos', sel_time=np.arange(2600-1960,3199-1960+1))

realization_ukesm = []
nao_ukesm = []
enso_ukesm = []
nao_flag_ukesm = []
enso_flag_ukesm = []
year_ukesm = []

#for file in sorted(glob.glob(path)):
for i, year in enumerate(years):
    file = glob.glob(path + 'r' + str(i + 1) + 'i1p1f2*')[0]
    realization_ukesm.append(file.split('/')[-1].split('_')[4])
    data_ukesm = xr.open_dataset(file, decode_times=time_coder)
    
    # start = datetime.strptime(data_ukesm.attrs['parent_time_units'].split(' ')[2], '%Y-%m-%d') 
    # year_post_eruption = str((start + timedelta(days=data_ukesm.attrs['branch_time_in_parent']) + timedelta(days=data_ukesm.attrs['branch_time_in_child'])).year + 1 )
    # print(year_post_eruption)
    year_post_eruption = str(year + 1)
    year_ukesm.append(str(year_post_eruption) + '-02-01')
    
    nao_ukesm.append(nao.sel(time=year_post_eruption).zg.values[0])
    enso_ukesm.append(enso.sel(time=year_post_eruption).tos.values[0])
    
    nao_flag_ukesm.append(nao.sel(time=year_post_eruption).tercile.values[0])
    enso_flag_ukesm.append(enso.sel(time=year_post_eruption).tercile.values[0])

df = pd.DataFrame({'realization': realization_ukesm, 'nao': nao_ukesm, 'enso': enso_ukesm, 'nao_flag': nao_flag_ukesm, 'enso_flag': enso_flag_ukesm, 'year': year_ukesm})
df['model'] = 'UKESM1-0-LL'
df_all.append(df)

# concatenate all dataframes and save as csv
pd.concat(df_all).to_csv(outfilename, index=False)