#%%
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px
import glob

####
#self made helper functions
import utility_functions
import configurations
root_dir =re.split('buildings', os.getcwd())[0]+'/buildings'
config = configurations.Config(root_dir)
###
# %%
# import economy data
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
# %%
from c1_projection_adjust_function import fuel_intensity_traj

# # %%
intensity_trajectory_interim = pd.read_csv(config.root_dir + '/output_data/fortrajectory/intensity_trajectory_data.csv')

# %%
# Define years list tp adjust later 
years = [i for i in range(1980, 2101, 1)]
# %%
###################################################################################################
# Alter trajectory where necesary
# select econonmy, fuels, proj_start_year, shape, magnitude, apex_mag, apex_loc, data=intensity_trajectory_interim

# %%
#################################### Australia #################################################################

# fuel_intensity_traj(economy = '01_AUS', fuels = '01_coal', proj_start_year = 2022, 
#                     shape = 'peak', magnitude = 50, apex_mag = 1.1, apex_loc = 50,
#                     data=intensity_trajectory_interim)

# %%
#################################### Canada #################################################################
# 01_coal
# coal is zero by 2017

# %%
# 07_petroleum_products
fuel_intensity_traj(economy = '03_CDA', fuels = '07_petroleum_products', proj_start_year = 2022, 
                    shape = 'decrease', magnitude = 0.5,
                    data=intensity_trajectory_interim)

# %%
# 08_gas
fuel_intensity_traj(economy = '03_CDA', fuels = '08_gas', proj_start_year = 2022, 
                    shape = 'decrease', magnitude = 0.5,
                    data=intensity_trajectory_interim)

# %%
# 15_solid_biomass
fuel_intensity_traj(economy = '03_CDA', fuels = '15_solid_biomass', proj_start_year = 2022, 
                    shape = 'decrease', magnitude = 0.5,
                    data=intensity_trajectory_interim)

# %%
# 16_others
fuel_intensity_traj(economy = '03_CDA', fuels = '16_others', proj_start_year = 2022, 
                    shape = 'decrease', magnitude = 0.5,
                    data=intensity_trajectory_interim)

# %%
# 17_electricity
fuel_intensity_traj(economy = '03_CDA', fuels = '17_electricity', proj_start_year = 2022, 
                    shape = 'decrease', magnitude = 0.5,
                    data=intensity_trajectory_interim)

# %%
# 18_heat
fuel_intensity_traj(economy = '03_CDA', fuels = '18_heat', proj_start_year = 2022, 
                    shape = 'decrease', magnitude = 0.5,
                    data=intensity_trajectory_interim)


# %%
# Consildate refined tracjectories

traj_overwrite_df = pd.DataFrame()

for economy in economy_list['economy_code']:
    filenames = glob.glob(config.root_dir + '/output_data/fuel_intensity_refine_auto/{}/*.csv'.format(economy))
    for i in filenames:
        temp_df = pd.read_csv(i)
        traj_overwrite_df = pd.concat([traj_overwrite_df, temp_df]).copy()

traj_overwrite_df.to_csv(config.root_dir + '/output_data/fuel_intensity_refine_auto/adjusted_intensities_csv.csv', index=False)
# need to keep these ones
# %%
# Merge the adjusted data onto the original data to get df with all economies and fuels even if not updated
intensity_trajectory_interim = intensity_trajectory_interim.copy()
traj_overwrite_df = traj_overwrite_df.copy()

fueluse_adj = intensity_trajectory_interim.merge(traj_overwrite_df, how = 'left',
                              on = ['economy', 'year', 'fuels', 
                                    'dataset', 'fuel_PJ', 'population', 'fuel_intensity_GJperCap'])
fueluse_adj.to_csv(config.root_dir + '/output_data/fuel_intensity_refine_auto/fueluse_testing_copy.csv', index = False)

# %%
# Keep values from the updated intensity when existing

fueluse_adj['intensity_GJ'] = fueluse_adj['adj_fuel_intensity'].fillna(fueluse_adj['fuel_intensity_GJperCap'])

# %%
# Clean up df
fueluse_adj = fueluse_adj.copy().drop(columns = ['fuel_intensity_GJperCap', 'adj_fuel_intensity'])
fueluse_adj['fueluse_adj'] = fueluse_adj['intensity_GJ'] * 1e-6 * fueluse_adj['population']
fueluse_adj.to_csv(config.root_dir + '/output_data/fuel_intensity_refine_auto/fueluse_adj_all.csv', index = False)


# %%
# Create fig
fig = px.line(fueluse_adj, x='year', y='fueluse_adj', color='fuels', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(config.root_dir + '/output_data/fuel_intensity_refine_auto/fueluse_adj.html')

# %%
