#we want to grab activity data for occupied_dwellings, residential_floor_area, residential_technology_stocks, services_employment

#%% Import necessary libraries
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px

# Optionally visualize with a heatmap
import matplotlib.pyplot as plt
import seaborn as sns
# Custom helper functions and configurations
import utility_functions
import configurations

# Set up root directory and config
root_dir = re.split('buildings', os.getcwd())[0] + '/buildings'
config = configurations.Config(root_dir)

#%% Load and preprocess macro data
macro_date_id = utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', 'macro'), 'APEC_GDP_data_')
macro = pd.read_csv(os.path.join(config.root_dir, 'input_data', 'macro', f'APEC_GDP_data_{macro_date_id}.csv'))
macro['economy_code'] = macro['economy_code'].replace({'17_SIN': '17_SGP', '15_RP': '15_PHL'})

#%% Load and preprocess EEI data
eei = pd.read_csv(os.path.join(config.root_dir, 'input_data', 'eei', 'buildings_final.csv'))

#%% Load and filter ESTO energy data
esto_energy_date_id = utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy'), 'model_df_wide_')
esto_energy = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', f'model_df_wide_{esto_energy_date_id}.csv'))

esto_energy_buildings = esto_energy.query("sectors == '16_other_sector' and sub1sectors == '16_01_buildings' and sub2sectors in ['16_01_01_commercial_and_public_services','16_01_02_residential'] and scenarios != 'target' and not is_subtotal").copy()

excluded_fuels = ['19_total', '20_total_renewables', '21_modern_renewables']
esto_energy_buildings = esto_energy_buildings[~esto_energy_buildings['fuels'].isin(excluded_fuels)]

#%% Reshape ESTO energy data
year_cols = [col for col in esto_energy_buildings.columns if re.match(r'\d{4}', col)]
esto_energy_melt = esto_energy_buildings.melt(id_vars=['scenarios','economy','sectors','sub1sectors','sub2sectors','sub3sectors','sub4sectors','fuels','subfuels'], value_vars=year_cols, var_name='year', value_name='energy_esto')

#%%
#make year an int in all dataframes
esto_energy_melt['year'] = esto_energy_melt['year'].astype(int)
eei['year'] = eei['year'].astype(int)
macro['year'] = macro['year'].astype(int)

#make macro wide and rename economy_code to economy
macro = macro[['economy_code','year', 'variable', 'value']].query("variable in ['real_GDP', 'population', 'GDP_per_capita']").copy()
macro_wide = macro.pivot_table(index=['year', 'economy_code'], columns='variable', values='value').reset_index()
macro_wide.rename(columns={'economy_code': 'economy'}, inplace=True)
#%%
#ay(['energy', 'energy_intensity', 'population', 'services_employment',
#    'occupied_dwellings', 'residential_floor_area',
#    'heating_degree_days', 'cooling_degree_days',
#    'residential_technology_stocks', 'gdp',
#    'percent_of_occupied_dwellings_heated_by_fuel_type',
#    'services_floor_area', 'peak_power'], dtype=object)
eei_activity = eei.query("measure in ['occupied_dwellings', 'residential_floor_area', 'residential_technology_stocks', 'services_employment', 'heating_degree_days', 'cooling_degree_days', 'services_floor_area', 'population', 'gdp']").copy()
#these are all useufl activity indicators for the buildings sector. we shouldtry to project them and how they might change in the future using the popualtion and gdp data we already ahve that is projected. then we can estimate what they might be for economies where we dont have data, and project them into the future for all economies
#using these we can esimate how much of each end use is


#rename 'economy' to economy_name
eei_activity.rename(columns={'country': 'economy_name'}, inplace=True)

#make wide
eei_activity = eei_activity[['year', 'economy', 'measure', 'value', 'economy_name']]

