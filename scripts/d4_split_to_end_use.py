# %%
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

economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')

# %%
# Now to break down the normalized fuels in each subsector back to the end uses for alteration ########################################################################
initial_df = pd.read_csv(config.root_dir + '/output_data/d3_subfuels_split/concat_subfuels.csv')
# economy	sub2sectors	fuels	subfuels	year	fuel_amount	name


# initial_df.drop(columns=['normalized_ratio', 'end_use_energy_compiled'], inplace=True)
# initial_df.sort_values(by=['fuel', 'year', 'sub2sectors', 'economy'], inplace=True)
# %%
initial_df['fuel'] = initial_df['fuels'].map({
    '15_solid_biomass': 'biofuels',
    '01_coal': 'coal',
    '02_coal_products': 'coal',
    '03_peat': 'coal',
    '04_peat_products': 'coal',
    '17_electricity': 'electricity',
    '08_gas': 'gas',
    '18_heat': 'heat',
    '06_crude_oil_and_ngl': 'oil',
    '07_petroleum_products': 'oil',
    '16_others': 'other',
    '12_solar': 'solar_thermal'
})

modelled_data = initial_df[initial_df['year'] > 2021]

# %%
# ratio data from d2 that describes how much of the fuel should go to the associated end use
ratios = pd.read_csv(config.root_dir + '/output_data/d2_normalization/ratio_for_d4.csv')
ratios.drop(columns=['year', 'fuel_ratio'], inplace=True)

# initial_df.to_csv(config.root_dir + '/testinitial.csv')
# make sure no info in missing combinations for the economy about to be analyzed
# if missing combinations, then readjust ratios to incorporate the fuel as needed


# %%
unique_end_uses = ratios[['end_use']].drop_duplicates()
# %%
# Step 2: Perform a cross join to replicate each row in modelled_data for every unique end use
modelled_data_expanded = modelled_data.merge(unique_end_uses, how='cross')
# %%
# Step 3: Merge the expanded modelled_data with ratios based on the common columns
merged_df = pd.merge(
    modelled_data_expanded,
    ratios,
    how='left',
    on=['economy', 'sub2sectors', 'fuel', 'end_use']
)
# %%
# Step 4: Handle missing values for `fuel_ratio` and calculate the fuel amount for each end use
merged_df['fuel_ratio_normalized'] = merged_df['fuel_ratio_normalized'].fillna(0)
merged_df['subfuel_amount'] = merged_df['fuel_amount'] * merged_df['fuel_ratio_normalized']

output_dir_csv = config.root_dir + '/output_data/d4_split_to_end_use/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

# merged_df = merged_df[(merged_df['sub2sectors'] == '16_01_01_commercial_and_public_services') &
#                       (~(merged_df['end_use'].isin(['space_heating', 'space_cooling', 'lighting'])))].copy()
                      
condition = (merged_df['sub2sectors'] == '16_01_01_commercial_and_public_services') & (merged_df['end_use'].isin(['residential_appliances', 'water_heating', 'cooking']))
merged_df = merged_df[~condition].copy()

merged_df.to_csv(output_dir_csv + 'subfuel_end_use.csv', index=False)

# %%
merged_df_res = merged_df[merged_df['sub2sectors'] != '16_01_01_commercial_and_public_services']
merged_df_srv = merged_df[merged_df['sub2sectors'] == '16_01_01_commercial_and_public_services']

output_dir_fig = config.root_dir + '/plotting_output/d4_split_to_end_use/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

# %%
for econ in economy_list['economy_code']:
    filter_df = merged_df_res[merged_df_res['economy'] == econ]

    fig = px.area(filter_df, x='year', y='subfuel_amount', color='name', facet_col='end_use', facet_col_wrap=3)
    fig.update_yaxes(matches=None, showticklabels=True)

    fig.write_html(output_dir_fig + f'res_{econ}.html')

for econ in economy_list['economy_code']:
    filter_df = merged_df_srv[merged_df_srv['economy'] == econ]

    fig = px.area(filter_df, x='year', y='subfuel_amount', color='name', facet_col='end_use', facet_col_wrap=3)
    fig.update_yaxes(matches=None, showticklabels=True)

    fig.write_html(output_dir_fig + f'srv_{econ}.html')

