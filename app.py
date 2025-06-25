import pandas as pd
import altair as alt
import streamlit as st
import numpy as np

@st.cache_data
def load_data(path):
    # Loading data from csv file
    df = pd.read_csv(path)
    
    # Check to ensure predictions & residuals exist in dataframe
    if 'y_pred' not in df or 'residual' not in df :
        import statsmodels.formula.api as smf
        mod = smf.ols('asthma_rate ~ median_aqi + C(county) + C(year)', data=df).fit()
        df['y_pred'] = mod.fittedvalues
        df['residual'] = mod.resid

    return df

def create_worst_aqi_chart(df, selected_years):
    worst_aqi = df[df['year'].isin(selected_years)].groupby('county')['median_aqi'].mean().sort_values(ascending=False).head(10)

    # Convert to a dataframe
    worst_aqi = worst_aqi.reset_index()

    return (
        alt.Chart(worst_aqi)
            .mark_bar()
            .encode(
                x=alt.X('median_aqi:Q', title='Median AQI', axis=alt.Axis(tickCount=10)),
                y=alt.Y('county:N', sort='-x', title='County'),
                color=alt.Color('county:N', legend=None),
                tooltip=[
                    alt.Tooltip('county:N', title='County'),
                    alt.Tooltip('median_aqi:Q', title='Median Aqi')
                ]
            )
            .properties(title=f'Top 10 Counties With the Worst Median AQI', width=400, height=400)
    )

def create_actual_vs_predicted_chart(df, selected_years):
    low = df[['asthma_rate','y_pred']].min().min()
    high = df[['asthma_rate','y_pred']].max().max()
    diag = pd.DataFrame({ 'asthma_rate': [low, high], 'y_pred': [low, high] })

    points = (
        alt.Chart(df)
        .mark_point(filled=True, size=60, opacity=0.6)
        .encode(
            x=alt.X('asthma_rate:Q', title='Observed rate', axis=alt.Axis(tickCount=10)),
            y=alt.Y('y_pred:Q', title='Predicted rate'),
            color=alt.Color('year:O', scale=alt.Scale(scheme='category10')),
            tooltip=[
                alt.Tooltip('county:N', title='County'),
                alt.Tooltip('year:O', title='Year'),
                alt.Tooltip('asthma_rate:Q', title='Observed'),
                alt.Tooltip('y_pred:Q', title='Predicted')
            ]
        )
        .transform_filter(alt.FieldOneOfPredicate(field='year', oneOf=selected_years))  # filter based on selected years
    )

    line = (
        alt.Chart(diag)
        .mark_line(color='red', strokeDash=[5,5])
        .encode(x='asthma_rate:Q', y='y_pred:Q')
    )

    return (
        alt.layer(points, line)
            .properties(title='Actual vs. Predicted Asthma ED Rate', width=600, height=600)
            .configure_view(fill="white")
            .interactive()
    )

def main():
    st.set_page_config(page_title="AQI→Asthma Dashboard")
    st.title("California Air Quality & Asthma Emergency Department Visits Analysis")
    #st.title("AQI vs. Asthma ED Rate: OLS Diagnostics")

    df = load_data('processed_data/ols_results.csv')

    years   = sorted(df['year'].unique())
    counties = sorted(df['county'].unique())

    st.sidebar.header("Filter Data")



    # Year selection with an "All" option
    selected_years = st.sidebar.multiselect("Select year(s):", ['All'] + years, default=['All'])

    # County selection with an "All" option
    selected_counties = st.sidebar.multiselect("Select county(ies):", ['All'] + counties, default=['All'])

    # If "All" is selected, show all years
    if 'All' in selected_years:
        selected_years = years

    if 'All' in selected_counties:
        selected_counties = counties 

    # Apply filters to the dataframe
    filtered = df[df['year'].isin(selected_years) & df['county'].isin(selected_counties)]


    st.subheader("AQI vs. Asthma ED Rate: OLS Diagnostics")

    # Render the chart
    chart = create_actual_vs_predicted_chart(filtered, selected_years)

    st.altair_chart(chart, use_container_width=True)

    st.markdown(
        """
        **Instructions:**  
        - **Zoom/Pan:** scroll or drag edges  
        - **Tooltip:** hover over points for details
        """
    )


    top_aqi_chart = create_worst_aqi_chart(filtered, selected_years)
    st.altair_chart(top_aqi_chart, use_container_width=True)

    if len(selected_years) != 1:
        st.markdown("Median AQI is averaged across selected years")


if __name__ == "__main__":
    main()
