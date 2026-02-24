import glob 
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from aostools import climate
time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)


def create_dataset(data, time, plev):
    ds = xr.Dataset(
        data_vars={'nam': (('time', 'plev'), data)},
        coords={'time': time, 'plev': plev}
    )
    return ds

path = "/sto4/data/Intermediate/VolMIP/piControl/"
models = ['CanESM5', 'GISS-E2-1-G','MPI-ESM1-2-LR', 'MIROC-ES2L', 'UKESM1-0-LL']
outdir = "/sto4/data/Intermediate/VolMIP/"

ua = {}
for model in models:
    ua = xr.open_dataset(glob.glob(path + model + '/ua_AmonZ*.nc')[0], decode_times=time_coder)
    start = str(ua.time[0].values).split('-')[0]
    end = str(ua.time[-1].values).split('-')[0]
    data = ua.ua.squeeze()
    nam = climate.ComputeAnnularMode(data.lat.values, data.plev.values, data.values, choice='', hemi='NH')
    nam_ds = create_dataset(nam, ua.time, ua.plev)
    nam_ds.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_NAM_'+ start + '-' + end + '.nc')
    nam_clim = nam_ds.groupby('time.month').mean('time')
    nam_clim.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_NAM_clim.nc')