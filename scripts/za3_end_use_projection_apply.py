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
from za2_end_use_projection_adjustment import traj

# %%
end_use_trajectory_interim1 = pd.read_csv(config.root_dir + '/output_data/a1_projection/projection_w_end_use_scaled.csv')
end_use_trajectory_interim = end_use_trajectory_interim1[end_use_trajectory_interim1['year'] != 2101]



# %%
# Define years list tp adjust later 
years = [i for i in range(1980, 2101, 1)]
# %%
###################################################################################################
# Alter trajectory where necesary

# def traj(economy='01_AUS', 
#         end_use = 'cooking',   ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances']
#         sector = '16_01_02_residential',          # 16_01_01_commercial_and_public_services 
#         proj_start_year=2021, 
#         shape='increase', 
#         magnitude=1.5, 
#         apex_mag=1.5, 
#         apex_loc=10, 
#         data=end_use_trajectory):

# %%
#################################### Australia #################################################################

# fuel_intensity_traj(economy = '01_AUS', fuels = '01_coal', proj_start_year = 2022, 
#                     shape = 'peak', magnitude = 50, apex_mag = 1.1, apex_loc = 50,
#                     data=intensity_trajectory_interim)

# %%
#################################### Canada #################################################################
# 01_coal
# coal is zero by 2017 so no adjustments needed
# %%

# traj(economy = '03_CDA', end_use = 'space_heating', sector = '16_01_02_residential', proj_start_year = 2021, 
#                     shape = 'increase', magnitude = 1.1,
#                     data=end_use_trajectory_interim)

# traj(economy = '03_CDA', end_use = 'space_cooling', sector = '16_01_02_residential', proj_start_year = 2021, 
#                     shape = 'decrease', magnitude = 1.1,
#                     data=end_use_trajectory_interim)

# traj(economy = '03_CDA', end_use = 'cooking', sector = '16_01_02_residential', proj_start_year = 2021, 
#                     shape = 'increase', magnitude = 1.05,
#                     data=end_use_trajectory_interim)

# traj(economy = '03_CDA', end_use = 'lighting', sector = '16_01_02_residential', proj_start_year = 2021, 
#                     shape = 'increase', magnitude = 1.009,
#                     data=end_use_trajectory_interim)

# traj(economy = '03_CDA', end_use = 'residential_appliances', sector = '16_01_02_residential', proj_start_year = 2021, 
#                     shape = 'increase', magnitude = 1.05,
#                     data=end_use_trajectory_interim)

# traj(economy = '03_CDA', end_use = 'water_heating', sector = '16_01_02_residential', proj_start_year = 2021, 
#                     shape = 'increase', magnitude = 1.05,
#                     data=end_use_trajectory_interim)


# traj(economy = '03_CDA', end_use = 'space_heating', sector = '16_01_01_commercial_and_public_services', proj_start_year = 2021, 
#                     shape = 'peak', magnitude= 1.2, apex_mag = 0.9995, apex_loc= 40,
#                     data=end_use_trajectory_interim)

# traj(economy = '03_CDA', end_use = 'space_cooling', sector = '16_01_01_commercial_and_public_services', proj_start_year = 2021, 
#                     shape = 'decrease', magnitude = 1.2,
#                     data=end_use_trajectory_interim)

# traj(economy = '03_CDA', end_use = 'lighting', sector = '16_01_01_commercial_and_public_services', proj_start_year = 2021, 
#                     shape = 'decrease', magnitude = 1.2,
#                     data=end_use_trajectory_interim)




# %%
# Consildate refined tracjectories

traj_overwrite_df = pd.DataFrame()


for economy in economy_list['economy_code']:
    filenames = glob.glob(config.root_dir + '/output_data/a3_energy_refine_auto/{}/*.csv'.format(economy))
    for i in filenames:
        temp_df = pd.read_csv(i)
        traj_overwrite_df = pd.concat([traj_overwrite_df, temp_df]).copy()

# %%

output_dir_csv = config.root_dir + '/output_data/a3_projection_adjustment/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