eei_activity_wide = eei_activity.pivot_table(index=['year', 'economy', 'economy_name'], columns='measure', values='value').reset_index()
#calcaulte gdp per cpita uing the gdp and population data from iea. note that our gdp 
eei_activity_wide['GDP_per_capita'] = (eei_activity_wide['gdp'] / eei_activity_wide['population'])*1000 #convert to same magnitude as outlook data
#alsop times pop and real gdp by 1000 to match the magnitude of the outlook data
eei_activity_wide['population'] = eei_activity_wide['population']*1000
eei_activity_wide['gdp'] = eei_activity_wide['gdp']*1000
#%%
#rename real_GDP to gdp in the macro data
macro_wide.rename(columns={'real_GDP': 'gdp'}, inplace=True)
#merge the macro data with the eei data
eei_activity_wide = eei_activity_wide.merge(macro_wide, on=['year', 'economy'], how='outer', suffixes=('_eei', ''))
#for the values with _eei in the name, if the original macro values are na, we want to fill their original values with the _eei values then drop the _eei cols.
for col in ['gdp', 'population', 'GDP_per_capita']:
    eei_activity_wide[col] = eei_activity_wide[col].fillna(eei_activity_wide[f'{col}_eei'])
    eei_activity_wide.drop(columns=[f'{col}_eei'], inplace=True)
  

#pad out the coolign and heating degree days
eei_activity_wide['cooling_degree_days'] = eei_activity_wide.groupby(['economy', 'economy_name'])['cooling_degree_days'].transform(lambda x: x.ffill().bfill())
eei_activity_wide['heating_degree_days'] = eei_activity_wide.groupby(['economy', 'economy_name'])['heating_degree_days'].transform(lambda x: x.ffill().bfill())

#then do some quick analysis of the remaining indicators and how they correlate to each other and to the macro data
#%%
import plotly.express as px

# Create single axis scatter plot for GDP per capita, colored by economy
eei_activity_wide_avg = eei_activity_wide[['economy', 'economy_name', 'GDP_per_capita']].dropna().groupby(['economy', 'economy_name']).mean().reset_index()
#order them
eei_activity_wide_avg = eei_activity_wide_avg.sort_values(by='GDP_per_capita', ascending=False)
#create groups based on some threshold
# Define categories for GDP per capita using quantiles (quartiles in this case)
eei_activity_wide_avg['gdp_per_capita_group'] = pd.qcut(eei_activity_wide_avg['GDP_per_capita'], q=8, labels=['Lowest', 'Low', 'Below Average', 'Average', 'Above Average', 'High', 'Higher', 'Highest'])

# Check the distribution of economies in each group
print(eei_activity_wide_avg.groupby('gdp_per_capita_group')['economy'].nunique())
#%%
fig = px.scatter(eei_activity_wide_avg, y='GDP_per_capita', x='economy_name',color='gdp_per_capita_group', symbol='economy_name',
                 title='GDP per Capita avgs by Economy')

# Show the plot
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'gdp_per_capita_avgs.html'))
#hard to say whether theres a tpoint where an economy is considered high income...
#at least just add them to the df
eei_activity_wide = eei_activity_wide.merge(eei_activity_wide_avg[['economy', 'gdp_per_capita_group']], on='economy', how='left')


############################################################


#%%
#but what if instead of looking at simply the cvorrelation between the variables, and macro we could look at the variables/population and then see how they correlate to the macro data, also, especailly check hwo they change over time and whether they reach a point where they are saturated

#calc 'per capita' values for the activity indicators
for col in ['occupied_dwellings', 'residential_floor_area', 'residential_technology_stocks']:
    eei_activity_wide[f'{col}_per_capita'] = eei_activity_wide[col] / eei_activity_wide['population']
#%%
# Plot all the values
plot_data = eei_activity_wide.melt(id_vars=['year', 'economy', 'economy_name', 
                                            'gdp_per_capita_group'], value_name='value', var_name='measure')

# #lets avg by gdp_per_capita_group
# plot_data_avg = plot_data.groupby(['year','gdp_per_capita_group', 'measure']).mean(numeric_only=True).reset_index()
fig = px.line(plot_data, x='year', y='value', color='economy_name', facet_col='measure', title='All Activity Indicators', facet_col_wrap=4)
#make the y axis independent for each plot
fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'all_activity_indicators.html'))
#%%
#maybe simplfy it by calcaulting the average growth rate and then putting that in a bar plot
plot_data_simplifed = plot_data.copy()
plot_data_simplifed.drop(columns=['gdp_per_capita_group'], inplace=True)
plot_data_simplifed['%_growth'] = plot_data_simplifed.groupby(['economy', 'economy_name', 'measure'])['value'].pct_change()
#drop nans
plot_data_simplifed.dropna(subset=['%_growth'], inplace=True)
#get avg
plot_data_simplifed = plot_data_simplifed.groupby(['economy', 'economy_name', 'measure'])['%_growth'].mean().reset_index()
#drop nans
plot_data_simplifed.dropna(subset=['%_growth'], inplace=True)

