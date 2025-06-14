import pandas as pd

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
    # Load the data into a DataFrame
    df = pd.read_csv('raw_data/annual_aqi_by_county_' + str(i + aqi_files_start_year) + '.csv')
    df = df[df['State'] == 'California'].drop(columns=['State'])
    df.set_index('County', inplace=True)
    aqi_df.append(df)

# combine all aqi years dataframes into one
combined_aqi_df = pd.concat(aqi_df, ignore_index=False)

#, axis=1

combined_aqi_df.to_csv('processed_data/combined_aqi_data.csv')