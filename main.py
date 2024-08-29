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
#%%

#start by creating a mock projection for using the intensity times the population over the projection period:

#first we need to get the population data
population_9th = macro.loc[macro['variable'] == 'population'].copy()
population_9th['value'] = population_9th['value']*1e3#convert from thousands to individuals
END_USES = ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances', 'non_specified', 'space_heating', 'space_cooling', 'lighting', 'other_building_energy_use', 'non_building_energy_use']

intensity = eei.loc[(eei['measure'] == 'energy_intensity') & (eei.end_use.isin(END_USES))].copy()
intensity.end_use.unique()#array(['space_heating', 'space_cooling', 'lighting', 'water_heating',
#    'cooking', 'residential_appliances'], dtype=object)
#%%
#double check that this covers all intended end uses by checking that the sum of energy is the same as the total:
energy_by_end_use = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES) & (eei.fuel=='all'))].copy()
energy_total = eei.loc[(eei['measure'] == 'energy')& (eei.end_use.isin(['total'])) & (eei.fuel=='all')].copy()
#sum value  by year and economy
energy_by_end_use = energy_by_end_use.groupby(['economy','year','sector']).sum().reset_index()[['economy','year','value','sector']]
energy_total = energy_total.groupby(['economy','year','sector']).sum().reset_index()[['economy','year','value','sector']]
energy_total_no_sector = energy_total.groupby(['economy','year']).sum().reset_index()[['economy','year','value']]
energy_by_end_use_no_sector = energy_by_end_use.groupby(['economy','year']).sum().reset_index()[['economy','year','value']]
#########
#VIS
#find the difference between the two:
energy_diff = energy_total_no_sector.merge(energy_by_end_use_no_sector, on=['economy','year'], suffixes=('_total','_end_use'))
energy_diff['diff'] = energy_diff['value_total'] - energy_diff['value_end_use']
#plot the difference on plotly

fig = px.line(energy_diff, x='year', y='diff', color='economy')
fig.show()

#NOTE THAT BY UING THE _NO_SECTOR DATA WE ARE NOT TAKING INTO ACCOUNT THE SECTORAL BREAKDOWN OF THE ENERGY USE. dID THIS BECAUSE IT SEEMED LIKE SECTORS WERE NOT SPECIFIED CORRECTLY FOR THE TOTAL ENERGY USE. i DONT REALLY KNOW WHAT WAS GOING ON.
#########
#%%
#note that we dont have intensity by the end uses for non_specified, other_building_energy_use, and non_building_energy_use. We snhould try quantify these differences:
energy_by_end_use = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES) & (eei.fuel=='all'))].copy()
#label the end uses that are not covered by the intensity data
energy_by_end_use['end_use_label'] = 'total'
energy_by_end_use.loc[~energy_by_end_use['end_use'].isin(intensity.end_use.unique()), 'end_use_label'] = 'no_intensity_data'
#sum value  by year and economy
energy_by_end_use = energy_by_end_use.groupby(['economy','year','end_use_label','sector']).sum().reset_index()[['economy','year','value','end_use_label','sector']]
energy_total['end_use_label'] = 'total'
#merge the two dataframes and find the difference
energy_by_end_use = energy_by_end_use.merge(energy_total, on=['economy','year','end_use_label','sector'], suffixes=('_end_use','_total'), how='inner')

energy_by_end_use['diff'] = energy_by_end_use['value_total'] - energy_by_end_use['value_end_use']
#calculate the percentage difference
energy_by_end_use['diff_percentage'] = energy_by_end_use['diff']/energy_by_end_use['value_total']
#########
#VIS
#plot the difference on plotly
fig = px.line(energy_by_end_use, x='year', y='diff_percentage', color='economy', line_dash='sector')
fig.show()

#and clacualte the average percentage difference
print('The average missing percentage of energy in the intensity data is: ' + str(energy_by_end_use['diff_percentage'].mean()))
#The average missing percentage of energy in the intensity data is: 0.44187177629088087
#########
#thats quite a lot... we should try to find a way to estimate this
#finally cal;cualte the percent that each of those end uses makes up of the total:

