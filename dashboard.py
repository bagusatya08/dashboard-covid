import streamlit as st
import plotly.express as px
import pandas as pd
import datetime

st.set_page_config(layout="wide")
data_ch = pd.read_csv("dataset/dataset.csv")

# Konversi kolom "Date" menjadi datetime
data_ch['Date'] = pd.to_datetime(data_ch['Date'])

# Membuat dictionary dari dataset
country_province_dict = data_ch.groupby('country')['province'].unique().apply(list).to_dict()

st.header("The Trend of COVID-19 Cases from 2020 to 2022", divider="grey")

# semua widget disini
with st.expander("Click to Change the Filter Settings"):
    col1, col2, col3 = st.columns(3)
    with col1:
        country_option = st.selectbox(
            "Countries Option",
        list(country_province_dict.keys()),
        index=0,
        placeholder="Please select one of the country ...",
        )
    with col2:
        if country_option:
            province_list = country_province_dict.get(country_option, [])
            province_option = st.selectbox(
                "Province Option",
                province_list,
                index=0,
                placeholder="Please select one of the province ...",
            )
        else:
            province_option = None
    with col3:
        today       = datetime.datetime.now()
        next_year   = today.year + 1
        first_case  = datetime.date(2020,1,22)
        last_case   = datetime.date(2022,4,16)
        
        d = st.date_input(
            "Datespan Option",
            (first_case, last_case),
            first_case,
            last_case,
            format="DD.MM.YYYY",
        )

if province_option and isinstance(d, tuple) and len(d) == 2:
        filter_country  = data_ch[data_ch["country"] == country_option]
        filter_province = filter_country[filter_country["province"] == province_option]
        filter_timeline = filter_province[(filter_province["Date"] >= pd.to_datetime(d[0])) & (filter_province["Date"] <= pd.to_datetime(d[1]))]
else:
    st.write("Please select the correct datespan")

with st.container():
    st.markdown("#####")

maincol1, maincol2 = st.columns([1,3])
with maincol1:
    confirmed = filter_timeline.Confirmed.sum()
    recovered = int(filter_timeline.Recovered.sum())
    deaths    = filter_timeline.Deaths.sum()

    total_confirmed = data_ch.Confirmed.sum()
    total_recovered = data_ch.Recovered.sum()
    total_deaths    = data_ch.Deaths.sum()

    percen_confirmed = round(confirmed/total_confirmed*100,2)
    percen_recovered = round(recovered/total_recovered*100,2)
    percen_deaths    = round(deaths/total_deaths*100,2)
    st.metric(label="Total Confirmed", value=f"{confirmed:,}", delta=percen_confirmed)
    st.markdown("####")
    st.metric(label="Total Recovered", value=f"{recovered:,}", delta=percen_recovered)
    st.markdown("####")
    st.metric(label="Total Deaths",    value=f"{deaths:,}",    delta=percen_deaths)
    st.markdown("####")

with maincol2:
    # visualisasi geomap
    country_stats = data_ch.groupby('country').agg({
        'Confirmed': 'sum',
        'Recovered': 'sum',
        'Deaths': 'sum'
    }).reset_index()

    # Membuat peta interaktif menggunakan Plotly Express
    fig = px.choropleth(country_stats,
                        locations='country',
                        locationmode='country names',
                        color='Confirmed',
                        hover_name='country',
                        hover_data=['Confirmed', 'Recovered', 'Deaths'],
                        color_continuous_scale='Viridis',
                        labels={'Confirmed': 'Total Confirmed Cases'}
                    )

    # Mengaktifkan fitur interaktif dengan menambahkan fungsi callback
    fig.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, showocean=True, oceancolor="LightBlue", showcountries=True)
    fig.update_layout(height=300, margin={"r":0,"t":40,"l":0,"b":0})

    # Menambahkan callback untuk menampilkan data ketika negara diklik
    fig.update_layout(clickmode='event+select')

    def update_stats(trace, points, selector):
        if points.point_inds:
            selected_country = country_stats.iloc[points.point_inds[0]]['country']
            confirmed = country_stats.loc[country_stats['country'] == selected_country, 'Confirmed'].values[0]
            recovered = country_stats.loc[country_stats['country'] == selected_country, 'Recovered'].values[0]
            deaths = country_stats.loc[country_stats['country'] == selected_country, 'Deaths'].values[0]
            fig.update_layout(
                annotations=[
                    dict(
                        text=f"Country: {selected_country}<br>" +
                            f"Confirmed: {confirmed}<br>" +
                            f"Recovered: {recovered}<br>" +
                            f"Deaths: {deaths}",
                        x=0.02,
                        y=0.95,
                        showarrow=False,
                        bgcolor="white",
                        font=dict(size=12),
                        bordercolor="black",
                        borderwidth=1
                    )
                ]
            )

    fig.data[0].on_click(update_stats)
    st.plotly_chart(fig)

    # visualisasi linechart
    fig = px.line(filter_timeline, x="Date", y=["Confirmed","Recovered","Deaths"], markers=True,
                    color_discrete_map={
                        "Confirmed": "#0072f0",
                        "Recovered": "#00b6cb",
                        "Deaths"   : "#f10096"
                    },
                    template="plotly_white", height=300)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    st.plotly_chart(fig)