#plot the data on a bar
fig = px.bar(plot_data_simplifed, x='economy_name', y='%_growth', color='economy_name', facet_col='measure', title='All Activity Indicators simplified', facet_col_wrap=4)

fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'all_activity_indicators_simplified.html'))
#its weird, basically no economy has a negative growth rate,but theres only a group who have high positive growth rates and then everything else is super low growth rates.
#%%
# Function to calculate year-over-year growth rates
def calculate_growth_rate(df, columns, group_cols=['economy', 'economy_name', 'gdp_per_capita_group']):
    df_growth = df.copy()
    for col in columns:
        growth_col = f'{col}_growth'
        df_growth[growth_col] = df.groupby(group_cols)[col].pct_change()
        df_growth[growth_col] = df_growth[growth_col].mask(df[col].isna())
    return df_growth
# Calculate growth rates for the key variables
growth_columns = ['occupied_dwellings', 'residential_floor_area', 'residential_technology_stocks', 
                  'services_employment', 'gdp', 'GDP_per_capita', 'population', 'occupied_dwellings_per_capita', 'residential_floor_area_per_capita', 'residential_technology_stocks_per_capita']

eei_activity_wide_growth = calculate_growth_rate(eei_activity_wide, growth_columns)
growth_rate_columns = [f'{col}_growth' for col in growth_columns]
#%%

#hmm theres really not much to garner here. they all seem to increase continuously over time. But some things i think we could keep in mind are:
# 1. these economies might have had their growth periods pre-2000 and we dont have that data, so its hard to tell what the trend on a longer time scale is
# 2. the gdp per capita groupings dont show us ANYTHING haha
# 3. what if we inmdex all the data so it ranges between 0 and 1. then we can better compare how the indicators change over time and how they correlate to each other


############################################################


#%%
#maybe we need to be groupoing by things like energy too? asnd what about how energy use changes? maybe the esto or eei data shows saturation points for some of these indicators?

energy = pd.read_csv(os.path.join(config.root_dir, 'output_data', f'energy_and_intensity_by_end_use_subfuels.csv'))

#group energy by end_use and sector and economy and year and then include with the other data
energy_grouped = energy.groupby(['end_use', 'sector', 'economy', 'year']).sum().reset_index()[['end_use', 'sector', 'economy', 'year', 'estimated_energy']]

energy_total = energy_grouped.groupby(['economy', 'year']).sum().reset_index().copy()
energy_total['end_use'] = 'total'
energy_total['sector'] = 'total'
energy_grouped = pd.concat([energy_grouped, energy_total], ignore_index=True)
#convert to growth rates
energy_growth = calculate_growth_rate(energy_grouped, ['estimated_energy'], group_cols=['end_use', 'sector', 'economy'])
energy_growth['end_use_sector'] = energy_growth['end_use'] + '_' + energy_growth['sector']
energy_growth = energy_growth[['economy', 'year', 'end_use_sector', 'estimated_energy_growth']]
#pivot the growth so we have a column for each end use/seector combo
energy_growth_wide = energy_growth.pivot_table(index=['economy', 'year'], columns='end_use_sector', values='estimated_energy_growth').reset_index()
energy_growth_cols = energy_growth_wide.columns[2:]
#%%
energy_and_activity_growth = eei_activity_wide_growth.merge(energy_growth_wide, on=['economy', 'year'], how='outer')
#drop non apec iea
energy_and_activity_growth = energy_and_activity_growth.query("economy != 'non_apec_iea'")
#check teh correlation in growth rates between the energy use and the activity indicators
# growth_columns = [col for col in energy_and_activity_growth.columns if '_growth' in col] + energy_growth_cols.tolist()
growth_columns = [#'occupied_dwellings_growth',
#  'residential_floor_area_growth',
#  'residential_technology_stocks_growth',
#  'services_employment_growth',
#  'gdp_growth',
#  'GDP_per_capita_growth',
#  'population_growth',
 'occupied_dwellings_per_capita_growth',
 'residential_floor_area_per_capita_growth',
 'residential_technology_stocks_per_capita_growth',
 'appliances_residential',
 'cooking_residential',
 'lighting_residential',
 'lighting_services',
#  'non_building_energy_use_residential',
#  'non_specified_residential',
#  'other_building_energy_use_residential',
 'space_cooling_residential',
 'space_cooling_services',
 'space_heating_residential',
 'space_heating_services',
 'water_heating_residential',
 'total_total',]

