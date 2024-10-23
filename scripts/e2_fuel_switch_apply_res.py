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
# df = pd.read_csv(config.root_dir + '/output_data/d2_normalization/end_use_adjusted.csv')
# df.drop(columns=['fuel_amount', 'fuel_ratio_normalized'], inplace=True)
# df.rename(columns={'end_use_fuel': 'fuel_amount'}, inplace=True)

df = pd.read_csv(config.root_dir + '/output_data/d4_split_to_end_use/subfuel_end_use.csv')

# %%
# grouped_df = df.groupby(['economy', 'sub2sectors', 'fuel', 'year']).agg({'fuel_amount': 'sum'}).reset_index()
# sum_df = df.groupby(['economy', 'sub2sectors', 'year'], as_index=False)['fuel_amount'].sum()
# %%
# Merge summed_df onto grouped_df
# merged_df = pd.merge(grouped_df, sum_df, on=['economy', 'sub2sectors', 'year'], how='left', suffixes=('', '_total'))

# %%
from e1_fuel_switch_function import switch_fuel_with_trajectory

# %%
############################################ RESIDENTIAL ######################################################################
df_res =df[df['sub2sectors'] != '16_01_01_commercial_and_public_services']

# '01_coal: 01_x_thermal_coal' 
# '01_coal: 01_05_lignite'
# '02_coal_products: x' 
# '03_peat: x'
# '04_peat_products: x' 

# '07_petroleum_products: 07_08_fuel_oil' 
# '07_petroleum_products: 07_01_motor_gasoline'
# '07_petroleum_products: 07_09_lpg'
# '07_petroleum_products: 07_06_kerosene'
# '07_petroleum_products: 07_07_gas_diesel_oil'
# '08_gas: 08_03_gas_works_gas' 
# '08_gas: 08_01_natural_gas' 

# '12_solar: 12_x_other_solar'

# '15_solid_biomass: 15_01_fuelwood_and_woodwaste' 
# '15_solid_biomass: 15_02_bagasse']
# '15_solid_biomass: 15_03_charcoal'
# '15_solid_biomass: 15_05_other_biomass' 

# '16_others: 16_01_biogas'
# '16_others: 16_05_biogasoline'
# '16_others: 16_06_biodiesel'

# '17_electricity: x'

# '18_heat: x'

# %%
############################################ AUSTRALIA ############################################################################################################################
############################################ COOKING ######################################################################
# %%
# df_res_cooking_aus =df_res[(df_res['end_use'] == 'cooking') & (df_res['economy'] == '01_AUS')]

# # %%
# res_copy = df_res.copy()
# # Call the modified function for a specific economy on the copied DataFrame

# df_bio_to_elec = switch_fuel_with_trajectory(res_copy, economy='01_AUS', end_use='cooking', fuel_1='biofuels', fuel_2='electricity', 
#                                           start_year=2000, end_year=2003, efficiency_factor=0.8,
#                                           proportion_to_switch=0.5, shape='increase', 
#                                            apex_mag=1.5, apex_loc=1)
# # %%
# res_copy = df_bio_to_elec

# df_gas_to_elec = switch_fuel_with_trajectory(res_copy, economy='01_AUS', end_use='cooking', fuel_1='gas', fuel_2='electricity', 
#                                           start_year=2000, end_year=2003, efficiency_factor=0.9,
#                                           proportion_to_switch=0.5, shape='increase', 
#                                            apex_mag=1.5, apex_loc=1)

# # %%
# df_final_cooking = df_gas_to_elec.copy() # to be updated as needed

# output_dir_csv = config.root_dir + '/output_data/a7_fuel_switch/res/'
# if not os.path.exists(output_dir_csv):
#     os.makedirs(output_dir_csv)
# # output dir will have aus 
# df_final_cooking.to_csv(output_dir_csv + '01_AUS_res_cooking.csv', index=False)

# %%
# Consildate refined tracjectories

# %%
############################################ LIGHTING ######################################################################
# tbd



