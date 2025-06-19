import pandas as pd

aqi_data = ['annual_aqi_by_county_2017.csv',
            'annual_aqi_by_county_2018.csv',
            'annual_aqi_by_county_2019',
            'annual_aqi_by_county_2020',
            'annual_aqi_by_county_2021']

aqi_df = []

aqi_files_start_year = 2017

for df, i in range(5) :
    # Load the data into a DataFrame
    aqi_df[df] = pd.read_csv('raw_data/annual_aqi_by_county_' + str(i + aqi_files_start_year) + '.csv',
                     index_col=0,
                     parse_dates=True,
                     encoding='utf-8',
                     low_memory=False)
    
    ##print(f"File {i + aqi_files_start_year} loaded successfully.")

print(aqi_df)

## https://chatgpt.com/c/685087ee-c978-8011-ae04-43bcdfc3dbc9

