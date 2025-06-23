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

    return cleaned_aqi_df





# clean asthma emergency department visits data
def clean_asthma_ed_visits_data(start_year, num_years, input_folder) :
    asthma_df = []
    for i in range(num_years) :
        # load the data into a dataframe
        df = pd.read_excel(f'{input_folder}/Asthma_Emergency_{start_year + i}.xlsx')

        # clean up the dataframe
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df.rename(columns={'counties': 'county', 'age-adjusted_rate_per_10,000': 'asthma_rate'}, inplace=True)
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

    return cleaned_asthma_df





# note: not necessary to run this function, but useful for checking data (merging automatically ignores missing data pairs)
# check if all counties data for all years
def check_missing_data(cleaned_aqi_df, cleaned_asthma_df, all_counties) :
    # check aqi data counties appear consistently (all numbers should be equal)
    year_counts = cleaned_aqi_df.groupby('county')['year'].nunique()
    if year_counts.nunique() == 1 :
        print("All counties have aqi data for the same number of years.")
    else :
        print("Counties have inconsistent aqi data across years.")
        print(year_counts.sort_values())
        # optional, find the specific years
    
    # find counties missing all years in aqi data
    aqi_counties = cleaned_aqi_df['county'].unique()
    missing_counties_aqi = set(all_counties) - set(aqi_counties)
    print("Counties missing across all years in AQI data:", missing_counties_aqi)

    # find rows with null values in ashtma data
    missing_counties_asthma = cleaned_asthma_df[cleaned_asthma_df.isnull().any(axis=1)]
    print("Counties that have missing asthma data:", missing_counties_asthma['county'].unique())

    # print the subdataframe of specific years that counties have null values
    print("Subdataframe with specific years:")
    print(missing_counties_asthma)






# merge cleaned data sets
def merge_cleaned_data(cleaned_aqi_df, cleaned_asthma_df) :
    # merge cleaned data sets
    merged_data = pd.merge(cleaned_aqi_df, cleaned_asthma_df, on=['county', 'year'], how='inner')
    merged_data_timeframe = str(merged_data['year'].min()) + "-" + str(merged_data['year'].max())

    #print(f"Final dataset: {len(merged_data)} rows, {len(merged_data.columns)} columns")
    #print(f"Counties covered: {merged_data['county'].nunique()}")
    #print(f"Years covered: ", merged_data_timeframe)

    return merged_data, merged_data_timeframe




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


if __name__ == "__main__":
    clean_aqi = clean_aqi_quality_data(2017, 5, 'raw_data')
    clean_asthma = clean_asthma_ed_visits_data(2017, 5, 'raw_data')
    #clean_aqi.to_csv('processed_data/cleaned_aqi.csv')
    #clean_asthma.to_csv('processed_data/cleaned_asthma.csv')

    #find_missing_data(clean_aqi, clean_asthma, all_counties)

    merged_data, merged_data_timeframe = merge_cleaned_data(clean_aqi, clean_asthma)
    merged_data.to_csv('processed_data/merged_data_' + merged_data_timeframe + '.csv')


### may make test_data.py and convert to clean_data.py in src, where may use glob
### may figure out how to use glob to load all files
### may clean up code formatting