# end_use = concat_final[concat_final['year'] > 2021]
# %%
# ratio_multiplier = initial_df.copy()
# ratio_multiplier = ratio_multiplier[ratio_multiplier['year'] == 2021]
# # %%

# ratio_multiplier['total_fuel_amount'] = ratio_multiplier.groupby(['economy', 'fuel', 'year'])['fuel_amount'].transform('sum')

# # Step 2: Calculate the ratio of each end use by dividing fuel_amount by the total_fuel_amount
# ratio_multiplier['fuel_ratio'] = ratio_multiplier['fuel_amount'] / ratio_multiplier['total_fuel_amount']
# ratio_multiplier.drop(columns=['fuel_amount', 'total_fuel_amount'], inplace=True)


# # %%
# ratio_normalized = ratio_multiplier.copy()
# ratio_normalized['fuel_ratio_normalized'] = ratio_normalized.groupby(['economy', 'sub2sectors', 'fuel'])['fuel_ratio'].transform(lambda x: x / x.sum())

# ratio_normalized.to_csv(config.root_dir + '/testnorm.csv')

# # %%
# # Step 1: Create a list of years to extend the ratio_multiplier DataFrame
# years = list(range(2022, 2071))  # From 2022 to 2070

# # Step 2: Create a cross product of all rows in ratio_multiplier with the new years
# extended_ratio_multiplier = ratio_normalized.loc[ratio_normalized.index.repeat(len(years))].copy()
# extended_ratio_multiplier['year'] = np.tile(years, len(ratio_normalized))
# # %%
# # Step 3: Merge the extended ratio_multiplier with the end_use DataFrame
# merged_df = pd.merge(
#     end_use,
#     extended_ratio_multiplier,
#     how='left',
#     left_on=['economy', 'sub2sectors', 'fuel', 'year'],
#     right_on=['economy', 'sub2sectors', 'fuel', 'year']
# )

# # ratio_multiplier.to_csv(output_dir_csv + 'ratio_multiplier.csv')
# # end_use.to_csv(output_dir_csv + 'end_use.csv')

# # %%
# # Merge ratio_multiplier onto end_use, matching economy, sub2sectors, and fuel (year is ignored for the merge)

# merged_df.drop(columns=['fuel_ratio'], inplace=True)

# # %%

# # plot the end uses by fuel for each economy

# output_dir_fig = config.root_dir + '/plotting_output/d2_normalization/end_use_breakdown/'
# if not os.path.exists(output_dir_fig):
#     os.makedirs(output_dir_fig)

# result_df = merged_df.copy()
# result_df['end_use_fuel'] = result_df['fuel_amount'] * result_df['fuel_ratio_normalized']

# result_df.to_csv(output_dir_csv + 'end_use_adjusted.csv', index=False)

# # %%
# result_df = result_df.dropna(subset=['end_use_fuel'])
# # %%
# # this is the total value of fuel from 2020 to 2070 for each economy after multiplying through the end use ratios
# result_grouped = result_df.groupby(['economy', 'fuel', 'year'], as_index=False)['end_use_fuel'].sum()
# # result_grouped = result_grouped[result_grouped['end_use_fuel'] != 0]
# fig = px.area(result_grouped, x='year', y='end_use_fuel', color='fuel', facet_col='economy', facet_col_wrap=7)
# fig.update_yaxes(matches=None, showticklabels=True)

# output_file = output_dir_fig + 'normalized_end_use_fuels.html'
# fig.write_html(output_file)


# # %%
# sectors = ('16_01_02_residential', '16_01_01_commercial_and_public_services')

# for economy in economy_list['economy_code']:
#     # Filter the DataFrame for the current economy
#     filtered_df1 = result_df[(result_df['economy'] == economy)]

#     for sector in sectors:
#         filtered_df = filtered_df1[(filtered_df1['sub2sectors'] == sector)]
#         # Create the plot
#         # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
#         fig = px.area(filtered_df, x='year', y='end_use_fuel', color='fuel', facet_col='end_use', facet_col_wrap=3)
#         fig.update_yaxes(matches=None, showticklabels=True)
        
#         # Save the plot to an HTML file
#         output_file = output_dir_fig + f'{economy}_{sector}_end_use_fuels.html'
#         fig.write_html(output_file)

# %%
