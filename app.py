from pickle import FALSE
from tkinter.font import ITALIC
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.figure_factory as ff

# Setting page configuration
st.set_page_config(
    page_title="Dashboard Most Streamed Spotify Songs 2023",
    page_icon="🎶",
    layout="wide",
)

# Caching data loading
@st.cache_data
def load_data_from_csv():
    df = pd.read_csv('spotify-2023.csv', nrows=1000)
    return df

st.title('Most Streamed Spotify Songs :rainbow[2023]🎈')
st.text('Dashboard created by Jes🔮')


# Custom formatting function
def format_number(number):
    if number >= 1e9:
        return f"{number / 1e9:.2f}B"
    elif number >= 1e6:
        return f"{number / 1e6:.2f}M"
    elif number >= 1e3:
        return f"{number / 1e3:.2f}K"
    else:
        return f"{number:.2f}"
    
# Custom function to convert user input to numeric value
def convert_input_to_numeric(input_str):
    input_str = input_str.strip().lower()
    if input_str.endswith('k'):
        return int(float(input_str[:-1]) * 1000)
    elif input_str.endswith('m'):
        return int(float(input_str[:-1]) * 1000000)
    elif input_str.endswith('b'):
        return int(float(input_str[:-1]) * 1000000000)
    else:
        return int(input_str)
    
# Sidebar filters
with st.sidebar:
    st.header("Please Filter Here:")
    
    # Released Year Filter
    released_years_options = load_data_from_csv()["released_year"].unique()
    released_years = st.multiselect(
        "Select Released Year",
        options=released_years_options,
    )

    # Autocomplete for Search by Artist
    artist_options = load_data_from_csv()["artist_name"].unique().tolist()
    selected_artists = st.multiselect(
        "Search by Artist",
        options=artist_options,
        format_func=lambda x: x,
    )

    # Autocomplete for Search by Song
    song_options = load_data_from_csv()["track_name"].unique().tolist()
    selected_songs = st.multiselect(
        "Search by Song",
        options=song_options,
        format_func=lambda x: x,
    )


# Apply filters
df_selection = load_data_from_csv().copy()
if released_years:
    df_selection = df_selection[df_selection['released_year'].isin(released_years)]

if selected_artists:
    artist_condition = df_selection['artist_name'].isin(selected_artists)
    df_selection = df_selection[artist_condition]

if selected_songs:
    song_condition = df_selection['track_name'].isin(selected_songs)
    df_selection = df_selection[song_condition]

# Quantity of Streams Filter in the Sidebar
with st.sidebar:
    st.header("Stream # Filter")
     
    # Quantity of Streams Filter in the Sidebar
    filter_option = st.radio("Select Stream Filtering Option", ["Bar Selector", "Manual Input"])

    if filter_option == "Bar Selector":
        min_streams, max_streams = st.slider(
            "Select Range of # Streams",
            min_value=int(df_selection['streams'].min()),
            max_value=int(df_selection['streams'].max()),
            value=(int(df_selection['streams'].min()), int(df_selection['streams'].max())),
            step=1
        )

        # Format slider labels
        min_streams_label = format_number(min_streams)
        max_streams_label = format_number(max_streams)
        
        # Display formatted labels
        st.write(f"Selected Range: {min_streams_label} to {max_streams_label}")
    
    else:
        # Display the minimum stream number
        st.write(f"Minimum Stream Number: {format_number(int(df_selection['streams'].min()))}")
        # Set default values for min_streams and max_streams
        min_streams = int(df_selection['streams'].min())
        max_streams = int(df_selection['streams'].max())

        min_streams_input = st.text_input("Enter Minimum # Streams (e.g., 1M)", value=format_number(min_streams))
        max_streams_input = st.text_input("Enter Maximum # Streams (e.g., 1B)", value=format_number(max_streams))

        # Convert user input to numeric values
        min_streams = convert_input_to_numeric(min_streams_input)
        max_streams = convert_input_to_numeric(max_streams_input)

        
 
# Apply the streams filter
streams_condition = (df_selection['streams'] >= min_streams) & (df_selection['streams'] <= max_streams)
df_selection = df_selection[streams_condition]