#and also just plot them ion a line plot
plot_data_energy_activity = energy_and_activity_growth.melt(id_vars=['year', 'economy', 'economy_name', 'gdp_per_capita_group'], value_name='value', var_name='measure')
#smooth out the growth rates using a 5 year rolling average
plot_data_energy_activity['value'] = plot_data_energy_activity.groupby(['economy', 'economy_name', 'measure', 'gdp_per_capita_group'])['value'].transform(lambda x: x.rolling(20, min_periods=1).mean())
#drop any outliers
plot_data_energy_activity = plot_data_energy_activity.query("value < 1 and value > -1")
#drop ct
plot_data_energy_activity = plot_data_energy_activity.query("economy != '18_CT'")

plot_data_energy_activity = plot_data_energy_activity.loc[plot_data_energy_activity['measure'].isin(growth_columns)]
fig = px.line(plot_data_energy_activity, x='year', y='value', color='measure', facet_col='economy', title='Energy Use and Activity Indicators Growth Rates', facet_col_wrap=7)
#make the y axis independent for each plot
fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_and_activity_indicators_growth.html')
)

#%%
#just plot the enegy use, no growth #'end_use', 'sector', 'economy', 'year', 'estimated_energy'
energy_plot = energy_grouped.copy()
energy_plot['end_use_sector'] = energy_plot['end_use'] + '_' + energy_plot['sector']
energy_plot = energy_plot[['economy', 'year', 'end_use_sector', 'estimated_energy']]
energy_plot = energy_plot.groupby(['economy', 'year', 'end_use_sector', 'estimated_energy']).sum().reset_index()
#smooth out the data using a 5 year rolling average
energy_plot['estimated_energy'] = energy_plot.groupby(['economy', 'end_use_sector'])['estimated_energy'].transform(lambda x: x.rolling(20, min_periods=1).mean())
fig = px.line(energy_plot, x='year', y='estimated_energy', color='end_use_sector', facet_col='economy', title='Energy Use by End Use and Sector', facet_col_wrap=7)
#make the y axis independent for each plot
fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_use.html')
)

#%%
#the difference in scale is hard. lets try check the gorwth of the data again
energy_plot_growth = energy_plot.copy()
energy_plot_growth['estimated_energy_growth'] = energy_plot.groupby(['economy', 'end_use_sector'])['estimated_energy'].pct_change()
#drop any outliers
energy_plot_growth = energy_plot_growth.query("estimated_energy_growth < 0.1 and estimated_energy_growth > -0.1")
#smmooth it
energy_plot_growth['estimated_energy_growth'] = energy_plot_growth.groupby(['economy', 'end_use_sector'])['estimated_energy_growth'].transform(lambda x: x.rolling(20, min_periods=1).mean())
fig = px.line(energy_plot_growth, x='year', y='estimated_energy_growth', color='end_use_sector', facet_col='economy', title='Energy Use Growth Rates by End Use and Sector', facet_col_wrap=7)
#make the y axis independent for each plot
# fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_use_growth.html')
)


#%%
#what about energy use per capita? seems most important
energy_per_capita = energy_plot.copy()

per_capita_all = eei_activity_wide[['year', 'economy', 'economy_name','population', 'GDP_per_capita', 'occupied_dwellings_per_capita',
       'residential_floor_area_per_capita',
       'residential_technology_stocks_per_capita']].drop_duplicates()
#where economy is non_apec_iea, replace the economy with economy_name
per_capita_all.loc[per_capita_all['economy'] == 'non_apec_iea', 'economy'] = per_capita_all.loc[per_capita_all['economy'] == 'non_apec_iea', 'economy_name']
#drop the economy_name column
per_capita_all.drop(columns=['economy_name'], inplace=True)

energy_per_capita = energy_per_capita.merge(per_capita_all[['year', 'economy', 'population']].drop_duplicates(), on=['year', 'economy'], how='outer').copy()

