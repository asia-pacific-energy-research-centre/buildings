# %%
import pandas as pd
import itertools
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

import utility_functions
import configurations
root_dir =re.split('buildings', os.getcwd())[0]+'/buildings'
config = configurations.Config(root_dir)

# Define the lists for each category
economies = ['01_AUS', '02_BD', '03_CDA', '04_CHL', '05_PRC', '06_HKC', '07_INA', 
             '08_JPN', '09_ROK', '10_MAS', '11_MEX', '12_NZ', '13_PNG', '14_PE', 
             '15_PHL', '16_RUS', '17_SGP', '18_CT', '19_THA', '20_USA', '21_VN']

sectors = ['16_01_01_commercial_and_public_services', '16_01_02_residential']

end_uses = ['space_heating', 'space_cooling', 'water_heating', 'cooking', 'lighting', 'residential_appliances']

fuels = ['biofuels', 'coal', 'electricity', 'gas', 'heat', 'oil', 'other', 'solar_thermal']

years = list(range(2000, 2101))

# Create all combinations of economy, sector, end_use, fuel, and year
combinations = list(itertools.product(economies, sectors, end_uses, fuels, years))

# Convert to DataFrame
df = pd.DataFrame(combinations, columns=['economy', 'sector', 'end_use', 'fuel', 'year'])

# Display the first few rows
print(df.head())

df_sorted = df.sort_values(by=['economy', 'sector', 'end_use', 'year', 'fuel'])
print(df_sorted.head())

output_dir_csv = config.root_dir + '/output_data/a4a_df_created/'
if not os.path.exists(output_dir_csv):
    os.makedirs(output_dir_csv)

# Optionally, save to CSV
df_sorted.to_csv(output_dir_csv + '/df_created_fuels_enduses.csv', index=False)
# %%