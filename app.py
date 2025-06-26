import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import statsmodels.formula.api as smf

from sklearn.metrics import mean_squared_error

@st.cache_data
def load_data(path):
    # Loading data from csv file
    df = pd.read_csv(path)
    df = df.drop(columns=["Unnamed: 0"]) # remove index column
    
    model = smf.ols('asthma_rate ~ median_aqi + C(county) + C(year)', data=df).fit()

    # add predicted values of y (asthma rate) & residuals to df
    df['y_pred'] = model.fittedvalues
    df['residual'] = df['asthma_rate'] - df['y_pred']

    return df, model

def plot_top_ten_counties_by_metric(df, years, metric, title):
    #feature_title = str(feature).title().replace('_', ' ')

    highest_of_metric = df[df['year'].isin(years)].groupby('county')[metric].mean().sort_values(ascending=False).head(10)

    # Convert to a dataframe
    highest_of_metric = highest_of_metric.reset_index()

    return (
        alt.Chart(highest_of_metric)
            .mark_bar()
            .encode(
                x=alt.X(f'{metric}:Q', title=title, axis=alt.Axis(tickCount=10)),
                y=alt.Y('county:N', sort='-x', title='County'),
                color=alt.Color('county:N', scale=alt.Scale(scheme='yellowgreenblue'), legend=None), ####pastel2, lightmulti, purplered, teals, purples
                tooltip=[
                    alt.Tooltip('county:N', title='County'),
                    alt.Tooltip(f'{metric}:Q', title=title)
                ]
            )
            .properties(title=f'Highest {title}', width=400, height=400)
    )

