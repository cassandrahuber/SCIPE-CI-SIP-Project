import pandas as pd

df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
        )