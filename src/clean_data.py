import pandas as pd
import glob

# clean air quality data:
def clean_aqi_quality_data(start_year, num_years, input_folder) :
    aqi_df = []
    for i in range(num_years) :
        # load the data into a dataframe
        df = pd.read_csv(f'{input_folder}/annual_aqi_by_county_{start_year + i}.csv')

        # filter only California data and clean up the dataframe
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
        )
        df = df[df['state'] == 'California'].drop(columns=['state'])

        aqi_df.append(df)

    # combine all aqi years dataframes into one
    cleaned_aqi_df = pd.concat(aqi_df, ignore_index=True)
    #print(cleaned_aqi_df)

    return cleaned_aqi_df


files = glob.glob('raw_data/annual_aqi_by_county_*.csv')