#%%
energy_by_end_use_other = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES)) & (~eei['end_use'].isin(intensity.end_use.unique()) & (eei.fuel=='all'))].copy()
energy_by_end_use_other = energy_by_end_use_other.groupby(['economy','year','end_use','sector']).sum().reset_index()[['economy','year','value','end_use','sector']]
#join total onto this and calculate the percentage
energy_by_end_use_other = energy_by_end_use_other.merge(energy_total, on=['economy','year','sector'], suffixes=('_end_use','_total'))
energy_by_end_use_other['percentage'] = (energy_by_end_use_other['value_end_use']/energy_by_end_use_other['value_total'])*100
#########
#plot the percentage of the total that each of these end uses make up
fig = px.line(energy_by_end_use_other, x='year', y='percentage', color='end_use', facet_col='economy', facet_col_wrap=3, line_dash='sector')
fig.write_html('plotting_output/analysis/energy_by_end_use_others.html')
#########
#%%
#calcaulte their weighted average intensity, weighted by the amount of years before the latest year, so that the most recent data is weighted the most

#first we need to attach population to them and then calcualte intensity. we will use the population in that dataset for this:
population = eei[eei.measure=='population'].copy()
#sum up the population by economy and year
population = population.groupby(['economy','year']).sum().reset_index()[['economy','year','value']]
#merge the population onto the energy data
intensity_other = energy_by_end_use_other.merge(population[['economy','year', 'value']], on=['economy','year'], suffixes=('_energy','_population'))[['economy','year','value_end_use','end_use','value','sector']].rename(columns={'value':'value_population', 'value_end_use':'value_energy'})
#calculate the intensity
intensity_other['intensity'] = intensity_other['value_energy']/intensity_other['value_population']

#lets jsut recalculate intensity for the original data to make sure we are doing it correctly
intensity_original = eei.loc[(eei['measure'] == 'energy') & (eei['end_use'].isin(intensity.end_use.unique()) & (eei.fuel=='all'))].copy()
intensity_original = intensity_original.groupby(['economy','year','end_use','sector']).sum().reset_index()[['economy','year','value','end_use','sector']]
intensity_original = intensity_original.merge(population[['economy','year', 'value']], on=['economy','year'], suffixes=('_energy','_population'))[['economy','year','value_energy','end_use','value_population','sector']]
intensity_original['intensity'] = intensity_original['value_energy']/intensity_original['value_population']

#concat with the intensity data
intensity_prev = intensity.loc[intensity.per=='capita'][['economy','year','end_use','value','sector']].rename(columns={'value':'intensity_prev'})

intensity_calculated = pd.concat([intensity_original, intensity_other], axis=0)
#%%
intensity_all = intensity_prev.merge(intensity_calculated, on=['economy','end_use','sector', 'year'], suffixes=('_current','_prev'), how='right')

#where not nan, find the difference between the intensity and the calculated intensity
intensity_all['diff'] = intensity_all['intensity_prev'] - intensity_all['intensity']
intensity_all['diff_percentage'] = intensity_all['diff']/intensity_all['intensity_prev']
#set any infs to nan
intensity_all = intensity_all.replace([np.inf, -np.inf], np.nan)
##calc the average absolute difference. have to drop the non_apec_iea economy as it isnt calcaulting right since we would have needed to get a weighted average of non_apec_iea for the intensity data
print('The average absolute difference between the calculated intensity and the intensity in the data is: ' + str(intensity_all.loc[intensity_all.economy!='non_apec_iea']['diff_percentage'].dropna().mean()))
#The average absolute difference between the calculated intensity and the intensity in the data is: 6.838644604046977e-05

#%%
#ok looks like we are doing it right. now we can use this to project the energy use over the projection period


