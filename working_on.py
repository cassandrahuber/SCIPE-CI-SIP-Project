import pandas as pd

# clean air quality data

df = pd.read_csv('raw_data/annual_aqi_by_county_2017.csv', 
                 index_col=0,
                 parse_dates=True,
                 encoding='utf-8',
                 low_memory=False)

# filtering only california data
df = df[df['State'] == 'California'].drop(columns=['State'])

df.set_index('County', inplace=True)

##

aqi_df = []
aqi_files_start_year = 2017

for i in range(5) :
    # load the data into a dataframe
    df = pd.read_csv('raw_data/annual_aqi_by_county_' + str(i + aqi_files_start_year) + '.csv')
    #print(df.info())

    # filter only California data and clean up the dataframe
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df = df[df['state'] == 'California'].drop(columns=['state'])
    #df.set_index('County', inplace=True)

    aqi_df.append(df)

# combine
combined_aqi_df = pd.concat(aqi_df, ignore_index=True)
combined_aqi_df.to_csv('processed_data/combined_aqi_data.csv')
#print(combined_aqi_df)






# clean asthma emergency department visits data


df = pd.read_excel('raw_data/Asthma_Emergency_2017.xlsx')
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
df = df.drop(columns=['lower_95%_limit', 'upper_95%_limit'])    # optional, but cleaner
df.rename(columns={'counties': 'county'}, inplace=True)
df['year'] = 2017
#print(df.info())



asthma_df = []
asthma_files_start_year = 2017

for i in range(5) :
    # load the data into a dataframe
    df = pd.read_excel('raw_data/Asthma_Emergency_' + str(i + asthma_files_start_year) + '.xlsx')
    #print(df.info())

    # clean
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df = df.drop(columns=['lower_95%_limit', 'upper_95%_limit'])  # optional, but cleaner
    df = df[df['county'] != 'California'] # remove rows with 'California' in county name
        ##possibly make a list of these rows for extra data?
    df.rename(columns={'counties': 'county'}, inplace=True)
 
    # add year column and reorder columns to have year after county (like in aqi_df)
    df['year'] = i + asthma_files_start_year
    columns_order = ['county', 'year'] + [col for col in df.columns if col not in ['county', 'year']]
    df = df[columns_order]

    asthma_df.append(df)

# combine
combined_asthma_df = pd.concat(asthma_df, ignore_index=True)
print(combined_asthma_df)
combined_asthma_df.to_csv('processed_data/combined_asthma_data.csv')

##figure out what do to abt 'NA' in sheet






# find counties missing

# count number of years county appears in aqi data
year_counts = combined_aqi_df.groupby('county')['year'].nunique()
#print(year_counts.sort_values())

# figure out which counties missing in aqi data
all_counties = combined_asthma_df['county'].unique()
aqi_counties = combined_aqi_df['county'].unique()
#print(len(all_counties), len(aqi_counties))
missing_counties_aqi = set(all_counties) - set(aqi_counties)
#print("Counties missing in AQI data:", missing_counties)


# check if all counties data for all years in asthma data


#for row in combined_asthma_df.itertuples():
    #print(row)

num_null_rows = combined_asthma_df['number_of_cases'].isnull().sum()
print(num_null_rows)

# find rows with null values
missing_counties_asthma = combined_asthma_df[combined_asthma_df.isnull().any(axis=1)]

print("Counties with null values:")
print(missing_counties_asthma['county'].unique())

print("Rows with null values:")
print(missing_counties_asthma)


print("HELLO")
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
#combined_aqi_df.to_csv('processed_data/combined_aqi_data.csv')







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

#combined_asthma_df.to_csv('processed_data/combined_asthma_data.csv')




# check if all counties data for all years

# how many distinct years each county appears in aqi (check if all listed counties have data for all years)
year_counts = combined_aqi_df.groupby('county')['year'].nunique()
print(year_counts.sort_values())

# figure out which counties missing in aqi data
all_counties = combined_asthma_df['county'].unique()
aqi_counties = combined_aqi_df['county'].unique()
#print(len(all_counties), len(aqi_counties))

missing_counties_aqi = set(all_counties) - set(aqi_counties)
#print("Counties missing in AQI data:", missing_counties)


# find rows with null values in ashtma data
missing_counties_asthma = combined_asthma_df[combined_asthma_df.isnull().any(axis=1)]

# print counties with null values
print(missing_counties_asthma['county'].unique())

# print the entire rows with null values
print(missing_counties_asthma)


####deal with null data

###add counties with null data to aqi data


all_counties = ['Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa',
                'Del Norte', 'El Dorado', 'Fresno', 'Glenn', 'Humboldt', 'Imperial', 'Inyo',
                'Kern', 'Kings', 'Lake', 'Lassen', 'Los Angeles', 'Madera', 'Marin', 'Mariposa',
                'Mendocino', 'Merced', 'Modoc', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Orange',
                'Placer', 'Plumas', 'Riverside', 'Sacramento', 'San Benito', 'San Bernardino',
                'San Diego', 'San Francisco', 'San Joaquin', 'San Luis Obispo', 'San Mateo',
                'Santa Barbara', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra', 'Siskiyou',
                'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity', 'Tulare',
                'Tuolumne', 'Ventura', 'Yolo', 'Yuba']



#import itertools

#years = sorted(combined_aqi_df['year'].unique())
#skeleton = pd.DataFrame(itertools.product(all_counties, years),
#                        columns=['county','year'])

#merged = skeleton.merge(combined_aqi_df, on=['county','year'], how='left')

# rows where median_aqi is missing:
#gaps = merged[merged['median_aqi'].isna()]

# count gaps per county
#gap_counts = gaps.groupby('county').size().sort_values(ascending=False)
#print(gap_counts)