#%%
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px

####
#self made helper functions
import scripts.x3_utility_functions as x3_utility_functions
import scripts.x1_configurations as x1_configurations
root_dir =re.split('buildings', os.getcwd())[0]+'/buildings'
config = x1_configurations.Config(root_dir)
####
# %%
# import economy data
economy_list = pd.read_csv(config.root_dir + '/config/economy_code_to_name.csv')
# %%
# Import fuel split (from fuelsplit.py) and projection (from main.py) data
fuel_split = pd.read_csv(config.root_dir + '/output_data/fuel_split_ratio.csv')
fuel_split['fuel_ratio_of_total'] = fuel_split['fuel_ratio_of_total'].astype(float)
fuel_split = fuel_split.loc[fuel_split['fuel_ratio_of_total'] != 0].copy()
projection_total = pd.read_csv(config.root_dir + '/output_data/summedannual_energy_data.csv')
projection_total = projection_total.loc[(projection_total['dataset'] == 'projection')].copy()

# %%
# Merge value of total energy for each economy and subsector 
fuel_split_projection = pd.merge(projection_total, fuel_split[['economy', 'sub2sectors', 'fuels', 'subfuels', 'fuel_ratio_of_total']], 
                     on=['economy', 'sub2sectors'], how='left')
fuel_split_projection['fuel_PJ'] = fuel_split_projection['energy'] * fuel_split_projection['fuel_ratio_of_total']

fuel_split_projection.to_csv(config.root_dir + '/output_data/fuel_split_projection.csv', index=False)
# %%
# CAN BE RUN as a check that the sum of fuel_PJ equals the sub2sector total as expected
# grouped_df = fuel_split_projection.groupby(['economy', 'year', 'sub2sectors']).agg({'fuel_PJ': 'sum', 'energy': 'first'}).reset_index()
# not_equal_df = grouped_df[~np.isclose(grouped_df['fuel_PJ'], grouped_df['energy'])]
# print(not_equal_df)
# %%
# PLOTTING PREP
# Splitting and grouping data for plotting
fuel_split_projection_plot = fuel_split_projection.copy()
fuel_split_projection_plot.drop(columns=['energy','fuel_ratio_of_total'], inplace=True)
# Group by fuel
fuel_grouped_projection_plot = fuel_split_projection_plot.groupby(['economy', 'year', 'fuels', 'sub2sectors', 'dataset']).agg({'fuel_PJ': 'sum'}).reset_index()
# Group by fuel and sub2sector
fuelsubsec_grouped_projection_plot = fuel_split_projection_plot.groupby(['economy', 'year', 'fuels', 'dataset']).agg({'fuel_PJ': 'sum'}).reset_index()
# %%
# Subsectors and subfuel split
fuel_split_projection_plot_res = fuel_split_projection_plot.loc[(fuel_split_projection_plot['sub2sectors'] != '16_01_01_commercial_and_public_services')]
fuel_split_projection_plot_srv = fuel_split_projection_plot.loc[(fuel_split_projection_plot['sub2sectors'] != '16_01_02_residential')]

fuel_grouped_projection_plot_res = fuel_grouped_projection_plot.loc[(fuel_grouped_projection_plot['sub2sectors'] != '16_01_01_commercial_and_public_services')]
fuel_grouped_projection_plot_srv = fuel_grouped_projection_plot.loc[(fuel_grouped_projection_plot['sub2sectors'] != '16_01_02_residential')]
# %%
# to csv
output_dir_csv = config.root_dir + '/output_data/forplots/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

fuel_grouped_projection_plot.to_csv(output_dir_csv + 'fuel_grouped_projection_plot.csv', index=False)
fuel_split_projection_plot_res.to_csv(output_dir_csv + 'fuel_split_projection_plot_res.csv', index=False)
fuel_split_projection_plot_srv.to_csv(output_dir_csv + 'fuel_split_projection_plot_srv.csv', index=False)
# ones used listed below
fuelsubsec_grouped_projection_plot.to_csv(output_dir_csv + 'fuelsubsec_grouped_projection_plot.csv', index=False)
fuel_grouped_projection_plot_res.to_csv(output_dir_csv + 'fuel_grouped_projection_plot_res.csv', index=False)
fuel_grouped_projection_plot_srv.to_csv(output_dir_csv + 'fuel_grouped_projection_plot_srv.csv', index=False)

