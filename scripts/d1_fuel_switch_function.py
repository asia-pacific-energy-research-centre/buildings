

# def apply_fuel_switching(row):
#     if row['year'] >= switch_year and row['old_fuel'] == 'fuel_type_1':
#         return 'fuel_type_2'
#     return row['old_fuel']

# df['new_fuel_type'] = df.apply(apply_fuel_switching, axis=1)
# df['adjusted_fuel_use'] = df.apply(lambda row: row['fuel_use'] * fuel_efficiency_factors[row['new_fuel_type']], axis=1)

import pandas as pd

# Initial DataFrame
data = {
    'year': [2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034] * 2,
    'economy': ['Economy_A'] * 10 + ['Economy_B'] * 10,
    'fuel_type': ['fuel_type_1'] * 10 + ['fuel_type_3'] * 10,
    'fuel_use': [100, 105, 110, 115, 120, 125, 130, 135, 140, 145] * 2,
}

df = pd.DataFrame(data)

# Define fuel efficiency factors
fuel_efficiency_factors = {
    'fuel_type_1': 1.0,
    'fuel_type_2': 0.8,
    'fuel_type_3': 0.9,
    'fuel_type_4': 0.7,
}

# Function to calculate the proportion of each fuel type during the transition
def calculate_fuel_proportion(row, start_year, end_year):
    transition_duration = end_year - start_year + 1
    
    if row['year'] < start_year:
        return 1.0, 0.0  # 100% original fuel
    elif row['year'] > end_year:
        return 0.0, 1.0  # 100% new fuel
    else:
        # Linear transition: gradually reduce original fuel and increase new fuel
        original_fuel_proportion = (end_year - row['year']) / transition_duration
        new_fuel_proportion = 1 - original_fuel_proportion
        return original_fuel_proportion, new_fuel_proportion

# Apply the function to each row
def apply_transition(row, fuel_efficiency_factors, start_year, end_year, new_fuel):
    fuel_1_proportion, fuel_2_proportion = calculate_fuel_proportion(row, start_year, end_year)
    
    adjusted_fuel_use = (
        row['fuel_use'] * fuel_1_proportion * fuel_efficiency_factors[row['fuel_type']] +
        row['fuel_use'] * fuel_2_proportion * fuel_efficiency_factors[new_fuel]
    )
    
    return pd.Series({
        'fuel_1_proportion': fuel_1_proportion,
        'fuel_2_proportion': fuel_2_proportion,
        'new_fuel_type': new_fuel,
        'adjusted_fuel_use': adjusted_fuel_use
    })

# Example of applying the transition for different fuels and economies
# For Economy_A: fuel_type_1 -> fuel_type_2 from 2028 to 2032
df_A = df[df['economy'] == 'Economy_A'].copy()
df_A[['fuel_1_proportion', 'fuel_2_proportion', 'new_fuel_type', 'adjusted_fuel_use']] = df_A.apply(
    apply_transition, 
    axis=1, 
    fuel_efficiency_factors=fuel_efficiency_factors, 
    start_year=2028, 
    end_year=2032, 
    new_fuel='fuel_type_2'
)

# For Economy_B: fuel_type_3 -> fuel_type_4 from 2027 to 2031
df_B = df[df['economy'] == 'Economy_B'].copy()
df_B[['fuel_1_proportion', 'fuel_2_proportion', 'new_fuel_type', 'adjusted_fuel_use']] = df_B.apply(
    apply_transition, 
    axis=1, 
    fuel_efficiency_factors=fuel_efficiency_factors, 
    start_year=2027, 
    end_year=2031, 
    new_fuel='fuel_type_4'
)

# Combine the results
df_combined = pd.concat([df_A, df_B])
print(df_combined)

#test ing 
