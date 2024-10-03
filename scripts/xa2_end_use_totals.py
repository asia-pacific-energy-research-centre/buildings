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

economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
#%%

#first we need to get the population data
population_9th = macro.loc[macro['variable'] == 'population'].copy()
population_9th['value'] = population_9th['value']*1e3#convert from thousands to individuals
# END_USES = ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances', 'space_heating', 'space_cooling', 'lighting']
END_USES = ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances']
# END_USES = ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances', 'non_specified', 'space_heating', 'space_cooling', 'lighting', 'other_building_energy_use', 'non_building_energy_use']
intensity = eei.loc[(eei['measure'] == 'energy_intensity') & (eei.end_use.isin(END_USES))].copy()
intensity.end_use.unique()
#array(['space_heating', 'space_cooling', 'lighting', 'water_heating',
#    'cooking', 'residential_appliances'], dtype=object)

#%%
#double check that this covers all intended end uses by checking that the sum of energy is the same as the total:
# IEA data
# filter for total fuel use for each end use
energy_by_end_use1 = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES)) & (eei['fuel']=='all')].copy()
energy_by_end_use = energy_by_end_use1.loc[energy_by_end_use1['economy'].isin(economy_list['economy_code'])].copy()


energy_total = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(['total'])) & (eei['fuel']=='all')].copy()
# energy_total_by_end_use = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES)) & (eei['fuel']=='all')]

# & (eei.end_use.isin([END_USES])) 
# %%
#########
output_dir = config.root_dir + '/testing/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# This is the IEA reported total energy each year per end use
# What I need to calculate the ratio of fuel in each end use. Need to merge this on to the sheet with fuel breakdown of each end use
energy_by_end_use.to_csv(output_dir + '/energy_by_end_use.csv', index=False)
# country	end_use	measure	per	unit	economy	fuel	sector	year	value

# IEA totals for each end use
# energy_total_by_end_use.to_csv(output_dir + '/energy_total_by_end_use.csv', index=False)

# This is IEA total not separated by end use
energy_total.to_csv(output_dir + '/test_energy_total.csv', index=False)

# %%
energy_annual_total_IEA = energy_total[energy_total['economy'].isin(economy_list['economy_code'])]
energy_annual_total_IEA.to_csv(output_dir + '/energy_annual_total_IEA.csv', index=False)

# %%
for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df = energy_by_end_use[energy_by_end_use['economy'] == economy]

    # Create the plot
    fig = px.line(filtered_df, x='year', y='value', color='sector', facet_col='end_use', facet_col_wrap=3)
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Save the plot to an HTML file
    output_file = output_dir + f'{economy}_IEA_energy_by_end_use.html'
    fig.write_html(output_file)

# %%
# To determine the proportion of total of each fuel type in each end use
end_use_energy = eei.loc[eei['fuel'] != 'all'].copy()
end_use_energy2 = end_use_energy.loc[end_use_energy['measure'] == 'energy'].copy()
end_use_energy3 = end_use_energy2[end_use_energy2['economy'].isin(economy_list['economy_code'])].copy()
end_use_energy4 = end_use_energy3[end_use_energy3['end_use'].isin(END_USES)]
end_use_energy_breakdown = end_use_energy4.copy()
# country	end_use	measure	per	unit	economy	fuel	sector	year	value
# This sheet is the IEA by fuel break down of end uses. 
# Need to take the totals of each end use in each ear from the energy by end use sheet and merge it on, so then I can divide to get the ratios

# %%
# set up sheets to merge, can get rid of country column 
# end_use_energy_breakdown # fuel breakdown
# energy_by_end_use # is the totals that need to be merged onto the above sheet

end_uses_merged = end_use_energy_breakdown.merge(energy_by_end_use[['economy', 'end_use', 'sector', 'year', 'fuel', 'value']], on=['economy', 'end_use', 'sector', 'year'], how='left', suffixes=('', '_total'))
end_uses_merged['ratio'] = end_uses_merged['value'] / end_uses_merged['value_total']
end_uses_merged = end_uses_merged.drop(['country', 'per', 'fuel_total'], axis=1).copy()