# %%
output_dir = config.root_dir + '/plotting_output/analysis/fuel_breakdown'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

######## Residential + services summed, plotted by fuel
fig = px.area(fuelsubsec_grouped_projection_plot, x='year', y='fuel_PJ', 
              color='fuels', facet_col='economy', 
              facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir + '/fuel_projection_ressrv_sum.html')

####### Residential only, grouped by fuels in df
fig = px.area(fuel_grouped_projection_plot_res, x='year', y='fuel_PJ', 
              color='fuels', facet_col='economy', 
              facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir + '/grouped_fuel_projection_residential.html')

###### Servics only, grouped by fuels in df
fig = px.area(fuel_grouped_projection_plot_srv, x='year', y='fuel_PJ', 
              color='fuels', facet_col='economy', 
              facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir + '/grouped_fuel_projection_services.html')

# ####### Residential only, subfuels in df
# fig = px.area(fuel_split_projection_plot_res, x='year', y='fuel_PJ', 
#               color='fuels', facet_col='economy', 
#               facet_col_wrap=7)
# fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir + '/fuel_projection_residential.html')

# ###### Servics only, subfuels in df
# fig = px.area(fuel_split_projection_plot_srv, x='year', y='fuel_PJ', 
#               color='fuels', facet_col='economy', 
#               facet_col_wrap=7)
# fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir + '/fuel_projection_services.html')


# %%
ninth_data = pd.read_excel(config.root_dir + '/input_data/all_economies_merged_adjusted.xlsx')
ninth_data = ninth_data.loc[(ninth_data['scenarios'] == 'reference')].copy()
ninth_data = ninth_data.loc[ninth_data['is_subtotal']==False].copy()
ninth_data.drop(columns=['sectors','sub1sectors', 'sub3sectors', 'sub4sectors', 'is_subtotal'], inplace=True)
# ninth_data = ninth_data.rename(columns={'scenarios': 'dataset'})
# %%
# make it TALL!!!!!!!!!!!!!!!!!!!!!!!!
ninth_data.columns = ninth_data.columns.map(str)
year_cols = [col for col in ninth_data.columns if re.match(r'\d{4}', col)]
all_9th_melt = ninth_data.melt(id_vars=['scenarios','economy','sub2sectors','fuels', 'subfuels'], value_vars=year_cols, var_name='year', value_name='fuel_PJ')

# generate dataset column to match projection dataset, then drop the scenarios column
all_9th_melt['dataset'] = 'iteration 1_9th ' + all_9th_melt['scenarios']
all_9th_melt.drop(columns=['scenarios'], inplace=True)

#drop all data that is 0's
all_9th_melt = all_9th_melt.loc[all_9th_melt['fuel_PJ']!=0].copy()
# %%

# Group by fuel
all_9th_grouped_fuel = all_9th_melt.groupby(['economy', 'year', 'fuels', 'sub2sectors', 'dataset']).agg({'fuel_PJ': 'sum'}).reset_index()
	# economy	year	fuels	sub2sectors	dataset	fuel_P

# Group by fuel and sub2sector
all_9th_grouped_fuelsubsec = all_9th_melt.groupby(['economy', 'year', 'fuels', 'dataset']).agg({'fuel_PJ': 'sum'}).reset_index()
    # economy	year	fuels	dataset	fuel_PJ

# all_9th_grouped_fuelsubsec : fuelsubsec_grouped_projection_plot

# not groupd by subsector
# all_9th_grouped_fuel : fuel_grouped_projection_plot
# fuel_grouped_projection_plot_res :
# fuel_grouped_projection_plot_srv :
# %%

