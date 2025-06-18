import pandas as pd

# clean air quality data:

aqi_df = []
aqi_files_start_year = 2017

for i in range(5) :
    # load the data into a dataframe
    df = pd.read_csv('raw_data/annual_aqi_by_county_' + str(i + aqi_files_start_year) + '.csv')
    #print(df.info())

    # filter only California data and clean up the dataframe
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df = df[df['state'] == 'California'].drop(columns=['state'])

    aqi_df.append(df)

# combine all aqi years dataframes into one
combined_aqi_df = pd.concat(aqi_df, ignore_index=True)
#print(combined_aqi_df)
combined_aqi_df.to_csv('processed_data/combined_aqi_data.csv')







# clean asthma emergency department visits data

asthma_df = []
asthma_files_start_year = 2017

for i in range(5) :
    # load the data into a dataframe
    df = pd.read_excel('raw_data/Asthma_Emergency_' + str(i + asthma_files_start_year) + '.xlsx')
    #print(df.info())

    # clean up the dataframe
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df.rename(columns={'counties': 'county'}, inplace=True)
    df = df[df['county'] != 'California'] # remove rows with 'California' in county name
    df = df.drop(columns=['lower_95%_limit', 'upper_95%_limit'])  # optional, but cleaner

 
    # add year column and reorder columns to have year after county (like in aqi_df)
    df['year'] = i + asthma_files_start_year
    columns_order = ['county', 'year'] + [col for col in df.columns if col not in ['county', 'year']]
    df = df[columns_order]

    asthma_df.append(df)

# combine all asthma years dataframes into one
combined_asthma_df = pd.concat(asthma_df, ignore_index=True)
#print(combined_asthma_df)
combined_asthma_df.to_csv('processed_data/combined_asthma_data.csv')




# check if all counties data for all years

# list of all county names in california
all_counties = ['Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa',
                'Del Norte', 'El Dorado', 'Fresno', 'Glenn', 'Humboldt', 'Imperial', 'Inyo',
                'Kern', 'Kings', 'Lake', 'Lassen', 'Los Angeles', 'Madera', 'Marin', 'Mariposa',
                'Mendocino', 'Merced', 'Modoc', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Orange',
                'Placer', 'Plumas', 'Riverside', 'Sacramento', 'San Benito', 'San Bernardino',
                'San Diego', 'San Francisco', 'San Joaquin', 'San Luis Obispo', 'San Mateo',
                'Santa Barbara', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Siskiyou',
                'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tulare',
                'Tuolumne', 'Ventura', 'Yolo', 'Yuba']

# check aqi data counties appear consistently (all numbers should be equal)
year_counts = combined_aqi_df.groupby('county')['year'].nunique()
#print(year_counts.sort_values())

# figure out which counties missing in aqi data
aqi_counties = combined_aqi_df['county'].unique()
missing_counties_aqi = set(all_counties) - set(aqi_counties)
#print(missing_counties_aqi)

# find rows with null values in ashtma data
missing_counties_asthma = combined_asthma_df[combined_asthma_df.isnull().any(axis=1)]

# print counties with null values
print(missing_counties_asthma['county'].unique())

# print the entire rows with null values
print(missing_counties_asthma)


####deal with null data



# combine asthma and aqi cleaned data
