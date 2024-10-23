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
####
# %%
from x2_useful_functions import generate_smooth_curve
# %%
# import economy data
economy_list = pd.read_csv(config.root_dir + '/input_data/APEC_economies.csv')


# %%

def switch_fuel_with_trajectory(df_initial, economy, end_use, fuel_1, fuel_2, start_year, end_year, proportion_to_switch, efficiency_factor, shape='increase', apex_mag=1.5, apex_loc=10):
    # Get the number of years for the trajectory
    num_years = end_year - start_year + 1

     # Filter data for the specific economy and fuel
    df = df_initial[(df_initial['economy'] == economy) &
                    (df_initial['end_use'] == end_use)].copy().reset_index(drop=True)
    # Generate the trajectory amounts to switch each year
    traj_amounts = generate_smooth_curve(num_years, shape, 0, proportion_to_switch, apex_mag, apex_loc)
    
    for year, switch_amount in zip(range(start_year, end_year + 1), traj_amounts):
        # Get rows for fuel_1 and fuel_2 for the given year and specified economy
        # fuel_1_rows = df[(df['fuel'] == fuel_1) & (df['year'] == year) & (df['economy'] == economy) & (df['end_use'] == end_use)]
        # fuel_2_rows = df[(df['fuel'] == fuel_2) & (df['year'] == year) & (df['economy'] == economy) & (df['end_use'] == end_use)]
        fuel_1_rows = df[(df['name'] == fuel_1) & (df['year'] == year) & (df['economy'] == economy) & (df['end_use'] == end_use)]
        fuel_2_rows = df[(df['name'] == fuel_2) & (df['year'] == year) & (df['economy'] == economy) & (df['end_use'] == end_use)]
        
        for index, row in fuel_1_rows.iterrows():
            # Calculate the actual amount to switch
            fuel_to_switch = row['subfuel_amount'] * switch_amount
            
            # Subtract from fuel_1 and add adjusted amount to fuel_2 based on efficiency
            df.loc[index, 'subfuel_amount'] -= fuel_to_switch
            
            # Adjust for efficiency when adding to fuel_2
            adjusted_fuel_to_add = fuel_to_switch * efficiency_factor
            
            # Find the corresponding fuel_2 row
            corresponding_fuel_2 = fuel_2_rows[(fuel_2_rows['sub2sectors'] == row['sub2sectors'])]
            
            if not corresponding_fuel_2.empty:
                # Add the adjusted switched fuel to the existing fuel_2 row
                df.loc[corresponding_fuel_2.index, 'subfuel_amount'] += adjusted_fuel_to_add
            else:
                # If fuel_2 doesn't exist for this economy/year, create a new row
                new_row = row.copy()
                new_row['name'] = fuel_2
                new_row['subfuel_amount'] = adjusted_fuel_to_add
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df





# %%
