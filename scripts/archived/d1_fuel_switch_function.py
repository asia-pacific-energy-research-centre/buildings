#%%
import pandas as pd
import numpy as np
import os
import re
import plotly.express as px
import glob

####
#self made helper functions
import scripts.x3_utility_functions as x3_utility_functions
import scripts.x1_configurations as x1_configurations
root_dir =re.split('buildings', os.getcwd())[0]+'/buildings'
config = x1_configurations.Config(root_dir)

# %%

# Import data of adjusted fuel use from c2 intensity adjustments
df_initial = pd.read_csv(config.root_dir + '/output_data/fuel_intensity_refine_auto/fueluse_adj_all.csv')

df = df_initial.loc[
    (df_initial['dataset'] == 'projection') &
    (df_initial['fuels'].isin(['01_coal', '08_gas', '17_electricity'])) &
    (df_initial['economy'].isin(['01_AUS', '03_CDA']))
]

df = df.rename(columns={'fueluse_adj': 'fuel_use'}).copy()

# %%

# ALL DUMMY VALUES FOR NOW
# Define transitions for each economy
economy_transitions = {
    '01_AUS': [
        {'from_fuel': '01_coal', 'to_fuel': '08_gas', 'start_year': 2022, 'end_year': 2029},
        {'from_fuel': '08_gas', 'to_fuel': '17_electricity', 'start_year': 2028, 'end_year': 2045}
    ],
    '03_CDA': [
        {'from_fuel': '08_gas', 'to_fuel': '17_electricity', 'start_year': 2022, 'end_year': 2035}
    ]
}

# Define specific efficiency factors for each transition
# Add more as needed
transition_efficiency_factors = {
    ('01_coal', '08_gas'): 0.8,  # Gas is 0.8 times as efficient as coal
    ('08_gas', '17_electricity'): 0.75,  # Electricity is 0.75 times as efficient as gas
}
# %%

# Function to calculate fuel use with specific transitions iteratively

def calculate_fuel_use_with_transitions(row, transitions, transition_efficiency_factors):
    adjusted_fuel_uses = {}
    current_fuel = row['fuels']
    current_fuel_use = row['fuel_use']  # Assuming 'fuel_use' is the column with the original fuel use
    
    for transition in transitions:
        if current_fuel == transition['from_fuel']:
            start_year = transition['start_year']
            end_year = transition['end_year']
            new_fuel = transition['to_fuel']
            
            # Initialize fuel proportions
            fuel_1_proportion = 0.0
            fuel_2_proportion = 0.0
            
            if row['year'] <= start_year:
                fuel_1_proportion = 1.0
                fuel_2_proportion = 0.0
            elif row['year'] > end_year:
                fuel_1_proportion = 0.0
                fuel_2_proportion = 1.0
            else:
                # Exponential transition
                transition_duration = end_year - start_year
                year_position = row['year'] - start_year
                # Set swtich equation/relationship at this line ###########################
                fuel_2_proportion = 1 - np.exp(-5 * (year_position / transition_duration))
                ###########################################################################
                fuel_1_proportion = 1 - fuel_2_proportion
            
            # Calculate the amount of fuel transitioning
            fuel_1_use = current_fuel_use * fuel_1_proportion
            fuel_2_use = current_fuel_use * fuel_2_proportion
            
            efficiency_factor = transition_efficiency_factors.get((current_fuel, new_fuel), 1.0)

            # Apply efficiency only to the transitioning fuel
            adjusted_fuel_uses[f'{current_fuel}_use'] = adjusted_fuel_uses.get(f'{current_fuel}_use', 0) + fuel_1_use
            adjusted_fuel_uses[f'{new_fuel}_use'] = adjusted_fuel_uses.get(f'{new_fuel}_use', 0) + fuel_2_use * efficiency_factor
            
            # Update current fuel and fuel use for the next transition
            current_fuel = new_fuel
            current_fuel_use = fuel_2_use
    
    # If no transition was applied, return the original fuel use
    if not adjusted_fuel_uses:
        adjusted_fuel_uses[f'{current_fuel}_use'] = current_fuel_use
    
    return pd.Series(adjusted_fuel_uses)
# %%
# Loop through each economy, apply the transition rules, and combine results
df_final = pd.DataFrame()

# %%

for economy, transitions in economy_transitions.items():
    df_economy = df[df['economy'] == economy].copy()
    df_transitions = df_economy.apply(
        calculate_fuel_use_with_transitions,
        axis=1,
        transitions=transitions,
        transition_efficiency_factors=transition_efficiency_factors
    )
    df_combined = pd.concat([df_economy, df_transitions], axis=1)
    df_final = pd.concat([df_final, df_combined], ignore_index=True)
# %%
# Display the resulting DataFrame
df_final.sort_values(by=['economy', 'year'])
df_final.to_csv(config.root_dir + '/plotting_output/test_fuel_exchange.csv', index=False)
# %%
