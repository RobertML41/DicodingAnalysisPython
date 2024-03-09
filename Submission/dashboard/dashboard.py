import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.patches as mpatches
import streamlit as st

all_df = pd.read_csv('main_data.csv')
#inisialiasi list dan dictionary yang dibutuhkan
stations_substances_df = all_df.drop(["year","month","day","hour","station",'wd'],axis=1)
substances = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "WSPM", "RAIN"]

substances_threshold = {
    "PM2.5" : {"year": 5, "day":15},
    "PM10" : {"year": 15, "day":45},
    "SO2" : {"day":40},
    "NO2" : {"year": 10, "day":25},
    "CO" : {"day":7},

}

#inisialiasi fungsi

def analyze_substances(df, method, by,station=""):
    df_analyze = pd.concat([df[by].sort_index().reset_index(), stations_substances_df.sort_index().reset_index()],axis=1)
    if station != "":
        df_analyze = df_analyze.where(df["station"] == station)
        df_analyze.name = station
    df_analyze = df_analyze.groupby(by=by).agg(method)
    return df_analyze

def bar_chart(df, time, method, substance, station =""):
    group_df = df.reset_index()
    group_df = group_df.sort_values(by=substance, ascending=False)
    fig = plt.figure(figsize=(12, 5))

    highest_level_color = '#FF0000' #warna mera
    other_level_colors = "#72BCD4" #warna biru

    #cari index yang memiliki level substansi yang tertinggi, untuk diberikan pewarnaan yang berbeda
    highest_index = group_df[substance].idxmax()

    #secara dinamis, urutkan warna berdasarkan urutan level substansi
    colors = [highest_level_color if i == highest_index else other_level_colors for i in range(len(group_df))]

    ax = sns.barplot(
        x=time,
        y=substance,
        data=group_df,
        palette=colors,
        hue= None
    )

    #tambahkan label pada setiap bar
    for container in ax.containers:
        ax.bar_label(container, fontsize=10)

    plt.title('{} {} {} levels Throughout {}s'.format(station,substance ,method.capitalize(), time.capitalize()), size=20)
    plt.xlabel(time, size=15)
    plt.ylabel(f'{substance} Levels', size=15)
    plt.tick_params(axis='x', labelsize=12)
    st.pyplot(fig)
def compare_stations(df,substance,method):
    color_list = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3","#D3D3D3","#D3D3D3","#D3D3D3","#D3D3D3","#D3D3D3","#D3D3D3"]
    
    station_df = df.reset_index().groupby("station").agg({substance: method})
    fig = plt.figure(figsize=(10,5))

    sns.barplot(
        x=substance, 
        y="station",
        data=station_df.sort_values(by=substance, ascending=False),
        palette=color_list
    )
    plt.title("{} Levels's {} Through All Stations".format(substance, method.capitalize()), loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)


# def iterate_station_comparison(df,method):
#     for substance in substances:
#         compare_stations(df,substance, method)
def bar_chart_assess_quality(df,substance, station):
    safe_levels_color = "#72BCD4"
    unsafe_levels_color = '#FF0000'

    group_df = df.reset_index()
    if (station!=""):
        group_df = group_df.where(group_df["station"]==station)

    group_day_df = group_df.groupby(by="day").agg({substance: "mean"})

    day_substance_threshold = substances_threshold[substance]["day"]
    colors_day = [safe_levels_color if x < day_substance_threshold else unsafe_levels_color for x in group_day_df[substance]]

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 10))
    
    sns.barplot(
        x="day",
        y=substance,
        data=group_day_df,
        palette=colors_day,
        hue= None,
        ax=ax[0]
    )

    safe_patch = mpatches.Patch(color=safe_levels_color, label='Safe Level')
    unsafe_patch = mpatches.Patch(color=unsafe_levels_color, label='Unsafe Level')

    ax[0].legend(handles=[safe_patch, unsafe_patch], loc='upper right')

    if('year' in substances_threshold.get(substance, {})):
        
        group_annual_df = group_df.groupby(by="year").agg({substance: "mean"})
        annual_substance_threshold = substances_threshold[substance]["year"]
        colors_annual = [safe_levels_color if x < annual_substance_threshold else unsafe_levels_color for x in group_annual_df[substance]]
       
        ax[1].set_ylabel(substance,size=15)
        ax[1].set_xlabel('Annually',size=15)
        ax[1].set_title("{} {} Level Annual-Mean Assessment".format(station.capitalize(), substance), loc="center", fontsize=18)
        ax[1].tick_params(axis ='x', labelsize=15, rotation=45)
    
        sns.barplot(
            x="year",
            y=substance,
            data=group_annual_df,
            palette=colors_annual,
            hue= None,
            ax=ax[1]
        )


    

    ax[0].set_ylabel(substance,size=15)
    ax[0].set_xlabel('Day',size=15)
    ax[0].set_title("{} {} Level 24 Hours-Mean Assessment".format(station.capitalize(), substance), loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=15, rotation=45)

    plt.suptitle("{} {} Quality Assessment".format(station, substance), fontsize=20)
    st.pyplot(fig)
