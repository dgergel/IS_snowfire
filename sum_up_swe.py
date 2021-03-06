### TAKES IN lats, lons, swe 

import numpy as np
import math
from snowpack_functions import mask_out_other_mtns,get_dist,calc_area,unpack_netcdf_swe_month,unpack_netcdf_file_var,historical_sum_swe
import sys
import os
## get command line arguments
args = sys.argv[1:]
type = args[0]
basin = args[1]
if (type == "ensavg"):
        scenario = args[2]
else:
        model = args[2]
        scenario = args[3]

direc = '/raid9/gergel/agg_snowpack/goodleap/%s' %basin

if (type == "ensavg"):
        file_swe = 'SWE_ensavg_%s_%s.nc' %(scenario,basin)
else:
        if (scenario == "historical"):
                file_swe = '%s__%s.monday1.SWE.1950_2005_%s.nc' %(model,scenario,basin)
        else:
                file_swe = '%s__%s.monday1.SWE.2006_2099_%s.nc' %(model,scenario,basin)
lats,lons,swe,datess_swe = unpack_netcdf_file_var(direc,file_swe,"swe")


resol=0.0625
swe_yearly_agg = np.ndarray(shape = (len(swe),1), dtype=float)
sm_yearly_agg_mar = np.ndarray(shape = (len(swe),1),dtype=float)
sm_yearly_agg_aug = np.ndarray(shape = (len(swe),1),dtype=float)
    
## get historical data for soil moisture to be done
if (type == "ensavg"):
	## historical file names
	file_sm_mar_hist = 'TotalSoilMoist_ensavg_%s_%s_march.nc' %("historical",basin)
    	file_sm_aug_hist = 'TotalSoilMoist_ensavg_%s_%s_august.nc' %("historical",basin)
	## other filenames
	file_sm_mar = 'TotalSoilMoist_ensavg_%s_%s_march.nc' %(scenario,basin)
        file_sm_aug = 'TotalSoilMoist_ensavg_%s_%s_august.nc' %(scenario,basin)
	## load historical files
	lats,lons,sm_mar_hist,datess_sm_mar = unpack_netcdf_file_var(direc,file_sm_mar_hist,"TotalSoilMoist")
        lats,lons,sm_aug_hist,datess_sm_aug = unpack_netcdf_file_var(direc,file_sm_aug_hist,"TotalSoilMoist")
	## load rcp 45/85 files
    	lats,lons,sm_mar,datess_sm_mar = unpack_netcdf_file_var(direc,file_sm_mar,"TotalSoilMoist")
    	lats,lons,sm_aug,datess_sm_aug = unpack_netcdf_file_var(direc,file_sm_aug,"TotalSoilMoist")
else: 
	## historical file names
        file_sm_mar_hist = '%s__%s.monday1.TotalSoilMoist.1950_2005_%s_march.nc' %(model,"historical",basin)
        file_sm_aug_hist = '%s__%s.monday1.TotalSoilMoist.1950_2005_%s_august.nc' %(model,"historical",basin)
        ## other filenames
	if (scenario != "historical"):
        	file_sm_mar = '%s__%s.monday1.TotalSoilMoist.2006_2099_%s_march.nc' %(model,scenario,basin)
        	file_sm_aug = '%s__%s.monday1.TotalSoilMoist.2006_2099_%s_august.nc' %(model,scenario,basin)
        else: 
		file_sm_mar = '%s__%s.monday1.TotalSoilMoist.1950_2005_%s_march.nc' %(model,scenario,basin)
                file_sm_aug = '%s__%s.monday1.TotalSoilMoist.1950_2005_%s_august.nc' %(model,scenario,basin)
	## load historical files
	print(file_sm_mar_hist) 
        lats,lons,sm_mar_hist,datess_sm_mar = unpack_netcdf_file_var(direc,file_sm_mar_hist,"TotalSoilMoist")
        lats,lons,sm_aug_hist,datess_sm_aug = unpack_netcdf_file_var(direc,file_sm_aug_hist,"TotalSoilMoist")
        ## load rcp 45/85 files
	print(file_sm_mar) 
        lats,lons,sm_mar,datess_sm_mar = unpack_netcdf_file_var(direc,file_sm_mar,"TotalSoilMoist")
        lats,lons,sm_aug,datess_sm_aug = unpack_netcdf_file_var(direc,file_sm_aug,"TotalSoilMoist")

