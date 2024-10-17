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

economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')

# %%

initial_df = pd.read_csv(config.root_dir + '/output_data/a5_end_use_fuel_split/fuel_split_end_use.csv')
initial_df.drop(columns=['normalized_ratio', 'end_use_energy_compiled'], inplace=True)

initial_df.sort_values(by=['fuel', 'year', 'sub2sectors', 'economy'], inplace=True)

# economy	sub2sectors	end_use	fuel	year	fuel_amount
# is the fuel split by end use deduced using the model for years 2000 to 2070

# %%
# sum up the total of each fuel in each year

df_sum = initial_df.groupby(['economy', 'fuel', 'year', 'sub2sectors'])['fuel_amount'].sum().reset_index()

# 	economy	fuel	year	sub2sectors	fuel_amount
#  is the total fuel in each year for each fuel separated by economy and subsector


# %%
# df_merged = initial_df.merge(df_sum[['economy', 'sub2sectors', 'fuel', 'year', 'fuel_amount']],
#                       on=['economy', 'sub2sectors', 'fuel', 'year'], 
#                       suffixes=('', '_total_for_fuel_type'),
#                       how='left')
# # 	economy	sub2sectors	end_use	fuel	year	fuel_amount	fuel_amount_total_for_fuel_type
# # is the total fuel in each year for each fuel merged onto the end use split

# # %%
# # determine ratio of the fuel that goes toward each end use

# df_fuel_to_end_use_ratio = df_merged.copy()
# df_fuel_to_end_use_ratio['ratio'] = df_fuel_to_end_use_ratio['fuel_amount'] / df_fuel_to_end_use_ratio['fuel_amount_total_for_fuel_type']
# # economy	sub2sectors	end_use	fuel	year	fuel_amount	fuel_amount_total_for_fuel_type	ratio
# # using the model values, it deduces how much of each end use is comprised by each fuel
# # in other words, it shows what percentage of electricity demand is allocated to each end use, for example
# # can take this ratio, and match it to esto. so if we take esto total for electricity for subsector in 2021, and multiply it by the ratio,
# # we can see how much of the esto total goes to each end use
# # then take the difference between that and the modelled amount to get a normalization factor to align the fuels in 2021 with esto

# %%
# now to prepare the esto data to determine the normalization factor
esto_energy_date_id = utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy'), 'model_df_wide_') 
esto_energy = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', f'model_df_wide_{esto_energy_date_id}.csv'))
esto_energy = esto_energy[(esto_energy['sectors'] == '16_other_sector') & 
                          (esto_energy['sub1sectors'] == '16_01_buildings') &
                          (esto_energy['sub2sectors'] != 'x') &
                          (esto_energy['is_subtotal'] == False)
                          ] 
# & is subtotal = false to get out the subtotal columns #######################################################  
esto_energy.drop(columns=['subfuels', 'sub1sectors', 'sub3sectors', 'sub4sectors'], inplace=True)

# %%
year_columns = esto_energy.loc[:, '1980':'2070'].columns  # Adjust the start and end year if needed
melted_df = pd.melt(esto_energy, 
                    id_vars=['scenarios', 'economy', 'sub2sectors', 'fuels'], 
                    value_vars=year_columns, 
                    var_name='year', 
                    value_name='fuel_amount')
melted_df['year'] = melted_df['year'].astype(int)

# %%
melted_df = melted_df[(melted_df['fuels'] != '19_total') &
                      (melted_df['fuels'] != '20_total_renewables') &
                      (melted_df['fuels'] != '21_modern_renewables')                     
                      ]


