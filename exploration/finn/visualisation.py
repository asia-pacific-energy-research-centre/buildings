
#import eei data from input_data/EEI/activity.xlsx
#%%
import pandas as pd
import numpy as np
import os
import re
os.chdir(re.split('buildings', os.getcwd())[0]+'/buildings')


buildings_final_df = pd.read_csv('input_data/EEI/buildings_final.csv', index=False)







############################################################################################################
#VISUALISATION
############################################################################################################


#%%
#time for som visualisation:
import plotly.express as px

#by economy (as the facet col), create a time series of the energy with color as the end use and y as the year

for sector in buildings_final_df['sector'].unique():
    print(sector)
    #get the data for this sector
    sector_data = buildings_final_df[(buildings_final_df['sector'] == sector) & (buildings_final_df['measure'] == 'energy') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['fuel'] == 'all')]# & (~buildings_final_df['economy'].isna())]
    #extract sector_data for apec economies to add that at the end as end_use=all_apec_only
    apec_sector_data = sector_data[sector_data['economy'] != 'non_apec_iea']
    if sector_data.empty:
        continue
    #sum up in case there are multiple entries for the same economy and year
    sector_data = sector_data.groupby(['year', 'economy', 'end_use']).sum().reset_index()
    #convert to proportions
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['year','economy'])['value'].transform('sum')
    apec_sector_data = apec_sector_data.groupby(['year', 'economy', 'end_use']).sum().reset_index()
    apec_sector_data['value'] = apec_sector_data['value'] / apec_sector_data.groupby(['year','economy'])['value'].transform('sum')
    
    #create an economy which is the avg of the proportion of all the economies
    all_econ = sector_data.copy()
    all_econ['economy'] = 'All'
    all_econ = all_econ.groupby(['year', 'economy', 'end_use']).mean(numeric_only=True).reset_index()
    sector_data = pd.concat([sector_data, all_econ], ignore_index=True)
    apec_sector_data['economy'] = 'All APEC'
    apec_sector_data = apec_sector_data.groupby(['year', 'economy', 'end_use']).mean(numeric_only=True).reset_index()
    sector_data = pd.concat([sector_data, apec_sector_data], ignore_index=True)
    
    #plot
    fig = px.line(sector_data, x='year', y='value', color='end_use', facet_col='economy', facet_col_wrap=3, title=f'{sector} energy use by end use')
    
        
    WRITE_HTML = False
    if WRITE_HTML:
    #save to file
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_use_by_end_use.html')
    #create bar versions which will use the average of all years
    sector_data = sector_data.groupby(['economy', 'end_use']).mean(numeric_only=True).reset_index()
    fig = px.bar(sector_data, x='end_use', y='value', color='end_use', facet_col='economy', facet_col_wrap=3, title=f'{sector} energy use by end use')
        
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_use_by_end_use_bar.html')

#by end use (as the facet col), create a time series of the energy with color as the fuel and y as the year
for sector in buildings_final_df['sector'].unique():
    print(sector)
    #get the data for this sector
    sector_data = buildings_final_df[(buildings_final_df['sector'] == sector) & (buildings_final_df['measure'] == 'energy') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['fuel'] != 'all')]# & (~buildings_final_df['economy'].isna())]
    #extract sector_data for apec economies to add that at the end as end_use=all_apec_only
    apec_sector_data = sector_data[sector_data['economy'] != 'non_apec_iea']
    if sector_data.empty:
        continue
    #sum up in case there are multiple entries for the same economy and year
    sector_data = sector_data.groupby(['year', 'end_use', 'fuel']).sum().reset_index()
    apec_sector_data = apec_sector_data.groupby(['year', 'end_use', 'fuel']).sum().reset_index()
    #convert to proportions
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['year','end_use'])['value'].transform('sum')
    apec_sector_data['value'] = apec_sector_data['value'] / apec_sector_data.groupby(['year','end_use'])['value'].transform('sum')
    
    #create an end use which is the avg of the proportion of all the end uses
    all_econ = sector_data.copy()
    all_econ['end_use'] = 'All'
    all_econ = all_econ.groupby(['year', 'end_use', 'fuel']).mean(numeric_only=True).reset_index()
    sector_data = pd.concat([sector_data, all_econ], ignore_index=True)
    apec_sector_data['end_use'] = 'All APEC'
    apec_sector_data = apec_sector_data.groupby(['year', 'end_use', 'fuel']).mean(numeric_only=True).reset_index()
    sector_data = pd.concat([sector_data, apec_sector_data], ignore_index=True)
    
    #plot
    fig = px.line(sector_data, x='year', y='value', color='fuel', facet_col='end_use', facet_col_wrap=3, title=f'{sector} energy use by fuel')
        
    WRITE_HTML = False
    if WRITE_HTML:
        #save to file
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_end_use_energy_use_by_fuel.html')
    #create bar versions which will use the average of all years
    sector_data = sector_data.groupby(['end_use', 'fuel']).mean(numeric_only=True).reset_index()
    fig = px.bar(sector_data, x='fuel', y='value', color='fuel', facet_col='end_use', facet_col_wrap=3, title=f'{sector} energy use by fuel')
        
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_end_use_energy_use_by_fuel_bar.html')

