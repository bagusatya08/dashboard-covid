import streamlit as st

import plotly.express as px
import pandas as pd
import datetime

st.set_page_config(layout="wide")
data_ch = pd.read_csv("dataset/dataset_covid.csv")

# semua widget disini
with st.expander("Sesuaikan Filter dengan Kebutuhan"):
    col1, col2, col3 = st.columns(3)
    with col1:
        country_option = st.selectbox(
            "Negara Pilihan",
           ('Australia', 'China', 'Denmark', 'France', 'Netherlands','New Zealand', 'United Kingdom'),
           index=None,
           placeholder="Silahkan pilih salah satu negara..",
        )
    with col2:
        province_option = st.selectbox(
            "Provinsi Pilihan",
           ('Australia', 'China', 'Denmark', 'France', 'Netherlands','New Zealand', 'United Kingdom'),
           index=None,
           placeholder="Silahkan pilih salah satu negara..",
        )
    with col3:
        today       = datetime.datetime.now()
        next_year   = today.year + 1
        first_case  = datetime.date(2020,1,22)
        last_case   = datetime.date(2022,4,16)
        
        d = st.date_input(
            "Pilih rentang tanggal",
            (first_case, last_case),
            first_case,
            last_case,
            format="DD.MM.YYYY",
        )

# visualisasi linechart
filter_country  = data_ch[data_ch["country"]==country_option]
# filter_timeline = data_ch.loc[d]

fig = px.line(filter_country, x="Date", y=["Confirmed","Recovered","Deaths"],markers=True,
              color_discrete_map={
                 "Confirmed": "#0072f0",
                 "Recovered": "#00b6cb",
                 "Deaths"   : "#f10096"
             },
              title="Covid Patients over time", template="plotly_white",height=600)

fig.update_layout(yaxis_range=[0,40000])

st.plotly_chart(fig)

