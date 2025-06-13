import pandas as pd

# clean air quality data
aqi_df = []
aqi_files_start_year = 2017

for i in range(5) :
    # load the data into a DataFrame
    df = pd.read_csv('raw_data/annual_aqi_by_county_' + str(i + aqi_files_start_year) + '.csv')
    
    df = df[df['State'] == 'California'].drop(columns=['State'])
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    #print(df.info())

    ##add missing county check
    ##figure out which counties missing?

    aqi_df.append(df)

# combine all aqi years dataframes into one
combined_aqi_df = pd.concat(aqi_df, ignore_index=True)
combined_aqi_df.to_csv('processed_data/combined_aqi_data.csv')
#print(combined_aqi_df)

# how many distinct years each county appears  (check if all listed counties have data for all years):
year_counts = combined_aqi_df.groupby('county')['year'].nunique()
print(year_counts.sort_values())



# clean asthma emergency department visits data
