#!/bin/bash

### volc-pinatubo-full 
# iterate over each ensemble member
# for file in /sto4/data/Intermediate/VolMIP/pinatubo-full/Can*/raw/zg*;
# do
#     echo $file
#     new_name=${file//"raw/zg"/"NAO"}
#     echo $new_name
#     nccopy -c time/10,lat/10,lon/10 $file z_decompress.nc
#     cdo sellevel,50000  z_decompress.nc zg_500.nc
#     cdo -fldmean -sellonlatbox,-90,60,20,55 zg_500.nc zg_500_ma.nc
#     cdo -fldmean -sellonlatbox,-90,60,55,90 zg_500.nc zg_500_na.nc
#     cdo sub zg_500_ma.nc zg_500_na.nc $new_name
#     rm zg_500.nc zg_500_ma.nc zg_500_na.nc z_decompress.nc
# done

# PiControl
# iterate over models
for file in /sto4/data/Intermediate/VolMIP/piControl/Can*;
do 
    echo $file
    cdo mergetime "$file/raw/zg*" "$file/zg_merge.nc"

    nccopy -c time/10,lat/10,lon/10 "$file/zg_merge.nc" "$file/z_decompress.nc"
    cdo sellevel,50000  "$file/z_decompress.nc" "$file/zg_500.nc"
    cdo -fldmean -sellonlatbox,-90,60,20,55 "$file/zg_500.nc" "$file/zg_500_ma.nc"
    cdo -fldmean -sellonlatbox,-90,60,55,90 "$file/zg_500.nc" "$file/zg_500_na.nc"
    cdo sub "$file/zg_500_ma.nc" "$file/zg_500_na.nc" "$file/NAO_Amon_piControl.nc"
    rm "$file/zg_500.nc" "$file/zg_500_ma.nc" "$file/zg_500_na.nc" "$file/zg_merge.nc" "$file/z_decompress.nc"
done