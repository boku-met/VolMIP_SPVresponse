from intake_esgf import ESGFCatalog
import matplotlib.pyplot as plt
import xarray as xr
import xesmf as xe

def anomaly_calculation(model, clim):
    ano_list = []
    for i in range(1,13):
        ano_list.append(model.sel(time=model.time[model.time.dt.month.isin(i)]) - clim.sel(month=i))
    return xr.concat(ano_list, dim='time').sortby('time')

def regrid(in_grid,out_grid, var): 
    reg_bil = xe.Regridder(in_grid,out_grid, "bilinear")
    var_bil = reg_bil(in_grid[var])
    return var_bil

def clim(ds):
    return ds.groupby('time.month').mean('time')

def shift_lon(ds, lon_name = 'lon'):
    # Adjust lon values to make sure they are within (-180, 180)
    ds['_longitude_adjusted'] = xr.where(
        ds[lon_name] > 180,
        ds[lon_name] - 360,
        ds[lon_name])

    # reassign the new coords to as the main lon coords
    # and sort DataArray using new coordinate values
    ds = (
        ds
        .swap_dims({lon_name: '_longitude_adjusted'})
        .sel(**{'_longitude_adjusted': sorted(ds._longitude_adjusted)})
        .drop_vars(lon_name))

    ds = ds.rename({'_longitude_adjusted': lon_name})
    return ds

def calculate_nino34_index(ds):
    # ds needs to be tos-anomalies
    # 170° - 120°W -> 190 - 240°E
    nino = ds.sel(lon=slice(190,240), lat=slice(-5,5)).mean(['lon', 'lat']).compute()
    return nino

def calculate_nao(ds):
    ds_south = ds.sel(lat=slice(20,55), lon=slice(-90,60)).mean(['lon','lat'])
    ds_north = ds.sel(lat=slice(55,90), lon=slice(-90,60)).mean(['lon','lat'])
    nao = (ds_south - ds_north).compute()
    nao = nao.zg.to_dataset(name='zg')
    return nao


def calculate_djf_mean(ds):
    ds_seasons = ds.resample(time='QE-FEB').mean()
    ds_djf = ds_seasons.sel(time=(ds_seasons['time.season'] == 'DJF'))
    return ds_djf

outdir = "/sto4/data/Intermediate/VolMIP/"
models = ['CanESM5', 'MIROC-ES2L', 'MPI-ESM1-2-LR', 'GISS-E2-1-G', 'UKESM1-0-LL']

# according to member id in VOLMIP!!
member_id = ['r1i1p2f1', 'r1i1p1f2', 'r1i1p1f1', 'r1i1p1f1', 'r1i1p1f2']


for model, id in zip(models, member_id):
    print(model)
    # open ESGF catalog
    cat=ESGFCatalog()
    metagrid_search = cat.search(activity_id='CMIP', experiment_id='piControl', source_id=model,
            variable_id=['tos', 'zg'], latest=True, table_id=['Omon','Amon'], member_id=id, grid_label='gn')
    ds = metagrid_search.to_path_dict()
    
    #####################################
    # NAO (Northern Atlanic Oscillation)#
    #####################################

    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    ds_zg = xr.open_mfdataset(ds['Amon.zg'], decode_times=time_coder)
    start = str(ds_zg.time[0].values).split('-')[0]
    end = str(ds_zg.time[-1].values).split('-')[0]
    # shift lon to °W-°E so there is no problem at 0° 
    ds_prep = shift_lon(ds_zg.sel(plev=50000, lat=slice(0,100)))

    # calculate nao index
    nao = calculate_nao(ds_prep)
    nao_djf = calculate_djf_mean(nao)
    # write output
    nao.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_NAO_'+ start + '-' + end + '.nc')
    nao_djf.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_NAO_djf_'+ start + '-' + end + '.nc')
    
    ######################################
    # ENSO (El Nino Southern Oscillation)#
    ######################################
    ds_tos = xr.open_mfdataset(ds['Omon.tos'], decode_times=time_coder)
    # regrid to regular lat lon grid
    ds_tos_reg = regrid(ds_tos, ds_zg, 'tos')

    # sst climatology
    tos_clim = clim(ds_tos_reg)
    tos_clim.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_tos_clim_'+ start + '-' + end + '.nc')

    # calculate nino index
    nino = calculate_nino34_index(ds_tos_reg)
    nino = nino.to_dataset(name='tos')
    nino_djf = calculate_djf_mean(nino)

    # build anomalies & calculate rsst nino index
    tos_clim20 = tos_clim.sel(lat=slice(-20,20)).mean(['lat','lon'])
    ds_ano = anomaly_calculation(ds_tos_reg, tos_clim20)
    rsstnino = calculate_nino34_index(ds_ano)
    rsstnino = rsstnino.to_dataset(name='tos')
    rsstnino_djf = calculate_djf_mean(rsstnino)

    nino.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_Nino34_'+ start + '-' + end + '.nc')
    nino_djf.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_Nino34_djf_'+ start + '-' + end + '.nc')

    rsstnino.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_RNino34_'+ start + '-' + end + '.nc')
    rsstnino_djf.to_netcdf(outdir + 'piControl/' + model + '/piControl_' + model + '_RNino34_djf_'+ start + '-' + end + '.nc')