energy_per_capita['estimated_energy_per_capita'] = energy_per_capita['estimated_energy'] / energy_per_capita['population']
#pviot the end use sector so we have a column for each end use sector combo's energy per capita
energy_per_capita = energy_per_capita[['year', 'economy','end_use_sector','estimated_energy_per_capita']].pivot_table(index=['year', 'economy'], columns='end_use_sector', values='estimated_energy_per_capita').reset_index()

per_capita_all = energy_per_capita.merge(per_capita_all, on=['year', 'economy'], how='outer').copy()
#drop data after 2021
per_capita_all = per_capita_all.query("year <= 2021")

#melt the data
per_capita_all_melt = per_capita_all.melt(id_vars=['year', 'economy'], value_name='value', var_name='measure')
#order the data
per_capita_all_melt = per_capita_all_melt.sort_values(by=['economy', 'year', 'measure'])

per_capita_all_melt = per_capita_all_melt.sort_values(by=['economy', 'year', 'measure'])
#cacualte a growth rate version
per_capita_all_growth = per_capita_all_melt.copy()
per_capita_all_growth['value_growth'] = per_capita_all_growth.groupby(['economy', 'measure'])['value'].pct_change()
#drop any outliers
per_capita_all_growth = per_capita_all_growth.query("value_growth < 1 and value_growth > -1")
#smooth it
per_capita_all_growth['value_growth'] = per_capita_all_growth.groupby(['economy', 'measure'])['value_growth'].transform(lambda x: x.rolling(20, min_periods=1).mean())

#%%
#plot the energy per capita and then the growth rates
fig = px.line(per_capita_all_melt, x='year', y='value', color='economy', facet_col='measure', title='Energy Use per Capita by End Use and Sector and activity per capita', facet_col_wrap=7)
#make the y axis independent for each plot
fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_and_activity_per_capita.html')
)

#plot the growth rates
#first drop the outliers (anyhtin more than 0,1)
per_capita_all_growth  = per_capita_all_growth.query("value_growth < 0.1 and value_growth > -0.1")
fig = px.line(per_capita_all_growth, x='year', y='value_growth', color='economy', facet_col='measure', title='Energy Use per Capita Growth Rates by End Use and Sector and activity per capita', facet_col_wrap=7)
#make the y axis independent for each plot
fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_and_activity_per_capita_growth.html')
)
#reduce the growth rates down to a simple average and then pltoa s a bar
per_capita_all_growth_avg = per_capita_all_growth.groupby(['economy', 'measure'])['value_growth'].mean().reset_index()
fig = px.bar(per_capita_all_growth_avg, x='economy', y='value_growth', color='economy',  facet_col='measure',facet_col_wrap=7, title='Energy Use per Capita Growth Rates by Economy and End Use Sector and activity per capita')
#make the y axis independent for each plot
fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_and_activity_per_capita_growth_avg.html')
)
#%%

############################################################


#need to idntuocue the energy use form the eei data as well, so then we can see the data for them too
#also we should look at how energy use per capita changes for certain economies grouped by their heating and cooling degree days. this way we could see if there are expected levels at which energy use per capita might saturate?
eei_energy = eei.query("measure in ['energy']").copy()
eei_energy = eei_energy.loc[eei_energy['economy'] =='non_apec_iea']
#set economy to be the same as economy name
eei_energy['economy'] = eei_energy['country']
eei_energy = eei_energy[['year', 'economy','value']].groupby(['year', 'economy']).sum().reset_index()
#rename vallue to energy
eei_energy.rename(columns={'value': 'energy'}, inplace=True)

#join with eei_activity_wide and energy_plot
energy_total_aperc = energy_total[['year', 'economy', 'estimated_energy']].rename(columns={'estimated_energy': 'energy'}).copy()

#in eei_activity_wide, where economy = nonapec_iea, repalce the economy with economy_name
eei_activity_wide_plot = eei_activity_wide.copy()
eei_activity_wide_plot.loc[eei_activity_wide_plot['economy'] == 'non_apec_iea', 'economy'] = eei_activity_wide_plot.loc[eei_activity_wide_plot['economy'] == 'non_apec_iea', 'economy_name']
eei_activity_wide_plot.drop(columns=['economy_name'], inplace=True)
#somehow we got duplicates in here. lets jsut drop them quickly
eei_activity_wide_plot.drop_duplicates(subset=['year', 'economy'], inplace=True)
#now join the data
energy_all = pd.concat([energy_total_aperc, eei_energy], ignore_index=True)

