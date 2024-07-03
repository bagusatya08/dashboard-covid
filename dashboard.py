import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import folium
from streamlit_folium import folium_static
import json
from IPython.display import display
import geopandas as gpd

st.set_page_config(layout="wide")
data_ch = pd.read_csv("dataset_covid.csv")

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
        today = datetime.datetime.now()
        next_year = today.year + 1
        first_case = datetime.date(2020,1,22)
        last_case = datetime.date(2022,4,16)

        d = st.date_input(
            "Datespan Option",
            (first_case, last_case),
            first_case,
            last_case,
            format="YYYY.MM.DD",
        )

# maincol1, maincol2 = st.columns(2)

if province_option and isinstance(d, tuple) and len(d) == 2:
        filter_country = data_ch[data_ch["country"] == country_option]
        filter_province = filter_country[filter_country["province"] == province_option]

        start_date = pd.to_datetime(d[0])
        end_date = pd.to_datetime(d[1])

        filter_timeline = filter_province[(filter_province["Date"] >=start_date) & (filter_province["Date"] <=end_date)]

def style_function(feature):
            return {
                'fillColor': 'yellow' if feature['properties']['STATE_NAME'] == province_option else '#3186cc',
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.7
            }

def style_function_uk(feature):
            return {
                'fillColor': 'yellow' if feature['properties']['name'] == province_option else '#3186cc',
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.7
            }

uk_op = {
    'Anguilla': [18.2206,-63.0686],
    'Bermuda': [32.3078,-64.7505],
    'British Virgin Islands': [18.4207, -64.639],
    'Cayman Islands': [19.3133,-81.2546],
    'Channel Islands': [49.3723,-2.3644],
    'Falkland Islands (Malvinas)': [-51.7963, -59.5236],
    'Gibraltar': [36.1408, -5.3536],
    'Guernsey': [49.4657, -2.5853],
    'Isle of Man': [54.2361, -4.5481],
    'Jersey': [49.2144, -2.1313],
    'Montserrat': [16.7425, -62.1874],
    'Saint Helena, Ascension and Tristan da Cunha': [-15.9656, -5.7089],
    'Turks and Caicos Islands': [21.694, -71.7979]
}

nz_op = {
     'Cook Islands': [-21.234, -159.792]
}


# Create a list of tuples with index and name
index_name_list = [(index, name) for index, name in enumerate(uk_op.keys())]

# Create a DataFrame
uk_keys = pd.DataFrame(index_name_list, columns=['Index', 'name'])