#%%
#do similar things with energy intensity but we will ahve to include the effect of the per column which is wat the energy intensity's activity is per (e.g. per capita, per floor area etc).
#we want to understand this data by economy and end use so we might have to create a lot of charts. maybe we can drop the year and just have the economy as the facet col, x and color as the end use and a new chart for each per column and sector. THen after we can normalise all per columns to be the same and then compare the indexed intensity of end uses by economy. When we normalise i guess it should be done in two ways, across the columns:  end use and sector and then across the rows: sector


for sector in buildings_final_df['sector'].unique():
    for per_col in buildings_final_df['per'].unique():
        sector_data = buildings_final_df[(buildings_final_df['sector'] == sector) & (buildings_final_df['measure'] == 'energy_intensity') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['per'] == per_col) & (buildings_final_df['fuel'] == 'all')]
        #extract sector_data for apec economies to add that at the end as end_use=all_apec_only
        apec_sector_data = sector_data[sector_data['economy'] != 'non_apec_iea']
        if sector_data.empty:
            continue
        #sum up in case there are multiple entries for the same economy and year
        sector_data = sector_data.groupby(['economy', 'end_use']).mean(numeric_only=True).reset_index()
        apec_sector_data = apec_sector_data.groupby(['economy', 'end_use']).mean(numeric_only=True).reset_index()
        #create an end use which is the avg of all economies intensities (not weighted!)
        all_econ = sector_data.copy()
        all_econ['economy'] = 'All'
        all_econ = all_econ.groupby(['economy', 'end_use']).mean(numeric_only=True).reset_index()
        sector_data = pd.concat([sector_data, all_econ], ignore_index=True)
        apec_sector_data['economy'] = 'All APEC'
        apec_sector_data = apec_sector_data.groupby(['economy', 'end_use']).mean(numeric_only=True).reset_index()
        sector_data = pd.concat([sector_data, apec_sector_data], ignore_index=True)
        
        #plot
        fig = px.bar(sector_data, x='end_use', y='value', color='end_use', facet_col='economy', facet_col_wrap=3, title=f'{sector} energy intensity by end use per {per_col}')
        #save to file
                
        WRITE_HTML = False
        if WRITE_HTML:
            fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_intensity_by_end_use_per_{per_col}.html')
        
    #normalise by the per columns 'THen after we can normalise all per columns to be the same and then compare the indexed intensity of end uses by economy. When we normalise i guess it should be done by removing the end use column and then normlising across the rows: sector'
    normalised_1 = buildings_final_df[(buildings_final_df['sector'] == sector) & (buildings_final_df['measure'] == 'energy_intensity') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['fuel'] == 'all')]
    if normalised_1.empty:
        continue
    normalised_apec_1 = normalised_1[normalised_1['economy'] != 'non_apec_iea']
    #first take the mean across all other columns but the per and grouping columns
    normalised_1 = normalised_1.groupby(['economy', 'end_use', 'per']).mean(numeric_only=True).reset_index()
    #create the all apec economy now
    normalised_apec_1 = normalised_apec_1.groupby(['economy', 'end_use', 'per']).mean(numeric_only=True).reset_index()
    normalised_apec_1['economy'] = 'All APEC'
    normalised_apec_1 = normalised_apec_1.groupby(['economy', 'end_use', 'per']).mean(numeric_only=True).reset_index()
    normalised_1 = pd.concat([normalised_1, normalised_apec_1], ignore_index=True)
    
    #now normalise the data in the value column by the mean of the value column for each per column
    normalised_1['value'] = normalised_1['value'] / normalised_1.groupby(['economy', 'per'])['value'].transform('mean')
    #to uderstand the effect, take the mean of the normalised values for each end use and then by each economy, and then by both and then by per and then by per and end use and then by per and economy
    # to understand the effect of the normalisation
    for groups in [['economy'], ['end_use'], ['economy', 'end_use'], ['per'], ['per', 'end_use']]:
        #plot a bar
        normalised_2 = normalised_1.groupby(groups).mean(numeric_only=True).reset_index().copy()
        
        if len(groups) != 1:        
            normalised_2['group'] = normalised_2[groups[0]] + ' ' + normalised_2[groups[1]]
            fig = px.bar(normalised_2, x='group', y='value', color='group', title=f'{sector} normalised energy intensity by end use per {groups}')
        else:
            normalised_2['group'] = normalised_2[groups[0]]
            
        
                
        WRITE_HTML = False
        if WRITE_HTML:
            fig.write_html(f'plotting_output/analysis/buildings/{sector}_normalised_energy_intensity_by_end_use_per_{groups}.html')
        
    #plot
    fig = px.bar(normalised_1, x='end_use', y='value', color='per', facet_col='economy', facet_col_wrap=3, title=f'{sector} normalised energy intensity by end use')
        
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_normalised_energy_intensity_by_end_use_with_per.html')
    #plot with average of all pers
    normalised_2 = normalised_1.groupby(['economy', 'end_use']).mean(numeric_only=True).reset_index()
    fig = px.bar(normalised_2, x='end_use', y='value', color='end_use', facet_col='economy', facet_col_wrap=3, title=f'{sector} normalised energy intensity by end use')
    #save to file
        
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_normalised_energy_intensity_by_end_use.html')
    
