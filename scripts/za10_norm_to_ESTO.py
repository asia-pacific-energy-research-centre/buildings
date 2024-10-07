# to isolate an economy
# then match the fuel to the fuel from esto 
# ESTO data is grouped by fuel for each year
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

# %%
# import economy data
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')


# %%
esto_energy_date_id = utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy'), 'model_df_wide_') 
esto_energy = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', f'model_df_wide_{esto_energy_date_id}.csv'))
esto_energy = esto_energy[(esto_energy['sectors'] == '16_other_sector') & 
                          (esto_energy['sub1sectors'] == '16_01_buildings') &
                          (esto_energy['sub2sectors'] != 'x') &
                          (esto_energy['is_subtotal'] == False)
                          ] 
# & is subtotal = false to get out the subtotal columns #######################################################  
esto_energy.drop(columns=['subfuels', 'sub1sectors', 'sub3sectors', 'sub4sectors'], inplace=True)

# referemce
# esto_energy_ref = esto_energy[esto_energy['scenarios'] == 'reference']

# target
esto_energy_tgt = esto_energy[esto_energy['scenarios'] == 'target']                        
                          
year_columns = esto_energy_tgt.loc[:, '1980':'2070'].columns  # Adjust the start and end year if needed

melted_df = pd.melt(esto_energy_tgt, 
                    id_vars=['scenarios', 'economy', 'sub2sectors', 'fuels'], 
                    value_vars=year_columns, 
                    var_name='year', 
                    value_name='fuel_amount')
melted_df['year'] = melted_df['year'].astype(int)
# melted_df = melted_df[melted_df['year'] >= 2000]

# %%
melted_df = melted_df[(melted_df['fuels'] != '19_total') &
                      (melted_df['fuels'] != '20_total_renewables') &
                      (melted_df['fuels'] != '21_modern_renewables')                     
                      ]

sum_melt_df = melted_df.groupby(['economy', 'sub2sectors', 'fuels', 'year'], as_index=False)['fuel_amount'].sum()
# %%
sum_melt_df['fuel_category'] = sum_melt_df['fuels'].map({
    '15_solid_biomass': 'biofuels',
    '01_coal': 'coal',
    '02_coal_products': 'coal',
    '03_peat': 'coal',
    '04_peat_products': 'coal',
    '17_electricity': 'electricity',
    '08_gas': 'gas',
    '18_heat': 'heat',
    '06_crude_oil_and_ngl': 'oil',
    '07_petroleum_products': 'oil',
    '16_others': 'other',
    '12_solar': 'solar_thermal'
})

esto_fuel_type_totals = sum_melt_df.groupby(['economy', 'year', 'sub2sectors', 'fuel_category'], as_index=False)['fuel_amount'].sum()

# %%
# merge the total for each fuel type onto the esto data broken down further
esto_ratio = sum_melt_df.merge(esto_fuel_type_totals, on=['economy', 'year', 'sub2sectors', 'fuel_category'], 
                            how='left', suffixes=('', '_summed'))

esto_ratio['ratio'] = esto_ratio['fuel_amount'] / esto_ratio['fuel_amount_summed']

# %%
esto_ratio_sorted = esto_ratio.sort_values(by=['year', 'economy', 'sub2sectors', 'fuels'])

# esto_ratio_sorted.drop(columns=['fuel_amount', 'fuel_amount_summed'], inplace=True)
esto_ratio_sorted = esto_ratio_sorted[esto_ratio_sorted['year'] >= 2000]


# %%
fuel_to_norm = pd.read_csv(config.root_dir + '/output_data/a5_end_use_fuel_split/fuel_split_end_use.csv')
fuel_to_norm.drop(columns=['normalized_ratio', 'end_use_energy_compiled'], inplace=True)

model_fuels = fuel_to_norm.groupby(['economy', 'sub2sectors', 'year', 'fuel'], as_index=False)['fuel_amount'].sum()
model_fuels.rename(columns={'fuel': 'fuel_category'}, inplace=True)