#NOTE THAT WE ARE MISSING SOME COMBINATIONS OF END USES AND SECTORS IN THE INTENSITY DATA. WE SHOULD TRY TO FIND A WAY TO ESTIMATE THESE:
#set any 0's to na in intensity
intensity_all.loc[intensity_all['intensity']==0, 'intensity'] = np.nan
#find the missing combinations
available_combinations = intensity_all.loc[intensity_all['intensity'].notna()][['end_use','sector', 'economy']].drop_duplicates()
#find combinations that are missing
all_combinations = intensity_all[['end_use','sector', 'economy']].drop_duplicates()
missing_combinations = all_combinations.loc[~all_combinations.set_index(['end_use','sector', 'economy']).index.isin(available_combinations.set_index(['end_use','sector', 'economy']).index)]

#%%

#calcualte average of the available intensities for each end use and sector, weigthted by the amount of years before the latest year, so that the most recent data is weighted the most.
# Unfortunately we cant do this just by timesing the intensity by the inverse of year difference, since that would jsut decrease the intensity of the least recent data, which is not actually decreasing the impact of that intensity on the average. 
# We need to weight the intensity by the amount of years so the most recent data is MOST INFLUENTIAL on the average.
new_data = pd.DataFrame(columns=['economy','end_use','sector','intensity'])
for year in range(intensity_all['year'].max(), intensity_all['year'].min() - 1, -1):
    print(year)
    new_data_year = intensity_all.loc[intensity_all['year']==year][['economy','end_use','sector','intensity']].copy()
    new_data_year.dropna(subset=['intensity'], inplace=True)
    new_data = pd.concat([new_data, new_data_year], axis=0)
    #average out the intensity for each end use and sector
    new_data= new_data.groupby(['end_use','sector','economy']).mean().reset_index()
   
#that gives us the average intensity for each end use and sector. now we can use this to estimate the missing intensities 
#now calculate the average intensity for each end use and sector so we can use it for missing economies or rows
new_data_no_economy = new_data.groupby(['end_use','sector']).mean(numeric_only=True).reset_index()

#%%
#generate a dataframe with every unique combination of economy, end use, and sector, which will also include theunique economies in population_9th
unique_economies = population_9th['economy_code'].unique()

all_combinations_no_economy = all_combinations[['end_use','sector']].drop_duplicates()
all_combinations_no_economy['key'] = 0
unique_economies = pd.DataFrame(unique_economies, columns=['economy'])
unique_economies['key'] = 0
all_combinations_no_economy = all_combinations_no_economy.merge(unique_economies, on='key', how='outer')
all_combinations_no_economy.drop(columns='key', inplace=True)

#merge the average intensity onto this dataframe. then where missing we can use the average intensity without the economy
all_combinations_no_economy = all_combinations_no_economy.merge(new_data, on=['end_use','sector','economy'], how='left')
all_combinations_final = all_combinations_no_economy.merge(new_data_no_economy, on=['end_use','sector'], suffixes=('','_no_economy'), how='left')
#label where we are using an average or original intensity value
all_combinations_final['source'] = 'original'
all_combinations_final.loc[all_combinations_final['intensity'].isna(), 'source'] = 'average'
all_combinations_final['intensity'] = all_combinations_final['intensity'].fillna(all_combinations_final['intensity_no_economy'])
all_combinations_final.drop(columns=['intensity_no_economy'], inplace=True)

final_intensity = all_combinations_final.copy()
final_population = population_9th[['economy_code','year','value']].rename(columns={'economy_code':'economy'}).copy()
#divide population by 1million since thats the unit of the intensity data
final_population['value'] = final_population['value']/1e6
#%%
#now we have a quick estiamte of intensity.We should times these by population in population 9th, then plot each economy by end use and sector and year!

#merge the population onto the intensity data
all_combinations_final = final_intensity.merge(final_population, on=['economy'], how='left')
#calcaulte the energy use
all_combinations_final['energy'] = (all_combinations_final['intensity']*all_combinations_final['value'])#/1e6#divide by 1 million to get the energy in PJ

#concat sector and end use
all_combinations_final['end_use_sector'] = all_combinations_final['end_use'] + ' - ' + all_combinations_final['sector']
#plot the energy use by end use and sector for each economy
fig = px.area(all_combinations_final, x='year', y='energy', color='end_use_sector', facet_col='economy', facet_col_wrap=7)
#make axes indepent

fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html('plotting_output/analysis/energy_use_by_end_use_sector.html')
#%%


#now lets scale the data to have the total energy equal the total energy for buildings in esto_energy:
#extract the data from esto_energy for the following:
# sectors	sub1sectors	sub2sectors
# 16_other_sector	16_01_buildings	16_01_01_commercial_and_public_services
# 16_other_sector	16_01_buildings	16_01_02_residential

esto_energy_buildings = esto_energy.loc[(esto_energy['sectors']=='16_other_sector') & (esto_energy['sub1sectors']=='16_01_buildings') & (esto_energy['sub2sectors'].isin(['16_01_01_commercial_and_public_services','16_01_02_residential']))].copy()
#FOR NOW JSUT DROP THE target sceanrio 
esto_energy_buildings = esto_energy_buildings.loc[esto_energy_buildings['scenarios']!='target'].copy()
esto_energy_buildings = esto_energy_buildings.loc[esto_energy_buildings['is_subtotal']==False].copy()
#keep only fiuel == total for now
esto_energy_buildings = esto_energy_buildings.loc[esto_energy_buildings['fuels']=='19_total'].copy()
#drop is_subtotal
esto_energy_buildings.drop(columns='is_subtotal', inplace=True)
#%%
#make it tall byfinding the year cols and then melting
year_cols = [col for col in esto_energy_buildings.columns if re.match(r'\d{4}', col)]
#other cols are scenarios	economy	sectors	sub1sectors	sub2sectors	sub3sectors	sub4sectors	fuels	subfuels
#for
esto_energy_melt = esto_energy_buildings.melt(id_vars=['scenarios','economy','sectors','sub1sectors','sub2sectors','sub3sectors','sub4sectors','fuels','subfuels'], value_vars=year_cols, var_name='year', value_name='energy_esto')

#%%
#in our other df, rename the sectors to match the esto_energy_melt df
sector_map_dict = {
    'residential':'16_01_02_residential',
    'services':'16_01_01_commercial_and_public_services'
}

projection_df = all_combinations_final.copy()
projection_df['sub2sectors'] = projection_df['sector'].map(sector_map_dict)

#clean up all_combinations_final so we have the measures in one column, remove end_use_sector
projection_df.drop(columns=['end_use_sector','value', 'sector','source'], inplace=True)
#%%
# projection_df_melt = projection_df.melt(id_vars=['economy','year','sub2sectors','end_use'], value_vars=['energy', 'intensity'], var_name='measures', value_name='value')#['end_use', 'economy', 'intensity',  'year', 'energy','sub2sectors'

projection_df_energy = projection_df.drop(columns='intensity')
#sum projection_df by syb2sectors and year and economy
projection_df_energy = projection_df_energy.groupby(['economy','year','sub2sectors']).sum(numeric_only=True).reset_index()
#merge with esto_energy_melt
projection_df['year'] = projection_df['year'].astype(int)
esto_energy_melt['year'] = esto_energy_melt['year'].astype(int)
projection_df_merge = projection_df_energy.merge(esto_energy_melt, on=['economy','year','sub2sectors'], how='outer', suffixes=('','_esto'))

#calcualte the ratio of the energy to the energy in esto_energy
projection_df_merge['ratio_to_esto'] = projection_df_merge['energy']/projection_df_merge['energy_esto']
projection_df_merge = projection_df_merge.replace([np.inf, -np.inf], np.nan)#this is where we are missing data
#%%
#now times those by itnenisty so we can reproject the energy
projection_df_intensity = projection_df.drop(columns='energy').copy()
#merge on the ratio
projection_df_intensity = projection_df_intensity.merge(projection_df_merge[['economy','year','sub2sectors','ratio_to_esto']], on=['economy','year','sub2sectors'], how='left')
#times the intensity by the ratio
projection_df_intensity['intensity'] = projection_df_intensity['intensity']/projection_df_intensity['ratio_to_esto']

new_scaled_projection_df = projection_df_intensity.copy()
new_scaled_projection_df = new_scaled_projection_df.drop(columns='ratio_to_esto')

