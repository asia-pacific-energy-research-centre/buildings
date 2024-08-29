
#%%
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px

####
root_dir =re.split('buildings', os.getcwd())[0]+'/buildings'
#set the root directory for the project
os.chdir(root_dir)
#self made helper functions
import utility_functions
import configurations
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

#%%
#create a quick graph of gdp per capita for all economies:
gdp_per_capita = macro.loc[macro['variable']=='GDP_per_capita'].copy()
fig = px.line(gdp_per_capita, x='year', y='value', color='economy_code')
fig.write_html('plotting_output/analysis/gdp_per_capita.html')
#put them in order and then show gdp per capita average over the period between 2000 and 2050
#%%
gdp_per_capita_avg = gdp_per_capita.loc[(gdp_per_capita['year']>=2000) & (gdp_per_capita['year']<=2050)].copy()
gdp_per_capita_avg = gdp_per_capita_avg[['economy_code', 'economy', 'value']].groupby(['economy_code','economy']).mean().reset_index()
#sort
gdp_per_capita_avg = gdp_per_capita_avg.sort_values('value', ascending=False)

#create groupings of economies to base the colors on, and then sort by them and value
# 1. high income, high dens: Japan, Korea, Chinese Taipei
# 2. low income low dens: Chile, Peru, Mexico, Papua New Guinea, Russia
# 3. high income low dens: Australia, Canada, New Zealand, United States
# 4. low income high dens:  Indonesia, Malaysia, Phillipines, Thailand, Viet Nam
# 5. City states: Singapore, Hong Kong, Brunei
# 6. china
codes = [
    '02_BD',
    '03_CDA',
    '04_CHL',
    '05_PRC',
    '06_HKC',
    '07_INA',
    '08_JPN',
    '09_ROK',
    '10_MAS',
    '11_MEX',
    '12_NZ',
    '13_PNG',
    '14_PE',
    '15_PHL',
    '16_RUS',
    '17_SGP',
    '18_CT',
    '19_THA',
    '20_USA',
    '21_VN'
]
gdp_per_capita_avg['Grouping'] = np.nan
mapping = {
    'High income, high density': ['08_JPN', '09_ROK', '18_CT'],
        'Lower income low density': ['04_CHL', '14_PE', '11_MEX', '13_PNG', '16_RUS'],
    'High income low density': ['12_NZ', '20_USA', '01_AUS', '03_CDA'],
    'Lower income high density': ['19_THA', '10_MAS', '15_PHL', '21_VN', '07_INA'],
    'Microstates': ['17_SGP', '06_HKC', '02_BD'],
    'China': ['05_PRC']
}
#map colors for them
mapping_colors = {
    'High income, high density': 'rgb(255, 165, 0)',  # Orange
    'Lower income low density': 'rgb(220, 20, 60)',  # Crimson
    'High income low density': 'rgb(34, 139, 34)',  # Forest Green
    'Lower income high density': 'rgb(30, 144, 255)',  # Dodger Blue
    'Microstates': 'rgb(186, 85, 211)',  # Medium Orchid
    'China': 'rgb(0, 206, 209)'  # Dark Turquoise
}
for group in mapping:
    gdp_per_capita_avg.loc[gdp_per_capita_avg['economy_code'].isin(mapping[group]), 'Grouping'] = group

gdp_per_capita_avg = gdp_per_capita_avg.sort_values(['Grouping', 'value'], ascending=[True, False])
#label the 
fig = px.bar(gdp_per_capita_avg, x='economy', y='value', color='Grouping', color_discrete_map=mapping_colors)
#label the y axis as gdp per capita and the x axis will be dropped. then title it as Average gdp per capita between 2000 and 2050
#and amke text a bit bigger, and make the labels for x axis a bit vertical
fig.update_layout(
    yaxis_title='GDP per capita',
    title='Average GDP per capita between 2000 and 2050',
    font=dict(
        size=22
    ),
    xaxis_tickangle=-45,
    xaxis_title=None)
fig.write_html('plotting_output/analysis/gdp_per_capita_avg.html')

# %%
