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

economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
####

# %%
end_use_projection = pd.read_csv(config.root_dir + '/output_data/projection_w_end_use.csv')

output_dir = config.root_dir + '/plotting_output/analysis/end_use_projection/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# %%

# #plot
# fig = px.area(end_use_projection, x='year', y='energy', color='sub2sectors', facet_col='end_use_sector')
# # , facet_col_wrap=7
# fig.update_yaxes(matches=None, showticklabels=True)
# fig.write_html(output_dir + 'energy_projection_use_by_end_use.html')

# 'economy_list' is the list of APEC economies
for economy in economy_list['economy_code']:
    # Filter the DataFrame for the current economy
    filtered_df = end_use_projection[end_use_projection['economy'] == economy]

    # Create the plot
    fig = px.line(filtered_df, x='year', y='energy', color='sub2sectors', facet_col='end_use', facet_col_wrap=3)
    fig.update_yaxes(matches=None, showticklabels=True)
    
    # Save the plot to an HTML file
    output_file = output_dir + f'{economy}_energy_projection_use_by_end_use.html'
    fig.write_html(output_file)
# %%

eei = pd.read_csv(os.path.join(config.root_dir, 'input_data','eei', 'buildings_final.csv'))
filtered_df = eei[eei['economy'].isin(economy_list['economy_code'])]
filtered_df.to_csv(config.root_dir + '/testforendus.csv')
# print(filtered_df['economy'].unique())
# filtered_df_all_energy = 



# %%




# %%