# NorESM1-M__rcp85.monday1.TotalSoilMoist.2006_2099_whites_march.nc

## arrays for latitude and longitude values included in the historical mean mask 
lats_lons_inc_in_mask = list()

################# loop through array and get latitude, longitude and swe values for each #############
count_appending_latslons = 0

for i in np.arange(len(swe)):     ### loop over year
	count_appending_latslons += 1
        ## initialize value of SWE for each year to zero
        swe_gridcell_total = 0
	sm_mar_gridcell_total = 0
	sm_aug_gridcell_total = 0

        for j in np.arange(len(lats)):       ### loop over latitude

        	for k in np.arange(len(lons)):   ### loop over longitude
                ### don't calculate area for missing value elements
                	if (math.isnan(swe[i,j,k])) == False:
				## REMOVE ADDITIONAL GRID CELLS ACCORDING TO LAT_LON_ADJUST FOR BOXES AND ADJUSTMENTS (LATER MASKS)
				#if_in_box = mask_latlon(lats[j],lons[k],basin)
				#adjust_mask = lat_lon_adjust(lats[j],lons[k],basin)
				if_in_box = mask_out_other_mtns(lats[j],lons[k])
				if if_in_box:
                    			mean_swe = historical_sum_swe(j,k)
		    			########################### EXCLUDE GRID CELLS WITH MEAN HISTORICAL SWE < 10 MM 
                    			if mean_swe: 
						### calculate area of grid cell
                        			cellarea = calc_area(lats[j],lons[k],resol)
                        			## calculate amount of swe and soil moisture in each grid cell: swe (in mm) * area of grid cell; adjust for units
                        			swe_gridcell = cellarea*(swe[i,j,k]*0.000001)
						swe_gridcell_total += swe_gridcell

						## do soil moisture analysis
						sm_in_storage_march = np.min(np.asarray(sm_mar_hist[:,j,k]))*cellarea*0.000001
						sm_in_storage_aug = np.min(np.asarray(sm_aug_hist[:,j,k]))*cellarea*0.000001
						sm_mar_gridcell = (cellarea*(sm_mar[i,j,k]*0.000001)) - sm_in_storage_march
						sm_aug_gridcell = (cellarea*(sm_aug[i,j,k]*0.000001)) - sm_in_storage_aug
						## sum up soil moisture
						sm_mar_gridcell_total += sm_mar_gridcell 
						sm_aug_gridcell_total += sm_aug_gridcell
						
						
						## ONLY ADD LATS/LONS TO LIST FOR FIRST LOOP
						if (count_appending_latslons < 2): 
                        				points = [lats[j],lons[k]]
                        				lats_lons_inc_in_mask.append(points)
                
        ## summed up yearly April 1 aggregate snowpack
        swe_yearly_agg[i] = swe_gridcell_total
	
	sm_yearly_agg_mar[i] = sm_mar_gridcell_total
	sm_yearly_agg_aug[i] = sm_aug_gridcell_total
    
##### save arrays to files for a multimodel average (and for spatial plots with lats and lons)
## define path based on scenario
if (type == "ensavg"):
	filearrayname = '/raid9/gergel/agg_snowpack/%s/%s.npz' %(scenario,basin)
    	np.savez(filearrayname,dates=datess_swe,swe=swe_yearly_agg,sm_mar=sm_yearly_agg_mar,sm_aug=sm_yearly_agg_aug,latslons=np.asarray(lats_lons_inc_in_mask))
else: 
	filearrayname = '/raid9/gergel/agg_snowpack/%s/%s_%s.npz' %(scenario,model,basin)
	np.savez(filearrayname,dates=datess_swe,swe=swe_yearly_agg,sm_mar=sm_yearly_agg_mar,sm_aug=sm_yearly_agg_aug,latslons=np.asarray(lats_lons_inc_in_mask))
#file_mask = '/raid9/gergel/agg_snowpack/%s/%s_latslonsinmask_%s.npz' %(scenario,basin,model)
#np.savez(file_mask,x=np.asarray(lats_lons_inc_in_mask))


if (type == "ensavg"):
	print ("finished calculations for %s %s %s" %(type,basin,scenario))
else:
	print ("finished calculations for %s %s %s %s" %(type,basin,model,scenario))    
            


