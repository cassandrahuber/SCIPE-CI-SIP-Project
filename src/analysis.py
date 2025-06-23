import pandas as pd
import statsmodels.formula.api as smf

# 1) Load your merged file
df = pd.read_csv("../processed_data/merged_data_2017-2021.csv")

# 2) Drop that auto‐generated index column
df = df.drop(columns=["Unnamed: 0"])

# "only aqi matters" ~ simple regression
# 3) Fit an OLS model: asthma_rate ~ median_aqi
model = smf.ols("asthma_rate ~ median_aqi", data=df).fit()
print(model.summary())

###########

import statsmodels.formula.api as smf

mod = smf.ols('asthma_rate ~ median_aqi + C(county) + C(year)', data=df).fit()
mod.summary()
#print(mod.summary())