#visualize dashboard
st.header('Final Project: Air Quality Analysis')
st.subheader('Average Level Substansi')

col1, col2 = st.columns(2)
with col1:
    total_substances = len(substances)
    st.metric("Total Substances", total_substances)
with col2:
    st.metric("Highest average substance in year", 2014)

substances = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "TEMP", "PRES", "DEWP", "WSPM", "RAIN"]

tabPM25, tabPM10, tabSO2,tabNO2 ,tabCO, tabO3, tabTEMP, tabPRES,tabDEWP, tabWSPM, tabRAIN= st.tabs(substances)
with tabPM25:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','PM2.5') 

with tabPM10:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','PM10') 
with tabSO2:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','SO2') 
with tabNO2:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','NO2') 
 
with tabCO:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','CO') 
with tabO3:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','O3') 
 
with tabTEMP:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','TEMP') 
with tabPRES:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','PRES') 
with tabDEWP:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','DEWP') 
 
with tabWSPM:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','WSPM') 
with tabRAIN:
    bar_chart(analyze_substances(all_df,"mean","year"), 'year','mean','RAIN') 
 

st.subheader('Highest Substances Frequencies/Levels based on Station')

col1, col2 = st.columns(2)
with col1:
    total_substances = len(substances)
    st.metric("Total Station", 12)
with col2:
    st.metric("Highest substances average occurs in station ", "Wanliu")


tabPM25, tabPM10, tabSO2,tabNO2 ,tabCO, tabO3, tabTEMP, tabPRES,tabDEWP, tabWSPM, tabRAIN= st.tabs(substances)
with tabPM25:
    compare_stations(all_df, "PM2.5","mean")
with tabPM10:
    compare_stations(all_df, "PM10","mean")
with tabSO2:
    compare_stations(all_df, "SO2","mean")
with tabNO2:
    compare_stations(all_df, "NO2","mean")
 
with tabCO:
    compare_stations(all_df, "CO","mean")
with tabO3:
    compare_stations(all_df, "O3","mean")
 
with tabTEMP:
    compare_stations(all_df, "TEMP","mean")
with tabPRES:
    compare_stations(all_df, "PRES","mean")
with tabDEWP:
    compare_stations(all_df, "DEWP","mean")
 
with tabWSPM:
    compare_stations(all_df, "WSPM","mean")
with tabRAIN:
    compare_stations(all_df, "RAIN","mean")
 

st.subheader('Highest Substances Frequencies/Levels based on Station')

col1, col2 = st.columns(2)
with col1:
    total_substances = len(substances)
    st.metric("Total Station", 12)
with col2:
    st.metric("Highest substances average occurs in station ", "Wanliu")

stations = ['Aotizhongxin', 'Changping', 'Dingling', 'Dongsi', 'Guanyuan', 'Gucheng', 'Huairou', 'Nongzhanguan', 'Shunyi', 'Tiantan', 'Wanliu', 'Wanshouxigong']

tabAotizhongxin, tabChangping, tabDingling, tabDongsi, tabGuanyuan, tabGucheng, tabHuarou, tabNongzhanguan, tabShunyi, tabTiantan, tabWanliu, tabWanshouxigong = st.tabs(stations)

with tabAotizhongxin:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Aotizhongxin')

with tabChangping:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Changping')

with tabDingling:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Dingling')

with tabDongsi:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Dongsi')

with tabGuanyuan:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Guanyuan')

with tabGucheng:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Gucheng')

with tabHuarou:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Huarou')

with tabNongzhanguan:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Nongzhanguan')

with tabShunyi:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Shunyi')

with tabTiantan:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Tiantan')

with tabWanliu:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Wanliu')

with tabWanshouxigong:
    for substance in substances[:5]:
        bar_chart_assess_quality(all_df, substance, 'Wanshouxigong')


 

