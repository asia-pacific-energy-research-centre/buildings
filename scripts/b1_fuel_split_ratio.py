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
####

#NOTE THAT WE WILL MOVE THESE IMPORTS AND SO ON ONCE WE HAVE THE FINAL STRUCTURE OF THE PROJECT
#import apec macro data
macro_date_id = utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', 'macro'), 'APEC_GDP_data_')
macro = pd.read_csv(os.path.join(config.root_dir, 'input_data', 'macro', f'APEC_GDP_data_{macro_date_id}.csv'))
#reaplce 17_SIN with SGP
macro['economy_code'] = macro['economy_code'].replace('17_SIN','17_SGP')
#reaplce 15_RP with PHL
macro['economy_code'] = macro['economy_code'].replace('15_RP','15_PHL')

eei = pd.read_csv(os.path.join(config.root_dir, 'input_data','eei', 'buildings_final.csv'))

esto_energy_date_id = utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy'), 'model_df_wide_') 

esto_energy = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', f'model_df_wide_{esto_energy_date_id}.csv'))
# %%
iea_energy_totals_by_fuel = eei.loc[(eei['measure'] == 'energy') & (eei['end_use'] == 'total') & (eei['year'] == 2021) & (eei['economy'] != 'non_apec_iea')].copy()

#now lets scale the data to have the total energy equal the total energy for buildings in esto_energy:
#extract the data from esto_energy for the following:
# sectors	sub1sectors	sub2sectors
# 16_other_sector	16_01_buildings	16_01_01_commercial_and_public_services
# 16_other_sector	16_01_buildings	16_01_02_residential

# %%
esto_energy_buildings_fuelsplit = esto_energy.loc[(esto_energy['sectors']=='16_other_sector') & (esto_energy['sub1sectors']=='16_01_buildings') & (esto_energy['sub2sectors'].isin(['16_01_01_commercial_and_public_services','16_01_02_residential']))].copy()
#FOR NOW JSUT DROP THE target sceanrio 
esto_energy_buildings_fuelsplit = esto_energy_buildings_fuelsplit.loc[esto_energy_buildings_fuelsplit['scenarios']!='target'].copy()
esto_energy_buildings_fuelsplit = esto_energy_buildings_fuelsplit.loc[esto_energy_buildings_fuelsplit['is_subtotal']==False].copy()

#drop is_subtotal
esto_energy_buildings_fuelsplit.drop(columns='is_subtotal', inplace=True)
#%%
#make it tall byfinding the year cols and then melting
year_cols = [col for col in esto_energy_buildings_fuelsplit.columns if re.match(r'\d{4}', col)]
#other cols are scenarios	economy	sectors	sub1sectors	sub2sectors	sub3sectors	sub4sectors	fuels	subfuels
esto_energy_melt_fuelsplit_2021 = esto_energy_buildings_fuelsplit.melt(id_vars=['scenarios','economy','sectors','sub1sectors','sub2sectors','sub3sectors','sub4sectors','fuels','subfuels'], value_vars=year_cols, var_name='year', value_name='energy_esto')
esto_energy_melt_fuelsplit_2021['year'] = esto_energy_melt_fuelsplit_2021['year'].astype(int)
# Filter for only year 2021 as that is what will be use to get fuel ratio 
esto_energy_melt_fuelsplit_2021 = esto_energy_melt_fuelsplit_2021.loc[esto_energy_melt_fuelsplit_2021['year']==2021].copy()
# %%
#
esto_energy_buildings_fuelsplit_total = esto_energy_buildings_fuelsplit.loc[esto_energy_buildings_fuelsplit['fuels']=='19_total'].copy()
esto_energy_buildings_fuelsplit_total_melt = esto_energy_buildings_fuelsplit_total.melt(id_vars=['scenarios','economy','sectors','sub1sectors','sub2sectors','sub3sectors','sub4sectors','fuels','subfuels'], value_vars=year_cols, var_name='year', value_name='energy_esto')
esto_energy_buildings_fuelsplit_total_melt['year'] = esto_energy_buildings_fuelsplit_total_melt['year'].astype(int)
# Filter for only year 2021 as that is what will be use to get fuel ratio 
esto_energy_buildings_fuelsplit_total_melt = esto_energy_buildings_fuelsplit_total_melt.loc[esto_energy_buildings_fuelsplit_total_melt['year']==2021].copy()
# %%
# Merge the totals into each row for the energy use
esto_total_merged = esto_energy_melt_fuelsplit_2021.merge(esto_energy_buildings_fuelsplit_total_melt[['economy', 'sub2sectors', 'year', 'energy_esto']], on=['economy', 'sub2sectors', 'year'], how='left', suffixes=('', '_annualtotal'))
esto_total_merged.drop(columns=['sectors','sub1sectors','sub3sectors','sub4sectors'], inplace=True)
esto_total_merged = esto_total_merged.loc[(esto_total_merged['fuels'] != '19_total')].copy() 
esto_total_merged = esto_total_merged.loc[(esto_total_merged['fuels'] != '20_total_renewables')].copy() 
esto_total_merged = esto_total_merged.loc[(esto_total_merged['fuels'] != '21_modern_renewables')].copy() 
esto_total_merged = esto_total_merged.loc[(esto_total_merged['subfuels'] !='12_01_of_which_photovoltaics')].copy()

esto_total_merged['fuel_ratio_of_total'] = esto_total_merged['energy_esto']/esto_total_merged['energy_esto_annualtotal']

# Check that sum and ratio is correct
grouped_df = esto_total_merged.groupby(['economy', 'sub2sectors'])['fuel_ratio_of_total'].sum().reset_index()
formatted_values = [f"{value:.1f}" for value in grouped_df['fuel_ratio_of_total']]
print(f'Sum of ratios should equal 1.0: {formatted_values}')

# %%
# Prepare for csv export
esto_total_export = esto_total_merged.copy()
esto_total_export.drop(columns=['year', 'energy_esto', 'energy_esto_annualtotal'], inplace=True)
esto_total_export.to_csv(config.root_dir + '/output_data/fuel_split_ratio.csv', index=False)

# %%