#check for duplicates
print(energy_all[['economy', 'year']].duplicated().sum())

#%%
all_data = eei_activity_wide_plot.merge(energy_all, on=['year', 'economy'], how='outer')
#drop iea_total frrom economy
all_data = all_data.query("economy != 'iea_total'")
#%%
# Quantile-based grouping of economies by heating and cooling degree days# Calculate average HDD and CDD for each economy
temp_avgs = all_data.groupby(['economy'])[['heating_degree_days', 'cooling_degree_days']].mean().reset_index().copy()
#drop nas
temp_avgs.dropna(inplace=True)

# Define thresholds or use quantiles for HDD and CDD groupings
def classify_hdd(row):
    if row['heating_degree_days'] > temp_avgs['heating_degree_days'].quantile(0.75):
        return 'cold'
    elif row['heating_degree_days'] > temp_avgs['heating_degree_days'].quantile(0.25):
        return 'temperate'
    else:
        return 'hot'

def classify_cdd(row):
    if row['cooling_degree_days'] > temp_avgs['cooling_degree_days'].quantile(0.75):
        return 'hot'
    elif row['cooling_degree_days'] > temp_avgs['cooling_degree_days'].quantile(0.25):
        return 'temperate'
    else:
        return 'cold'

# Apply the classification to each economy for both HDD and CDD
temp_avgs['hdd_group'] = temp_avgs.apply(classify_hdd, axis=1)
temp_avgs['cdd_group'] = temp_avgs.apply(classify_cdd, axis=1)

# Combine HDD and CDD groupings into a single column
temp_avgs['temperature_group'] = temp_avgs['hdd_group'] + '_' + temp_avgs['cdd_group']

# Check the distribution of economies in each combined group
print(temp_avgs.groupby('temperature_group')['economy'].nunique())

# Scatter plot of HDD vs CDD, color-coded by the temperature group
import plotly.express as px
fig = px.scatter(temp_avgs, x='cooling_degree_days', y='heating_degree_days', color='temperature_group',
                 hover_name='economy', title='Heating vs Cooling Degree Days by Temperature Group')
fig.show()

#they could be better if we could weight them by wehre the people live but thats a bit too much for now.
#now what we cna do is group the economies by their heating and cooling degree days and then see how energy use per capita changes for them over time, are there certain levels at which energy use per capita might saturate? that might help us tell what might happen to the other economies, which we still need to get temp data for

#i used chatgpt to remap some of the econmies:
# 01_AUS	temperate_hot
# 03_CDA	cold_temperate
# 04_CHL	temperate_temperate
# 08_JPN	temperate_hot
# 09_ROK	temperate_temperate
# 11_MEX	hot_hot
# 12_NZ	temperate_temperate
# 20_USA	temperate_hot
# argentina	temperate_temperate
# armenia	cold_temperate
# austria	cold_temperate
# belgium	temperate_temperate
# brazil	hot_hot
# bulgaria	temperate_temperate
# croatia	temperate_temperate
# cyprus	hot_hot
# czech_republic	cold_temperate
# estonia	cold_cold
# finland	cold_cold
# france	temperate_temperate
# germany	temperate_temperate
# greece	hot_temperate
# hungary	temperate_temperate
# italy	temperate_hot
# kyrgyzstan	cold_cold
# latvia	cold_cold
# lithuania	cold_cold
# luxembourg	temperate_temperate
# malta	hot_hot
# netherlands	temperate_temperate
# poland	cold_temperate
# portugal	temperate_hot
# republic_of_tÃ¼rkiye	temperate_temperate
# romania	temperate_temperate
# slovak_republic	temperate_temperate
# slovenia	hot_temperate
# spain	hot_temperate
# uruguay	temperate_temperate
temp_avgs = {
        '01_AUS': 'temperate_hot',
    '03_CDA': 'cold_temperate',
    '04_CHL': 'temperate_temperate',
    '08_JPN': 'temperate_hot',
    '09_ROK': 'temperate_temperate',
    '11_MEX': 'hot_hot',
    '12_NZ': 'temperate_temperate',
    '20_USA': 'temperate_hot',
    'argentina': 'temperate_temperate',
    'armenia': 'cold_temperate',
    'austria': 'cold_temperate',
    'belgium': 'temperate_temperate',
    'brazil': 'hot_hot',
    'bulgaria': 'temperate_temperate',
    'croatia': 'temperate_temperate',
    'cyprus': 'hot_hot',
    'czech_republic': 'cold_temperate',
    'estonia': 'cold_cold',
    'finland': 'cold_cold',
    'france': 'temperate_temperate',
    'germany': 'temperate_temperate',
    'greece': 'hot_temperate',
    'hungary': 'temperate_temperate',
    'italy': 'temperate_hot',
    'kyrgyzstan': 'cold_cold',
    'latvia': 'cold_cold',
    'lithuania': 'cold_cold',
    'luxembourg': 'temperate_temperate',
    'malta': 'hot_hot',
    'netherlands': 'temperate_temperate',
    'poland': 'cold_temperate',
    'portugal': 'temperate_hot',
    'republic_of_tÃ¼rkiye': 'temperate_temperate',
    'romania': 'temperate_temperate',
    'slovak_republic': 'temperate_temperate',
    'slovenia': 'hot_temperate',
    'spain': 'hot_temperate',
    'uruguay': 'temperate_temperate'
}
temp_avgs = pd.DataFrame(temp_avgs.items(), columns=['economy', 'temperature_group'])
#%%