output_dir_fig = config.root_dir + '/plotting_output/a3_projection_adjustment/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

traj_overwrite_df.to_csv(output_dir_csv + 'adjusted_enduse_all.csv', index=False)
# need to keep these ones
fig = px.area(traj_overwrite_df, x='year', y='energy', color='end_use_sector', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'energy_adj_enduses_area_traj_all.html')

# %%
# Merge the adjusted data onto the original data to get df with all economies and fuels even if not updated
end_use_trajectory_interim = end_use_trajectory_interim.copy()
# end_use	economy	intensity	year	sub2sectors	value	energy	end_use_sector

traj_overwrite_df = traj_overwrite_df.copy()
# year	end_use	economy	intensity	sub2sectors	value	energy	end_use_sector	adj_energy
# %%
enduse_adj = pd.merge(end_use_trajectory_interim, traj_overwrite_df[['year', 'economy', 'end_use', 'sub2sectors', 'adj_energy']],
                     on=['year', 'economy', 'end_use', 'sub2sectors'], how='left')
# enduse_adj.to_csv(config.root_dir + '/output_data/energy_refine_auto/enduse_testing_copy.csv', index = False)

# %%
# Keep values from the updated intensity when existing

enduse_adj['end_use_energy_compiled'] = enduse_adj['adj_energy'].fillna(enduse_adj['energy'])

# %%
# Clean up df
enduse_adj = enduse_adj.copy().drop(columns = ['intensity', 'value', 'energy', 'adj_energy'])

# %%
enduse_adj.to_csv(output_dir_csv + 'adjusted_end_use_compiled.csv', index = False)

# column headings
# end_use	economy	year	sub2sectors	end_use_energy_compiled

# %%
# Create fig
fig = px.line(enduse_adj, x='year', y='end_use_energy_compiled', color='end_use_sector', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'energy_adj_enduses.html')

fig = px.area(enduse_adj, x='year', y='end_use_energy_compiled', color='end_use_sector', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'energy_adj_enduses_area.html')

# %%
# created figures for each economy

# adjusted_end_use_compiled.csv


output_dir_fig_line = config.root_dir + '/plotting_output/a3_projection_adjustment/by_economy/line_plots/'
if not os.path.exists(output_dir_fig_line):
    os.makedirs(output_dir_fig_line)

output_dir_fig_area = config.root_dir + '/plotting_output/a3_projection_adjustment/by_economy/area_plots/'
if not os.path.exists(output_dir_fig_area):
    os.makedirs(output_dir_fig_area)

data_res = enduse_adj[enduse_adj['sub2sectors'] == '16_01_02_residential']
data_srv = enduse_adj[enduse_adj['sub2sectors'] == '16_01_01_commercial_and_public_services']

for economy in economy_list['economy_code']:
    plot_res = data_res[data_res['economy'] == economy]

    # fig = px.area(plot_res, x='year', y='end_use_energy_compiled', color='end_use_sector')
    # fig.update_yaxes(matches=None, showticklabels=True)
    # fig.write_html(output_dir_fig_area + economy + '_16_01_02_residential.html')

    fig = px.line(plot_res, x='year', y='end_use_energy_compiled', color='end_use_sector')
    fig.update_yaxes(matches=None, showticklabels=True)
    fig.write_html(output_dir_fig_line + economy + '_16_01_02_residential.html')

for economy in economy_list['economy_code']:
    plot_srv = data_srv[data_srv['economy'] == economy]

    # fig = px.area(plot_srv, x='year', y='end_use_energy_compiled', color='end_use_sector')
    # fig.update_yaxes(matches=None, showticklabels=True)
    # fig.write_html(output_dir_fig_area + economy + '_16_01_01_commercial_and_public_services.html')

    fig = px.line(plot_srv, x='year', y='end_use_energy_compiled', color='end_use_sector')
    fig.update_yaxes(matches=None, showticklabels=True)
    fig.write_html(output_dir_fig_line + economy + '_16_01_01_commercial_and_public_services.html')


# %%
