import pandas as pd

df = pd.read_csv('raw_data/annual_aqi_by_county_2017.csv', 
                 index_col=0,
                 parse_dates=True,
                 encoding='utf-8',
                 low_memory=False)

# filtering only california data
df = df[df['State'] == 'California'].drop(columns=['State'])

df.set_index('County', inplace=True)