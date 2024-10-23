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
# import file from za3 that has end use projections

end_use_projections = pd.read_csv(config.root_dir + '/output_data/a3_projection_adjustment/adjusted_end_use_compiled.csv')
eei = pd.read_csv(os.path.join(config.root_dir, 'input_data','eei', 'buildings_final.csv'))

# made in za4a
df_ratios = pd.read_csv(config.root_dir + '/output_data/a4a_df_created/df_created_fuels_enduses.csv')

END_USES = ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances']

economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
# %%

energy_by_end_use1 = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES)) & (eei['fuel']!='all')].copy()
energy_by_end_use = energy_by_end_use1.loc[energy_by_end_use1['economy'].isin(economy_list['economy_code'])].copy()

energy_by_end_use_all = eei.loc[(eei['measure'] == 'energy') & (eei.end_use.isin(END_USES)) & (eei['fuel']=='all')].copy()

end_uses_merged = energy_by_end_use.merge(energy_by_end_use_all[['economy', 'sector', 'year', 'end_use', 'value']],
                      on=['economy', 'sector', 'year', 'end_use'], 
                      how='left',  # 'left' keeps all rows from df1 and adds matching data from df2
                      suffixes=('', '_all'))

end_uses_merged['ratio'] = end_uses_merged['value'] / end_uses_merged['value_all']

# %%
end_uses_merged['sector'] = end_uses_merged['sector'].replace('residential','16_01_02_residential').copy()
end_uses_merged['sector'] = end_uses_merged['sector'].replace('services','16_01_01_commercial_and_public_services').copy()

# end_uses_merged.to_csv(config.root_dir + '/test.csv', index=False)
# %%

# now merge the ratio data onto the created sheet

# end_uses_merged # contains ratio column # economy	sector	end_use	fuel year ratio
# df_ratios # to be merged onto # economy	sector	end_use	fuel	year

output_dir_csv = config.root_dir + '/output_data/a4_fuel_split_by_end_use/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)
    
ratios = df_ratios.merge(
    end_uses_merged[['economy', 'sector', 'end_use', 'fuel', 'year', 'ratio']], 
    on=['economy', 'sector', 'end_use', 'fuel', 'year'], 
    how='left'
)

ratios.to_csv(output_dir_csv + 'ratios.csv', index=False)

# ratio calculated for IEA and merged onto total sheet




































# # %%
# # Assuming df is your DataFrame with columns 'economy', 'sector', 'end_use', 'fuel', 'year', and 'ratio'

# # First, we want to sort the DataFrame by 'economy', 'sector', 'end_use', 'fuel', and 'year'
# ratios_fill = ratios.sort_values(by=['economy', 'sector', 'end_use', 'fuel', 'year'])



# # %%
# # Right now, just populate na values as 1/6 as placeholder
# ratios_placeholder = ratios_fill[ratios_fill['ratio'] != 0]
# ratios_placeholder['ratio'] = ratios_placeholder['ratio'].fillna(1/6)
# # %%

# # %%

# # Group by 'end_use', 'sector', 'year', and 'economy' and calculate the sum of ratios
# ratios_placeholder['ratio_sum'] = ratios_placeholder.groupby(['end_use', 'sector', 'year', 'economy'])['ratio'].transform('sum')

# # Normalize the ratios to ensure they add up to 1
# ratios_placeholder['normalized_ratio'] = ratios_placeholder['ratio'] / ratios_placeholder['ratio_sum']
# ratios_placeholder.drop(columns=['ratio_sum'], inplace=True)


# # normalized and placeholder ratios of fuels used in each end use
# ratios_placeholder.to_csv(output_dir_csv + '/ratios_fuel_in_end_use.csv', index=False)


# CAN EDIT THE RATIOS HERE ?????????????????






# need fuel split ratios from 2000-2021
# this ratio can be calculated from IEA and then needs to be normalized to 1
# so IEA fuel/total_end use and then keep 2021 out to 2100

#find missing combos and add to a df
#populate


# put ratio onto the sheet with all economies, then fill the empty ones

# %%
# available_combinations = ratios.loc[ratios['ratio'].notna()][['end_use','sector', 'economy', 'year', 'fuel']].drop_duplicates()
# #find combinations that are missing by identifying the combinations in all combinations that are missing from the available combinations set
# all_combinations = ratios[['end_use','sector', 'economy', 'year', 'fuel']].drop_duplicates()
# missing_combinations = all_combinations.loc[~all_combinations.set_index(['end_use','sector', 'economy', 'year', 'fuel']).index.isin(available_combinations.set_index(['end_use','sector', 'economy', 'year']).index)]







# %%
# new_data = pd.DataFrame(columns=['end_use','sector', 'economy', 'year', 'fuel', 'ratio'])
# for year in range(ratios['year'].max(), ratios['year'].min() - 1, -1):
#     print(year)
#     new_data_year = ratios.loc[ratios['year']==year][['end_use','sector', 'economy', 'fuel', 'ratio']].copy()
#     new_data_year.dropna(subset=['ratio'], inplace=True)
#     new_data = pd.concat([new_data, new_data_year], axis=0)
#     #average out the intensity for each end use and sector
#     new_data= new_data.groupby(['end_use','sector','economy', 'fuel', 'year']).mean().reset_index()
   
# #that gives us the average intensity for each end use and sector. now we can use this to estimate the missing intensities 
# #now calculate the average intensity for each end use and sector so we can use it for missing economies or rows
# new_data_no_economy = new_data.groupby(['end_use','sector', 'fuel', 'year']).mean(numeric_only=True).reset_index()

# # %%
# #generate a dataframe with every unique combination of economy, end use, and sector, which will also include theunique economies in population_9th
# unique_economies = economy_list['economy_code'].unique()

# all_combinations_no_economy = all_combinations[['end_use','sector', 'fuel', 'year']].drop_duplicates()
# all_combinations_no_economy['key'] = 0
# unique_economies = pd.DataFrame(unique_economies, columns=['economy'])
# unique_economies['key'] = 0
# all_combinations_no_economy = all_combinations_no_economy.merge(unique_economies, on='key', how='outer')
# all_combinations_no_economy.drop(columns='key', inplace=True)

# # %%

# #merge the average intensity onto this dataframe. then where missing we can use the average intensity without the economy
# all_combinations_no_economy = all_combinations_no_economy.merge(new_data, on=['end_use','sector','economy', 'fuel', 'year'], how='left')
# all_combinations_final = all_combinations_no_economy.merge(new_data_no_economy, on=['end_use','sector', 'fuel', 'year'], suffixes=('','_no_economy'), how='left')
# #label where we are using an average or original intensity value
# all_combinations_final['source'] = 'original'
# all_combinations_final.loc[all_combinations_final['ratio'].isna(), 'source'] = 'average'
# all_combinations_final['ratio'] = all_combinations_final['ratio'].fillna(all_combinations_final['ratio_no_economy'])
# all_combinations_final.drop(columns=['ratio_no_economy'], inplace=True)

# final_intensity = all_combinations_final.copy()
# %%
