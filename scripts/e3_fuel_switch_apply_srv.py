#%%
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px


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

# data prep
df = pd.read_csv(config.root_dir + '/output_data/d4_split_to_end_use/subfuel_end_use.csv')

# grouped_df = df.groupby(['economy', 'sub2sectors', 'fuel', 'year']).agg({'fuel_amount': 'sum'}).reset_index()
# sum_df = df.groupby(['economy', 'sub2sectors', 'year'], as_index=False)['fuel_amount'].sum()
# %%
# Merge summed_df onto grouped_df
# merged_df = pd.merge(grouped_df, sum_df, on=['economy', 'sub2sectors', 'year'], how='left', suffixes=('', '_total'))

# %%
from e1_fuel_switch_function import switch_fuel_with_trajectory

# %%
############################################ COMMERCIAL AND SERVICES ######################################################################
df_srv = df[df['sub2sectors'] != '16_01_02_residential']
# %%
############################################ AUSTRALIA ######################################################################
############################################ LIGHTING ######################################################################
# %%
srv_copy = df_srv.copy()
# Call the modified function for a specific economy on the copied DataFrame

df_1 = switch_fuel_with_trajectory(srv_copy, economy='01_AUS', end_use='lighting', fuel_1='17_electricity: x', fuel_2='08_gas: 08_01_natural_gas', 
                                          start_year=2023, end_year=2030, efficiency_factor=0.8,
                                          proportion_to_switch=0.5, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)
df_plot = df_1.copy()
df_plot = df_plot[df_plot['subfuel_amount'] != 0]
fig = px.area(df_plot, x='year', y='subfuel_amount', color='name')
fig.show()

# %%
srv_copy = df_1.copy()

df_2 = switch_fuel_with_trajectory(srv_copy, economy='01_AUS', end_use='lighting', fuel_1='17_electricity: x', fuel_2='08_gas: 08_01_natural_gas', 
                                          start_year=2035, end_year=2060, efficiency_factor=0.9,
                                          proportion_to_switch=0.5, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)
df_plot = df_2.copy()
df_plot = df_plot[df_plot['subfuel_amount'] != 0]
fig = px.area(df_plot, x='year', y='subfuel_amount', color='name')
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

output_dir_csv = config.root_dir + '/output_data/e2_fuel_switch_apply/srv/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

df_combined_adjustments = pd.concat([df_aus], ignore_index=True)

# %%
old_data = df_srv.copy()

merged_df = pd.merge(old_data, df_combined_adjustments[['economy', 'sub2sectors', 'end_use', 'fuel', 'year', 'subfuel_amount']],  
    on=['economy', 'sub2sectors', 'end_use', 'fuel', 'year'],
    how='left',
)

merged_df['subfuel_amount'] = merged_df['subfuel_amount_y'].combine_first(merged_df['subfuel_amount_x'])
merged_df = merged_df.drop(columns=['subfuel_amount_x', 'subfuel_amount_y'])
sorted = merged_df.sort_values(by=['economy', 'sub2sectors', 'fuel', 'year']).reset_index(drop=True)


# %%

sorted.to_csv(output_dir_csv + 'merged_srv_adjusted_fuel.csv', index=False)
# %%
