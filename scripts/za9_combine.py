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
sectors = ['srv', 'res']

# %%
# Consildate refined tracjectories

traj_overwrite_df = pd.DataFrame()

output_dir_csv = config.root_dir + '/output_data/a9_conslidated_data/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

for sector in sectors:
    # Use the sector name in the file path
    filenames = glob.glob(config.root_dir + f'/output_data/a7_fuel_switch/{sector}/*.csv')
    for i in filenames:
        temp_df = pd.read_csv(i)
        traj_overwrite_df = pd.concat([traj_overwrite_df, temp_df]).copy()
    
    # # Loop through the matched filenames and process each file
    # for filename in filenames:
    #     # Example: print the filename or process the file
    #     print(f"Processing file: {filename}")

traj_overwrite_df.to_csv(output_dir_csv + 'consolidated_adjusted_fuel.csv', index=False)
# economy	sub2sectors	end_use	fuel	year	fuel_amount
# need to keep these ones
# %%
# Merge the adjusted data onto the original data to get df with all economies and fuels even if not updated
df = pd.read_csv(config.root_dir + '/output_data/a5_end_use_fuel_split/fuel_split_end_use.csv')
df.drop(columns=['normalized_ratio', 'end_use_energy_compiled'], inplace=True)
# economy	sub2sectors	end_use	fuel	year	fuel_amount

# %%
df = df.copy()
traj_overwrite_df = traj_overwrite_df.copy()

df_merged = pd.merge(df, traj_overwrite_df[['economy', 'sub2sectors', 'end_use', 'fuel', 'year', 'fuel_amount']],
                     on=['economy', 'sub2sectors', 'end_use', 'fuel', 'year'],
                     how='left',  # Use 'left' to keep all rows from df and fill from traj_overwrite_df
                     suffixes=('', '_overwrite'))  # Distinguish between columns
# If you want to overwrite the fuel_amount from traj_overwrite_df, where it exists:
df_merged['fuel_amount'] = df_merged['fuel_amount_overwrite'].combine_first(df_merged['fuel_amount'])
# Drop the temporary 'fuel_amount_overwrite' column
df_merged.drop(columns=['fuel_amount_overwrite'], inplace=True)



# %%
# clean up df, we don't need end use anymore because that analysis was already confirmed
# agg fuels by year, subsector, economy

# total amount of each type of fuel for each economy, subsector and year
df_grouped1 = df_merged.groupby(['economy', 'sub2sectors', 'fuel', 'year'], as_index=False)['fuel_amount'].sum()

# total amount of fuel for each subsector, year, and economy (ie not separated by fuel at all, 19_total equivalent)
df_grouped2 = df_merged.groupby(['economy', 'sub2sectors', 'year'], as_index=False)['fuel_amount'].sum()

# total amount of fuel not separated by subsector, for each year and economy
df_grouped3 = df_merged.groupby(['economy', 'fuel', 'year'], as_index=False)['fuel_amount'].sum()

# %%
df_grouped2.to_csv(output_dir_csv + 'total_fuel_by_subsector.csv', index=False)
df_grouped3.to_csv(output_dir_csv + 'total_fuel_by_fuel_type.csv', index=False)

df_grouped1.to_csv(output_dir_csv + 'consolidated_all_fuel.csv', index=False)


# %%
output_dir_fig = config.root_dir + '/plotting_output/a9_conslidated_data/'
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
fig = px.line(df_grouped3, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_line.html')

fig = px.area(df_grouped3, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_area.html')
# %%
# Create fig sectoral totals of fuels
df_grouped1_res = df_grouped1[df_grouped1['sub2sectors'] == '16_01_02_residential']
df_grouped1_srv = df_grouped1[df_grouped1['sub2sectors'] == '16_01_01_commercial_and_public_services']

fig = px.area(df_grouped1_res, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_area_res.html')

fig = px.area(df_grouped1_srv, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir_fig + 'fuel_totals_area_srv.html')
# %%
df_grouped1_res.to_csv(output_dir_csv + 'df_grouped_res.csv', index=False)
df_grouped1_srv.to_csv(output_dir_csv + 'df_grouped_srv.csv', index=False)
# %%