#%% 





#try taking the average intensity by 'per', 'end_use' and economy then plot that with per and end use as facet cols and rows and then economyas x
for sector in buildings_final_df['sector'].unique():
    print(sector)
    #get the data for this sector
    sector_data = buildings_final_df[(buildings_final_df['sector'] == sector) & (buildings_final_df['measure'] == 'energy_intensity') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['fuel'] == 'all')]# & (~buildings_final_df['economy'].isna())]
    
    #############
    #lets also average out all the applicances (that is teh end uses: 'clothes_dryers', 'clothes_washers','dish_washers',
    #     'freezers', 'personal_computers',
    #     'refrigerator_freezer_combinations', 'refrigerators',
    #     'televisions', 
    # sector_data.end_use.unique()
    # array(['clothes_dryers', 'clothes_washers', 'cooking', 'dish_washers',
    #     'freezers', 'lighting', 'other_appliances', 'personal_computers',
    #     'refrigerator_freezer_combinations', 'refrigerators',
    #     'residential_appliances', 'space_cooling', 'space_heating',
    #     'televisions', 'water_heating'], dtype=object)
    
    appliances = ['clothes_dryers', 'clothes_washers','dish_washers', 'freezers', 'personal_computers', 'refrigerator_freezer_combinations', 'refrigerators', 'televisions']
    sector_data['end_use'] = sector_data['end_use'].replace(appliances, 'appliances')#this really should be weighted. lets jsut rmeove them since qwe have 'residential_appliances'
    sector_data = sector_data[sector_data['end_use'] != 'appliances']
    #############
    
    #then drop per = unit_equipment as we are not interested in that now all appliances are grouped
    sector_data = sector_data[sector_data['per'] != 'unit_equipment']
    
    #extract sector_data for apec economies to add that at the end as end_use=all_apec_only
    apec_sector_data = sector_data[sector_data['economy'] != 'non_apec_iea']
    if sector_data.empty:
        continue
    #sum up in case there are multiple entries for the same economy and year
    sector_data = sector_data.groupby(['economy', 'end_use', 'per']).mean(numeric_only=True).reset_index()
    apec_sector_data = apec_sector_data.groupby(['economy', 'end_use', 'per']).mean(numeric_only=True).reset_index()
    #create an end use which is the avg of all economies intensities (not weighted!)
    all_econ = sector_data.copy()
    all_econ['economy'] = 'All'
    all_econ = all_econ.groupby(['economy', 'end_use', 'per']).mean(numeric_only=True).reset_index()
    sector_data = pd.concat([sector_data, all_econ], ignore_index=True)
    apec_sector_data['economy'] = 'All APEC'
    apec_sector_data = apec_sector_data.groupby(['economy', 'end_use', 'per']).mean(numeric_only=True).reset_index()
    sector_data = pd.concat([sector_data, apec_sector_data], ignore_index=True)
    
    #try taking the average intensity by 'per', 'end_use' and economy then plot that with per and end use as facet cols and rows and then economyas x
    #plot
    fig = px.bar(sector_data, x='economy', y='value', color='economy', facet_col='per', facet_row='end_use', title=f'{sector} energy intensity by end use and per')
        
    WRITE_HTML = False
    if WRITE_HTML:
    #save to file
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_intensity_by_end_use.html')
    
    #what about a scatter with x = end use, facet row = per, y = value, color = economy
    breakpoint()
    fig = px.scatter(sector_data, x='end_use', y='value', color='economy', facet_col='per', title=f'{sector} energy intensity by end use and per') 
    #make axes independent usign matches = False
    
    #make the facets y axis independent
    fig.update_yaxes(matches=None, showticklabels=True)
    fig.update_xaxes(matches=None, showticklabels=True)
    
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_intensity_by_end_use_scatter.html')
    
    
    
    
#%%
#from this we've found some things that we can do to clean up the data and simplify it. We will:
#drop the following appliances since they contain more detial than we need:
appliances = ['clothes_dryers', 'clothes_washers','dish_washers', 'freezers', 'personal_computers', 'refrigerator_freezer_combinations', 'refrigerators', 'televisions']
buildings_final_df['end_use'] = buildings_final_df['end_use'].replace(appliances, 'appliances')#this really should be weighted. lets jsut rmeove them since qwe have 'residential_appliances'
buildings_final_df = buildings_final_df[buildings_final_df['end_use'] != 'appliances']

