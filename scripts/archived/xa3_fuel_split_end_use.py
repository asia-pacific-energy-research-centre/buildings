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

#NOTE THAT WE WILL MOVE THESE IMPORTS AND SO ON ONCE WE HAVE THE FINAL STRUCTURE OF THE PROJECT
#import apec macro data
macro_date_id = x3_utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', 'macro'), 'APEC_GDP_data_')
macro = pd.read_csv(os.path.join(config.root_dir, 'input_data', 'macro', f'APEC_GDP_data_{macro_date_id}.csv'))
#reaplce 17_SIN with SGP
macro['economy_code'] = macro['economy_code'].replace('17_SIN','17_SGP')
#reaplce 15_RP with PHL
macro['economy_code'] = macro['economy_code'].replace('15_RP','15_PHL')

eei = pd.read_csv(os.path.join(config.root_dir, 'input_data','eei', 'buildings_final.csv'))

esto_energy_date_id = x3_utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy'), 'model_df_wide_') 

esto_energy = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', f'model_df_wide_{esto_energy_date_id}.csv'))

economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
# %%
# ESTO energy times ratio - totals of how much energy in each end use of total econ energy use
energy_end_use_esto_times_ratio = pd.read_csv(config.root_dir + '/testing/end_uses_ratios/energy_end_use_esto_totals.csv')
# %%
# need 
END_USES = ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances']

energy_by_end_use1 = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES)) & (eei['fuel']!='all')].copy()
energy_by_end_use = energy_by_end_use1.loc[energy_by_end_use1['economy'].isin(economy_list['economy_code'])].copy()

energy_by_end_use_all = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES)) & (eei['fuel']=='all')].copy()
# %%
# merge the all values onto the fuel values

# Perform the merge on 'economy', 'sub2sectors', and 'year'
end_uses_merged = energy_by_end_use.merge(energy_by_end_use_all[['economy', 'sector', 'year', 'end_use', 'value']],
                      on=['economy', 'sector', 'year', 'end_use'], 
                      how='left',  # 'left' keeps all rows from df1 and adds matching data from df2
                      suffixes=('', '_all'))

end_uses_merged['ratio'] = end_uses_merged['value'] / end_uses_merged['value_all']
# %%

end_uses_merged.rename(columns={'sector' : 'sub2sectors'}, inplace=True)

end_uses_merged['sub2sectors'].replace({
    'residential': '16_01_02_residential',
    'services': '16_01_01_commercial_and_public_services'}, inplace=True)

# add end_use_energy_PJ value of IEA x ESTO values then apply ratio to see fuel split of end uses
# %%


end_use_fuel_ratio_merge = end_uses_merged.merge(energy_end_use_esto_times_ratio[['economy', 'sub2sectors', 'year', 'end_use', 'end_use_energy_use_PJ']],
                      on=['economy', 'sub2sectors', 'year', 'end_use'], 
                      how='left',  # 'left' keeps all rows from df1 and adds matching data from df2
                      suffixes=('', '_estoIEA'))

# %%
end_use_by_fuel = end_use_fuel_ratio_merge.copy()

end_use_by_fuel['fuel_PJ'] = end_use_by_fuel['ratio'] * end_use_by_fuel['end_use_energy_use_PJ']

# %%
end_use_by_fuel.to_csv(config.root_dir + '/testing/end_uses_fuelbreakdown_ratios/end_use_by_fuel.csv')

# %%
# plot the end uses by fuel and also plot the ratios #########################################################################


output_dir = config.root_dir + '/testing/end_uses_fuelbreakdown_ratios/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sectors = ('16_01_02_residential', '16_01_01_commercial_and_public_services')

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df1 = end_use_by_fuel[(end_use_by_fuel['economy'] == economy)]

    for sector in sectors:
        filtered_df = filtered_df1[(filtered_df1['sub2sectors'] == sector)]
        # Create the plot
        # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig = px.area(filtered_df, x='year', y='ratio', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig.update_yaxes(matches=None, showticklabels=True)
        
        # Save the plot to an HTML file
        output_file = output_dir + f'{economy}_{sector}_end_use_ratio.html'
        fig.write_html(output_file)
# %%
# plot of the energy breakdown from ratio x ESTO energy total

output_dir = config.root_dir + '/testing/end_uses_fuelbreakdown/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sectors = ('16_01_02_residential', '16_01_01_commercial_and_public_services')

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df1 = end_use_by_fuel[(end_use_by_fuel['economy'] == economy)]

    for sector in sectors:
        filtered_df = filtered_df1[(filtered_df1['sub2sectors'] == sector)]
        # Create the plot
        # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig = px.area(filtered_df, x='year', y='fuel_PJ', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig.update_yaxes(matches=None, showticklabels=True)
        
        # Save the plot to an HTML file
        output_file = output_dir + f'{economy}_{sector}_end_use_fuels.html'
        fig.write_html(output_file)

# %%

# group by fuels for plots

grouped_fuel_sectoral = end_use_by_fuel.groupby(['year', 'economy', 'sub2sectors', 'fuel']).agg({
    'fuel_PJ': 'sum'  # Summing up fuel_PJ values by fuel
}).reset_index()
# %%
grouped_fuel = end_use_by_fuel.groupby(['year', 'economy', 'fuel']).agg({
    'fuel_PJ': 'sum'  # Summing up fuel_PJ values by fuel
}).reset_index()

# %%
# plot grouped by fuels
output_dir = config.root_dir + '/testing/fuel_totals/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create the plot
# fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
fig = px.area(grouped_fuel, x='year', y='fuel_PJ', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)

# Save the plot to an HTML file
output_file = output_dir + 'fuels.html'
fig.write_html(output_file)

# %%
