import pandas as pd

# clean air quality data
aqi_df = []
aqi_files_start_year = 2017

for i in range(5) :
    # load the data into a DataFrame
    df = pd.read_csv('raw_data/annual_aqi_by_county_' + str(i + aqi_files_start_year) + '.csv')
    
    df = df[df['State'] == 'California'].drop(columns=['State'])
    df.set_index('County', inplace=True)
    ##print(df.info())
    ##df.set_index('County', inplace=True)
    ######## add missing county check
    aqi_df.append(df)

# combine all aqi years dataframes into one
combined_aqi_df = pd.concat(aqi_df, ignore_index=True)

combined_aqi_df.to_csv('processed_data/combined_aqi_data.csv')

# clean asthma emergency department visits data
asthma_df = pd.read_csv('raw_data/asthma_emergency_department_visits.csv',
                        index_col=0,