# Remove years 2022-2070 from the 9th results
all_9th_grouped_fuelsubsec['year'] = all_9th_grouped_fuelsubsec['year'].astype(int)
# all_9th_grouped_fuelsubsec_yearfiltered = all_9th_grouped_fuelsubsec[(all_9th_grouped_fuelsubsec['year'] >= 2000) & (all_9th_grouped_fuelsubsec['year'] <= 2021)]
all_9th_grouped_fuelsubsec_yearfiltered = all_9th_grouped_fuelsubsec[(all_9th_grouped_fuelsubsec['year'] >= 2000)]
# %%
# all_fuel = pd.concat([fuelsubsec_grouped_projection_plot, all_9th_grouped_fuelsubsec], axis=0)
all_fuel_yearfiltered = pd.concat([fuelsubsec_grouped_projection_plot, all_9th_grouped_fuelsubsec_yearfiltered], axis=0)
all_fuel_yearfiltered.to_csv(config.root_dir + '/output_data/all_fuel_yearfiltered.csv')
# %%
# fig = px.area(all_fuel_yearfiltered, x='year', y='fuel_PJ', 
#               color='fuels', facet_col='economy', 
#               facet_col_wrap=7)
# fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir + '/9th_projection_fuel_test.html')
# %%
fig = px.line(all_fuel_yearfiltered, x='year', y='fuel_PJ', color='fuels', facet_col='economy', facet_col_wrap=7, line_dash='dataset', range_x=[2000, 2070])
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir + '/9th_projection_fuel_line.html')
# %%
# import ESTO data to add to plot
esto_energy_date_id = x3_utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy'), 'model_df_wide_') 
esto_energy = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', f'model_df_wide_{esto_energy_date_id}.csv'))

esto_energy_buildings_fuelsplit = esto_energy.loc[(esto_energy['sectors']=='16_other_sector') & (esto_energy['sub1sectors']=='16_01_buildings') & (esto_energy['sub2sectors'].isin(['16_01_01_commercial_and_public_services','16_01_02_residential']))].copy()
#FOR NOW JSUT DROP THE target sceanrio 
esto_energy_buildings_fuelsplit = esto_energy_buildings_fuelsplit.loc[esto_energy_buildings_fuelsplit['scenarios']!='target'].copy()
esto_energy_buildings_fuelsplit = esto_energy_buildings_fuelsplit.loc[esto_energy_buildings_fuelsplit['is_subtotal']==False].copy()

#drop is_subtotal
esto_energy_buildings_fuelsplit.drop(columns='is_subtotal', inplace=True)
#make it tall byfinding the year cols and then melting
year_cols = [col for col in esto_energy_buildings_fuelsplit.columns if re.match(r'\d{4}', col)]
#other cols are scenarios	economy	sectors	sub1sectors	sub2sectors	sub3sectors	sub4sectors	fuels	subfuels
esto_energy_melt_fuelsplit = esto_energy_buildings_fuelsplit.melt(id_vars=['scenarios','economy','sectors','sub1sectors','sub2sectors','sub3sectors','sub4sectors','fuels','subfuels'], value_vars=year_cols, var_name='year', value_name='fuel_PJ')
esto_energy_melt_fuelsplit['year'] = esto_energy_melt_fuelsplit['year'].astype(int)

esto_total_plot = esto_energy_melt_fuelsplit.copy()
esto_total_plot.drop(columns=['sectors','sub1sectors','sub3sectors','sub4sectors'], inplace=True)
esto_total_plot = esto_total_plot.loc[(esto_total_plot['fuels'] != '19_total')].copy() 
esto_total_plot = esto_total_plot.loc[(esto_total_plot['fuels'] != '20_total_renewables')].copy() 
esto_total_plot = esto_total_plot.loc[(esto_total_plot['fuels'] != '21_modern_renewables')].copy() 
esto_total_plot = esto_total_plot.loc[(esto_total_plot['subfuels'] !='12_01_of_which_photovoltaics')].copy()

