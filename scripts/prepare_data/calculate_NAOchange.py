import glob
import numpy as np
import pandas as pd
import xarray as xr 
import seaborn as sns
import matplotlib.pyplot as plt

time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)


def calculate_djf_mean(ds):
    ds_seasons = ds.resample(time='QE-FEB').mean()
    ds_djf = ds_seasons.sel(time=(ds_seasons['time.season'] == 'DJF'))
    return ds_djf

def calculate_tercile_flags(data, var):
    # calculate terciles to cluster indices into 3 categories: -1 (negative/cold), 0 (netural), 1 (positive/warm state)
    df = data[var].to_dataframe()
    df = df.reset_index()
    df = df.set_index('time')
    tertiles = df[var].quantile([1/3, 2/3]).to_list()
    tertiles = [-float('inf')] + tertiles + [float('inf')]

    return tertiles

datadir = "/sto4/data/Intermediate/VolMIP/"
models = ['CanESM5', 'MIROC-ES2L', 'MPI-ESM1-2-LR', 'GISS-E2-1-G', 'UKESM1-0-LL']

# piControl NAO and ENSO information
df_flags = pd.read_csv("/home/kperny/VolMIP_stratosphere/tab/nao_enso_flags.csv")

collect_df = []
for model in models:
    df_model = df_flags.where(df_flags['model'] == model).dropna()
    # calculate terciles based on piControl data
    data_control = xr.open_dataset(glob.glob(datadir + 'piControl/' + model + '/piControl_' + model + '_NAO_djf*.nc')[0], decode_times=time_coder)
    tertiles = calculate_tercile_flags((data_control- data_control.mean('time') ) /  np.sqrt(data_control.var('time')), 'zg')

    # iterate over individual ensemble members and calculate NAO index
    nao = []
    for ens in df_model['realization']:
        data_volc = xr.open_dataset(glob.glob(datadir + 'pinatubo-full/' + model + '/NAO_*' + ens + '*_fixed_dates.nc')[0])
        nao.append((calculate_djf_mean(data_volc).sel(time='1992') - data_control.mean('time') ) /  np.sqrt(data_control.var('time')))
    #concat and rename
    nao_volc = xr.concat(nao, dim='realization')
    nao_volc['realization'] = df_model['realization'].values
    df_volc = nao_volc.rename({'zg': 'nao'}).nao.to_dataframe().reset_index().drop(['time', 'plev', 'lat', 'lon'], axis=1)

    # calcualte NAO flag based on terciles from piControl
    df_volc['nao_flag'] = pd.cut(df_volc['nao'], bins=tertiles, labels=[-1,0,1])
    df_volc['experiment'] = 'volc'
    df_cut = df_model[['realization', 'nao', 'nao_flag']]
    df_cut['experiment'] = 'piControl'

    df = pd.concat([df_cut, df_volc])
    df['model'] = model
    collect_df.append(df)

# concat, sort and save
df_nao = pd.concat(collect_df)
df_nao = df_nao.set_index(['model', 'realization', 'experiment']).sort_index()
df_nao.reset_index().to_csv("/home/kperny/VolMIP_stratosphere/tab/nao_change.csv", index=False)