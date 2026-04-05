import streamlit as st
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="NOAA Data Dashboard", layout="wide")

PROVINCES = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька',
    5: 'Житомирська', 6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська',
    9: 'Київська', 10: 'Кіровоградська', 11: 'Луганська', 12: 'Львівська',
    13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська', 16: 'Рівненська',
    17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська',
    25: 'Республіка Крим', 26: 'м. Київ', 27: 'м. Севастополь'
}

@st.cache_data
def load_data():
    all_files = glob.glob("data/*.csv")
    if not all_files:
        return pd.DataFrame()
    
    df_list = []
    col_names = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    
    for file in all_files:
        prov_id = int(os.path.basename(file).split('_')[2])
        
        df = pd.read_csv(file, skiprows=1, header=None, names=col_names)
        df = df.drop('empty', axis=1, errors='ignore')
        
        df = df.dropna()
        df['Year'] = df['Year'].astype(str).str.replace('<tt><pre>', '').str.strip()
        
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Week'] = pd.to_numeric(df['Week'], errors='coerce')
        
        df = df.dropna(subset=['Year', 'Week'])
        
        df['Year'] = df['Year'].astype(int)
        df['Week'] = df['Week'].astype(int)
        
        for col in ['VCI', 'TCI', 'VHI']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df[(df['VCI'] >= 0) & (df['TCI'] >= 0) & (df['VHI'] >= 0)]
            
        df['Province'] = PROVINCES.get(prov_id, 'Невідомо')
        df_list.append(df)
        
    full_df = pd.concat(df_list, ignore_index=True)
    return full_df.dropna(subset=['VHI', 'VCI', 'TCI'])

df = load_data()

if df.empty:
    st.error("Дані не знайдено! Запустіть скрипт download_data.py перед запуском додатку.")
    st.stop()

if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = False

def reset_filters():
    st.session_state.index_choice = 'VHI'
    st.session_state.province_choice = 'Київська'
    st.session_state.year_range = (1981, 2024)
    st.session_state.week_range = (1, 52)
    st.session_state.sort_asc = False
    st.session_state.sort_desc = False

if 'index_choice' not in st.session_state: reset_filters()

st.title("Аналіз вегетаційних індексів України (NOAA)")

col_controls, col_content = st.columns([1, 3])

with col_controls:
    st.header("Фільтри")
    
    selected_index = st.selectbox("Виберіть індекс", ['VCI', 'TCI', 'VHI'], key='index_choice')
    selected_province = st.selectbox("Виберіть область", list(PROVINCES.values()), key='province_choice')
    
    year_range = st.slider("Інтервал років", 
                           min_value=int(df['Year'].min()), 
                           max_value=int(df['Year'].max()), 
                           value=st.session_state.year_range, 
                           key='year_range')
                           
    week_range = st.slider("Інтервал тижнів", 1, 52, 
                           value=st.session_state.week_range, 
                           key='week_range')
    
    st.subheader("Сортування")
    sort_asc = st.checkbox("Сортувати за зростанням", key='sort_asc')
    sort_desc = st.checkbox("Сортувати за спаданням", key='sort_desc')
    
    st.button("Скинути фільтри", on_click=reset_filters)

filtered_df = df[
    (df['Province'] == selected_province) & 
    (df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1]) &
    (df['Week'] >= week_range[0]) & (df['Week'] <= week_range[1])
]

if sort_asc and sort_desc:
    st.warning("Обрано обидва типи сортування. Дані залишаться без сортування.")
elif sort_asc:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=True)
elif sort_desc:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=False)

with col_content:
    tab1, tab2, tab3 = st.tabs(["Таблиця даних", "Графік по області", "Порівняння областей"])
    
    with tab1:
        st.subheader(f"Дані для області: {selected_province}")
        st.dataframe(filtered_df[['Year', 'Week', 'Province', selected_index]], use_container_width=True)
        
    with tab2:
        st.subheader(f"Динаміка {selected_index} ({selected_province}, {year_range[0]}-{year_range[1]})")
        
        plot_data = filtered_df.groupby('Year')[selected_index].mean().reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=plot_data, x='Year', y=selected_index, marker='o', ax=ax)
        ax.set_title(f"Середнє значення {selected_index} по роках (тижні {week_range[0]}-{week_range[1]})")
        ax.grid(True)
        st.pyplot(fig)
        
    with tab3:
        st.subheader(f"Порівняння {selected_index} між областями ({year_range[0]}-{year_range[1]})")
        
        comp_df = df[
            (df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1]) &
            (df['Week'] >= week_range[0]) & (df['Week'] <= week_range[1])
        ]
        
        comp_grouped = comp_df.groupby('Province')[selected_index].mean().sort_values(ascending=False).reset_index()
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        colors = ['red' if prov == selected_province else 'steelblue' for prov in comp_grouped['Province']]
        sns.barplot(data=comp_grouped, x='Province', y=selected_index, palette=colors, ax=ax2)
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
        ax2.set_title(f"Середній {selected_index} за обраний період (виділено: {selected_province})")
        st.pyplot(fig2)