esto_total_plot['dataset'] = 'esto ' + esto_total_plot['scenarios']
esto_total_plot.drop(columns=['scenarios'], inplace=True)

# %%
esto_grouped = esto_total_plot.groupby(['economy', 'year', 'fuels', 'dataset']).agg({'fuel_PJ': 'sum'}).reset_index()
esto_grouped = esto_grouped.loc[esto_grouped['fuel_PJ']!=0].copy()
# %%
# ADD ESTO data to new concat file for plot
# all_fuel = pd.concat([fuelsubsec_grouped_projection_plot, all_9th_grouped_fuelsubsec], axis=0)
estoproj9th_plot = pd.concat([fuelsubsec_grouped_projection_plot, all_9th_grouped_fuelsubsec_yearfiltered, esto_grouped], axis=0)
estoproj9th_plot.to_csv(config.root_dir + '/output_data/esto_projection_9th_forplot.csv')
# %%
fig = px.line(estoproj9th_plot, x='year', y='fuel_PJ', color='fuels', facet_col='economy', facet_col_wrap=7, line_dash='dataset', range_x=[2000, 2070])
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir + '/esto_projection_9th_fuel_line.html')

# %%
# %%
# Find intensity for each fuel from projection / population

fuelsubsec_grouped_projection_plot.to_csv(config.root_dir + '/output_data/fuelsubsec_grouped_intensity.csv')
# %%
macro_date_id = x3_utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', 'macro'), 'APEC_GDP_data_')
macro = pd.read_csv(os.path.join(config.root_dir, 'input_data', 'macro', f'APEC_GDP_data_{macro_date_id}.csv'))

#reaplce 17_SIN with SGP
macro['economy_code'] = macro['economy_code'].replace('17_SIN','17_SGP')
#reaplce 15_RP with PHL
macro['economy_code'] = macro['economy_code'].replace('15_RP','15_PHL')

population_9th = macro.loc[macro['variable'] == 'population'].copy()
population_9th['population'] = population_9th['value']*1e3#convert from thousands to individuals

population_9th.drop(columns=['units', 'value', 'variable', 'economy'], inplace=True)
population_9th.rename(columns={'economy_code': 'economy'}, inplace=True)

# %%

# merge population onto energy projection (year 2022 to 2100)
fuel_intensity_projection = pd.merge(fuelsubsec_grouped_projection_plot, population_9th[['economy', 'year', 'population']], on=['economy', 'year'], how='left')
fuel_intensity_projection['fuel_intensity (GJ/cap)'] = (fuel_intensity_projection['fuel_PJ'] * 1000000) / fuel_intensity_projection['population']
# %%
fig = px.line(fuel_intensity_projection, x='year', y='fuel_intensity (GJ/cap)', color='fuels', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html(output_dir + '/fuel_intensity_projection.html')

# %%
fuel_intensity_projection.to_csv(config.root_dir + '/output_data/fortrajectory/fuel_intensity_projection_data.csv', index=False)
# %%
esto_intensity_projection = pd.merge(esto_grouped, population_9th[['economy', 'year', 'population']], on=['economy', 'year'], how='left')
esto_intensity_projection['fuel_intensity (GJ/cap)'] = (esto_intensity_projection['fuel_PJ'] * 1000000) / esto_intensity_projection['population']
# %%
df_merged = pd.concat([esto_intensity_projection, fuel_intensity_projection], ignore_index=True)
df_merged = df_merged.sort_values(by=['economy', 'year']).reset_index(drop=True)
df_merged = df_merged.loc[df_merged['year']!=2101].copy()
df_merged.rename(columns={'fuel_intensity (GJ/cap)': 'fuel_intensity_GJperCap'}, inplace=True)
df_merged.to_csv(config.root_dir + '/output_data/fortrajectory/intensity_trajectory_data.csv', index=False)
# %%
