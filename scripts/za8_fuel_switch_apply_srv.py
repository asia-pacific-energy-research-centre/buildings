#%%
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px


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

# data prep
df = pd.read_csv(config.root_dir + '/output_data/a5.5_attempting_again/end_use_adjusted.csv')
df.drop(columns=['fuel_amount', 'fuel_ratio'], inplace=True)
df.rename(columns={'end_use_fuel': 'fuel_amount'}, inplace=True)

# grouped_df = df.groupby(['economy', 'sub2sectors', 'fuel', 'year']).agg({'fuel_amount': 'sum'}).reset_index()
# sum_df = df.groupby(['economy', 'sub2sectors', 'year'], as_index=False)['fuel_amount'].sum()
# %%
# Merge summed_df onto grouped_df
# merged_df = pd.merge(grouped_df, sum_df, on=['economy', 'sub2sectors', 'year'], how='left', suffixes=('', '_total'))

# %%
from za6_fuel_switch_function import switch_fuel_with_trajectory

# %%
############################################ COMMERCIAL AND SERVICES ######################################################################
df_srv = df[df['sub2sectors'] != '16_01_02_residential']
# %%
############################################ AUSTRALIA ######################################################################
############################################ LIGHTING ######################################################################
# %%
srv_copy = df_srv.copy()
# Call the modified function for a specific economy on the copied DataFrame

df_1 = switch_fuel_with_trajectory(srv_copy, economy='01_AUS', end_use='lighting', fuel_1='electricity', fuel_2='gas', 
                                          start_year=2023, end_year=2030, efficiency_factor=0.8,
                                          proportion_to_switch=0.5, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)
df_plot = df_1.copy()
df_plot = df_plot[df_plot['fuel_amount'] != 0]
fig = px.area(df_plot, x='year', y='fuel_amount', color='fuel')
fig.show()

# %%
srv_copy = df_1.copy()

df_2 = switch_fuel_with_trajectory(srv_copy, economy='01_AUS', end_use='lighting', fuel_1='electricity', fuel_2='gas', 
                                          start_year=2035, end_year=2060, efficiency_factor=0.9,
                                          proportion_to_switch=0.5, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)
df_plot = df_2.copy()
df_plot = df_plot[df_plot['fuel_amount'] != 0]
fig = px.area(df_plot, x='year', y='fuel_amount', color='fuel')
fig.show()

df_final_lighting = df_2.copy() # to be updated as needed


# %%
df_aus = pd.concat([df_final_lighting], ignore_index=True)



# %%
# df_final = df_gas_to_elec.copy() # to be updated as needed

# output_dir_csv = config.root_dir + '/output_data/a7_fuel_switch/srv/'
# if not os.path.exists(output_dir_csv):
#     os.makedirs(output_dir_csv)
# # output dir will have aus 
# df_final.to_csv(output_dir_csv + '01_AUS_srv_lighting.csv', index=False)
# %%

output_dir_csv = config.root_dir + '/output_data/a7_fuel_switch/srv/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

df_combined_adjustments = pd.concat([df_aus], ignore_index=True)

# %%
old_data = df_srv.copy()

merged_df = pd.merge(old_data, df_combined_adjustments[['economy', 'sub2sectors', 'end_use', 'fuel', 'year', 'fuel_amount']],  
    on=['economy', 'sub2sectors', 'end_use', 'fuel', 'year'],
    how='left',
)

merged_df['fuel_amount'] = merged_df['fuel_amount_y'].combine_first(merged_df['fuel_amount_x'])
merged_df = merged_df.drop(columns=['fuel_amount_x', 'fuel_amount_y'])
sorted = merged_df.sort_values(by=['economy', 'sub2sectors', 'fuel', 'year']).reset_index(drop=True)

# %%

sorted.to_csv(output_dir_csv + 'merged_srv_adjusted_fuel.csv', index=False)
# %%
