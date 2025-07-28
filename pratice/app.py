import streamlit as st
import pandas as pd

# 假資料
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 40],
    'city': ['Taipei', 'Kaohsiung', 'Taipei', 'Tainan']
})

# GUI 控件
age_min = st.slider('最小年齡', 0, 100, 25)
age_max = st.slider('最大年齡', 0, 100, 40)
city_options = df['city'].unique()
selected_city = st.multiselect('選擇城市', city_options, default=list(city_options))

# 條件篩選
filtered_df = df[
    (df['age'] >= age_min) &
    (df['age'] <= age_max) &
    (df['city'].isin(selected_city))
]

st.dataframe(filtered_df)
