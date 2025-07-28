import streamlit as st
import pandas as pd

# 假設資料
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 40],
    'city': ['Taipei', 'Kaohsiung', 'Taipei', 'Tainan'],
    'score': [80, 65, 90, 75]
})

st.title("動態篩選條件 GUI (AND / OR)")

# 選擇邏輯組合方式
logic_operator = st.selectbox("條件邏輯組合方式", ['AND', 'OR'])

# 建立多條篩選條件
condition_count = st.number_input("條件數量", min_value=1, max_value=10, value=2, step=1)

columns = df.columns.tolist()
operators = ['==', '!=', '>', '<', '>=', '<=']

conditions = []

for i in range(condition_count):
    st.markdown(f"### 條件 {i+1}")
    col = st.selectbox(f"欄位 {i+1}", columns, key=f"col_{i}")
    op = st.selectbox(f"運算符 {i+1}", operators, key=f"op_{i}")
    val = st.text_input(f"值 {i+1}", key=f"val_{i}")
    
    # 建立條件表達式
    if val != '':
        try:
            # 嘗試轉型數字（如果可能）
            typed_val = eval(val)
        except:
            typed_val = f'"{val}"'  # 加上引號做成字串
            
        conditions.append(f"(df['{col}'] {op} {typed_val})")

# 建構 query 字串
if conditions:
    join_str = ' & ' if logic_operator == 'AND' else ' | '
    query_str = join_str.join(conditions)

    st.code(f"df[{query_str}]", language='python')

    try:
        # 執行查詢
        filtered_df = df[eval(query_str)]
        st.dataframe(filtered_df)
    except Exception as e:
        st.error(f"錯誤：{e}")
