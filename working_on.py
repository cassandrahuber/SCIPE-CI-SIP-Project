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
    # load the data into a DataFrame
    df = pd.read_csv('raw_data/annual_aqi_by_county_' + str(i + aqi_files_start_year) + '.csv')
    
    df = df[df['State'] == 'California'].drop(columns=['State'])
    df.set_index('County', inplace=True)
    #print(df.info())
    #df.set_index('County', inplace=True)

    ##add missing county check
    ##figure out which counties missing?

    aqi_df.append(df)

# combine all aqi years dataframes into one
combined_aqi_df = pd.concat(aqi_df, ignore_index=True)

combined_aqi_df.to_csv('processed_data/combined_aqi_data.csv')

# clean asthma emergency department visits data

asthma_df = []
df = pd.read_excel('raw_data/Asthma_Emergency_2017.xlsx')
print(df.info())

##figure out what do to abt 'NA' in sheet
##remove lower and upper limit collumns
##change "Counties" column to "County"
##add years column + year data
##remove california row, add to list for extra data?
##combine together all excel sheets to one