# %%

# plot 
output_dir = config.root_dir + '/testing/end_uses_IEA/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

end_uses_merged.to_csv(output_dir + 'end_use_by_fuel_ratio.csv', index=False)

# plotting direct values from IEA data

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df_economy = end_uses_merged[(end_uses_merged['economy'] == economy)]

    # Create the plot
    fig = px.line(filtered_df_economy, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Save the plot to an HTML file
    output_file = output_dir + f'{economy}_energy_projection_use_by_end_use_line.html'
    fig.write_html(output_file)

# for sectors

sectors = ('residential', 'services')

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df_economy = end_uses_merged[(end_uses_merged['economy'] == economy)]

    for sector in sectors:

        filtered_df = filtered_df_economy[(filtered_df_economy['sector'] == sector)]
        # Create the plot
        # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig = px.area(filtered_df, x='year', y='value', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig.update_yaxes(matches=None, showticklabels=True)
        
        # Save the plot to an HTML file
        output_file = output_dir + f'{economy}_{sector}_energy_projection_use_by_end_use_area.html'
        fig.write_html(output_file)

# %%
# energy_annual_total_IEA  # total for each year from IEA for each subsector
# energy_by_end_use # total for each subsector for each end use

# need to merge total for each year/econ/subsector onto the data with breakdown by end use
# then determine the ratio of where the energy is going, ie how much to each end use

ratio_of_end_use_in_total_IEA = energy_by_end_use.merge(energy_annual_total_IEA[['economy', 'sector', 'year','value']], on=['economy', 'sector', 'year'], how='left', suffixes=('', '_total'))
ratio_of_end_use_in_total_IEA['ratio_of_end_use_in_total'] = ratio_of_end_use_in_total_IEA['value'] / ratio_of_end_use_in_total_IEA['value_total']                                                        

ratio_of_end_use_in_total_IEA.rename(columns={'sector' : 'sub2sectors'}, inplace=True)

ratio_of_end_use_in_total_IEA.to_csv(output_dir + '/ratio_of_end_use_in_total_IEA.csv', index=False)

ratio_of_end_use_in_total_IEA['sub2sectors'].replace({
    'residential': '16_01_02_residential',
    'services': '16_01_01_commercial_and_public_services'
}, inplace=True)


# %%
# Check that sum and ratio is correct
# grouped_df = ratio_of_end_use_in_total_IEA.groupby(['economy', 'year', 'sector'])['ratio_of_end_use_in_total'].sum().reset_index()
# grouped_df.to_csv(output_dir + '/groupeddf.csv')
# They don't equal 1. Issues with data persist in buildings. Probably fine to get an estimate to help projections and conceptualize what is going on more easily for me/economy leads. 
# Can use the ratio to multiply against ESTO totals to see end use split. #################################################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Need to now get ratio of fuel in each end use. Then can see how end uses may change, and then from that, incorporate fuel switching. 

# %%

# Put ESTO total energy by year, economy, sector onto the ratio_of_end_use_in_total_IEA.csv to calculate the proportion of each end use in esto energy as estimate
esto_energy_filtered = esto_energy[(esto_energy['fuels'] == '19_total') & (esto_energy['sub1sectors'] == '16_01_buildings') & (esto_energy['is_subtotal'] == False)]
esto_energy_filtered = esto_energy_filtered.drop(['is_subtotal'], axis=1).copy()

year_cols = [col for col in esto_energy_filtered.columns if re.match(r'\d{4}', col)]
esto_energy_filtered_melt = esto_energy_filtered.melt(id_vars=['scenarios','economy','sectors','sub1sectors','sub2sectors','sub3sectors','sub4sectors','fuels','subfuels'], value_vars=year_cols, var_name='year', value_name='energy_esto')

esto_energy_filtered_melt['year'] = esto_energy_filtered_melt['year'].astype(int)
esto_energy_filtered_melt = esto_energy_filtered_melt[(esto_energy_filtered_melt['year'] <= 2021) & (esto_energy_filtered_melt['year'] >= 2000)].copy()

#   REF ONLY FOR NOW
esto_energy_filtered_melt_ref = esto_energy_filtered_melt[esto_energy_filtered_melt['scenarios'] == 'reference']


# filtered_df_economy = end_uses_merged[(end_uses_merged['economy'] == economy)]
# print(esto_energy_filtered['sub1sectors'].unique())

# %%

# ratio_of_end_use_in_total_IEA
# esto_energy_filtered_melt_ref

# end_uses_totals_merged = ratio_of_end_use_in_total_IEA.merge
# (esto_energy_filtered_melt_ref['economy', 'sub2sectors', 'year', 'energy_esto'], 
# on=['economy', 'end_use', 'sector', 'year', 'fuel'], how='left', suffixes=('', '_total'))
                                                             

# Perform the merge on 'economy', 'sub2sectors', and 'year'
end_uses_totals_merged = ratio_of_end_use_in_total_IEA.merge(esto_energy_filtered_melt_ref[['economy', 'sub2sectors', 'year', 'energy_esto']],
                      on=['economy', 'sub2sectors', 'year'], 
                      how='left',  # 'left' keeps all rows from df1 and adds matching data from df2
                      suffixes=('', '_esto'))

# end_uses_merged = end_use_energy_breakdown.merge(energy_by_end_use[['economy', 'end_use', 'sector', 'year', 'fuel', 'value']], on=['economy', 'end_use', 'sector', 'year'], how='left', suffixes=('', '_total'))
# end_uses_merged['ratio'] = end_uses_merged['value'] / end_uses_merged['value_total']
# end_uses_merged = end_uses_merged.drop(['country', 'per', 'fuel_total'], axis=1).copy()

# %%
energy_end_use_esto_times_ratio = end_uses_totals_merged.copy()
energy_end_use_esto_times_ratio['end_use_energy_use_PJ'] = energy_end_use_esto_times_ratio['ratio_of_end_use_in_total'] * energy_end_use_esto_times_ratio['energy_esto']

# this is the iea derived end use ratios times the esto provided total energy data
# not for all economies as not all econs have IEA info
# %%
# plot of the ratios

output_dir = config.root_dir + '/testing/end_uses_ratios/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

energy_end_use_esto_times_ratio.to_csv(output_dir + 'energy_end_use_esto_totals.csv', index=False)

sectors = ('16_01_02_residential', '16_01_01_commercial_and_oublic_services')

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df = energy_end_use_esto_times_ratio[(energy_end_use_esto_times_ratio['economy'] == economy)]

    # Create the plot
    # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
    fig = px.area(filtered_df, x='year', y='ratio_of_end_use_in_total', color='end_use', facet_col='sub2sectors', facet_col_wrap=2)
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Save the plot to an HTML file
    output_file = output_dir + f'{economy}_{sector}_end_use_ratio.html'
    fig.write_html(output_file)
# %%
# plot of the energy breakdown from ratio x ESTO energy total

output_dir = config.root_dir + '/testing/end_uses_energy_breakdown/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


sectors = ('16_01_02_residential', '16_01_01_commercial_and_oublic_services')

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df = energy_end_use_esto_times_ratio[(energy_end_use_esto_times_ratio['economy'] == economy)]

    # Create the plot
    # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
    fig = px.area(filtered_df, x='year', y='end_use_energy_use_PJ', color='end_use', facet_col='sub2sectors', facet_col_wrap=2)
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Save the plot to an HTML file
    output_file = output_dir + f'{economy}_{sector}_end_use_ratio.html'
    fig.write_html(output_file)

# %%
# plot using the fuel split breakdown for each end use