#%%
#find the economys we ahve no temp data for and group themmanually
# print( all_data_new.query("temperature_group.isna()")['economy'].unique())
# ['18_CT' 'albania' 'azerbaijan' 'belarus' 'bosnia_and_herzegovina'
#  'colombia' 'denmark' 'georgia' 'hong_kong_(_china)' 'ireland'
#  'kazakhstan' 'kosovo' 'morocco' 'norway' 'republic_of_moldova'
#  'republic_of_north_macedonia' 'serbia' 'south_africa' 'sweden'
#  'switzerland' 'ukraine' 'united_kingdom' 'uzbekistan' '02_BD' '05_PRC'
#  '06_HKC' '07_INA' '10_MAS' '13_PNG' '14_PE' '15_PHL' '16_RUS' '17_SGP'
#  '19_THA' '21_VN']
temp_mappings = {}
# economy	temperature_group
# 18_CT	temperate_temperate
# albania	temperate_temperate
# azerbaijan	cold_temperate
# belarus	cold_cold
# bosnia_and_herzegovina	temperate_temperate
# colombia	hot_temperate
# denmark	temperate_temperate
# georgia	temperate_temperate
# hong_kong_(_china)	hot_temperate
# ireland	temperate_temperate
# kazakhstan	cold_cold
# kosovo	temperate_temperate
# morocco	hot_temperate
# norway	cold_cold
# republic_of_moldova	cold_temperate
# republic_of_north_macedonia	temperate_temperate
# serbia	temperate_temperate
# south_africa	hot_hot
# sweden	cold_cold
# switzerland	temperate_temperate
# ukraine	cold_cold
# united_kingdom	temperate_temperate
# uzbekistan	cold_cold
# 02_BD	hot_hot
# 05_PRC	hot_hot
# 06_HKC	hot_temperate
# 07_INA	hot_hot
# 10_MAS	hot_temperate
# 13_PNG	hot_temperate
# 14_PE	hot_temperate
# 15_PHL	hot_temperate
# 16_RUS	cold_temperate
# 17_SGP	hot_hot
# 19_THA	hot_temperate
# 21_VN	hot_temperate
temp_mappings = {
    '18_CT': 'hot_temperate',
    'albania': 'temperate_temperate',
    'azerbaijan': 'cold_temperate',
    'belarus': 'cold_cold',
    'bosnia_and_herzegovina': 'temperate_temperate',
    'colombia': 'hot_temperate',
    'denmark': 'temperate_temperate',
    'georgia': 'temperate_temperate',
    'hong_kong_(_china)': 'hot_temperate',
    'ireland': 'temperate_temperate',
    'kazakhstan': 'cold_cold',
    'kosovo': 'temperate_temperate',
    'morocco': 'hot_temperate',
    'norway': 'cold_cold',
    'republic_of_moldova': 'cold_temperate',
    'republic_of_north_macedonia': 'temperate_temperate',
    'serbia': 'temperate_temperate',
    'south_africa': 'hot_hot',
    'sweden': 'cold_cold',
    'switzerland': 'temperate_temperate',
    'ukraine': 'cold_cold',
    'united_kingdom': 'temperate_temperate',
    'uzbekistan': 'cold_cold',
    '02_BD': 'hot_hot',
    '05_PRC': 'hot_cold',
    '06_HKC': 'hot_temperate',
    '07_INA': 'hot_hot',
    '10_MAS': 'hot_temperate',
    '13_PNG': 'hot_temperate',
    '14_PE': 'hot_temperate',
    '15_PHL': 'hot_temperate',
    '16_RUS': 'cold_temperate',
    '17_SGP': 'hot_hot',
    '19_THA': 'hot_temperate',
    '21_VN': 'hot_temperate',
}
temp_mappings = pd.DataFrame(temp_mappings.items(), columns=['economy', 'temperature_group'])
all_temp = pd.concat([temp_avgs, temp_mappings], ignore_index=True)
#%%
# Merge the temperature groupings with the main data
all_data_new = all_data.merge(all_temp[['economy', 'temperature_group']], on='economy', how='left')
#%%
# Check the distribution of economies in each combined group
print(all_data_new.groupby('temperature_group')['economy'].nunique())
#finally, if a country has cold in their temp group, set temperature group to cold, if they have hot in their temp group, set to hot, otherwise set to temperate
# mappings = {'temperate_hot', 'cold_temperate', 'temperate_temperate',
#        'hot_hot', 'hot_temperate', 'cold_cold', nan, 'hot_cold'}
mappings = {
    'temperate_hot': 'hot',
    'cold_temperate': 'cold',
    'temperate_temperate': 'temperate',
    'hot_hot': 'hot',
    'hot_temperate': 'hot',
    'cold_cold': 'cold',
    'hot_cold': 'temperate'
}

