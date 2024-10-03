


#%% Import necessary libraries
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px

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

#%% Calculate proportion of energy by end use and fuel for each economy
#first filter for correct data:
eei_energy = eei.query("sector in ['residential', 'services'] and fuel in ['oil', 'gas', 'coal', 'biofuels', 'heat', 'electricity', 'other', 'solar_thermal', 'district_heating'] and end_use != 'total' and measure == 'energy'").rename(columns={'value': 'energy_eei'})

#drop per column
eei_energy = eei_energy.drop(columns='per')
#drop where end_use is na
eei_energy = eei_energy.dropna(subset=['end_use'])     

#we want to do some simplifciation of the end_uses. we want to group them into the following categories:
#these ar ethe end uses we ahve now: ['space_heating', 'space_cooling', 'lighting', 'cooking',
#        'non_building_energy_use', 'non_specified',
#        'other_building_energy_use', 'water_heating', 'clothes_dryers',
#        'clothes_washers', 'dish_washers', 'freezers', 'other_appliances',
#        'personal_computers', 'refrigerator_freezer_combinations',
#        'refrigerators', 'residential_appliances', 'televisions',
#        'accommodation_and_food', 'arts_entertainment_and_recreation',
#        'education', 'finance_insurance_real_estate_science_admin',
#        'health_and_social_work', 'information_and_communication',
#        'other_services', 'public_admin_excluding_defence',
#        'sewerage_waste_and_remediation',
#        'warehousing_support_for_transport_postal', 'wholesale_and_retail']
end_use_mapping = {
    'space_heating': ['space_heating'],
    'space_cooling': ['space_cooling'],
    'lighting': ['lighting'],
    'cooking': ['cooking'],
    'non_building_energy_use': ['non_building_energy_use'],
    'non_specified': ['non_specified'],
    'other_building_energy_use': ['other_building_energy_use'],
    'water_heating': ['water_heating'],
    'appliances':  ['clothes_dryers', 'clothes_washers', 'dish_washers', 'freezers', 'other_appliances', 'personal_computers', 'refrigerator_freezer_combinations', 'refrigerators', 'residential_appliances', 'televisions'],#im not sure if data is duplicated between some of these applicances? might be an issue to solve later
    'services': ['accommodation_and_food', 'arts_entertainment_and_recreation', 'education', 'finance_insurance_real_estate_science_admin', 'health_and_social_work', 'information_and_communication', 'other_services', 'public_admin_excluding_defence', 'sewerage_waste_and_remediation', 'warehousing_support_for_transport_postal', 'wholesale_and_retail'],
}

for key, value in end_use_mapping.items():
    eei_energy.loc[eei_energy['end_use'].isin(value), 'end_use'] = key

#REMOVE THE SERVICES END USE. THIS WAS DONE AFTER CAREFUL CONSIDERATION AND REALISING THAT IT WAS ONLY IN THE DATA FOR USA AND CHILE AND ONLY USED ELECTRICITY. WE REALISED IT WOULDNT AFFECT THE PROPORTIONS OF REMAINING END USES IN ELECTIRICYT/SERVICES SECTOR BECAUSETHE REAMINING END USES (LIGHTING,COOLING, HEATING) WERE ALL IN THE DATA FOR ALL COUNTRIES
eei_energy = eei_energy.query("end_use != 'services'")

#now sum up the energy use by 'scenarios', 'economy', 'fuels', 'subfuels','sector', 'end_use', 'year'
eei_energy = eei_energy.groupby(['country','end_use','measure','unit', 'economy', 'fuel', 'sector', 'year']).agg({'energy_eei': 'sum'}).reset_index()

#we also want to make sure that every 'country','measure','unit', 'economy',  'year' combination has every conbination of 'fuel', 'sector','end_use'so that our proportions can be compared across all combinations of these variables
# Extract unique combinations of 'country', 'measure', 'unit', 'economy', and 'year'
unique_combinations = eei_energy[['country', 'measure', 'unit', 'economy', 'year']].drop_duplicates()

# Extract unique combinations of 'fuel', 'sector', and 'end_use'
fuel_sector_end_use_combinations = eei_energy[['fuel', 'sector', 'end_use']].drop_duplicates()

# Create a Cartesian product of the two sets of combinations
cartesian_product = unique_combinations.merge(fuel_sector_end_use_combinations, how='cross')

# Merge the Cartesian product with the original DataFrame
eei_energy_complete = cartesian_product.merge(eei_energy, on=['country', 'measure', 'unit', 'economy', 'year', 'fuel', 'sector', 'end_use'], how='left')

eei_energy_complete = eei_energy_complete.fillna(0)

