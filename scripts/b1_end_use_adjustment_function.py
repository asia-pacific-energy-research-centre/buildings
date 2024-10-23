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
####
# %%
# import economy data
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
# %%
from x2_useful_functions import generate_smooth_curve

# %%
end_use_trajectory = pd.read_csv(config.root_dir + '/output_data/a1_projection/projection_w_end_use_scaled.csv')
# end_use_trajectory = end_use_trajectory1[end_use_trajectory1['year'] != 2101]



# %%
# Define years list tp adjust later 
years = [i for i in range(1980, 2071, 1)]

# %%
# Function definition to override modelled trajectory

def traj(economy='01_AUS', 
        end_use = 'cooking',
        sector = '16_01_02_residential', # 16_01_01_commercial_and_public_services 
        proj_start_year=2021, 
        shape='increase', 
        magnitude=1.5, 
        apex_mag=1.5, 
        apex_loc=10, 
        data=end_use_trajectory):
    print("Function started.")    
    # Create directory to save results
    energy_refine_auto_csv = config.root_dir + '/output_data/b2_end_use_adjustment_apply/{}/'.format(economy)
    if not os.path.isdir(energy_refine_auto_csv):
        os.makedirs(energy_refine_auto_csv)
    print(f"Creating directory: {energy_refine_auto_csv}")

    energy_refine_auto_fig = config.root_dir + '/plotting_output/b2_end_use_adjustment_apply/{}/'.format(economy)
    if not os.path.isdir(energy_refine_auto_fig):
        os.makedirs(energy_refine_auto_fig)
    print(f"Creating directory: {energy_refine_auto_fig}")

    # Filter data for the specific economy and fuel
    refined_df = data[(data['economy'] == economy) &
                      (data['end_use'] == end_use) &
                      (data['sub2sectors'] == sector)].copy().reset_index(drop=True)
    
    # Set year as index
    refined_df = refined_df.set_index('year')
    
    # Initialize new column for refined fuel intensity values
    refined_df['adj_energy'] = np.nan

    # Determine starting and ending points for trajectory
    traj_start = refined_df.loc[proj_start_year, 'energy'] 
    traj_end = refined_df.loc[proj_start_year, 'energy']  * magnitude
    apex = apex_mag * traj_end
    
    # Generate new fuel intensity trajectory
    outcome = generate_smooth_curve(num_points = max(years) - proj_start_year + 1, 
                                    shape = shape,
                                    start_value = traj_start,
                                    end_value = traj_end,
                                    apex_point = apex,
                                    apex_position = apex_loc)
  
    outcome_df = pd.DataFrame(outcome, index = range(proj_start_year, max(refined_df.index) + 1))
    # outcome_df = pd.DataFrame(outcome, index=range(proj_start_year, proj_start_year + num_points)
    # Populate the adjusted fuel intensity column
    for year in refined_df.index:
        if year < proj_start_year:
            refined_df.loc[year, 'adj_energy'] = refined_df.loc[year, 'energy']
        else:
            refined_df.loc[year, 'adj_energy'] = outcome_df.loc[year, 0] 

    # Reset index
    refined_df = refined_df.reset_index()

    # Melt the DataFrame for easy plotting
    # chart_df = refined_df.melt(id_vars=['year', 'economy', 'fuels', 'dataset', 'population', 'fuel_PJ'], 
    #                            value_vars=['fuel_intensity_GJperCap', 'adj_fuel_intensity'], 
    #                            value_name='fuel_intensity')

    chart_df = refined_df.copy()

    # Creating the line plot using Plotly Express
    fig = px.line(chart_df,
                x='year',
                y='adj_energy',
                # color='fuels',
                title=f"{economy} : {end_use} : {sector}"
                # labels={
                #     'year': 'Year',
                #     'fuel_intensity': 'Fuel Intensity (GJ/cap)',
                #     'fuels': 'Fuel Type'
                # } 
                )

    # Customize layout 
    fig.update_layout(
        yaxis=dict(range=[0, chart_df['adj_energy'].max() * 1.1]),
        template='plotly_white'
    )

    # Show the plot in an interactive window
    fig.show()

    # Save the plot as a PNG file
    fig.write_html(energy_refine_auto_fig + economy + '_' + end_use + '.html')
   
    # # Saving the adjusted data to a CSV file
    # adj_data = chart_df.copy()[['economy', 'year', 'fuels', 'fuel_PJ', 'population', 'fuel_intensity']]\
    #     .rename(columns={'fuel_intensity': 'adjusted_fuel_intensity'})
    adj_data = chart_df.copy()
    adj_data.to_csv(energy_refine_auto_csv + economy + '_' + end_use + '.csv', index=False)


# # %%
# fuel_intensity_traj(economy = '01_AUS', fuels = '01_coal', proj_start_year = 2022, 
#                     shape = 'peak', magnitude = 50, apex_mag = 1.1, apex_loc = 5)
# %%