# %%
melted_df['fuel_category'] = melted_df['fuels'].map({
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
# this is pure esto data but with fuel mapping to match modelled data


# %%
esto_sum = melted_df.groupby(['scenarios', 'economy', 'sub2sectors', 'fuel_category', 'year'], as_index=False)['fuel_amount'].sum()

# this is pure esto data but with fuel summed to match modelled data


# only need one set of data, so take reference. 
# reason is that only need esto now for the 2021 normalization value, and data the same between tgt and ref

# %%
esto_sum_ref = esto_sum[esto_sum['scenarios'] == 'reference']
                       


# %%
# data for only 2021
esto_sum_ref_2021 = esto_sum_ref[esto_sum_ref['year'] == 2021]
df_sum_2021 = df_sum[df_sum['year'] == 2021]

esto_sum_ref_2021.drop(columns=['scenarios'], inplace=True)
esto_sum_ref_2021.rename(columns={'fuel_category': 'fuel'}, inplace=True)

# now to merge these to get a normalization factor
# merge df_sum_2021 values onto esto_sum_ref_2021 values
# %%
merged_for_norm = esto_sum_ref_2021.merge(
    df_sum_2021[['economy', 'sub2sectors', 'fuel', 'year', 'fuel_amount']],
    on=['economy', 'sub2sectors', 'fuel', 'year'],
    suffixes=('_esto', '_model'),
    how='left'
)

# %%
# replace any zeroes or nan in the model column with the esto value, if it exists in esto but not in the modelled values
# Replace NaN values in '_model' with the corresponding values from '_esto'
merged_for_norm['fuel_amount_model'].fillna(merged_for_norm['fuel_amount_esto'], inplace=True)

# Replace 0 values in '_model' with the corresponding values from '_esto'
merged_for_norm['fuel_amount_model'] = merged_for_norm.apply(
    lambda row: row['fuel_amount_esto'] if row['fuel_amount_model'] == 0 and row['fuel_amount_esto'] != 0 else row['fuel_amount_model'], axis=1
)


# %%
# norm factor
merged_for_norm['norm'] = merged_for_norm['fuel_amount_esto'] / merged_for_norm['fuel_amount_model']

# %%
# need to multiply the normalization factor through each year of df_sum which is the modelled results from before
df_normalized = df_sum[df_sum['year'] > 2021]

df_normalized = df_normalized.merge(
    merged_for_norm[['economy', 'sub2sectors', 'fuel', 'norm']],
    on=['economy', 'sub2sectors', 'fuel'],
    how='left'
)
# %%

df_normalized['normalized_fuel'] = df_normalized['fuel_amount'] * df_normalized['norm']

# df_normalized.to_csv(config.root_dir + '/test3.csv')

# %%
# concat the model and esto data to ensure fluidity
# can then break down the model data later into end use for fuel switching


esto_sum_ref_concat = esto_sum_ref.copy()
esto_sum_ref_concat.drop(columns=['scenarios'], inplace=True)
esto_sum_ref_concat.rename(columns={'fuel_category': 'fuel'}, inplace=True)
esto_sum_ref_concat = esto_sum_ref_concat[esto_sum_ref_concat['year'] < 2022]
esto_sum_ref_concat = esto_sum_ref_concat[esto_sum_ref_concat['year'] > 1999]

df_normalized_concat = df_normalized.copy()
df_normalized_concat.drop(columns=['fuel_amount', 'norm'], inplace=True)
df_normalized_concat.rename(columns={'normalized_fuel': 'fuel_amount'}, inplace=True)

concat = pd.concat([esto_sum_ref_concat, df_normalized_concat], ignore_index=True)

# %%
concat['fuel_amount'].fillna(0, inplace=True)
# concat = concat[concat['fuel_amount'] != 0]

# concat = concat[concat['year'] > 1999]


output_dir_csv = config.root_dir + '/output_data/a5.5_attempting_again/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

concat.to_csv(output_dir_csv + 'concat.csv', index=False)

# %%
#  Generate entries for fuels if they exist where the esto data has 2021 values but the model does not include
#  Enters the 2021 value from ESTO as the value from 2022-2070

concat_2021 = concat[concat['year'] == 2021]

df_2022_2070 = concat[concat['year'].isin(range(2022, 2071))]
missing_combinations = concat_2021.merge(
    df_2022_2070[['economy', 'sub2sectors', 'fuel']],
    on=['economy', 'sub2sectors', 'fuel'],
    how='left',
    indicator=True
).query('_merge == "left_only"')[['economy', 'sub2sectors', 'fuel', 'fuel_amount']]


# Depending on missing combinations, may need to go back and update ratios in 4.56

new_rows = []
for _, row in missing_combinations.iterrows():
    for year in range(2022, 2071):
        new_rows.append({
            'economy': row['economy'],
            'sub2sectors': row['sub2sectors'],
            'fuel': row['fuel'],
            'year': year,
            'fuel_amount': row['fuel_amount']  # Use 2021 value for missing years
        })

df_new_rows = pd.DataFrame(new_rows)

concat_final = pd.concat([concat, df_new_rows], ignore_index=True)
concat_final_sorted = concat_final.sort_values(by=['economy', 'sub2sectors', 'fuel', 'year']).reset_index(drop=True)

concat_final.to_csv(output_dir_csv + 'concat_from_norm.csv', index=False)

# %%
# plot concat


output_dir_fig = config.root_dir + '/plotting_output/a5.5_attempting_again/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)


plot_res = concat_final[concat_final['sub2sectors'] == '16_01_01_commercial_and_public_services']
fig = px.area(plot_res, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.show()

plot_srv = concat_final[concat_final['sub2sectors'] == '16_01_02_residential']
fig = px.area(plot_srv, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
fig.show()

# %%

plot_total = concat_final.groupby(['economy', 'fuel', 'year'], as_index=False).agg({'fuel_amount': 'sum'})

fig = px.area(plot_total, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)

# Save the plot to an HTML file
output_file = output_dir_fig + 'normalized_fuels_total.html'
fig.write_html(output_file)


# %%

# Now to break down the normalized fuels in each subsector back to the end uses for alteration ########################################################################


# make sure no info in missing combinations for the economy about to be analyzed
# if missing combinations, then readjust ratios to incorporate the fuel as needed

end_use = concat_final[concat_final['year'] > 2021]

ratio_multiplier = initial_df.copy()
ratio_multiplier = ratio_multiplier[ratio_multiplier['year'] == 2021]


ratio_multiplier['total_fuel_amount'] = ratio_multiplier.groupby(['economy', 'fuel', 'year'])['fuel_amount'].transform('sum')

# Step 2: Calculate the ratio of each end use by dividing fuel_amount by the total_fuel_amount
ratio_multiplier['fuel_ratio'] = ratio_multiplier['fuel_amount'] / ratio_multiplier['total_fuel_amount']
ratio_multiplier.drop(columns=['fuel_amount', 'total_fuel_amount'], inplace=True)

# %%
# Step 1: Create a list of years to extend the ratio_multiplier DataFrame
years = list(range(2022, 2071))  # From 2022 to 2070

# Step 2: Create a cross product of all rows in ratio_multiplier with the new years
extended_ratio_multiplier = ratio_multiplier.loc[ratio_multiplier.index.repeat(len(years))].copy()
extended_ratio_multiplier['year'] = np.tile(years, len(ratio_multiplier))
# %%
# Step 3: Merge the extended ratio_multiplier with the end_use DataFrame
merged_df = pd.merge(
    end_use,
    extended_ratio_multiplier,
    how='left',
    left_on=['economy', 'sub2sectors', 'fuel', 'year'],
    right_on=['economy', 'sub2sectors', 'fuel', 'year']
)

# ratio_multiplier.to_csv(output_dir_csv + 'ratio_multiplier.csv')
# end_use.to_csv(output_dir_csv + 'end_use.csv')

# %%
# Merge ratio_multiplier onto end_use, matching economy, sub2sectors, and fuel (year is ignored for the merge)



# %%

# plot the end uses by fuel for each economy

output_dir_fig = config.root_dir + '/plotting_output/a5.5_attempting_again/end_use_bdown/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)

result_df = merged_df.copy()
result_df['end_use_fuel'] = result_df['fuel_amount'] * result_df['fuel_ratio']

result_df.to_csv(output_dir_csv + 'end_use_adjusted.csv', index=False)

# %%
result_df = result_df.dropna(subset=['end_use_fuel'])
# %%

result_grouped = result_df.groupby(['economy', 'fuel', 'year'], as_index=False)['end_use_fuel'].sum()
fig = px.area(result_df, x='year', y='end_use_fuel', color='fuel', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)

output_file = output_dir_fig + 'normalized_end_use_fuels.html'
fig.write_html(output_file)


# %%
sectors = ('16_01_02_residential', '16_01_01_commercial_and_public_services')

for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df1 = result_df[(result_df['economy'] == economy)]

    for sector in sectors:
        filtered_df = filtered_df1[(filtered_df1['sub2sectors'] == sector)]
        # Create the plot
        # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig = px.area(filtered_df, x='year', y='end_use_fuel', color='fuel', facet_col='end_use', facet_col_wrap=3)
        fig.update_yaxes(matches=None, showticklabels=True)
        
        # Save the plot to an HTML file
        output_file = output_dir_fig + f'{economy}_{sector}_end_use_fuels.html'
        fig.write_html(output_file)



















# # %%
# esto_concat = sum_melt_df.groupby(['economy', 'year', 'sub2sectors', 'fuel_category'], as_index=False)['fuel_amount'].sum()
# esto_fuel_type_totals = sum_melt_df.groupby(['economy', 'year', 'sub2sectors', 'fuel_category'], as_index=False)['fuel_amount'].sum()
# # %%
# esto_fuel_type_totals = esto_fuel_type_totals[esto_fuel_type_totals['year'] == 2021]
# df_fuel_to_end_use_ratio = df_fuel_to_end_use_ratio[df_fuel_to_end_use_ratio['year'] == 2021]
# df_fuel_to_end_use_ratio.drop(columns=['fuel_amount_total_for_fuel_type'], inplace=True)
# df_fuel_to_end_use_ratio.rename(columns={'fuel': 'fuel_category'}, inplace=True)

# df_model = df_fuel_to_end_use_ratio.copy()

# # %%
# # merge the total fuel amount for each fuel type from esto onto the breakdown of fuel for each end use, to see how much of each esto fuel goes into each end use
# df_merged_2021 = df_model.merge(esto_fuel_type_totals[['economy', 'sub2sectors', 'fuel_category', 'year', 'fuel_amount']],
#                       on=['economy', 'sub2sectors', 'fuel_category', 'year'], 
#                       suffixes=('', '_esto'),
#                       how='left')
# # %%
# esto_end_use_split = df_merged_2021.copy()

# esto_end_use_split['esto_by_end_use'] = esto_end_use_split['ratio'] * esto_end_use_split['fuel_amount_esto']

# # %%
# norm_factor = esto_end_use_split.copy()

# norm_factor.rename(columns={'fuel_amount': 'fuel_initial_model'}, inplace=True)

# # normalization factor is fuel esto divided by fuel model

# norm_factor['norm_factor'] = norm_factor['esto_by_end_use'] / norm_factor['fuel_initial_model'] 


# # %%
# # so now we have the normalization factor that corrects the 2021 modelled value to match the esto values
# # take model values from 2021 to 2070 and multiply it by the associated normalizatoin factor

# norm_factor = norm_factor.copy()
# norm_factor.drop(columns=['fuel_initial_model', 'fuel_amount_esto', 'esto_by_end_use', 'year', 'ratio'], inplace=True)
# norm_factor.rename(columns={'fuel_category': 'fuel'}, inplace=True)

# # %%

# # from before
# df_to_norm = initial_df.copy()
# df_to_norm.sort_values(by=['economy', 'sub2sectors', 'year'], inplace=True)
# df_to_norm = df_to_norm[df_to_norm['year'] > 2021]

# # %%
# # merge the norm factor on

# df_normed = df_to_norm.merge(norm_factor[['economy', 'sub2sectors', 'end_use', 'fuel', 'norm_factor']],
#                       on=['economy', 'sub2sectors', 'end_use', 'fuel'], 
#                       how='left')

# df_normed['norm_fuel'] = df_normed['fuel_amount'] * df_normed['norm_factor']

# # %%
# # can concat the esto historical grouped by fuel category with the df_normed

# df_model_concat = df_normed.copy()
# df_model_concat.drop(columns=['fuel_amount', 'norm_factor'], inplace=True)

# df_m_concat = df_model_concat.groupby(['economy', 'sub2sectors', 'year', 'fuel'])['norm_fuel'].sum().reset_index()


# # %%
# esto_concat.rename(columns={'fuel_category': 'fuel'}, inplace=True)
# df_m_concat.rename(columns={'norm_fuel': 'fuel_amount'}, inplace=True)


# # concat for check
# df_concat = pd.concat([esto_concat, df_m_concat], ignore_index=True)

# # %%
# # concat_srv = df_concat[df_concat['sub2sectors'] == '16_01_01_commercial_and_public_services']
# # concat_res = df_concat[df_concat['sub2sectors'] == '16_01_02_residential']



# output_dir_fig = config.root_dir + '/plotting_output/a5.5_normalized/'
# if not os.path.exists(output_dir_fig):
#     os.makedirs(output_dir_fig)

# sectors = ('16_01_02_residential', '16_01_01_commercial_and_public_services')

# for sector in sectors:
#     filtered_df = df_concat[(df_concat['sub2sectors'] == sector)]
#     # Create the plot
#     # fig = px.line(filtered_df, x='year', y='value', line_dash='sector', color='fuel', facet_col='end_use', facet_col_wrap=3)
#     fig = px.area(filtered_df, x='year', y='fuel_amount', color='fuel', facet_col='economy', facet_col_wrap=7)
#     fig.update_yaxes(matches=None, showticklabels=True)
    
#     # Save the plot to an HTML file
#     output_file = output_dir_fig + f'{sector}_end_use_fuels.html'
#     fig.write_html(output_file)



# # %%

# %%
