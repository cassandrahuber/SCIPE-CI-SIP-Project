import pandas as pd
import statsmodels.formula.api as smf

# load clean merged data
df = pd.read_csv("../processed_data/merged_data_2017-2021.csv")

# drop auto‐generated index column
df = df.drop(columns=["Unnamed: 0"])

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