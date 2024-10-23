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
# %%
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')

# %%
# ratios = pd.read_csv(config.root_dir + '/output_data/a4_fuel_split_by_end_use/ratios_fuel_in_end_use.csv')
ratios = pd.read_csv(config.root_dir + '/output_data/a4.56_ratio_adjust/norm_ratio_to_2100.csv')
ratios.rename(columns={'sector': 'sub2sectors'}, inplace=True)
ratios.drop(columns=['ratio'], inplace=True)
ratios = ratios[ratios['year'] <= 2070].copy()
# economy	sub2sectors	end_use	fuel	year	ratio	normalized_ratio

# %%
end_use_projection = pd.read_csv(config.root_dir + '/output_data/a3_projection_adjustment/adjusted_end_use_compiled.csv')
end_use_projection = end_use_projection[end_use_projection['year'] >= 2000]
end_use_projection = end_use_projection[end_use_projection['year'] <= 2070]
# end_use	economy	year	sub2sectors	end_use_sector	end_use_energy_compiled


# %%
merged_df = pd.merge(ratios, end_use_projection[['economy', 'sub2sectors', 'end_use', 'year', 'end_use_energy_compiled']], 
                     on=['economy', 'sub2sectors', 'end_use', 'year'], how='left')

# need the ratios
# need the end use projections data
# merge
# multiply


# %%
merged_df['fuel_amount'] = merged_df['normalized_ratio'] * merged_df['end_use_energy_compiled']

merged_df['fuel_amount'] = merged_df['fuel_amount'].fillna(0)
merged_df = merged_df[merged_df['fuel_amount'] != 0]
# merged_df.to_csv(config.root_dir + '/test.csv')
# %%
fuel_split_end_use = merged_df.copy()


output_dir_csv = config.root_dir + '/output_data/a5_end_use_fuel_split/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)
fuel_split_end_use.to_csv(output_dir_csv + '/fuel_split_end_use.csv', index=False)
# %%

# plot the end uses by fuel for each economy

output_dir_fig = config.root_dir + '/plotting_output/a5_end_use_fuel_split/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

sectors = ('16_01_02_residential', '16_01_01_commercial_and_public_services')

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df1 = fuel_split_end_use[(fuel_split_end_use['economy'] == economy)]

    for sector in sectors:
        filtered_df = filtered_df1[(filtered_df1['sub2sectors'] == sector)]
        # Create the plot
        # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig = px.area(filtered_df, x='year', y='fuel_amount', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig.update_yaxes(matches=None, showticklabels=True)
        
        # Save the plot to an HTML file
        output_file = output_dir_fig + f'{economy}_{sector}_end_use_fuels.html'
        fig.write_html(output_file)
# %%
