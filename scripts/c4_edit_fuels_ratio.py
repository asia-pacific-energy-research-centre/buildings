# to edit the ratios of fuels in each end use
# would need to renomralize the values after removal
# only look at ratios to 2021, after that the fuel switch function is used


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
# %%
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
df_ratios = pd.read_csv(config.root_dir + '/output_data/c3_ratio_adjust/normalized_ratios_all_years.csv')

# %%
ratios_placeholder = df_ratios[df_ratios['year'] <= 2021].copy()
df_to_concat = df_ratios[df_ratios['year'] > 2021].copy()

# %%
output_dir_csv = config.root_dir + '/output_data/c4_ratio_adjust/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

output_dir_fig = config.root_dir + '/plotting_output/c4_ratio_adjust/adjusted_ratios/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

# %%
data_for_update = ratios_placeholder.copy()

# UPDATE THE RATIO COLUMN, THEN CAN RENORMALIZE AS NEEDED

# FUELS #########################
# biofuels
# coal
# electricity
# gas
# oil
# other
# solar_thermal


# %%
############################ AUSTRALIA ########################################
data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'lighting') & 
       (data_for_update['fuel'] != 'electricity'), 'ratio'] = 0


data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_cooling') & 
       (~data_for_update['fuel'].isin(['gas', 'electricity'])), 'ratio'] = 0
data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_cooling') & 
       (data_for_update['fuel'].isin(['electricity'])), 'ratio'] = 0.90
data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_cooling') & 
       (data_for_update['fuel'].isin(['gas'])), 'ratio'] = 0.10


data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_heating') & 
       (data_for_update['fuel'].isin(['solar_thermal', 'other', 'coal'])), 'ratio'] = 0
data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_heating') & 
       (data_for_update['fuel'].isin(['electricity'])), 'ratio'] = 0.24
data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_heating') & 
       (data_for_update['fuel'].isin(['gas'])), 'ratio'] = 0.7
data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_heating') & 
       (data_for_update['fuel'].isin(['oil'])), 'ratio'] = 0.03
data_for_update.loc[(data_for_update['economy'] == '01_AUS') & (data_for_update['sector'] == '16_01_01_commercial_and_public_services') &
       (data_for_update['end_use'] == 'space_heating') & 
       (data_for_update['fuel'].isin(['biofuels'])), 'ratio'] = 0.03


# data_for_update.to_csv(output_dir_csv + 'adjusted_ratios.csv', index=False)


# %%
# normalize it
data = data_for_update.copy()
# normalize the ratios
data['ratio_sum'] = data.groupby(['end_use', 'sector', 'year', 'economy'])['ratio'].transform('sum')
data['normalized_ratio'] = data['ratio'] / data['ratio_sum']
data.drop(columns=['ratio_sum'], inplace=True)

# %%
# now that the data is filled in properly, ie populated for missing numbers etc, the only nan should be from any missing IEA values before. Can fill these in at zero, then drop zeroes
data['normalized_ratio'] = data['normalized_ratio'].fillna(0)
data = data[data['normalized_ratio'] != 0].copy()


data.to_csv(output_dir_csv + 'ratios.csv')
# %%
output_dir_fig = config.root_dir + '/plotting_output/a4.56_ratio_adjust/adjusted_ratios/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

# %%
res = data[data['sector'] == '16_01_02_residential']
srv = data[data['sector'] == '16_01_01_commercial_and_public_services']

# %%

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df1 = res[(res['economy'] == economy)]

    # Create the plot
    # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
    fig = px.area(filtered_df1, x='year', y='normalized_ratio', color='fuel', facet_col='end_use', facet_col_wrap=3)
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Save the plot to an HTML file
    output_file = output_dir_fig + f'{economy}_16_01_02_residential.html'
    fig.write_html(output_file)

# %%
for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df2 = srv[(srv['economy'] == economy)]

    # Create the plot
    # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
    fig = px.area(filtered_df2, x='year', y='normalized_ratio', color='fuel', facet_col='end_use', facet_col_wrap=3)
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Save the plot to an HTML file
    output_file = output_dir_fig + f'{economy}_16_01_01_commercial_and_public_services.html'
    fig.write_html(output_file)
# %%
##################################### To be done once ratios are finalized for each economy


# I think maybe this isnt needed anymore since we go to normalization next
data_to_2021 = data.copy()
df_combined = pd.concat([data_to_2021, df_to_concat], ignore_index=True)

# fill 2021 ratio steady out to 2100 as starting place for fuel switching

df_fill = df_combined.copy()
# Group by 'economy', 'sector', 'end_use', and 'fuel', and apply forward fill
df_fill['normalized_ratio'] = df_fill.groupby(['economy', 'sector', 'end_use', 'fuel'])['normalized_ratio'].ffill()
df_fill.to_csv(output_dir_csv + 'norm_ratio_to_2100.csv', index=False)


# %%
