# Made by Bhavya Kakwani
# Topic: COVID-19 Dashboard
# The theme of the dashboard is changed using the .streamlit/config.toml file present in the same directory as the dashboard.py file
# To run use the command: streamlit run dashboard.py

# Importing all the required libraries

import streamlit as st
import plotly.express as px
import pandas as pd
import pycountry
import copy

# Reading the Datasets

conf = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
dead = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
recd = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
recd = recd.iloc[:, :565]

# Setting the page configuration

st.set_page_config(page_title = "COVID-19 Dashboard", page_icon = ":mask:", layout = "wide")

# Printing the title

st.markdown("<h1 style = 'text-align: center; color: yellow;'> COVID-19 Dashboard by Bhavya Kakwani</h1>", unsafe_allow_html=True)
st.write("")

# Setting the sidebar

st.sidebar.header("**Please Filter Here**")
country = st.sidebar.selectbox("Select the Country : ", options = conf["Country/Region"].unique(), index = 80)
year = st.sidebar.multiselect("Select the Year : ", options = [2021, 2020], default = [2021, 2020])
window = st.sidebar.select_slider("Select Moving Average Window : ", options = [1, 3, 5, 7, 14])
st.sidebar.text("Selected : {} day(s)".format(window))

# Processing data for the selected country so it could be printed on the plot

@st.cache
def process_data(df, country = "India", year = [2021, 2020], window = 1):
    if year == [2020]:
        temp = df.iloc[:, :349]
        temp = temp[temp['Country/Region'] == country]
        fd = temp.T[4:].sum(axis = 'columns').diff().rolling(window = window).mean()[40:]
    elif year == [2021]:
        temp = df.iloc[:, 349:]
        temp["Country/Region"] = df["Country/Region"]
        temp = temp[temp['Country/Region'] == country]
        fd = temp.T[:len(temp.columns) - 1].sum(axis = 'columns').diff().rolling(window = window).mean()[1:]
    else:
        temp = df
        temp = temp[temp['Country/Region'] == country]
        fd = temp.T[4:].sum(axis = 'columns').diff().rolling(window = window).mean()[40:]
    final_dataset = pd.DataFrame(fd,columns=['Total'])
    return final_dataset

# Getting the latest world stats

@st.cache
def get_world_total(df):
    return (df.iloc[:,-1] - df.iloc[:,-2]).sum()

world_conf = get_world_total(conf)
world_dead = get_world_total(dead)
world_recd = get_world_total(recd)

world_data = [world_conf, world_dead, world_recd]

# Getting the latest stats for the selected country

@st.cache
def get_country_total(df, country = "India"):
    return (df[df['Country/Region'] == country].iloc[:,-1] - df[df['Country/Region'] == country].iloc[:,-2]).sum()

country_conf = get_country_total(conf, country)
country_dead = get_country_total(dead, country)
country_recd = get_country_total(recd, country)

country_data = [country_conf, country_dead, country_recd]
names = ["Confirmed", "Dead", "Recovered"]

# Printing the latest stats for the selected country

col1, col2, col3 = st.columns(3)
col1.error("**Confirmed Cases : {}**".format(country_conf))
col2.warning("**Deaths : {}**".format(country_dead))
col3.success("**Recovered Cases : {}**".format(country_recd))

# Printing the latest stats for the world

col1, col2, col3 = st.columns(3)
col1.error("**Worldwide : {}**".format(world_conf))
col2.warning("**Worldwide : {}**".format(world_dead))
col3.success("**Worldwide : {}**".format(world_recd))

st.markdown("")

# Plotting the choropleth plot for the world reprsenting the latest "hot spots" for the confirmed cases

@st.experimental_memo
def plot_world_graph(conf):
    daily_cases = conf.iloc[:, -1] - conf.iloc[:, -2]
    conf["Daily Cases"] = daily_cases
    list_countries = conf['Country/Region'].unique().tolist()
    d_country_code = {}  

    for country in list_countries:
        try:
            country_data = pycountry.countries.search_fuzzy(country)
            country_code = country_data[0].alpha_3
            d_country_code.update({country: country_code})
        except:
            d_country_code.update({country: ' '})

    for k, v in d_country_code.items():
        conf.loc[(conf["Country/Region"] == k), 'iso_alpha'] = v

    fig = px.choropleth(conf, locations="iso_alpha", color="Daily Cases", hover_name="Country/Region", color_continuous_scale=px.colors.sequential.Teal)
    fig.update_layout(title = "<b>COVID-19 Hotspots</b>", title_x = 0.5, plot_bgcolor = '#00172b', paper_bgcolor = '#00172b', height = 550, width = 750)

    conf = conf.drop(columns = ["Daily Cases", "iso_alpha"])
    return fig

