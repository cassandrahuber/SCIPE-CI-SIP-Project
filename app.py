import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
import streamlit as st

from sklearn.metrics import mean_squared_error
import statsmodels.formula.api as smf


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

def plot_prediction_accuracy(df, years):
    low = df[['asthma_rate','y_pred']].min().min()
    high = df[['asthma_rate','y_pred']].max().max()
    diag = pd.DataFrame({'asthma_rate': [low, high], 'y_pred': [low, high]})

    points = (
        alt.Chart(df)
        .mark_point(filled=True, size=60, opacity=0.6)
        .encode(
            x=alt.X('asthma_rate:Q', title='Actual ED Rate (per 10k)', axis=alt.Axis(tickCount=10)),
            y=alt.Y('y_pred:Q', title='Predicted ED Rate (per 10k)'),
            color=alt.Color('year:O', scale=alt.Scale(scheme='yellowgreenblue')),
            tooltip=[
                alt.Tooltip('county:N', title='County'),
                alt.Tooltip('year:O', title='Year'),
                alt.Tooltip('asthma_rate:Q', title='Actual'),
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
            .properties(title='Prediction Accuracy', width=600, height=600)
            .configure_view(fill="white")
            .interactive()
    )

def plot_prediction_errors(df):
    resid_hist = px.histogram(
        df,
        x='residual',
        title='Distribution of Prediction Errors',
        labels={'residual': 'Prediction Error (Actual - Predicted)', 'y': 'Number of Observations'},
        hover_data={'residual': False}, 
        color_discrete_sequence=['lightblue'],
        width=600,
        height=600,
    )
    resid_hist.add_vline(
        x=0,
        line_dash="dash",
        line_color="red",
        annotation_text="Perfect Prediction"
    )

    return resid_hist

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
            .properties(title=f'Highest {title}', width=600, height=400)
    )



def plot_time_series(df, group_by, color, title, show_covid):
    yearly_avg = df.groupby(group_by)['asthma_rate'].mean().reset_index()

    ts = px.line(yearly_avg, x='year', y='asthma_rate', color=color, title=title,
                    labels={'asthma_rate': 'Asthma ED Visits (per 10k)', 'year': 'Year'},
                    width=600,
                    height=600)
    
    if show_covid:
        ts.add_vrect(x0=2019.5, x1=2021.5, fillcolor="red", opacity=0.2, 
                    annotation_text="COVID-19 Period", annotation_position="top left")
        
    return ts




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




def main():
    st.set_page_config(page_title="AQI→Asthma Dashboard", layout="wide")    

    st.title("California Air Quality & Asthma Emergency Visits Dashboard") 
    st.markdown("*Analysis of county-level asthma emergency department (ED) visits and air quality data (2013-2022)*")

    st.header("Research")

    #st.markdown("""
    #**Research Question:**
    #How does annual air quality (as measured by the median AQI) affect asthma emergency department visit rates across California counties?
    #""")
    col1, col2 = st.columns(2, gap='medium')
    with col1:
        st.info("""
        **Research Question:**
        How does annual air quality (as measured by the median AQI) affect asthma ED visit rates across California counties?
        """)
    with col2:
        st.info("""
        **My Hypothesis:**
        Counties with poorer air quality would have higher rates of asthma ED visits
        """)
        
    with st.expander("What is AQI?"):
        col1, col2 = st.columns(2, gap='medium', border=False)
        with col1:
            st.markdown("""
            **Air Quality Index (AQI) is like a weather report for air pollution:**
            - **0-50**: Good - Air quality is satisfactory
            - **51-100**: Moderate - May affect very sensitive people
            - **101-150**: Unhealthy for sensitive groups
            - **151-200**: Unhealthy for everyone
            - **201+**: Very unhealthy to hazardous
            """)
        with col2:
            st.markdown("""
            **AQI measures pollution from:**
            - Ozone (smog)
            - Particle pollution (PM2.5 and PM10)
            - Carbon monoxide
            - Sulfur dioxide
            - Nitrogen dioxide
            
            *Higher numbers = worse air quality*
            """)

    # Load data & compute model
    df, model = load_data('processed_data/merged_data_2013-2022.csv')
    years = sorted(df['year'].unique())
    counties = sorted(df['county'].unique())

    st.subheader("Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Counties", len(counties))
    with col2:
        st.metric("Years of Data", f"{years[0]} - {years[-1]}")
    with col3:
        st.metric("Total Observations", len(df))


    st.markdown("---")

    # findings
    st.header("Key Findings")

    st.markdown("""
    **Hypothesis was only partially correct:**
    Expected air quality to be the main factor but the relationship is also influenced by other factors like time (year) and location (county)
    """)

    col1, col2 = st.columns(2, border=False)

    with col1:
        st.warning("""
    **Air Quality Still Matters (But Less Intense Than Expected)**
    - After accounting for location differences, air quality does affect asthma rates
    - For every 10-point increase in AQI, we see about 2 additional ED visits per 10,000 people
    - It's a real measurable effect, just along with other factors (time, location)
    """)

    with col2:
        st.warning("""
        **COVID-19 Impact**
        - Asthma ED visits dropped dramatically in 2020-2021 
        - People avoided hospitals during the pandemic
        - This affected all counties equally
        """)

    st.warning("""
        **Location Impact**
        - Your county is the additionally an influence on asthma ER visits
        - Some counties have 3 times more visits than others
        - This suggests factors beyond air quality matter (healthcare access, socioeconomic status, etc.)
    """)

    # Sidebar filters
    st.sidebar.header("Filters")

    # Year selection
    selected_year_mode = st.sidebar.radio("Select year mode:", ["Single Year", "Year Range"], index=1)

    if selected_year_mode == "Single Year":
        selected_year = st.sidebar.slider("Select year:", min_value=min(years), max_value=max(years), value=min(years))
        selected_years = [selected_year]  # Convert single year to a list for filtering
    else:
        year_range = st.sidebar.slider("Select year range:", min_value=min(years), max_value=max(years), value=(min(years), max(years)))
        selected_years = list(range(year_range[0], year_range[1] + 1))  # Create a list of years within the range

    # County selection
    selected_counties = st.sidebar.multiselect("Select counties (leave empty for all):", counties, default=[])
    
    # Apply filter to data
    filtered = df[df['year'].isin(selected_years)]
    if selected_counties:
        filtered =  filtered[filtered['county'].isin(selected_counties)]

    # Covid filter
    show_covid = st.sidebar.checkbox("Highlight COVID-19 Impact", value=True)

    # Tab layout for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        #"County Differences", 
        "Time Trends", 
        "Air Quality Impact", 
        "Regression Model",
        "Model Explained"
    ])

    with tab1:
        st.header("How Asthma ER Visits Changed Over Time")

        col1, col2 = st.columns(2, vertical_alignment='center')

        with col1:
            # Time series plot
            yearly_ts_chart = plot_time_series(df, 'year', None, 'Asthma ER Rate by Year (Average of All Counties)', show_covid)
            st.plotly_chart(yearly_ts_chart, use_container_width=True)

        with col2:
            st.text("\n")
            st.text("\n")
            st.markdown("""
            **What this tells us:**
            - ER visits were relatively stable from 2013-2019
            - Dramatic drop in 2020-2021 during COVID-19 pandemic
            - People avoided hospitals during pandemic, not necessarily fewer asthma cases
            - Demonstrates the importance of looking at year as a contributing factor to asthma ER rates
            """)
            st.markdown("\n")
            st.markdown("*Select specific counties in the filter to see additional comparisons by county!*")

        # County comparison over time
        if selected_counties:
            county_ts_chart = plot_time_series(filtered, ['year', 'county'], 'county', 'Asthma ER Rate by Year (Your Selected Counties)', show_covid)
            st.plotly_chart(county_ts_chart, use_container_width=True)

        st.subheader("Top 10 Counties by Metric Across Selected Years")
        col1, col2 = st.columns(2)
        col1.altair_chart(plot_top_ten_counties_by_metric(df, selected_years, 'median_aqi', 'Median AQI'), use_container_width=True)
        col2.altair_chart(plot_top_ten_counties_by_metric(df, selected_years, 'asthma_rate', 'Asthma ER Rate'), use_container_width=True)


    with tab2:
        st.header("Air Quality vs Asthma")
        st.subheader("Initial Analysis")
        st.markdown("""
        - The simple scatter plot and linear fit between median AQI and asthma rates shows almost no meaningful link across all counties and years 
        (only about 1.2% of the total variation explained)
        - Realized the relationship between AQI and asthma rates is possibly more complex (hidden by other factors ie: year and county)
        """)
        # Scatter plot with OLS trendline
        simple_scatter = px.scatter(filtered, x='median_aqi', y='asthma_rate', 
                                    title=f'Asthma ER Rates vs Median AQI',
                                    labels={'county': 'County',
                                            'median_aqi': 'Median AQI',
                                            'asthma_rate': 'Asthma ER Visits (per 10k)'},
                                    trendline="ols",
                                    trendline_color_override='purple',)
        st.plotly_chart(simple_scatter, use_container_width=True)

        # Simple OLS regression model
        simple_model = smf.ols("asthma_rate ~ median_aqi", data=filtered).fit()

        # R-squared from OLS model
        r_squared = simple_model.rsquared

        col1, col2 = st.columns(2)
        with col1:
            st.metric("R-squared", f"{r_squared:.3f}", 
                      help="")
        with col2:
            if r_squared < 0.05:
                strength = "Very Weak"
            elif r_squared < 0.2:
                strength = "Weak"
            elif r_squared < 0.5:
                strength = "Moderate" 
            else:
                strength = "Strong"
            st.metric("Relationship Strength", strength)

        st.header("Solution: Multiple Regression Model")
        st.markdown("""
        - The model accounts for differences between counties and years so it measures the AQI effect directly
        - It shows a **positive, statistically significant link:**
        """)

        st.success("""
        Each 1-point rise in AQI predicts about 0.2 more asthma ER visits (per 10,000), demonstrating air quality really does matter!
        """)
        st.markdown("*More on the model's findings are continued in the **next tabs**!*")

    with tab3:
        st.subheader("How the Model Works")
        st.markdown("""
        - The model examines past asthma rates in each county to establish a “usual” rate for that location and measures how much rates rise when AQI changes—so it captures both the location effect and the air quality effect.
        - It then adjusts those baseline and AQI effect numbers so its predictions line up as closely as possible with the actual data, highlighting each factor's impact
        - A good fit (low prediction error) means its estimates like “each AQI point adds about 0.2 visits” are more likely to reflect real world patterns
        """)
        st.subheader("How Accurate is the Model?")

        # Model Prediction Accuracy
        st.altair_chart(plot_prediction_accuracy(filtered, selected_years), use_container_width=True)
        st.markdown("This plot compares observed vs. predicted rates, points near the red line show strong prediction accuracy.")
        st.success("""
        The model predicts to within ±5.8 visits per 10,000
        """)

        # Prediction Errors
        st.plotly_chart(plot_prediction_errors(filtered), use_container_width=True)
        st.markdown("*Prediction errors* (residuals) are the differences between the actual ER rate and the model's prediction.")
        st.success("""
        No bias: Most errors cluster near zero, indicating the model isn't systematically over or under predicting.
        """)

    with tab4:
        st.header("Understanding the Statistical Model")
        st.markdown("""
        **What is a regression model?** Think of it like a recipe that helps us understand what ingredients contribute to asthma rates.
        """)

        st.markdown("""
        - The model examines past asthma rates in each county to establish a “usual” rate for that location and measures how much rates rise when AQI changes—so it captures both the location effect and the air quality effect.
        - It then adjusts those baseline and AQI effect numbers so its predictions line up as closely as possible with the actual data, highlighting each factor's impact
        """)

        # Model results in plain English
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Model Statistics:**
            - **R²**: 0.876
            - **Slope (AQI)**: 0.202
            - **RMSE**: 5.76
            - **Statistical Significance**: Very strong (p < 0.001)
            """)
            
        with col2:
            st.success("""
            **What This Means:**
            - The model can explain 87.56% of why asthma rates vary
            - Finds each 10-point AQI increase raises asthma visits by +2 per 10,000
            - Predicts to within ±5.8 visits per 10,000
            - The results are statistically reliable
            - We can be confident the findings aren't due to chance
            """)

        # Comparison with simple analysis
        st.warning("""
        **Why The First Analysis Was Wrong:**
        
        **Simple Analysis**: "Air quality and asthma barely correlate" (R² ≈ 0.012)
        
        **Advanced Analysis**: "After accounting for location, air quality does matter" (R² = 0.876)
        
        Sometimes you need to control for confounding factors to see the real relationships!
        """)


    st.markdown("---")

    # Data Table & Download
    st.header("Data Table")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    #filtered_csv = filtered.to_csv(index=False).encode('utf-8')

    st.download_button("Download data as CSV", csv, "aqi_asthma.csv", "text/csv")
    #st.download_button("Download filtered data as CSV", filtered_csv, "filtered_aqi_asthma.csv", "text/csv")

    st.markdown("Data from US EPA and Tracking California")

if __name__ == "__main__":
    main()
