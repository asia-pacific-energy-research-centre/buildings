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
# import economy data
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')
# %%
from useful_functions import generate_smooth_curve

# %%
intensity_trajectory = pd.read_csv(config.root_dir + '/output_data/fortrajectory/intensity_trajectory_data.csv')

# %%
# Define years list tp adjust later 
years = [i for i in range(1980, 2101, 1)]

# %%
# Function definition to override modelled trajectory

def fuel_intensity_traj(economy='01_AUS', 
                        fuels='01_coal', 
                        proj_start_year=2021, 
                        shape='increase', 
                        magnitude=1.5, 
                        apex_mag=1.5, 
                        apex_loc=10, 
                        data=intensity_trajectory):
    print("Function started.")    
    # Create directory to save results
    fuel_intensity_refine_auto = config.root_dir + '/output_data/fuel_intensity_refine_auto/{}/'.format(economy)
    if not os.path.isdir(fuel_intensity_refine_auto):
        os.makedirs(fuel_intensity_refine_auto)
    print(f"Creating directory: {fuel_intensity_refine_auto}")

    # Filter data for the specific economy and fuel
    refined_df = data[(data['economy'] == economy) &
                      (data['fuels'] == fuels)].copy().reset_index(drop=True)
    
    # Set year as index
    refined_df = refined_df.set_index('year')
    
    # Initialize new column for refined fuel intensity values
    refined_df['adj_fuel_intensity'] = np.nan

    # Determine starting and ending points for trajectory
    traj_start = refined_df.loc[proj_start_year, 'fuel_intensity_GJperCap'] 
    traj_end = refined_df.loc[proj_start_year, 'fuel_intensity_GJperCap']  * magnitude
    apex = apex_mag * traj_end
    
    # Generate new fuel intensity trajectory
    outcome = generate_smooth_curve(num_points = max(years) - proj_start_year + 1, 
                                    shape = shape,
                                    start_value = traj_start,
                                    end_value = traj_end,
                                    apex_point = apex,
                                    apex_position = apex_loc)
  
    outcome_df = pd.DataFrame(outcome, index = range(proj_start_year, max(refined_df.index) + 1))
    # outcome_df = pd.DataFrame(outcome, index=range(proj_start_year, proj_start_year + num_points))
    # Populate the adjusted fuel intensity column
    for year in refined_df.index:
        if year < proj_start_year:
            refined_df.loc[year, 'adj_fuel_intensity'] = refined_df.loc[year, 'fuel_intensity_GJperCap']
        else:
            refined_df.loc[year, 'adj_fuel_intensity'] = outcome_df.loc[year, 0] 

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
                y='adj_fuel_intensity',
                # color='fuels',
                title=f"{economy} : {fuels}"
                # labels={
                #     'year': 'Year',
                #     'fuel_intensity': 'Fuel Intensity (GJ/cap)',
                #     'fuels': 'Fuel Type'
                # } 
                )

    # Customize layout 
    fig.update_layout(
        yaxis=dict(range=[0, chart_df['adj_fuel_intensity'].max() * 1.1]),
        template='plotly_white'
    )

    # Show the plot in an interactive window
    fig.show()

    # Save the plot as a PNG file
    fig.write_html(fuel_intensity_refine_auto + economy + '_' + fuels + '.html')
   
    # # Saving the adjusted data to a CSV file
    # adj_data = chart_df.copy()[['economy', 'year', 'fuels', 'fuel_PJ', 'population', 'fuel_intensity']]\
    #     .rename(columns={'fuel_intensity': 'adjusted_fuel_intensity'})
    adj_data = chart_df.copy()
    adj_data.to_csv(fuel_intensity_refine_auto + economy + '_' + fuels + '.csv', index=False)


# # %%
# fuel_intensity_traj(economy = '01_AUS', fuels = '01_coal', proj_start_year = 2022, 
#                     shape = 'peak', magnitude = 50, apex_mag = 1.1, apex_loc = 5)
# %%