def plot_actual_vs_predicted_scatter(df, years):
    low = df[['asthma_rate','y_pred']].min().min()
    high = df[['asthma_rate','y_pred']].max().max()
    diag = pd.DataFrame({ 'asthma_rate': [low, high], 'y_pred': [low, high] })

    points = (
        alt.Chart(df)
        .mark_point(filled=True, size=60, opacity=0.6)
        .encode(
            x=alt.X('asthma_rate:Q', title='Observed rate', axis=alt.Axis(tickCount=10)),
            y=alt.Y('y_pred:Q', title='Predicted rate'),
            color=alt.Color('year:O', scale=alt.Scale(scheme='yellowgreenblue')),
            tooltip=[
                alt.Tooltip('county:N', title='County'),
                alt.Tooltip('year:O', title='Year'),
                alt.Tooltip('asthma_rate:Q', title='Observed'),
                alt.Tooltip('y_pred:Q', title='Predicted')
            ]
        )
        .transform_filter(alt.FieldOneOfPredicate(field='year', oneOf=years))  # filter based on selected years
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

def compute_model_metrics(df, model):
    mse  = mean_squared_error(df['asthma_rate'], df['y_pred'])
    rmse = np.sqrt(mse)    
    slope = model.params['median_aqi']
    pval  = model.pvalues['median_aqi']
    return {
        'r2':        model.rsquared,
        'adj_r2':    model.rsquared_adj,
        'rmse':      rmse,
        'slope':     slope,
        'slope_p':   pval,
        'n_obs':     int(model.nobs)
    }

def plot_residuals_histogram(df):
    return (
        alt.Chart(df)
           .mark_bar()
           .encode(
               x=alt.X('residual:Q', bin=alt.Bin(maxbins=30), title='Residual'),
               y=alt.Y('count()', title='Frequency'),
               tooltip=[alt.Tooltip('count()', title='Count')]
           )
           .properties(width=600, height=200, title='Residuals Distribution')
    )

def plot_time_series(df, counties):
    ts = (df[df['county'].isin(counties)]
          .groupby(['year','county'])[['median_aqi','asthma_rate']]
          .mean()
          .reset_index()
         )
    melt = ts.melt(
        id_vars=['year','county'],
        value_vars=['median_aqi','asthma_rate'],
        var_name='Metric',
        value_name='Value'
    )
    return (
        alt.Chart(melt)
           .mark_line(point=True)
           .encode(
               x=alt.X('year:O', title='Year'),
               y=alt.Y('Value:Q', title='Value'),
               color=alt.Color('county:N', title='County'),
               strokeDash=alt.StrokeDash('Metric:N', title='Metric',),
               tooltip=['county','year','Metric','Value']
           )
           .properties(width=700, height=400,
                       title='Time Series of AQI & Asthma ED Rate')
           .interactive()
    )


def main():
    st.set_page_config(page_title="AQI→Asthma Dashboard")
    st.title("California Air Quality & Asthma Emergency Department Visits Analysis")
    #st.title("AQI vs. Asthma ED Rate: OLS Diagnostics")

    df, model = load_data('processed_data/merged_data_2013-2022.csv')

    years   = sorted(df['year'].unique())
    counties = sorted(df['county'].unique())

    st.sidebar.header("Filter Data")
    
    # Option to select a single year
    selected_year_mode = st.sidebar.radio("Select year mode:", ["Single Year", "Year Range"], index=1)

    if selected_year_mode == "Single Year":
        selected_year = st.sidebar.slider("Select year:", min_value=min(years), max_value=max(years), value=min(years))
        selected_years = [selected_year]  # Convert single year to a list for filtering
    else:
        year_range = st.sidebar.slider("Select year range:", min_value=min(years), max_value=max(years), value=(min(years), max(years)))
        selected_years = list(range(year_range[0], year_range[1] + 1))  # Create a list of years within the range

    # County selection
    selected_counties = st.sidebar.multiselect("Select counties (leave empty for all):", counties, default=[])

    if len(selected_counties) == 0:
        selected_counties = counties 

    # Apply filters to the dataframe
    filtered = df[df['year'].isin(selected_years) & df['county'].isin(selected_counties)]


    # 1. Model KPIs
    # give users an at a glance sense of how well the model fits
    metrics = compute_model_metrics(df, model)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("R²",        f"{metrics['r2']:.3f}")
    col2.metric("Adj. R²",   f"{metrics['adj_r2']:.3f}")
    col3.metric("RMSE",      f"{metrics['rmse']:.3f}")
    col4.metric("Slope (AQI)", f"{metrics['slope']:.3f}")
    col5.metric("Slope p-value", f"{metrics['slope_p']:.3f}")

    st.markdown(f"**Observations:** {metrics['n_obs']} county-years")

    # 2. Actual vs Predicted
    st.subheader("Actual vs. Predicted Asthma ED Rate")
    #chart1 = plot_actual_vs_predicted_scatter(filtered, selected_years)
    st.altair_chart(plot_actual_vs_predicted_scatter(filtered, selected_years), use_container_width=True)

    # 3. Residuals diagnostics
    st.subheader("Residuals Diagnostics")
    st.altair_chart(plot_residuals_histogram(filtered), use_container_width=True)

    # 4. Top-10 bars (Asthma & AQI)
    st.subheader("Top 10 Counties by Metric")
    cols = st.columns(2)
    cols[0].altair_chart(
        plot_top_ten_counties_by_metric(filtered, selected_years, 'asthma_rate', 'Asthma ED Rate'),
        use_container_width=True
    )
    cols[1].altair_chart(
        plot_top_ten_counties_by_metric(filtered, selected_years, 'median_aqi',    'Median AQI'),
        use_container_width=True
    )

    # 5. Time Series
    st.subheader("Time Series by County & Metric")
    st.altair_chart(plot_time_series(filtered, selected_counties), use_container_width=True)


    import matplotlib.pyplot as plt

    # Compute yearly trends
    yearly_trends = df.groupby('year')[['median_aqi', 'asthma_rate']].mean().reset_index()

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(yearly_trends['year'], yearly_trends['median_aqi'], label='Median AQI', linestyle='-', color='blue')  # Solid line
    plt.plot(yearly_trends['year'], yearly_trends['asthma_rate'], label='Asthma Rate', linestyle='--', color='red')  # Dotted line

    # Add title, labels, and legend
    plt.title('California Air Quality and Asthma Trends Over Time')
    plt.xlabel('Year')
    plt.ylabel('Average Value')
    plt.legend()

    st.pyplot(plt)


    # 6. Data table & download
    st.subheader("Data Table")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download data as CSV", csv, "aqi_asthma.csv", "text/csv")

    filtered_csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download filtered data as CSV", filtered_csv, "filtered_aqi_asthma.csv", "text/csv")



if __name__ == "__main__":
    main()
