#!/bin/bash

for file in /sto4/data/Intermediate/VolMIP/piControl/IPSL*/raw/ua_*;
do
    newname=${file//"Amon"/"AmonZ"}
    cdo zonmean $file $newname
done