#%%
# Sum energy use by economy, sector, and end use
eei_energy_sum = eei_energy_complete.groupby(['economy', 'sector', 'end_use', 'fuel', 'year']).agg({'energy_eei': 'sum'}).reset_index()

# Method 1: Per economy - Calculate proportion for each end use within each economy
eei_energy_sum['energy_total_per_economy'] = eei_energy_sum.groupby(['economy', 'fuel', 'sector', 'year'])['energy_eei'].transform('sum')
eei_energy_sum['proportion_per_economy_avg'] = eei_energy_sum['energy_eei'] / eei_energy_sum['energy_total_per_economy']
#calc the average proportion per end use
average_proportion_per_end_use = eei_energy_sum.groupby(['sector', 'end_use', 'fuel',  'year']).agg({'proportion_per_economy_avg': 'mean'}).reset_index()
original_proportion_per_end_use = eei_energy_sum[['economy', 'sector', 'end_use', 'fuel',  'year', 'proportion_per_economy_avg']].copy()

# Method 2: Overall - Calculate proportion by summing energy across all economies
eei_energy_sum_total = eei_energy_sum.groupby(['sector', 'end_use', 'fuel',  'year']).agg({'energy_eei': 'sum'}).reset_index()
eei_energy_sum_total['energy_total'] = eei_energy_sum_total.groupby(['year','fuel',  'sector'])['energy_eei'].transform('sum')
eei_energy_sum_total['proportion_total'] = eei_energy_sum_total['energy_eei'] / eei_energy_sum_total['energy_total']

eei_proportions = eei_energy_sum_total.merge(average_proportion_per_end_use, on=['sector', 'end_use', 'fuel',  'year'], how='left')
#%% Fill missing intensity data using proportion-based estimation

# Create a dataframe for economies with missing data. they are jsut the economies who arent in the eei_intensity data
missing_economies = pd.DataFrame([eco for eco in esto_energy_melt['economy'].unique() if eco not in eei_energy_sum['economy'].unique()], columns=['economy'])
missing_economies['key'] = 1
eei_proportions['key'] = 1
#%%
missing_economy_proportions = missing_economies.merge(eei_proportions[['sector', 'end_use', 'fuel',  'year', 'proportion_per_economy_avg', 'proportion_total','key']], on='key', how='left')

#and where original_proportion_per_end_use is missing a proportion, join on the value from eei_proportions:
original_proportion_per_end_use = original_proportion_per_end_use.merge(eei_proportions[['sector', 'end_use', 'fuel',  'year', 'proportion_per_economy_avg', 'proportion_total']], on=['sector', 'end_use', 'fuel',  'year'], how='left', suffixes=('', '_eei'))
USE_AVERAGE_PROPORTION_PER_ECONOMY =True
USE_TOTAL_PROPORTION_ACROSS_ECONOMIES = False
if USE_AVERAGE_PROPORTION_PER_ECONOMY:
    original_proportion_per_end_use['proportion_per_economy_avg'] = original_proportion_per_end_use['proportion_per_economy_avg'].fillna(original_proportion_per_end_use['proportion_per_economy_avg_eei'])    
elif USE_TOTAL_PROPORTION_ACROSS_ECONOMIES:
    original_proportion_per_end_use['proportion_per_economy_avg'] = original_proportion_per_end_use['proportion_per_economy_avg'].fillna(original_proportion_per_end_use['proportion_total'])
#drop proportion_per_economy_avg_eei
original_proportion_per_end_use = original_proportion_per_end_use.drop(columns=['proportion_per_economy_avg_eei'])
#but note that this might now mean that if an economy was missing an end use in the eei data (which does happen) value and we inserted one, the proportions within each sector, year, economy, fuel combination might no longer sum to 1.
#so double check that they do after bringing everything together

all_proportions = pd.concat([original_proportion_per_end_use, missing_economy_proportions], ignore_index=True)

#remove key and also where proportion_per_economy_avg is missing, replace it with proportion_total
all_proportions = all_proportions.drop(columns='key')

#check that the proportions sum to 1
all_proportions_test = all_proportions.groupby(['sector', 'fuel', 'year', 'economy']).agg({'proportion_per_economy_avg': 'sum', 'proportion_total':'sum'}).reset_index().copy()
all_proportions_test['diff1'] = all_proportions_test['proportion_per_economy_avg'] - 1
all_proportions_test['diff2'] = all_proportions_test['proportion_total'] - 1
if len(all_proportions_test.loc[(abs(all_proportions_test['diff1']) > 0.0001) | (abs(all_proportions_test['diff2']) > 0.0001)]) > 0:
    raise ValueError('Proportions do not sum to 1')
# print(all_proportions_test.loc[(abs(all_proportions_test['diff1']) > 0.0001) | (abs(all_proportions_test['diff2']) > 0.0001)])