# %%
model_fuels_2021 = model_fuels[model_fuels['year'] == 2021]
esto_ratio_sorted_2021 = esto_ratio_sorted[esto_ratio_sorted['year'] == 2021]



esto_model_2021 = esto_ratio_sorted_2021.merge(model_fuels_2021, on=['economy', 'year', 'sub2sectors', 'fuel_category'], 
                            how='left', suffixes=('', '_summed'))




# %%
#  '01_coal' 
#  '02_coal_products' 
#  '03_peat'                    # RUSSIA
#  '04_peat_products'           # RUSSIA
#  '06_crude_oil_and_ngl'
#  '07_petroleum_products' 
#  '08_gas' 
#  '11_geothermal' 
#  '12_solar'
#  '15_solid_biomass' 
#  '16_others' 
#  '17_electricity' 
#  '18_heat' 
# 



# %%
# df_grouped_res # from projections
# df_grouped_srv # from projections

# melted_df_res #esto
# melted_df_srv #esto

# %%
# fuel_mapping = {
#     'biofuels': ['15_solid_biomass'],
#     'coal': ['01_coal', '02_coal_products', '03_peat', '04_peat_products'],
#     'electricity': ['17_electricity'],
#     'gas': ['08_gas'],
#     'heat': ['18_heat'],
#     'oil': ['06_crude_oil_and_ngl', '07_petroleum_products'],
#     'other': ['16_others'],
#     'solar_thermal': ['12_solar']
# }
 
# # Define the ratios for coal categories (e.g., 4:3:2:1)
# coal_ratios = {
#     '01_coal': 4,
#     '02_coal_products': 3,
#     '03_peat': 2,
#     '04_peat_products': 1
# }

# %%
fuel_to_norm = pd.read_csv(config.root_dir + '/output_data/a5_end_use_fuel_split/fuel_split_end_use.csv')
fuel_to_norm.drop(columns=['normalized_ratio', 'end_use_energy_compiled'], inplace=True)

# sum electricity total in each year for each subsector
# grouped_df = df.groupby(['economy', 'sub2sectors', 'fuels', 'year'], as_index=False)['fuel_amount'].sum()
tonorm_sum = fuel_to_norm.groupby(['economy', 'sub2sectors', 'fuel', 'year'], as_index=False)['fuel_amount'].sum()

# %%
merged_df = fuel_to_norm.merge(tonorm_sum[['economy', 'sub2sectors', 'fuel', 'year', 'fuel_amount']],
                               on=['economy', 'sub2sectors', 'fuel', 'year'], 
                               how='left',
                               suffixes=('_orig', '_tonorm'))

# this is the ratio of how much each end_use comprises the fuel total for each year
merged_df['ratio'] = merged_df['fuel_amount_orig'] / merged_df['fuel_amount_tonorm']

# attach the summed fuel amount to the fuel to norm df, then calculate the ratio of lighting/elec is making up the total elec values
#  normalize the total elec value to esto
# taek ratio to multiply through total fuel to resplit into end use for the fuel switch


# %%
# esto fuel ratios now 
# melted_df['fuel_category'] = melted_df['fuels'].map({
#     '15_solid_biomass': 'biofuels',
#     '01_coal': 'coal',
#     '02_coal_products': 'coal',
#     '03_peat': 'coal',
#     '04_peat_products': 'coal',
#     '17_electricity': 'electricity',
#     '08_gas': 'gas',
#     '18_heat': 'heat',
#     '06_crude_oil_and_ngl': 'oil',
#     '07_petroleum_products': 'oil',
#     '16_others': 'other',
#     '12_solar': 'solar_thermal'
# })

# grouped_df3 = melted_df.groupby(['economy', 'year', 'sub2sectors', 'fuel_category'], as_index=False)['fuel_amount'].sum()
# %%
merged_df = fuel_to_norm.merge(tonorm_sum[['economy', 'sub2sectors', 'fuel', 'year', 'fuel_amount']],
                               on=['economy', 'sub2sectors', 'fuel', 'year'], 
                               how='left',
                               suffixes=('_orig', '_tonorm'))