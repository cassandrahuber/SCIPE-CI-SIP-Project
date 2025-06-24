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


import matplotlib.pyplot as plt

# simple visualizations of the relationship between aqi and asthma rates:

#  median aqi vs asthma rate - scatter plot
# note: not accounting for county or year
plt.figure(figsize=(10, 6))
plt.scatter(df['median_aqi'], df['asthma_rate'], alpha=0.6)
plt.xlabel('Median AQI')
plt.ylabel('Asthma ED Rate per 100k')
plt.title('Air Quality vs Asthma Emergency Department Visits')
plt.show()

# time trends analysis - line plot
# note: not acounting for county just overall trends
yearly_trends = df.groupby('year')[['median_aqi', 'asthma_rate']].mean()
yearly_trends.plot(kind='line', figsize=(12, 6))
plt.title('California Air Quality and Asthma Trends Over Time')
plt.show()

# looking at more factors in the relationship (aqi & asthma):

# top counties with worst aqi and highest asthma rates - bar plots
# note: over course of 2013-2022
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
worst_aqi.head(10).plot(kind='barh', ax=ax1, title='Worst Air Quality Counties')
highest_asthma.head(10).plot(kind='barh', ax=ax2, title='Highest Asthma Rate Counties')
plt.tight_layout()
plt.show()

# median aqi vs asthma rate colored by year - scatter plot
plt.scatter(df['median_aqi'], df['asthma_rate'], c=df['year'])
plt.xlabel('Median AQI')
plt.ylabel('Asthma ED rate')
plt.title('AQI vs. Asthma (2013-2023)')
plt.colorbar(label='Year')
plt.show()





# using models to explore further on the complex relationship:

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

# extracting the observed, predicted, and residuals
y = df['asthma_rate']
y_pred  = mod.fittedvalues
residuals = mod.resid



###
import matplotlib.pyplot as plt

# visualizations of the regression results:

# actual vs predicted scatter plot
plt.figure(figsize=(6,6))
plt.scatter(y, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel('Observed asthma_rate')
plt.ylabel('Predicted asthma_rate')
plt.title('Actual vs. Predicted (Multiple OLS)')
plt.show()

# residuals distribution histogram
plt.figure(figsize=(6,4))
plt.hist(residuals, bins=30, edgecolor='k')
plt.xlabel('Residual (Observed - Predicted)')
plt.title('Residual Distribution')
plt.show()

# top county fixed effects
coefs = mod.params.filter(like='C(county)')
top_pos = coefs.sort_values(ascending=False).head(10) # plot top 10 positive
top_neg = coefs.sort_values().head(10) # plot top 10 negative
plot_coefs = pd.concat([top_pos, top_neg])

plt.figure(figsize=(8,6))
plot_coefs.plot(kind='barh')
plt.xlabel('Coefficient Value')
plt.title('Top 10 Negative & Positive County Fixed Effects')
plt.show()