from pandas.io.sql import DatabaseError
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LOADING DATA
DATE_TIME = "date/time"
data = pd.read_csv('Cantec-Location-Data-Nov.csv')

st.write(data)
st.write(data[DATE_TIME])
@st.cache(persist=True)

def load_data(nrows):
    data = pd.read_csv("Cantec-Location-Data-Nov.csv", nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data['Date/Time'] = pd.to_datetime(data['Date/Time'])
    return data
#load_data(100)

# CREATING FUNCTION FOR MAPS

def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2,3))

with row1_1:
    st.title("Cantec Mapping Test")
    hour_selected = st.slider("Select hours ", 0, 23)

with row1_2:
    st.write(
    """
    ##
    Select delivering hours
    """)

# FILTERING DATA BY HOUR SELECTED
data['date/time'] = pd.to_datetime(data['date/time'], errors = 'coerce')
data = data[data['date/time'].dt.hour == hour_selected]


# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.columns((2,1,1,1))

# SETTING THE ZOOM LOCATIONS For Vancouver
#la_guardia= [49.2439, -123.0629]
la_guardia = [49.2827, -123.1207]
surrey = [49.1913, -122.8490 ]
burnaby = [49.2488, -122.9805]
zoom_level = 12
midpoint = (np.average(data["lat"]), np.average(data["lon"]))

with row2_1:
    st.write("**British Columbia cities from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))
    map(data, midpoint[0], midpoint[1], 11)

with row2_2:
    st.write("**Vancouver**")
    map(data, la_guardia[0],la_guardia[1], zoom_level)

with row2_3:
    st.write("**Surrey**")
    map(data, surrey[0],surrey[1], zoom_level)

with row2_4:
    st.write("**Burnaby**")
    map(data, burnaby[0],burnaby[1], zoom_level)

# FILTERING DATA FOR THE HISTOGRAM
filtered = data[
    (data[DATE_TIME].dt.hour >= hour_selected) & (data[DATE_TIME].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of orders per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ).configure_mark(
        opacity=0.2,
        color='red'
    ), use_container_width=True)