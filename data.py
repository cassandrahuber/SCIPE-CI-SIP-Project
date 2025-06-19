import pandas as pd

# clean air quality data:
def clean_aqi_quality_data(start_year, num_years, input_folder) :
    aqi_df = []
    for i in range(num_years) :
        # load the data into a dataframe
        df = pd.read_csv(f'{input_folder}/annual_aqi_by_county_{start_year + i}.csv')

        # filter only California data and clean up the dataframe
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df = df[df['state'] == 'California'].drop(columns=['state'])

        aqi_df.append(df)

    # combine all aqi years dataframes into one
    cleaned_aqi_df = pd.concat(aqi_df, ignore_index=True)
    #print(cleaned_aqi_df)
    #cleaned_aqi_df.to_csv('processed_data/cleaned_aqi.csv')

    return cleaned_aqi_df





# clean asthma emergency department visits data
def clean_asthma_ed_visits_data(start_year, num_years, input_folder) :
    asthma_df = []
    for i in range(num_years) :
        # load the data into a dataframe
        df = pd.read_excel(f'{input_folder}/Asthma_Emergency_{start_year + i}.xlsx')

        # clean up the dataframe
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df.rename(columns={'counties': 'county'}, inplace=True)
        df = df[df['county'] != 'California'] # remove rows with 'California' in county name
        df = df.drop(columns=['lower_95%_limit', 'upper_95%_limit'])  # optional, but cleaner

        # add year column and reorder columns to have year after county (like in aqi_df)
        df['year'] = start_year + i
        columns_order = ['county', 'year'] + [col for col in df.columns if col not in ['county', 'year']]
        df = df[columns_order]

        asthma_df.append(df)

    # combine all asthma years dataframes into one
    cleaned_asthma_df = pd.concat(asthma_df, ignore_index=True)
    #print(cleaned_asthma_df)
    #cleaned_asthma_df.to_csv('processed_data/cleaned_asthma.csv')
    #cleaned_asthma_df.to_csv('processed_data/cleaned_asthma_' + str(asthma_files_start_year) + '-' + str(i + asthma_files_start_year) + '.csv')

    return cleaned_asthma_df





# check if all counties data for all years
def find_missing_data(cleaned_aqi_df, cleaned_asthma_df, all_counties) :
    
    # find counties missing in aqi data
    aqi_counties = cleaned_aqi_df['county'].unique()
    missing_counties_aqi = set(all_counties) - set(aqi_counties)

    # find rows with null values in ashtma data
    missing_counties_asthma = cleaned_asthma_df[cleaned_asthma_df.isnull().any(axis=1)]

    return missing_counties_aqi, missing_counties_asthma

# check aqi data counties appear consistently (all numbers should be equal)
year_counts = cleaned_aqi_df.groupby('county')['year'].nunique()
#print(year_counts.sort_values())

# list of all county names in california
all_counties = ['Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa',
                'Del Norte', 'El Dorado', 'Fresno', 'Glenn', 'Humboldt', 'Imperial', 'Inyo',
                'Kern', 'Kings', 'Lake', 'Lassen', 'Los Angeles', 'Madera', 'Marin', 'Mariposa',
                'Mendocino', 'Merced', 'Modoc', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Orange',
                'Placer', 'Plumas', 'Riverside', 'Sacramento', 'San Benito', 'San Bernardino',                    'San Diego', 'San Francisco', 'San Joaquin', 'San Luis Obispo', 'San Mateo',
                'Santa Barbara', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Siskiyou',
                'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tulare',
                'Tuolumne', 'Ventura', 'Yolo', 'Yuba']

# print counties with null values
print(missing_counties_asthma['county'].unique())

# print the entire rows with null values
print(missing_counties_asthma)


####deal with null data



# merge cleaned data sets
merged_data = pd.merge(cleaned_aqi_df, cleaned_asthma_df, on=['county', 'year'], how='inner')
#print(f"Final dataset: {len(merged_data)} rows, {len(merged_data.columns)} columns")
#print(f"Counties covered: {merged_data['county'].nunique()}")
#print(f"Years covered: {merged_data['year'].min()}-{merged_data['year'].max()}")

merged_data.to_csv('processed_data/merged_data.csv')


