import pandas as pd
import altair as alt
import streamlit as st

@st.cache_data
def load_data(path):
    # Loading data from csv file
    df = pd.read_csv(path)
    
    # Check to ensure predictions & residuals exist in dataframe
    if 'y_pred' not in df or 'residual' not in df:
        import statsmodels.formula.api as smf
        mod = smf.ols('asthma_rate ~ median_aqi + C(county) + C(year)', data=df).fit()
        df['y_pred']   = mod.fittedvalues
        df['residual'] = mod.resid

    return df


def create_actual_vs_predicted_chart(df) :
    low = df[['asthma_rate','y_pred']].min().min()
    high = df[['asthma_rate','y_pred']].max().max()
    diag = pd.DataFrame({ 'asthma_rate': [low, high], 'y_pred': [low, high] })

    points = (
        alt.Chart(df)
        .mark_point(filled=True, size=60, opacity=0.6)
        .encode(
            x=alt.X('asthma_rate:Q', title='Observed rate'),
            y=alt.Y('y_pred:Q', title='Predicted rate'),
            color='year:O',
            tooltip=[
                alt.Tooltip('county:N', title='County'),
                alt.Tooltip('year:O', title='Year'),
                alt.Tooltip('asthma_rate:Q', title='Observed'),
                alt.Tooltip('y_pred:Q', title='Predicted'),
            ]
        )
    )

    line = (
        alt.Chart(diag)
        .mark_line(color='red', strokeDash=[5,5])
        .encode(x='asthma_rate:Q', y='y_pred:Q')
    )

    return (
        alt.layer(points, line)
           .properties(
               width=500,
               height=500
           )
           .interactive()
    )

def main():
    st.set_page_config(page_title="AQI→Asthma Dashboard")
    st.title("AQI vs. Asthma ED Rate: OLS Diagnostics")

    df = load_data('processed_data/ols_results.csv')

    years   = sorted(df['year'].unique())
    counties = sorted(df['county'].unique())

    st.sidebar.header("Filter Data")



    chart = create_actual_vs_predicted_chart(df)
    st.altair_chart(chart, use_container_width=True)

    st.markdown(
        """
        **Instructions:**  
        - **Zoom/Pan:** scroll or drag edges  
        - **Tooltip:** hover for county, year  
        """
    )


if __name__ == "__main__":
    main()