#%% Estimate energy for missing economies using calculated proportions
esto_energy_melt_new =esto_energy_melt.copy()

esto_energy_melt_new['sector'] = esto_energy_melt['sub2sectors'].map({'16_01_01_commercial_and_public_services': 'services', '16_01_02_residential': 'residential'})
#%%
#map the fuels to the eei data:
# 01_coal	01_01_coking_coal
# 01_coal	01_05_lignite
# 01_coal	01_x_thermal_coal
# 02_coal_products	x
# 03_peat	x
# 04_peat_products	x
# 07_petroleum_products	07_01_motor_gasoline
# 07_petroleum_products	07_02_aviation_gasoline
# 07_petroleum_products	07_03_naphtha
# 07_petroleum_products	07_06_kerosene
# 07_petroleum_products	07_07_gas_diesel_oil
# 07_petroleum_products	07_08_fuel_oil
# 07_petroleum_products	07_09_lpg
# 07_petroleum_products	07_10_refinery_gas_not_liquefied
# 07_petroleum_products	07_11_ethane
# 07_petroleum_products	07_x_jet_fuel
# 07_petroleum_products	07_x_other_petroleum_products
# 08_gas	08_01_natural_gas
# 08_gas	08_02_lng
# 08_gas	08_03_gas_works_gas
# 11_geothermal	x
# 12_solar	12_01_of_which_photovoltaics
# 12_solar	12_x_other_solar
# 15_solid_biomass	15_01_fuelwood_and_woodwaste
# 15_solid_biomass	15_02_bagasse
# 15_solid_biomass	15_03_charcoal
# 15_solid_biomass	15_04_black_liquor
# 15_solid_biomass	15_05_other_biomass
# 16_others	16_01_biogas
# 16_others	16_02_industrial_waste
# 16_others	16_03_municipal_solid_waste_renewable
# 16_others	16_04_municipal_solid_waste_nonrenewable
# 16_others	16_05_biogasoline
# 16_others	16_06_biodiesel
# 16_others	16_07_bio_jet_kerosene
# 16_others	16_08_other_liquid_biofuels
# 16_others	16_09_other_sources
# 16_others	16_x_ammonia
# 16_others	16_x_efuel
# 16_others	16_x_hydrogen
# 17_electricity	x
# 18_heat	x
# 16_others	x
# 01_coal	x
# 07_petroleum_products	x
# 08_gas	x
# 12_solar	x
# 15_solid_biomass	x
# 06_crude_oil_and_ngl	06_01_crude_oil
# 06_crude_oil_and_ngl	06_02_natural_gas_liquids

esto_energy_melt_new['fuel'] = esto_energy_melt_new['fuels'].map({'01_coal': 'coal','02_coal_products':'coal', '03_peat':'coal','04_peat_products':'coal','08_gas': 'gas', '07_petroleum_products': 'oil', '15_solid_biomass': 'biofuels', '11_geothermal':'other', '18_heat': 'heat', '17_electricity': 'electricity', '16_others': 'other', '12_solar': 'other', '06_crude_oil_and_ngl': 'oil'})
#there is one sepcific one: we have to map sub_fuels for 12_x_other_solar where sector is residential to solar_thermal (but not where sector is services because the eei data only assumes there is solar thermal in the residential sector - whereas esto data doesnt make this distinction which seems about right to me!) -  this might mean we end up with weird step changes for solar thermal but we'll see how it goes
esto_energy_melt_new.loc[(esto_energy_melt_new['subfuels'] == '12_x_other_solar') & (esto_energy_melt_new['sector'] == 'residential'), 'fuel'] = 'solar_thermal'

#now join on the proportions. we will join on sector, end_use, fuel and year. this will give us multiple new rows for each row in esto_energy_melt_new. Then we just times the proportion by the energy use to get the estimated energy use for each combination of fuel, subfuel, end use, sector and economy
esto_energy_melt_merge = esto_energy_melt_new.merge(all_proportions, on=['sector', 'fuel', 'year', 'economy'], how='inner')

#%%
##################################################################################################################################################################################################################################################################################################################################################################

#one issue with what we'r doing is we're assigining ends uses to subfuels that are obviously not correct, for example 
# subfuels	year	energy_esto	sector	fuel	end_use	proportion_per_economy_avg
# 07_01_motor_gasoline	2000	0	residential	oil	cooking	0.148779771
#this means that we're assigining 15% of motor gasoline to cooking. This is obviously wrong. But for now we'll just leave it as is.