# Display filtered dataframe
st.dataframe(df_selection.style.format({'streams': format_number}), use_container_width=True, hide_index=True)

# Check if the dataframe is empty
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()  # This will halt the app from further execution.

# Aggregate data to get the count of streams per artist_name
artist_name_streams = df_selection.groupby('artist_name')['streams'].sum().reset_index()

# Select the top 10 most streamed artists
top_artist_names = artist_name_streams.nlargest(10, 'streams')


# Create a Plotly Express scatter chart with bubble size based on stream count
bubble_chart = px.scatter(
    top_artist_names,
    x='artist_name',
    y='streams',
    size='streams',
    labels={'streams': 'Total Streams'},
    title='Top 10 Most Streamed Artists',
    color='streams',  # Add this line to color bubbles based on stream count
    color_continuous_scale='Agsunset',  # Use Agsunset color scale https://plotly.com/python/builtin-colorscales/
)

bubble_chart.update_layout(
    xaxis_title='Artist Name',
    yaxis_title='Total Streams',
    margin=dict(l=0, r=0, t=40, b=0),  # Adjust margins for better layout
)

# Display the chart
st.plotly_chart(bubble_chart, use_container_width=True)



# Filter the top 50 songs
top_50_songs = df_selection.sort_values(by="streams", ascending=False).head(50)

# Display the top 50 songs and their album covers
st.title("Top 50 Most Streamed Songs in Spotify")

# Renaming columns for better clarity
columns_rename = {
    'streams': 'Streams',
    'track_name': 'Track Name',
    'artist_name': 'Artist Name',
    'released_year': 'Released Year'
}
top_50_songs = top_50_songs.rename(columns=columns_rename)

# Display the table

st.table(top_50_songs[['Streams', 'Track Name', 'Artist Name', 'Released Year']])

#st.markdown(top_50_songs[['Streams', 'Track Name', 'Artist Name', 'Released Year']].to_html(index=False), unsafe_allow_html=True)



# Create a bar chart for the 10 most popular songs
top_popular_songs = df_selection.sort_values(by="in_spotify_playlists", ascending=False).head(10)

bar_chart_popular_songs = px.bar(
    top_popular_songs,
    x='track_name',
    y='in_spotify_playlists',
    color='artist_name',
    labels={'in_spotify_playlists': 'Saved in Spotify Playlists'},
    title='Top 10 Most Saved Songs in Spotify Playlists',
    color_continuous_scale='Viridis',  # Use Viridis color scale
)

bar_chart_popular_songs.update_layout(
    xaxis_title='Track Name',
    yaxis_title='Saved in Spotify Playlist',
    margin=dict(l=0, r=0, t=40, b=0),
)

# Display the chart for top popular songs
st.plotly_chart(bar_chart_popular_songs, use_container_width=True)



# Monthly Trends #

# Convert to datetime with explicit format
df_selection['release_date'] = pd.to_datetime(
    df_selection[['released_year', 'released_month', 'released_day']].astype(str).agg('-'.join, axis=1),
    format='%Y-%m-%d',
    errors='coerce'
)

df_selection['release_date_str'] = df_selection['release_date'].dt.strftime('%Y-%m')

# Filter data for the last 10 years
last_10_years = pd.to_datetime('today') - pd.DateOffset(years=10)
df_last_10_years = df_selection[df_selection['release_date'] >= last_10_years]

# Display Temporal Trends using Plotly Express
monthly_trends_last_10_years = df_last_10_years.groupby('release_date_str')['streams'].sum().reset_index()

# Set line color 
line_chart_monthly_trends_last_10_years = px.line(
    monthly_trends_last_10_years,
    x='release_date_str',
    y='streams',
    labels={'streams': 'Total Streams'},
    title='Monthly Trends in Total (Last 10 Years)',
    line_shape='linear',
    color_discrete_sequence=['#ED7D31']  
)    

line_chart_monthly_trends_last_10_years.update_layout(
    xaxis_title='Month',
    yaxis_title='Total Streams',
    margin=dict(l=0, r=0, t=40, b=0),
)

# Display the chart for Monthly Trends in the last 10 years
st.plotly_chart(line_chart_monthly_trends_last_10_years, use_container_width=True)



 
 