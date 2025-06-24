import pandas as pd

# load clean merged data
df = pd.read_csv("../processed_data/merged_data_2017-2021.csv")
df = df.drop(columns=["Unnamed: 0"]) # remove index column


# basic exploration
print(f"Dataset shape: {df.shape}")
print(f"Counties: {df['county'].nunique()}")
print(f"Years: {df['year'].unique()}")
#print(f"\nMissing values: {df.isnull().sum()}")
#print(df.describe())


# which counties have the highest median aqi?
worst_aqi = df.groupby('county')['median_aqi'].mean().sort_values(ascending=False).head(10)
print("Counties with highest median AQI:")
print(worst_aqi)

# which counties have highest asthma rates?
highest_asthma = df.groupby('county')['asthma_rate'].mean().sort_values(ascending=False).head(10)
print("Counties with highest astham rates:")
print(highest_asthma)

##may add the worst aqi counties's asthma rates to the table
##may add the highest asthma counties's aqi to the table

from scipy import stats

# correlation analysis (pearson's correlation)
# note: this is a simple correlation, not accounting for county or year
correlation = df['median_aqi'].corr(df['asthma_rate'])
print(f"Correlation between AQI and Asthma rates: {correlation:.3f}")

# linear regression 
# note: this is a simple linear regression, not accounting for county or year
slope, intercept, r_value, p_value, std_err = stats.linregress(df['median_aqi'], df['asthma_rate'])
print(f"R-squared: {r_value**2:.3f}, P-value: {p_value:.3f}")


########







import statsmodels.formula.api as smf

# simple OLS regression model
# note: this fit does not account for the whole strength of the relationship

# "only aqi vs asthma rate"
#model = smf.ols("asthma_rate ~ median_aqi", data=df).fit()
#print(model.summary())


# multiple OLS regression model
# note: more complex model but gave much more stronger relationship between aqi and asthma rate

# "aqi vs asthma rate by county and year"
mod = smf.ols('asthma_rate ~ median_aqi + C(county) + C(year)', data=df).fit()
print(mod.summary())