#just pad the intensity out from the max year where it is available. this will essentially give us the intensity for the base year for the projection
new_scaled_projection_df['intensity'] = new_scaled_projection_df.groupby(['economy','sub2sectors', 'end_use'])['intensity'].transform(lambda x: x.fillna(method='pad'))
#change year to int
new_scaled_projection_df['year'] = new_scaled_projection_df['year'].astype(int)
#%%


new_scaled_projection_df_merge = new_scaled_projection_df.merge(final_population, on=['economy', 'year'], how='left')

#calcaulte the energy use
new_scaled_projection_df_merge['energy'] = (new_scaled_projection_df_merge['intensity']*new_scaled_projection_df_merge['value'])#/1e6#divide by 1 million to get the energy in PJ
new_scaled_projection_df_merge['end_use_sector'] = new_scaled_projection_df_merge['end_use'] + ' - ' + new_scaled_projection_df_merge['sub2sectors']

#plot
fig = px.area(new_scaled_projection_df_merge, x='year', y='energy', color='end_use_sector', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html('plotting_output/analysis/energy_use_by_end_use_sector_scaled.html')
#%%
#plot the intensity against the intensity we ahd origainlly:
intensity_all_plot = intensity_all.copy()
intensity_all_plot['source'] = 'original'
intensity_all_plot['sub2sectors'] = intensity_all_plot['sector'].map(sector_map_dict)
intensity_all_plot=intensity_all_plot[['economy','year','end_use','intensity','source','sub2sectors']]
intensity_all_plot['year'] = intensity_all_plot['year'].astype(int)

intensity_plot = new_scaled_projection_df_merge.copy()
intensity_plot['source'] = 'scaled'
intensity_plot = intensity_plot[['economy','year','end_use','intensity','source','sub2sectors']]
intensity_plot = pd.concat([intensity_all_plot, intensity_plot], axis=0)

intensity_plot['end_use_sector'] = intensity_plot['end_use'] + ' - ' + intensity_plot['sub2sectors']
fig = px.line(intensity_plot, x='year', y='intensity', color='end_use_sector', facet_col='economy', facet_col_wrap=7, line_dash='source')

fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html('plotting_output/analysis/intensity_by_end_use_sector_scaled.html')
#%%
#plot the population
fig = px.line(new_scaled_projection_df_merge, x='year', y='value', color='economy')
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html('plotting_output/analysis/population_by_economy.html')
#%%
#plot the esto_energy_melt
fig = px.area(esto_energy_melt, x='year', y='energy_esto', color='sub2sectors', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html('plotting_output/analysis/energy_use_by_end_use_sector_esto.html')
#%%

#NOW TO PROVIDE a good comparison we will plot the energy use by sub2sectors and as line charts, and include the esto_energy_melt data as well as the 8th outlook data *it would be nice but dont have access to that yet!*
new_scaled_projection_df_merge_no_end_use = new_scaled_projection_df_merge[['economy','year','sub2sectors','energy']].groupby(['economy','year','sub2sectors']).sum().reset_index()
#remove years before config.BASE_YEAR
new_scaled_projection_df_merge_no_end_use = new_scaled_projection_df_merge_no_end_use.loc[new_scaled_projection_df_merge_no_end_use['year']>=config.BASE_YEAR].copy()

esto_energy_melt_plot = esto_energy_melt[['economy','year','sub2sectors','energy_esto']].rename(columns={'energy_esto':'energy'}).copy()
#remove years after config.BASE_YEAR
esto_energy_melt_plot = esto_energy_melt_plot.loc[esto_energy_melt_plot['year']<=config.BASE_YEAR].copy()
new_scaled_projection_df_merge_no_end_use['dataset'] = 'projection'
esto_energy_melt_plot['dataset'] = 'esto'
all_energy_line = pd.concat([new_scaled_projection_df_merge_no_end_use, esto_energy_melt_plot], axis=0)

fig = px.line(all_energy_line, x='year', y='energy', color='sub2sectors', facet_col='economy', facet_col_wrap=7, line_dash='dataset')

fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html('plotting_output/analysis/energy_use_by_sub2sectors.html')
# %%



#import 8th data :
cn_8th = pd.read_csv(os.path.join(config.root_dir, 'input_data', '8th_outlook_energy', 'OSeMOSYS_to_EGEDA_2020_netzero.csv'))
ref_8th = pd.read_csv(os.path.join(config.root_dir, 'input_data', '8th_outlook_energy', 'OSeMOSYS_to_EGEDA_2020_reference.csv'))

cn_8th['scenario'] = 'carbon neutrality'
ref_8th['scenario'] = 'reference'
all_8th = pd.concat([cn_8th, ref_8th], axis=0)
#filter for item_code_new:
# 16_1_commercial_and_public_services
# 16_2_residential

all_8th = all_8th.loc[all_8th['item_code_new'].isin(['16_1_commercial_and_public_services','16_2_residential'])].copy()
#filter for fuel_codes that arent subtotals (ughhhh)
#oh actually just get 19_total
all_8th = all_8th.loc[all_8th['fuel_code']=='19_total'].copy()
#make it tall
year_cols = [col for col in all_8th.columns if re.match(r'\d{4}', col)]
all_8th_melt = all_8th.melt(id_vars=['scenario','economy','item_code_new','fuel_code'], value_vars=year_cols, var_name='year', value_name='energy')
all_8th_melt['dataset'] = '8th ' + all_8th_melt['scenario']
#rename the item_code_new to sub2sectors
all_8th_melt['sub2sectors'] = all_8th_melt['item_code_new'].replace({'16_1_commercial_and_public_services':'16_01_01_commercial_and_public_services','16_2_residential':'16_01_02_residential'})
all_8th_melt.drop(columns=['scenario', 'item_code_new', 'fuel_code'], inplace=True)
#drop economies not in all_energy_line
all_8th_melt = all_8th_melt.loc[all_8th_melt['economy'].isin(all_energy_line['economy'].unique())].copy()

#drop all data that is 0's
all_8th_melt = all_8th_melt.loc[all_8th_melt['energy']!=0].copy()
#%%
HAVE_ALL_FIRST_ITERATION_DATA_BY_ECONOMY = False
if HAVE_ALL_FIRST_ITERATION_DATA_BY_ECONOMY:
    #and do the same for the files we are usign for first iteration of 9th:
    # \9th_outlook_energy\merged_file_energy_00_APEC_20240809.csv which will ahve the same formatting and structure as the esto data:
    outlook_9th = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', 'merged_file_energy_00_APEC_20240809.csv'))
    outlook_9th = outlook_9th.loc[outlook_9th['sub2sectors'].isin(['16_01_02_residential','16_01_01_commercial_and_public_services'])].copy()
    outlook_9th = outlook_9th.loc[outlook_9th['fuels']=='19_total'].copy()
    #and subtotal_layout	subtotal_results are false
    outlook_9th = outlook_9th.loc[outlook_9th['subtotal_layout']==False].copy()
    outlook_9th = outlook_9th.loc[outlook_9th['subtotal_results']==False].copy()
    outlook_9th.drop(columns=['subtotal_layout','subtotal_results'], inplace=True)
    outlook_9th_melt = outlook_9th.melt(id_vars=['scenarios','economy','sub2sectors','fuels'], value_vars=year_cols, var_name='year', value_name='energy')
    #ah damn i didnt realise this was only for the sum of 00_APEC. id need to get the data for the individual economies. jsut skip.

#NOW concat the 8th and 9th data to the all_energy_line df
all_8th_melt['year'] = all_8th_melt['year'].astype(int)
all_energy_line_plot = pd.concat([all_energy_line, all_8th_melt], axis=0)

fig = px.line(all_energy_line_plot, x='year', y='energy', color='sub2sectors', facet_col='economy', facet_col_wrap=7, line_dash='dataset')

fig.update_yaxes(matches=None, showticklabels=True)
fig.write_html('plotting_output/analysis/energy_use_by_sub2sectors_8th_comp.html')
# %%

