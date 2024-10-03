#%%
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
####
# %%

input_data = pd.read_csv(config.root_dir + '/testing/end_uses_IEA/testing.csv')
# end_use  measure	 unit	economy	 fuel	sector	 year	value	value_total	  ratio
# %%
# Instead of setting 0 values to NaN, focus on identifying missing (NaN) values only
missing_combinations = input_data[input_data['value_total'].isna()].copy()


# %%
new_data = pd.DataFrame(columns=['end_use', 'measure', 'unit', 'economy', 'fuel', 'sector', 'year', 'value', 'value_total', 'ratio'])
for year in range(intensity_all['year'].max(), intensity_all['year'].min() - 1, -1):
    new_data_year = intensity_all.loc[intensity_all['year'] == year][['economy', 'end_use', 'sector', 'intensity']].copy()
    new_data_year.dropna(subset=['intensity'], inplace=True)
    new_data = pd.concat([new_data, new_data_year], axis=0)
    new_data = new_data.groupby(['end_use','sector','economy']).mean().reset_index()