#drop where per = dwelling_tc and floor_area_tc and unit_equipment and serices_employee (even though they are super interestin!)
buildings_final_df = buildings_final_df[~buildings_final_df['per'].isin(['dwelling_tc', 'floor_area_tc', 'unit_equipment', 'services_employee'])]

#%%
#now create anotehr set of charts just lkike the last but use the shape argument to show the sector.

#try taking the average intensity by 'per', 'end_use' and economy then plot that with per and end use as facet cols and rows and then economyas x

#get the data for this sector
intensity_plot_final = buildings_final_df[(buildings_final_df['measure'] == 'energy_intensity') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['fuel'] == 'all')]# & (~buildings_final_df['economy'].isna())]

#extract intensity_plot_final for apec economies to add that at the end as end_use=all_apec_only
apec_intensity_plot_final = intensity_plot_final[intensity_plot_final['economy'] != 'non_apec_iea']

#sum up in case there are multiple entries for the same economy and year
intensity_plot_final = intensity_plot_final.groupby(['economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()
apec_intensity_plot_final = apec_intensity_plot_final.groupby(['economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()
#create an end use which is the avg of all economies intensities (not weighted!)
all_econ = intensity_plot_final.copy()
all_econ['economy'] = 'All'
all_econ = all_econ.groupby(['economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()
intensity_plot_final = pd.concat([intensity_plot_final, all_econ], ignore_index=True)
apec_intensity_plot_final['economy'] = 'All APEC'
apec_intensity_plot_final = apec_intensity_plot_final.groupby(['economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()
intensity_plot_final = pd.concat([intensity_plot_final, apec_intensity_plot_final], ignore_index=True)

#try taking the average intensity by 'per', 'end_use' and economy then plot that with per and end use as facet cols and rows and then economyas x
#plot
fig = px.bar(intensity_plot_final, x='economy', y='value', color='economy', facet_col='per', facet_row='end_use', title=f'energy intensity by end use and per', pattern_shape='sector')

WRITE_HTML = False
if WRITE_HTML:
#save to file
    fig.write_html(f'plotting_output/analysis/buildings/by_economy_energy_intensity_by_end_use.html')

#what about a scatter with x = end use, facet row = per, y = value, color = economy
fig = px.scatter(intensity_plot_final, x='end_use', y='value', color='economy', facet_col='per', title=f'energy intensity by end use and per', symbol='sector')
#make axes independent usign matches = False

#make the facets y axis independent
fig.update_yaxes(matches=None, showticklabels=True)
fig.update_xaxes(matches=None, showticklabels=True)

WRITE_HTML = False
if WRITE_HTML:
    fig.write_html(f'plotting_output/analysis/buildings/by_economy_energy_intensity_by_end_use_scatter.html')
#%%
#since we know its a good chart, also show it by year, economy end use - normalised.
#we will normalis within each per sicne we know that the remaining values should all be on the same scale:

#get the data for this sector
intensity_plot_final = buildings_final_df[(buildings_final_df['measure'] == 'energy_intensity') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['fuel'] == 'all')]# & (~buildings_final_df['economy'].isna())]
#extract intensity_plot_final for apec economies to add that at the end as end_use=all_apec_only
apec_intensity_plot_final = intensity_plot_final[intensity_plot_final['economy'] != 'non_apec_iea']

#sum up in case there are multiple entries for the same economy and year
intensity_plot_final = intensity_plot_final.groupby(['year', 'economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()
apec_intensity_plot_final = apec_intensity_plot_final.groupby(['year', 'economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()

#create an end use which is the avg of all economies intensities (not weighted!)
all_econ = intensity_plot_final.copy()
all_econ['economy'] = 'All'
all_econ = all_econ.groupby(['year', 'economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()
intensity_plot_final = pd.concat([intensity_plot_final, all_econ], ignore_index=True)
apec_intensity_plot_final['economy'] = 'All APEC'
apec_intensity_plot_final = apec_intensity_plot_final.groupby(['year', 'economy', 'end_use', 'per', 'sector']).mean(numeric_only=True).reset_index()
intensity_plot_final = pd.concat([intensity_plot_final, apec_intensity_plot_final], ignore_index=True)


normalisation = intensity_plot_final.copy()
#do min max normalisation
normalisation['value'] = (normalisation['value'] - normalisation.groupby('per')['value'].transform('min')) / (normalisation.groupby('per')['value'].transform('max') - normalisation.groupby('per')['value'].transform('min'))
intensity_plot_final = normalisation.copy()

#now average out the normalised values
intensity_plot_final = intensity_plot_final.groupby(['year', 'economy', 'end_use', 'sector']).mean(numeric_only=True).reset_index()

fig = px.line(intensity_plot_final, x='year', y='value', color='end_use', facet_col='economy', facet_col_wrap=3, title=f'Normalised energy intensity by end use', line_dash='sector')
#make axes independent usign matches = False

#make the facets y axis independent
fig.update_yaxes(matches=None, showticklabels=True)
fig.update_xaxes(matches=None, showticklabels=True)

WRITE_HTML = False
if WRITE_HTML:
    fig.write_html(f'plotting_output/analysis/buildings/by_economy_energy_intensity_by_end_use_line_normalised.html')

#%%
##################################

















##################################
#GOOD CHART:
##################################
#and do a normalised scatter which will include the ability to look at how per cpita differs from the avg:

#sep the per capita out sicne we know tahts a a scale we would liek to use, then show that on the graph too so we can see how its normalised value compares to the others
normalisation_per_capita = normalisation[normalisation['per'] == 'capita']
normalisation_per_capita['per_capita'] = True
normalisation_per_capita = normalisation_per_capita.groupby([ 'end_use', 'sector','per_capita']).mean(numeric_only=True).reset_index()

#create a copy of it for each per in dweling and floor area so we can plot it against those:
normalisation_dwelling = normalisation[normalisation['per'] == 'dwelling']
normalisation_dwelling = normalisation_dwelling.groupby([ 'end_use', 'sector']).mean(numeric_only=True).reset_index()
normalisation_dwelling['per_capita'] = False
normalisation_dwelling = pd.concat([normalisation_dwelling, normalisation_per_capita], ignore_index=True)
normalisation_dwelling['per'] = 'dwelling'

normalisation_floor_area = normalisation[normalisation['per'] == 'floor_area']
normalisation_floor_area = normalisation_floor_area.groupby([ 'end_use', 'sector']).mean(numeric_only=True).reset_index()
normalisation_floor_area['per_capita'] = False
normalisation_floor_area = pd.concat([normalisation_floor_area, normalisation_per_capita], ignore_index=True)
normalisation_floor_area['per'] = 'floor_area'

normalisation_avg = normalisation.groupby([ 'end_use', 'sector']).mean(numeric_only=True).reset_index()
normalisation_avg['per_capita'] = False
normalisation_avg = pd.concat([normalisation_avg, normalisation_per_capita], ignore_index=True)
normalisation_avg['per'] = 'avg'

normalisation_per_capita['per'] ='capita'

normalisation_all = pd.concat([normalisation_dwelling, normalisation_floor_area, normalisation_avg, normalisation_per_capita], ignore_index=True)

#now show the scatter
fig = px.scatter(normalisation_all, x='end_use', y='value', color='sector', facet_col='per', title=f'Normalised energy intensity by end use', symbol='per_capita')

#add sentence at the bottom which explains this: per column is wat the energy intensity's activity is per (e.g. per capita, per floor area etc)
fig.add_annotation(
    x=0.5, y=1.25, xref='paper', yref='paper', showarrow=False,
    text=(
        'Per column is what the energy intensity\'s activity is per (e.g. per capita, per floor area etc).<br>'
        'Per capita will be True or False depending on if the datapoint is for the per capita intensity measure or not. The symbol is the sector of the data point.<br>'
        'When reading this chart, remember our goal is to see if we can use per capita intensity values as intensity values, since they are easily calculated and scaled against population in the projections.<br>'
        'And note that the per capita values are normalised to be on the same scale as the other values.<br>'
        'Therefore, if the per capita values are much different than the other values then maybe we should use other intensity measures for that end use.<br>'
        'But if the other values are relatively similar to each other in scale then if at least one of them is accurate then the others should be too.'
    ),
    font=dict(size=10)
)

fig.write_html(f'plotting_output/analysis/buildings/by_economy_energy_intensity_by_end_use_line_normalised_comp_with_per_cap.html')
##################################
#above is a good chart. shows how the per capita values compare to the other values when normalised. therefore it shows how the scale of the per capita values compare to the other values and between each other. i.e. per capita space heating intensity is a lot higher than the other 'per' values, which means that maybe we should use other intensity measures for space heating. But the other values are relatively similar to each other in scale which means that if at least one of them is accurate then the others should be too.
##################################























#%%Now lets do a simialr thig for energy use but jsut take the average proportion of energy use by end use, sector, economy, year and fuel
#then show a line and scatter of the proportion of energy use with :
# line: color = end use - sector, facet= economy and line_dash = fuel and y = value with x = year 
# scatter: color = fuel, facet = economy, x = year, y = value, symbol = end use - sector

#but also reduce the amount of end use categories by dropping the appliances:
appliances = ['clothes_dryers', 'clothes_washers','dish_washers', 'freezers', 'personal_computers', 'refrigerator_freezer_combinations', 'refrigerators', 'televisions']
energy = buildings_final_df[(buildings_final_df['measure'] == 'energy') & (buildings_final_df['end_use'] != 'total') & (buildings_final_df['fuel'] != 'all')]# & 

energy = energy[~energy['end_use'].isin(appliances)]

#extract energy for apec economies to add that at the end as end_use=all_apec_only
apec_energy = energy[energy['economy'] != 'non_apec_iea']
apec_energy['economy'] = 'All APEC'

#sum up in case there are multiple entries for the same economy and year
energy = energy.groupby(['year', 'economy', 'end_use', 'sector', 'fuel']).sum(numeric_only=True).reset_index()

apec_energy = apec_energy.groupby(['year', 'economy', 'end_use', 'sector', 'fuel']).sum(numeric_only=True).reset_index()

energy = pd.concat([energy, apec_energy], ignore_index=True)
#%%
for sector in energy['sector'].unique():
    print(sector)
    #get the data for this sector
    sector_data = energy[energy['sector'] == sector]
    if sector_data.empty:
        continue
    
    #now calculate the proportion of energy used for each economy/year combination
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['year', 'economy', 'sector'])['value'].transform('sum')

    #create color and line_dash columns
    sector_data['color'] = sector_data['end_use'] + ' - ' + sector_data['sector']
    sector_data['line_dash'] = sector_data['fuel']

    #plot
    fig = px.line(sector_data, x='year', y='value', color='color', facet_col='economy', facet_col_wrap=3, title=f'{sector} - energy use by end use', line_dash='line_dash')
        
    WRITE_HTML = False
    if WRITE_HTML:
        #save to file
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_use_by_end_use.html')
    ##################
    #and then remove the fuel and reclacualte: (by end use, no fuel)
    sector_data = energy[energy['sector'] == sector]
    sector_data = sector_data.groupby(['year', 'economy', 'end_use', 'sector']).sum(numeric_only=True).reset_index()
    #calculate the proportion
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['year', 'economy', 'sector'])['value'].transform('sum')
    fig = px.line(sector_data, x='year', y='value', color='end_use', facet_col='economy', facet_col_wrap=3, title=f'{sector} - energy use by end use')
        
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_use_by_end_use_no_fuel.html')
    ##################
    #and then do it by fuel, no end use
    sector_data = energy[energy['sector'] == sector]
    sector_data = sector_data.groupby(['year', 'economy','sector', 'fuel']).sum(numeric_only=True).reset_index()
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['year', 'economy','sector'])['value'].transform('sum')
    fig = px.line(sector_data, x='year', y='value', color='fuel', facet_col='economy', facet_col_wrap=3, title=f'{sector} - energy use by fuel')
        
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_use_by_fuel.html')
    ##################
    #and then do some scatter plots which remove the year 
    ##################
    #remove the year and recalcualte:
    sector_data = energy[energy['sector'] == sector]
    sector_data = sector_data.groupby(['year', 'economy', 'end_use', 'sector', 'fuel']).sum(numeric_only=True).reset_index()
    
    #take a look at the scatter plot of energy use by end use, with color as fuel 
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['year', 'economy', 'end_use','sector'])['value'].transform('sum')
    #average out the proportions with no year
    sector_data = sector_data.groupby(['economy', 'end_use', 'sector', 'fuel']).mean(numeric_only=True).reset_index()
    #reclculate the proportion
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['economy', 'end_use','sector'])['value'].transform('sum')
    fig = px.scatter(sector_data, x='end_use', y='value', color='fuel', facet_col='economy', facet_col_wrap=3, title=f'{sector} - energy use by end use', symbol='fuel')
    
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_use_by_end_use_scatter.html')
    ##################
    #take a look at the scatter plot of energy use by fuel, with color as end use
    sector_data = energy[energy['sector'] == sector]
    sector_data = sector_data.groupby(['year', 'economy', 'end_use', 'sector', 'fuel']).sum(numeric_only=True).reset_index()
    
    #take a look at the scatter plot of energy use by end use, with color as fuel 
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['year', 'economy', 'fuel','sector'])['value'].transform('sum')
    #average out the proportions with no year
    sector_data = sector_data.groupby(['economy', 'end_use', 'sector', 'fuel']).mean(numeric_only=True).reset_index()
    #reclculate the proportion
    sector_data['value'] = sector_data['value'] / sector_data.groupby(['economy', 'fuel','sector'])['value'].transform('sum')
    fig = px.scatter(sector_data, x='fuel', y='value', color='end_use', facet_col='economy', facet_col_wrap=3, title=f'{sector} - energy use by fuel', symbol='end_use')
        
    WRITE_HTML = False
    if WRITE_HTML:
        fig.write_html(f'plotting_output/analysis/buildings/{sector}_by_economy_energy_use_by_fuel_scatter.html')
    
#%%
#at the end of the day its not that interesting to see the energy use since we kind of expect it. more useful as a modelling input:












#%%
#ok lets see if we can calcualte the proportion of energy used for each end use
# as well as the proportion of end use by technology
# and proportion of technology by fuel type
#PROPORTIONS:
energy['value'] = energy['value'] / energy.groupby(['year', 'economy', 'sector', 'fuel'])['value'].transform('sum')
energy['value'] = energy['value'] / energy.groupby(['year', 'economy', 'sector'])['value'].transform('sum')
energy['value'] = energy['value'] / energy.groupby(['year', 'economy'])['value'].transform('sum')


#%%