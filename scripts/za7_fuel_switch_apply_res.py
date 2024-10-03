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
df = pd.read_csv(config.root_dir + '/output_data/a5_end_use_fuel_split/fuel_split_end_use.csv')
df.drop(columns=['ratio', 'normalized_ratio', 'end_use_energy_compiled'], inplace=True)

# %%
# grouped_df = df.groupby(['economy', 'sub2sectors', 'fuel', 'year']).agg({'fuel_amount': 'sum'}).reset_index()
# sum_df = df.groupby(['economy', 'sub2sectors', 'year'], as_index=False)['fuel_amount'].sum()
# %%
# Merge summed_df onto grouped_df
# merged_df = pd.merge(grouped_df, sum_df, on=['economy', 'sub2sectors', 'year'], how='left', suffixes=('', '_total'))

# %%
from za6_fuel_switch_function import switch_fuel_with_trajectory

# %%
############################################ RESIDENTIAL ######################################################################
df_res =df[df['sub2sectors'] != '16_01_01_commercial_and_public_services']

# %%
############################################ AUSTRALIA ######################################################################
############################################ COOKING ######################################################################
# %%
# df_res_cooking_aus =df_res[(df_res['end_use'] == 'cooking') & (df_res['economy'] == '01_AUS')]

# %%
res_copy = df_res.copy()
# Call the modified function for a specific economy on the copied DataFrame

df_bio_to_elec = switch_fuel_with_trajectory(res_copy, economy='01_AUS', end_use='cooking', fuel_1='biofuels', fuel_2='electricity', 
                                          start_year=2000, end_year=2003, efficiency_factor=0.8,
                                          proportion_to_switch=0.5, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)
# %%
res_copy = df_bio_to_elec

df_gas_to_elec = switch_fuel_with_trajectory(res_copy, economy='01_AUS', end_use='cooking', fuel_1='gas', fuel_2='electricity', 
                                          start_year=2000, end_year=2003, efficiency_factor=0.9,
                                          proportion_to_switch=0.5, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)

# %%
df_final_cooking = df_gas_to_elec.copy() # to be updated as needed

output_dir_csv = config.root_dir + '/output_data/a7_fuel_switch/res/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)
# output dir will have aus 
df_final_cooking.to_csv(output_dir_csv + '01_AUS_res_cooking.csv', index=False)

# %%
# Consildate refined tracjectories
# %%
############################################ AUSTRALIA ######################################################################
############################################ LIGHTING ######################################################################