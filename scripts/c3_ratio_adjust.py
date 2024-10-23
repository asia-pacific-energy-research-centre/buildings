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
# ratios_placeholder = ratios_placeholder[ratios_placeholder['year'] <= 2021]
# ratios_placeholder.drop(columns=['normalized_ratio'], inplace=True)
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
df_ratios = pd.read_csv(config.root_dir + '/output_data/c2_fuel_split_for_end_use/ratios.csv')
# %%
output_dir_csv = config.root_dir + '/output_data/c3_ratio_adjust/' 
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

# %%
data_for_update = df_ratios[df_ratios['year'] <= 2021].copy()
data_to_concat = df_ratios[df_ratios['year'] > 2021].copy()


# %%
# drop zero ratios
# fill misisng economies

# Group by 'economy', 'end_use', and 'sector' and check if all 'ratio' values are NaN in each group
nan_combinations = data_for_update.groupby(['economy', 'end_use', 'sector'])['ratio'].apply(lambda x: x.isna().all())
nan_combinations = nan_combinations[nan_combinations].index
nan_comb_list = [f"{economy}:{end_use}:{sector}" for economy, end_use, sector in nan_combinations]

# Output the list of combinations
print(nan_comb_list)

# nan_comb_list

# %% fill nan combinations with a number (normalize after so it doesn't matter)
for comb in nan_comb_list:
    economy, end_use, sector = comb.split(':')
    data_for_update.loc[(data_for_update['economy'] == economy) & 
           (data_for_update['end_use'] == end_use) & 
           (data_for_update['sector'] == sector), 'ratio'] = 1

# %%
# normalize the ratios
data_for_update['ratio_sum'] = data_for_update.groupby(['end_use', 'sector', 'year', 'economy'])['ratio'].transform('sum').copy()
data_for_update['normalized_ratio'] = data_for_update['ratio'] / data_for_update['ratio_sum'].copy()
data_for_update.drop(columns=['ratio_sum'], inplace=True)

# %%
output_dir_fig = config.root_dir + '/plotting_output/c3_ratio_adjust/adjusted_ratios/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

# %%
data=data_for_update.copy()

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
df_combined = pd.concat([data_for_update, data_to_concat], ignore_index=True)
df_combined.to_csv(output_dir_csv + 'normalized_ratios_all_years.csv', index=False)
# %%