all_data_new['temperature_group'] = all_data_new['temperature_group'].map(mappings)

#%%

#calcaulte energy use per cpaita
all_data_new['energy_per_capita'] = all_data_new['energy'] / all_data_new['population']
#%%
# Plot energy use per capita by temperature group
plot_data_temp = all_data_new.melt(id_vars=['year', 'economy', 'temperature_group', 'gdp_per_capita_group'], value_name='value', var_name='measure')

#smooth out the data using a 5 year rolling average
plot_data_temp['value'] = plot_data_temp.groupby(['economy', 'temperature_group', 'gdp_per_capita_group', 'measure'])['value'].transform(lambda x: x.rolling(20, min_periods=1).mean())
#order the data
plot_data_temp = plot_data_temp.sort_values(by=['economy', 'year', 'measure'])
#drop nas and pre 2000 data
plot_data_temp = plot_data_temp.query("year >= 2000")
plot_data_temp = plot_data_temp.dropna(subset=['value'])
fig = px.line(plot_data_temp.loc[plot_data_temp.measure=='energy_per_capita'], x='year', y='value', color='economy', facet_col='temperature_group', title='Energy Use per Capita by Temperature Group', facet_col_wrap=4)
#make the y axis independent for each plot
# fig.for_each_yaxis(lambda axis: axis.update(matches=None))
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_per_capita_by_temp_group.html'))

#wat if we take the average of energy use per capita and then gdp per capita for each economy and then plot that on scatters?
#%%
# Calculate average energy use per capita and GDP per capita by temperature group
temp_avgs = all_data_new.groupby(['economy', 'temperature_group'])[['energy_per_capita', 'GDP_per_capita']].mean().reset_index()
#plot
fig = px.scatter(temp_avgs, x='GDP_per_capita', y='energy_per_capita',facet_col='temperature_group', color='temperature_group', hover_name='economy', title='Energy Use per Capita vs GDP per Capita by Temperature Group', facet_col_wrap=4)
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_per_capita_vs_gdp_per_capita_by_temp_group.html'))
# %%
#and cause leanne askedm , just plot energy vs gdp
temp_avgs_gdp = all_data_new.groupby(['economy', 'temperature_group'])[['energy', 'gdp']].mean().reset_index()

fig = px.scatter(temp_avgs_gdp, x='gdp', y='energy',facet_col='temperature_group', color='temperature_group', hover_name='economy', title='Energy Use  vs GDP  by Temperature Group', facet_col_wrap=4)
fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'estimate_activity_data', 'energy_vs_gdp_by_temp_group.html'))#yeah theyre the same if you slide the x axis a bit to get the same scale, proportionaly.
# %%