#now we can calculate the estimated energy use
USE_AVERAGE_PROPORTION_PER_ECONOMY = True
USE_TOTAL_PROPORTION_ACROSS_ECONOMIES = False
if USE_AVERAGE_PROPORTION_PER_ECONOMY:
    esto_energy_melt_merge['estimated_energy'] = esto_energy_melt_merge['energy_esto'] * esto_energy_melt_merge['proportion_per_economy_avg']
elif USE_TOTAL_PROPORTION_ACROSS_ECONOMIES:
    esto_energy_melt_merge['estimated_energy'] = esto_energy_melt_merge['energy_esto'] * esto_energy_melt_merge['proportion_total']

#simplfiy the df:
# scenarios	economy	fuels	subfuels end_use estimated_energy sector
all_data = esto_energy_melt_merge[['scenarios', 'economy', 'fuels', 'subfuels','sector', 'end_use', 'estimated_energy', 'year']].copy()

#%%
#double check the total energy use is the same as teh original esto total
#first make sure we have the same years in botj
esto_energy_melt_test = esto_energy_melt.loc[esto_energy_melt['year'].isin(all_data['year'].unique())].copy()
if not np.isclose(esto_energy_melt_test['energy_esto'].sum(), all_data['estimated_energy'].sum()):
    #look at it by year and sector:
    esto_energy_melt_test['sector'] = esto_energy_melt_test['sub2sectors'].map({'16_01_01_commercial_and_public_services': 'services', '16_01_02_residential': 'residential'})
    esto_energy_melt_test = esto_energy_melt_test.groupby(['economy','year', 'sector', 'fuels', 'subfuels']).agg({'energy_esto': 'sum'}).reset_index()
    all_data_test = all_data.groupby(['economy','year', 'sector', 'fuels', 'subfuels']).agg({'estimated_energy': 'sum'}).reset_index()
    #join them and see where they differ
    test = esto_energy_melt_test.merge(all_data_test, on=['economy','year', 'sector', 'fuels', 'subfuels'], how='outer', suffixes=('_esto', '_estimated'))
    #check for any nas in the data
    if len(test.loc[test['energy_esto'].isna()]) > 0:
        print(test.loc[test['energy_esto'].isna()])
    if len(test.loc[test['estimated_energy'].isna()]) > 0:
        print(test.loc[test['estimated_energy'].isna()])
    test['diff'] = abs(test['energy_esto'].fillna(0) - test['estimated_energy'].fillna(0))
    if len(test.loc[test['diff'] > 0.0001]) > 0:
        print(test.loc[test['diff'] > 0.0001])
#%%

#Join on population
aperc_population = macro.query("variable == 'population'")[['economy_code', 'year', 'value']].rename(columns={'economy_code': 'economy', 'value': 'population'})

all_data = all_data.merge(aperc_population, on=['economy', 'year'], how='left')

#calculate intensity by end use and subfuel and year and economy
all_data['intensity'] = all_data['estimated_energy'] / all_data['population']

#%%
#great.

#now we can save this data and then do some analysis
import datetime as datetime
file_date_id = datetime.datetime.now().strftime('%Y%m%d')
all_data.to_csv(os.path.join(config.root_dir, 'output_data', f'energy_and_intensity_by_end_use_subfuels.csv'), index=False)
#%%

#we want to check out how intensity looks by end use and subfuel and how it varies for all the combinations.
#we can do this by plotting a box plot with x = subfuel, y=itnensity, faet= end use, color = economy
all_data_plot = all_data.loc[all_data['scenarios'] =='reference']
for sector in all_data_plot['sector'].unique():
    fig = px.scatter(all_data_plot.query(f"sector == '{sector}'"), x='fuels', y='intensity', facet_col='end_use', color='economy', facet_col_wrap=3)
    fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis','b2_split_esto_into_end_use',  f'energy_and_intensity_by_end_use_subfuels_{sector}.html'))
    
#and show a area chart of the total energy use by end use and subfuel and economy
# all_data_plot = all_data.copy()
# all_data_plot['sector - end_use'] = all_data_plot['sector'] + ' - ' + all_data_plot['end_use']
all_data_plot2 = all_data_plot.groupby(['economy', 'year', 'end_use', 'sector']).agg({'estimated_energy': 'sum'}).reset_index()
#order by sector
all_data_plot2['sector'] = pd.Categorical(all_data_plot2['sector'], ['residential', 'services'])
all_data_plot2 = all_data_plot2.sort_values('sector')

fig = px.area(all_data_plot2, x='year', y='estimated_energy', color='end_use', facet_col='economy', pattern_shape='sector', facet_col_wrap=7)

fig.write_html(os.path.join(config.root_dir, 'plotting_output', 'analysis', 'b2_split_esto_into_end_use', f'energy_by_end_use_subfuels.html'))

#%%
