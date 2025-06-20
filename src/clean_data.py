import pandas as pd
import glob

# clean air quality data:
def clean_aqi_quality_data(aqi_df) :
    # filter only California data and clean up the dataframe
    aqi_df.columns = aqi_df.columns.str.strip().str.lower().str.replace(' ', '_')

    # remove 'state' column and filter for California
    aqi_df = aqi_df[aqi_df['state'] == 'California'].drop(columns=['state'])

    #print(aqi_df)

    return aqi_df



# clean asthma emergency department visits data
def clean_asthma_ed_visits_data(asthma_df, year) :
    # clean up the dataframe
    asthma_df.columns = asthma_df.columns.str.strip().str.lower().str.replace(' ', '_')
    asthma_df.rename(columns={'counties': 'county', 'age-adjusted_rate_per_10_000': 'asthma_rate'}, inplace=True)

    # filter dataframe
    asthma_df = asthma_df[asthma_df['county'] != 'California']  # remove rows with 'California' in county name
    asthma_df = asthma_df.drop(columns=['lower_95%_limit', 'upper_95%_limit'])  # optional, but cleaner

    # add year column and reorder columns to have year after county (like in aqi_df)
    asthma_df['year'] = year
    columns_order = ['county', 'year'] + [col for col in asthma_df.columns if col not in ['county', 'year']]

    #print(asthma_df)

    return asthma_df



# note: not necessary to run this function, but useful for checking data (merging automatically ignores missing data pairs)
# check if all counties data for all years
#def check_missing_data() :



# merge cleaned data sets
def merge_cleaned_data(cleaned_aqi_df, cleaned_asthma_df) :
    # merge cleaned data sets
    merged_data = pd.merge(cleaned_aqi_df, cleaned_asthma_df, on=['county', 'year'], how='inner')
    merged_data_timeframe = str(merged_data['year'].min()) + "-" + str(merged_data['year'].max())

    #print(f"Final dataset: {len(merged_data)} rows, {len(merged_data.columns)} columns")
    #print(f"Counties covered: {merged_data['county'].nunique()}")
    #print(f"Years covered: ", merged_data_timeframe)

    return merged_data, merged_data_timeframe

if __name__ == "__main__":
    # aqi
    files = glob.glob('raw_data/annual_aqi_by_county_*.csv')

    aqi_dfs = []
    for f in files:
        aqi_dfs = pd.read_csv(f)
        aqi_dfs.append(clean_aqi_quality_data(aqi_dfs))

    clean_aqi = pd.concat(aqi_dfs, ignore_index=True)

    # asthma
    asthma_dfs = []

    for year in range(2017, 2022) :
        path = f'raw_data/Asthma_Emergency_{year}.xlsx'
        df = pd.read_excel(path)
        asthma_dfs.append(clean_asthma_ed_visits_data(df, year))

    clean_asthma = pd.concat(asthma_dfs, ignore_index=True)

    #clean_aqi.to_csv('processed_data/cleaned_aqi.csv')
    #clean_asthma.to_csv('processed_data/cleaned_asthma.csv')

    merged_data, merged_data_timeframe = merge_cleaned_data(clean_aqi, clean_asthma)
    #merged_data.to_csv(f'processed_data/merged_data_{merged_data_timeframe}.csv')


    ##check code esp merged to csv
    ##implement check func 
    ##create notebook to go with