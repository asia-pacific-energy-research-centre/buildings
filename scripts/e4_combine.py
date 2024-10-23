#%%
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px
import glob

####
#self made helper functions
import x3_utility_functions as x3_utility_functions
import x1_configurations as x1_configurations
root_dir =re.split('buildings', os.getcwd())[0]+'/buildings'
config = x1_configurations.Config(root_dir)
###
# %%
# import economy data
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
sectors = ['srv', 'res']

# %%
# Consildate refined tracjectories

traj_overwrite_df = pd.DataFrame()

output_dir_csv = config.root_dir + '/output_data/e4_combine/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

# srv = pd.read_csv(config.root_dir + '/output_data/a7_fuel_switch/srv/merged_srv_adjusted_fuel.csv')
# res = pd.read_csv(config.root_dir + '/output_data/a7_fuel_switch/res/merged_res_adjusted_fuel.csv')

# test = pd.concat([srv, res])

# %%

for sector in sectors:
    # Use the sector name in the file path
    filenames = glob.glob(config.root_dir + f'/output_data/e2_fuel_switch_apply/{sector}/*.csv')
    for i in filenames:
        temp_df = pd.read_csv(i)
        traj_overwrite_df = pd.concat([traj_overwrite_df, temp_df]).copy()
    
    # # Loop through the matched filenames and process each file
    # for filename in filenames:
    #     # Example: print the filename or process the file
    #     print(f"Processing file: {filename}")

traj_overwrite_df.to_csv(output_dir_csv + 'consolidated_adjusted_fuel.csv', index=False)
# %%
# group traj overwrite by end use etc to match the df for merge

traj_overwrite_df = traj_overwrite_df.copy()
traj_overwrite_df = traj_overwrite_df.groupby(['economy', 'sub2sectors', 'name', 'year'], as_index=False)['subfuel_amount'].sum()

traj_overwrite_df[['fuels', 'subfuels']] = traj_overwrite_df['name'].str.split(': ', expand=True)
traj_overwrite_df.rename(columns={'subfuel_amount': 'fuel_amount'}, inplace=True)
# %%
traj_overwrite_df = traj_overwrite_df[['economy', 'sub2sectors', 'fuels', 'subfuels', 'year', 'fuel_amount', 'name']]

# economy	sub2sectors	end_use	fuel	year	fuel_amount
# need to keep these ones
# %%
# Merge the adjusted data onto the original data to get df with all economies and fuels even if not updated
df = pd.read_csv(config.root_dir + '/output_data/d3_subfuels_split/concat_subfuels.csv')
# df.drop(columns=['normalized_ratio', 'end_use_energy_compiled'], inplace=True)
# economy	sub2sectors	end_use	fuel	year	fuel_amount

df = df[df['year'] <2022]
# economy	sub2sectors	fuels	subfuels	year	fuel_amount	name

# res = pd.read_csv(config.root_dir + '/output_data/a7_fuel_switch/res/merged_residential_adjusted_fuel.csv')
# srv = pd.read_csv(config.root_dir + '/output_data/a7_fuel_switch/srv/merged_srv_adjusted_fuel.csv')

# test_rest = pd.read_csv(config.root_dir + '/output_data/a7_fuel_switch/res/merged_residential_adjusted_fuel.csv')

# %%
df = df.copy()
traj_overwrite_df = traj_overwrite_df.copy()

combined_df = pd.concat([df, traj_overwrite_df], ignore_index=True)
sorted_combined = combined_df.sort_values(by=['economy', 'sub2sectors', 'fuels', 'year']).reset_index(drop=True)

#  dont need to merge anything anymore, just need them concatenated

# df_merged = pd.merge(df, traj_overwrite_df[['economy', 'sub2sectors', 'fuel', 'year', 'fuel_amount']],
#                      on=['economy', 'sub2sectors', 'fuel', 'year'],
#                      how='left',  # Use 'left' to keep all rows from df and fill from traj_overwrite_df
#                      suffixes=('', '_overwrite'))  # Distinguish between columns
# # If you want to overwrite the fuel_amount from traj_overwrite_df, where it exists:
# df_merged['fuel_amount'] = df_merged['fuel_amount_overwrite'].combine_first(df_merged['fuel_amount'])
# # Drop the temporary 'fuel_amount_overwrite' column
# df_merged.drop(columns=['fuel_amount_overwrite'], inplace=True)




# %%
# clean up df, we don't need end use anymore because that analysis was already confirmed
# agg fuels by year, subsector, economy

# total amount of each type of fuel for each economy, subsector and year
df_grouped1 = sorted_combined.copy()
# 	economy	sub2sectors	fuels	subfuels	year	fuel_amount	name
# 0	01_AUS	16_01_01_commercial_and_public_services	01_coal	01_x_thermal_coal	1980	4.664690	01_coal: 01_x_thermal_coal
# 1	01_AUS	16_01_01_commercial_and_public_services	01_coal	01_x_thermal_coal	1981	4.281405	01_coal: 01_x_thermal_coal


# total amount of fuel for each subsector, year, and economy (ie not separated by fuel at all, 19_total equivalent)
df_grouped2 = sorted_combined.groupby(['economy', 'sub2sectors', 'year'], as_index=False)['fuel_amount'].sum()
# economy	sub2sectors	year	fuel_amount


# total amount of fuel not separated by subsector, for each year and economy
df_grouped3 = sorted_combined.groupby(['economy', 'fuels', 'year'], as_index=False)['fuel_amount'].sum()
# economy	fuels	year	fuel_amount


# %%
df_grouped2.to_csv(output_dir_csv + 'total_fuel_by_subsector.csv', index=False)
df_grouped3.to_csv(output_dir_csv + 'total_fuel_by_fuel_type.csv', index=False)

df_grouped1.to_csv(output_dir_csv + 'consolidated_all_fuel.csv', index=False)


# %%
output_dir_fig = config.root_dir + '/plotting_output/e4_combine/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

# %%
# Create fig sectoral totals
fig = px.line(df_grouped2, x='year', y='fuel_amount', color='sub2sectors', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'sector_totals_line.html')

fig = px.area(df_grouped2, x='year', y='fuel_amount', color='sub2sectors', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'sector_totals_area.html')
# %%
# Create fig sectoral totals
fig = px.line(df_grouped3, x='year', y='fuel_amount', color='fuels', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_line.html')

fig = px.area(df_grouped3, x='year', y='fuel_amount', color='fuels', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_area.html')
# %%
# Create fig sectoral totals of fuels
df_grouped1_res = df_grouped1[df_grouped1['sub2sectors'] == '16_01_02_residential']
df_grouped1_srv = df_grouped1[df_grouped1['sub2sectors'] == '16_01_01_commercial_and_public_services']

fig = px.area(df_grouped1_res, x='year', y='fuel_amount', color='name', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_area_res.html')

fig = px.area(df_grouped1_srv, x='year', y='fuel_amount', color='name', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_area_srv.html')
# %%
df_grouped1_res.to_csv(output_dir_csv + 'df_grouped_res.csv', index=False)
df_grouped1_srv.to_csv(output_dir_csv + 'df_grouped_srv.csv', index=False)
# %%
sorted_combined.to_csv(output_dir_csv + 'final_sorted_combined.csv', index=False)

# %%
