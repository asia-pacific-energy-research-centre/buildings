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
grouped_df = pd.read_csv(config.root_dir + '\output_data\d2_normalization\concat_from_norm.csv')
grouped_df = grouped_df[grouped_df['year'] > 2021]
# %%
esto_energy_date_id = x3_utility_functions.get_latest_date_for_data_file(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy'), 'model_df_wide_') 
esto_energy = pd.read_csv(os.path.join(config.root_dir, 'input_data', '9th_outlook_energy', f'model_df_wide_{esto_energy_date_id}.csv'))
esto_energy = esto_energy[(esto_energy['sectors'] == '16_other_sector') & 
                          (esto_energy['sub1sectors'] == '16_01_buildings') &
                          (esto_energy['sub2sectors'] != 'x') &
                          (esto_energy['is_subtotal'] == False) &
                          (esto_energy['scenarios'] == 'reference')
                          ] 
# & is subtotal = false to get out the subtotal columns #######################################################  
esto_energy.drop(columns=['sub1sectors', 'sub3sectors', 'sub4sectors', 'scenarios'], inplace=True)

# %%
year_columns = esto_energy.loc[:, '1980':'2070'].columns  # Adjust the start and end year if needed
melted_df = pd.melt(esto_energy, 
                    id_vars=['economy', 'sub2sectors', 'fuels', 'subfuels'], 
                    value_vars=year_columns, 
                    var_name='year', 
                    value_name='fuel_amount')
melted_df['year'] = melted_df['year'].astype(int)



# %%

grouped_df = grouped_df[grouped_df['year'] > 2021]
esto = melted_df.copy()
# esto = melted_df[melted_df['year'] == 2021]
# esto = melted_df[melted_df['scenarios'] == 'reference']
# %%

# esto_aus
# grouped_df_aus


# Step 1: Create fuel mapping dictionary
fuel_mapping = {
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
}
# %%
# Step 2: Map subfuels in 'esto_df' to main fuel categories
esto['main_fuel'] = esto['fuels'].map(fuel_mapping)
esto_historical = esto[esto['year'] < 2022]
# %%
esto = esto[esto['year'] == 2021]
# %%

# Step 3: Group 'esto_df' to get the total amount for each economy, sub2sectors, main_fuel, and year
esto_grouped = esto.groupby(['economy', 'sub2sectors', 'main_fuel', 'year'])['fuel_amount'].sum().reset_index()
esto_grouped.rename(columns={'fuel_amount': 'total_esto_amount'}, inplace=True)
# %%

# Merge this grouped data back with 'esto_df' to get the ratio of each subfuel
esto_df = pd.merge(esto, esto_grouped, on=['economy', 'sub2sectors', 'main_fuel', 'year'])
esto_df['fuel_ratio'] = esto_df['fuel_amount'] / esto_df['total_esto_amount']

# %%
esto_df = esto_df.copy()
esto_df.drop(columns=['fuel_amount', 'total_esto_amount'], inplace=True)

# esto_df
# grouped_df


# %%
years = list(range(2022, 2071))

extended_esto_df = esto_df.loc[esto_df.index.repeat(len(years))].copy()
extended_esto_df['year'] = np.tile(years, len(esto_df))

fuel_total = grouped_df.rename(columns={'fuel': 'main_fuel'})

# Step 2: Merge the DataFrames
merged_df = pd.merge(
    extended_esto_df,
    fuel_total[['economy', 'sub2sectors', 'main_fuel', 'year', 'fuel_amount']],  # Select relevant columns
    how='left',
    on=['economy', 'sub2sectors', 'main_fuel', 'year']
)

merged_df.reset_index(drop=True, inplace=True)

# %%
# multiply to see how the fuels are broken down
modelled_subfuels = merged_df.copy()
modelled_subfuels['subfuel_amount'] = modelled_subfuels['fuel_ratio'] * modelled_subfuels['fuel_amount']

# %%

# drop na and 0
modelled_subfuels = modelled_subfuels[modelled_subfuels['subfuel_amount'].notna() & (modelled_subfuels['subfuel_amount'] != 0)].copy()


# %%
# concat this onto esto data 2000 to 2021
esto_historical = melted_df[melted_df['year'] < 2022]
esto_historical = esto_historical[~esto_historical['fuels'].isin(['19_total', '20_total_renewables', '21_modern_renewables'])]

# %%
esto_hist_res = esto_historical[esto_historical['sub2sectors'] == '16_01_02_residential']
esto_hist_res = esto_hist_res[esto_hist_res['fuel_amount'].notna() & (esto_hist_res['fuel_amount'] != 0)].copy()
esto_hist_res['name'] = esto_hist_res['fuels'] + ': ' + esto_hist_res['subfuels']
# %%
fig = px.area(esto_hist_res, x='year', y='fuel_amount', color='name', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir_fig + 'fuel_totals_area_srv.html')
fig.show()
fig.write_html(config.root_dir + '/testfig.html')

# %%
# clean up modelled data for concat
modelled = modelled_subfuels.copy()
modelled.drop(columns=['main_fuel', 'fuel_ratio', 'fuel_amount'], inplace=True)
modelled = modelled.rename(columns={'subfuel_amount': 'fuel_amount'})


# %%
concat_subfuels = pd.concat([esto_historical, modelled], ignore_index=True)
concat_subfuels['name'] = concat_subfuels['fuels'] + ': ' + concat_subfuels['subfuels']

concat_subfuels = concat_subfuels[concat_subfuels['fuel_amount'].notna() & (concat_subfuels['fuel_amount'] != 0)].copy()
# economy	sub2sectors	fuels	subfuels	year	fuel_amount	name
# %%
output_dir_csv = config.root_dir + '/output_data/d3_subfuels_split/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)



output_dir_fig = config.root_dir + '/plotting_output/d3_subfuels_split/'
if not os.path.exists(output_dir_fig):
    os.makedirs(output_dir_fig)



# %%
concat_subfuels.to_csv(output_dir_csv + 'concat_subfuels.csv', index=False)

concat_res = concat_subfuels[concat_subfuels['sub2sectors'] == '16_01_02_residential']
concat_srv = concat_subfuels[concat_subfuels['sub2sectors'] != '16_01_02_residential']

# %%
fig = px.area(concat_subfuels, x='year', y='fuel_amount', color='name', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir_fig + 'fuel_totals_area_srv.html')
fig.show()
fig.write_html(output_dir_fig + '/total_subfuels.html')
# %%
fig = px.area(concat_res, x='year', y='fuel_amount', color='name', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir_fig + 'fuel_totals_area_srv.html')
fig.show()
fig.write_html(output_dir_fig + '/res_subfuels.html')
# %%
fig = px.area(concat_srv, x='year', y='fuel_amount', color='name', facet_col='economy', facet_col_wrap=7)
fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir_fig + 'fuel_totals_area_srv.html')
fig.show()
fig.write_html(output_dir_fig + '/srv_subfuels.html')
# %%
