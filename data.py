import pandas as pd

for i, file in range(5) :
    pd.read_csv(f"data/annual_aqi_by_county_{i + 2017}.csv")
    print(f"File {i + 2017} loaded successfully.")