def add_marker(map_obj, lat, lon, label):
    popup_text = f"Province/State: {label}"
    folium.Marker(
        location=[lat, lon],
        popup=popup_text,
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(map_obj)

fr_op = {
    'French Guiana': {'lat': 3.9339, 'lon': -53.1258},
    'French Polynesia': {'lat': -17.6797, 'lon': -149.4068},
    'Guadeloupe': {'lat': 16.265, 'lon': -61.551},
    'Martinique': {'lat': 14.6415, 'lon': -61.0242},
    'Mayotte': {'lat': -12.8275, 'lon': 45.1662},
    'New Caledonia': {'lat': -20.9043, 'lon': 165.618},
    'Reunion': {'lat': -21.1151, 'lon': 55.5364},
    'Saint Barthelemy': {'lat': 17.9, 'lon': -62.8333},
    'Saint Pierre and Miquelon': {'lat': 46.8852, 'lon': -56.3159},
    'St Martin': {'lat': 18.0708, 'lon': -63.0501},
    'Wallis and Futuna': {'lat': -13.7688, 'lon': -177.156},
}

fr_p = {
    'French Guiana': [3.9339,-53.1258],
    'French Polynesia': [-17.6797, -149.4068],
    'Guadeloupe': [16.265, -61.551],
    'Martinique': [14.6415, -61.0242],
    'Mayotte': [-12.8275, 45.1662],
    'New Caledonia': [-20.9043, 165.618],
    'Reunion': [-21.1151, 55.5364],
    'Saint Barthelemy': [17.9, -62.8333],
    'Saint Pierre and Miquelon': [46.8852, -56.3159],
    'St Martin': [18.0708,-63.0501],
    'Wallis and Futuna': [-13.7688, -177.156]
}

# Lokasi dan nama daerah yang akan ditandai
dn_op = {
    'Faroe Islands': {'lat': 62.0, 'lon': -6.8},
    'Greenland': {'lat': 71.7, 'lon': -42.6},
}

# Lokasi dan nama daerah yang akan ditandai
net_op = {
    'Aruba': {'lat': 12.5, 'lon': -69.97},
    'Bonaire, Sint Eustatius and Saba': {'lat': 17.6, 'lon': -63.06},
    'Curacao': {'lat': 12.2, 'lon': -68.93},
    'Sint Maarten': {'lat': 18.0, 'lon': -63.05},
}


with st.container():
    oncol1, oncol2 = st.columns((1,3))
    with oncol1:
        confirmed = filter_timeline.Confirmed.sum()
        recovered = int(filter_timeline.Recovered.sum())
        deaths    = filter_timeline.Deaths.sum()

        total_confirmed = data_ch.Confirmed.sum()
        total_recovered = data_ch.Recovered.sum()
        total_deaths    = data_ch.Deaths.sum()

        percen_confirmed = round(confirmed/total_confirmed*100,2)
        percen_recovered = round(recovered/total_recovered*100,2)
        percen_deaths    = round(deaths/total_deaths*100,2)
        st.markdown("####")
        st.markdown("######")
        st.metric(label="Total Confirmed", value=f"{confirmed:,}", delta=percen_confirmed)
        st.markdown("####")
        st.metric(label="Total Recovered", value=f"{recovered:,}", delta=percen_recovered)
        st.markdown("####")
        st.metric(label="Total Deaths",    value=f"{deaths:,}",    delta=percen_deaths)
        st.markdown("####")
    with oncol2:
        st.markdown("####")

        if (country_option == "Australia"):
            geojson_data = json.load(open('dashboard/states.geojson'))
            # Highlight selected country
            m = folium.Map(location=[-25.2744, 133.7751], zoom_start=4)  # Adjust the starting location and zoom level as needed

            folium.GeoJson(
                geojson_data,
                name="geojson",
                style_function=style_function,
                tooltip=folium.GeoJsonTooltip(fields=['STATE_NAME'], aliases=['Province/State:'])
            ).add_to(m)

            folium.LayerControl().add_to(m)
            folium_static(m, width=1070, height=500)

        elif(country_option == "United Kingdom"):
            geojson_data = json.load(open('dashboard/uk_regions.geojson'))
            m = folium.Map(location=uk_op[province_option], zoom_start=8)  # Adjust the starting location and zoom level as needed

            for feature in geojson_data['features']:
                region_name = feature['properties']['name']
            
            folium.LayerControl().add_to(m)

            for location, coord in uk_op.items():
                add_marker(m, uk_op[province_option][0],  uk_op[province_option][1], uk_keys.query(f"name=='{province_option}'").name.to_string())

            folium_static(m, width=1070, height=500)
        elif(country_option == "New Zealand"):
            geojson_data = json.load(open('nz.geojson'))
            m = folium.Map(location=nz_op[province_option], zoom_start=4)  # Adjust the starting location and zoom level as needed

            for feature in geojson_data['features']:
                region_name = feature['properties']['name']
            
            folium.LayerControl().add_to(m)

            for location, coord in nz_op.items():
                add_marker(m, nz_op[province_option][0],  nz_op[province_option][1], "Cook Island")

            folium_static(m, width=1070, height=500)
        elif(country_option == "France"):
            # Membaca file GeoJSON France
            with open('dashboard/france.geojson', 'r') as f:
                geojson_data = json.load(f)

            # Membuat objek peta
            m = folium.Map(location=fr_p[province_option], zoom_start=4)

            # Menambahkan layer GeoJSON ke peta tanpa gaya yang berbeda untuk setiap region
            for feature in geojson_data['features']:
                province_name = feature['properties']['name']
                folium.GeoJson(
                    feature,
                    name=province_name,
                    tooltip=province_name
                ).add_to(m)

            # Menambahkan marker atau label untuk setiap daerah yang akan ditandai
            for location, coord in fr_op.items():
                add_marker(m, coord['lat'], coord['lon'], location)

            # Menambahkan kontrol layer
            folium.LayerControl().add_to(m)

            # Menampilkan peta di notebook
            folium_static(m, width=1070, height=500)

        elif(country_option == "China"):
            # Load geospatial data for Chinese provinces
            china_map = gpd.read_file('dashboard/chn_admbnda_adm1_ocha_2020.shp')

            # Load COVID-19 data
            covid_data = pd.read_csv('dashboard/dataset/updated_dataset_covid.csv')

            # Function to determine fill color based on confirmed cases
            def get_fill_color(confirmed_cases):
                if confirmed_cases < 1000:
                    return 'green'
                elif confirmed_cases < 10000:
                    return 'orange'
                else:
                    return 'red'

            # Function to create interactive map
            def create_map():
                # Create the Folium map
                m = folium.Map(location=[35, 105], zoom_start=4, tiles='cartodb positron')

                # Add GeoJSON layer for China provinces with COVID-19 data
                folium.GeoJson(
                    china_map,
                    name='China Province COVID-19 Data',
                    style_function=lambda feature: {
                        'fillColor': get_fill_color(covid_data[covid_data['province'] == feature['properties']['ADM1_EN']]['Confirmed'].sum()),
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.6
                    },
                    tooltip=folium.features.GeoJsonTooltip(
                        fields=['ADM1_EN'],
                        aliases=['Province:'],
                        labels=True,
                        localize=True,
                        style=('background-color: white; color: #333333; font-family: sans-serif')
                    )
                ).add_to(m)
                
                folium_static(m, width=1070, height=500)
            create_map()

        elif(country_option == "Denmark"):
            # Membaca file GeoJSON Denmark
            with open('dashboard/denmark.geojson', 'r') as f:
                denmark_geojson = json.load(f)

            # Membuat objek peta
            m = folium.Map(location=[68.0, 0.0], zoom_start=4)  # Koordinat tengah untuk Denmark

            # Menambahkan layer GeoJSON ke peta tanpa gaya yang berbeda untuk setiap region
            for feature in denmark_geojson['features']:
                province_name = feature['properties']['name']
                folium.GeoJson(
                    feature,
                    name=province_name,
                    tooltip=province_name
                ).add_to(m)

            # Menambahkan marker atau label untuk setiap daerah yang akan ditandai
            for location, coord in dn_op.items():
                add_marker(m, coord['lat'], coord['lon'], location)

            # Menambahkan kontrol layer
            folium.LayerControl().add_to(m)

            # Menampilkan peta di notebook
            folium_static(m, width=1070, height=500)

        elif(country_option == "Netherlands"):
            # Membaca file GeoJSON Netherlands
            with open('dashboard/netherlands.geojson', 'r') as f:
                netherlands_geojson = json.load(f)

            # Membuat objek peta
            m = folium.Map(location=[12.5, -69.97], zoom_start=8)  # Koordinat tengah untuk Aruba

            # Menambahkan layer GeoJSON ke peta tanpa gaya yang berbeda untuk setiap region
            for feature in netherlands_geojson['features']:
                province_name = feature['properties']['name']
                folium.GeoJson(
                    feature,
                    name=province_name,
                    tooltip=province_name
                ).add_to(m)

            # Menambahkan marker atau label untuk setiap daerah yang akan ditandai
            for location, coord in net_op.items():
                add_marker(m, coord['lat'], coord['lon'], location)

            # Menambahkan kontrol layer
            folium.LayerControl().add_to(m)

            # Menampilkan peta di notebook
            folium_static(m, width=1070, height=500)

with st.container():
    # visualisasi linechart
    st.markdown("#####")
    fig = px.line(filter_timeline, x="Date", y=["Confirmed","Recovered","Deaths"], markers=True,
                    color_discrete_map={
                        "Confirmed": "#0072f0",
                        "Recovered": "#00b6cb",
                        "Deaths": "#f10096"
                    },
                    template="plotly_white", height=500)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

st.plotly_chart(fig)