# %%
############################################ WATER HEATING ######################################################################
res_copy = df_res.copy()
# Call the modified function for a specific economy on the copied DataFrame

df_1 = switch_fuel_with_trajectory(res_copy, economy='01_AUS', end_use='water_heating', fuel_1='08_gas: 08_01_natural_gas' , fuel_2='17_electricity: x', 
                                          start_year=2021, end_year=2070, efficiency_factor=0.7,
                                          proportion_to_switch=0.2, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)

df_plot = df_1.copy()
df_plot = df_plot[df_plot['subfuel_amount'] != 0]
fig = px.area(df_plot, x='year', y='subfuel_amount', color='name')
fig.show()

df_final_water_heating = df_1.copy() # to be updated as needed
# %%
# df_aus = pd.concat([df_final_water_heating], ignore_index=True) dummy concat (since only on). mak this, then try to concat with cda, then merge etc. then plot and make sure it worked fine
df_aus = df_final_water_heating


# %%
############################################ CANADA ##########################################################################################################################################
############################################ SPACE_HEATING ######################################################################
res_copy = df_res.copy()
# Call the modified function for a specific economy on the copied DataFrame

df_1 = switch_fuel_with_trajectory(res_copy, economy='03_CDA', end_use='space_heating', fuel_1='08_gas: 08_01_natural_gas', fuel_2='17_electricity: x', 
                                          start_year=2022, end_year=2070, efficiency_factor=0.4,
                                          proportion_to_switch=0.75, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)

df_plot = df_1.copy()
df_plot = df_plot[df_plot['subfuel_amount'] != 0]
fig = px.area(df_plot, x='year', y='subfuel_amount', color='name')
fig.show()

df_final_space_heating = df_1.copy() # to be updated as needed


# %%
############################################ WATER HEATING ######################################################################
res_copy = df_res.copy()
# Call the modified function for a specific economy on the copied DataFrame

df_1 = switch_fuel_with_trajectory(res_copy, economy='03_CDA', end_use='water_heating', fuel_1='08_gas: 08_01_natural_gas', fuel_2='17_electricity: x', 
                                          start_year=2022, end_year=2070, efficiency_factor=0.4,
                                          proportion_to_switch=0.75, shape='increase', 
                                           apex_mag=1.5, apex_loc=1)

df_plot = df_1.copy()
df_plot = df_plot[df_plot['subfuel_amount'] != 0]
fig = px.area(df_plot, x='year', y='subfuel_amount', color='name')
fig.show()

df_final_water_heating = df_1.copy() # to be updated as needed

# %%
df_cda = pd.concat([df_final_space_heating, df_final_water_heating], ignore_index=True)






# %%
# can probably concatenate all the adjusted ones here?
# then can do an import and merge, export to res_copy (the merge)


output_dir_csv = config.root_dir + '/output_data/e2_fuel_switch_apply/res/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

df_combined_adjustments = pd.concat([df_cda, df_aus], ignore_index=True)
# economy	sub2sectors	fuels	subfuels	year	fuel_amount	name	fuel	end_use	fuel_ratio_normalized	subfuel_amount
# %%
old_data = df_res.copy()
# %%
merged_df = pd.merge(old_data, df_combined_adjustments[['economy', 'sub2sectors', 'end_use', 'fuel', 'year', 'subfuel_amount']],  
    on=['economy', 'sub2sectors', 'end_use', 'fuel', 'year'],
    how='left',
)
# %%
merged_df['subfuel_amount'] = merged_df['subfuel_amount_y'].combine_first(merged_df['subfuel_amount_x'])
merged_df = merged_df.drop(columns=['subfuel_amount_x', 'subfuel_amount_y'])
sorted = merged_df.sort_values(by=['economy', 'sub2sectors', 'fuel', 'year']).reset_index(drop=True)



# %%

sorted.to_csv(output_dir_csv + 'merged_res_adjusted_fuel.csv', index=False)

# %%