fig1 = plot_world_graph(copy.deepcopy(conf))
st.plotly_chart(fig1, use_container_width = True)

# Plotting the pie chart for Confirmed cases, Deaths & Recoveries Worldwide

fig2 = px.pie(values = world_data, names = names, color = names, color_discrete_map = {'Confirmed': '#FF3131', 'Recovered': 'lime', 'Dead': '#FFAD00'}, hole = 0.6, hover_name = names)
fig2.update_layout(title = "<b>Confirmed cases, Deaths & Recoveries Worldwide</b>", title_x = 0.5, plot_bgcolor = '#1f4788', paper_bgcolor = '#1f4788', height = 300, width = 500)

# Plotting the Horizontal Bar Graph depicting Countries with Max Confirmed Cases

@st.experimental_memo
def top_10(conf):
    daily_cases = conf.iloc[:, -1] - conf.iloc[:, -2]
    conf["Daily Cases"] = daily_cases
    conf = conf.nlargest(10, ["Daily Cases"])
    fig = px.bar(conf, x = "Daily Cases", y = "Country/Region", orientation = 'h', color = "Country/Region", color_discrete_sequence = px.colors.qualitative.Light24)
    fig.update_layout(title = "<b>Countries with Max Confirmed Cases</b>", title_x = 0.5, plot_bgcolor = '#1f4788', paper_bgcolor = '#1f4788', xaxis_title = "<b>Daily Cases</b>", yaxis_title = "<b>Country</b>", height = 300, width = 500, xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)))
    return fig

fig3 = top_10(copy.deepcopy(conf))

# Printing the above 2 plots in 2 columns

col1, col2 = st.columns(2)
col1.plotly_chart(fig2, use_column_width=True)
col2.plotly_chart(fig3, use_column_width=True)

# Plotting the pie chart depicting Confirmed cases, Deaths & Recoveries for the selected country

fig4 = px.pie(values = country_data, names = names, color = names, color_discrete_map = {'Confirmed': '#FF3131', 'Recovered': 'lime', 'Dead': '#FFAD00'}, hole = 0.6, hover_name = names)
fig4.update_layout(title = "<b>Confirmed cases, Deaths & Recoveries for {}</b>".format(country), title_x = 0.5, plot_bgcolor = '#1f4788', paper_bgcolor = '#1f4788', height = 300, width = 500)

# Plotting the line chart depicting Daily confirmed cases trend for the selected country

df = process_data(conf, country, year, window)
fig5 = px.line(df, x = df.index, y = "Total", title = "<b>Daily Confirmed cases trend for {}</b>".format(country), color_discrete_sequence = ['#FF3131'])
fig5.update_layout(title_x = 0.5, plot_bgcolor = '#1f4788', paper_bgcolor = '#1f4788', xaxis_title = "<b>Date</b>", yaxis_title = "<b>Daily Cases</b>", height = 300, width = 500, xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)))
fig5.add_vline(x = 0, line_color = "#ffffff")

# Printing the above 2 plots in 2 columns

col1, col2 = st.columns(2)
col1.plotly_chart(fig4, use_column_width=True)
col2.plotly_chart(fig5, use_column_width=True)

# Plotting the line chart depicting Daily deaths trend for the selected country

df = process_data(dead, country, year, window)
fig6 = px.line(df, x = df.index, y = "Total", title = "<b>Daily Deaths trend for {}</b>".format(country), color_discrete_sequence = ['#FFAD00'])
fig6.update_layout(title_x = 0.5, plot_bgcolor = '#1f4788', paper_bgcolor = '#1f4788', xaxis_title = "<b>Date</b>", yaxis_title = "Daily Deaths", height = 300, width = 500, xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)))
fig6.add_vline(x = 0, line_color = "#ffffff")

# Plotting the line chart depicting Daily recovered cases trend for the selected country

df = process_data(recd, country, year, window)
fig7 = px.line(df, x = df.index, y = "Total", title = "<b>Daily Recovered cases trend for {}</b>".format(country), color_discrete_sequence = ['lime'])
fig7.update_layout(title_x = 0.5, plot_bgcolor = '#1f4788', paper_bgcolor = '#1f4788', xaxis_title = "<b>Date</b>", yaxis_title = "<b>Daily Recoveries</b>", height = 300, width = 500, xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)))
fig7.add_vline(x = 0, line_color = "#ffffff")

# Printing the above 2 plots in 2 columns

col1, col2 = st.columns(2)
col1.plotly_chart(fig6, use_column_width=True)
col2.plotly_chart(fig7, use_column_width=True)

# Removing main menu & footer from the dashboard

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Removing the top & bottom padding from the dashboard

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)