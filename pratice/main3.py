import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📊 Excel 規則引擎系統（多條件 + 編輯刪除 + 順序調整）")

# 初始化狀態
for key in ["rules", "current_conditions", "df", "edit_index"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key != "df" else None
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# 載入 Excel
st.sidebar.header("1. 載入 Excel")
uploaded_data = st.sidebar.file_uploader("上傳 Excel 檔 (.xlsx)", type="xlsx")
if uploaded_data:
    df = pd.read_excel(uploaded_data)
    st.session_state.df = df.copy()
    st.sidebar.success("Excel 資料已載入")

# 下載規則json
def save_rules():
    return json.dumps(st.session_state.rules, ensure_ascii=False, indent=2)

# 載入規則json
def load_rules(file):
    try:
        rules = json.load(file)
        if isinstance(rules, list):
            st.session_state.rules = rules
            st.success("規則已載入")
        else:
            st.error("JSON 格式錯誤，應該是一個 List")
    except Exception as e:
        st.error(f"讀取失敗：{e}")

# 下載結果 Excel
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="結果")
    return output.getvalue()

# UI：規則管理區（左側）
with st.sidebar.expander("2. 規則管理", expanded=True):

    # 載入規則檔
    uploaded_rules = st.file_uploader("載入規則 JSON", type="json", key="rule_upload")
    if uploaded_rules:
        load_rules(uploaded_rules)

    # 下載規則
    if st.session_state.rules:
        st.download_button(
            label="下載規則 JSON",
            data=save_rules(),
            file_name="rules.json",
            mime="application/json"
        )

    st.markdown("---")
    st.write(f"目前規則數量：{len(st.session_state.rules)}")

    # 顯示規則清單
    def show_rule(rule, idx):
        cond_txt = []
        for c in rule["conditions"]:
            cond_txt.append(f"{c['col']} {c['op']} {c['val']}")
        cond_str = f" {rule['logic']} ".join(cond_txt)
        return f"規則 {idx+1}: IF {cond_str} THEN → {rule['result']}"

    # 刪除、編輯、上下移動按鈕
    for i, rule in enumerate(st.session_state.rules):
        cols = st.columns([7,1,1,1])
        cols[0].markdown(show_rule(rule, i))
        if cols[1].button("⬆️", key=f"up_{i}", disabled=(i==0)):
            st.session_state.rules[i], st.session_state.rules[i-1] = st.session_state.rules[i-1], st.session_state.rules[i]
            st.experimental_rerun()
        if cols[2].button("⬇️", key=f"down_{i}", disabled=(i==len(st.session_state.rules)-1)):
            st.session_state.rules[i], st.session_state.rules[i+1] = st.session_state.rules[i+1], st.session_state.rules[i]
            st.experimental_rerun()
        if cols[3].button("🗑️", key=f"del_{i}"):
            st.session_state.rules.pop(i)
            st.experimental_rerun()
        if cols[0].button("✏️ 編輯", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.session_state.current_conditions = st.session_state.rules[i]["conditions"].copy()
            st.session_state.logic = st.session_state.rules[i]["logic"]
            st.session_state.result = st.session_state.rules[i]["result"]
            st.experimental_rerun()

# 主區：Excel 預覽 & 規則編輯
if st.session_state.df is not None:
    df = st.session_state.df
    st.subheader("📄 Excel 預覽")
    st.dataframe(df)

    st.markdown("---")
    st.subheader("➕ 建立 / 編輯條件規則")

    # 編輯模式
    is_editing = st.session_state.edit_index is not None

    # 預設條件參數
    if "current_conditions" not in st.session_state or not st.session_state.current_conditions:
        st.session_state.current_conditions = []

    # 欄位、運算子、值輸入
    cols = st.columns(3)
    selected_col = cols[0].selectbox("欄位", df.columns)
    selected_op = cols[1].selectbox("運算子", [">", "<", ">=", "<=", "==", "!=", "包含", "開頭是", "結尾是"])
    input_val = cols[2].text_input("值")

    if cols[2].button("➕ 加入條件"):
        def parse_val(v):
            try:
                return float(v)
            except:
                return v.strip()
        cond = {
            "col": selected_col,
            "op": selected_op,
            "val": parse_val(input_val)
        }
        st.session_state.current_conditions.append(cond)

    # 顯示目前條件組
    if st.session_state.current_conditions:
        st.markdown("**目前條件組：**")
        for i, c in enumerate(st.session_state.current_conditions):
            c1, c2 = st.columns([8,1])
            c1.write(f"{c['col']} {c['op']} {c['val']}")
            if c2.button("❌", key=f"del_cond_{i}"):
                st.session_state.current_conditions.pop(i)
                st.experimental_rerun()

        logic = st.radio("條件間邏輯", ["AND", "OR"], index=0 if not is_editing else ["AND", "OR"].index(st.session_state.logic))
        result = st.text_input("符合結果", value="" if not is_editing else st.session_state.result)

        if st.button("✅ 儲存規則"):
            new_rule = {
                "logic": logic,
                "conditions": st.session_state.current_conditions.copy(),
                "result": result
            }
            if is_editing:
                st.session_state.rules[st.session_state.edit_index] = new_rule
                st.session_state.edit_index = None
            else:
                st.session_state.rules.append(new_rule)
            st.session_state.current_conditions.clear()
            st.experimental_rerun()

    # 套用規則函數
    def apply_rules(row, rules):
        for rule in rules:
            results = []
            for cond in rule["conditions"]:
                val = cond["val"]
                col_val = row.get(cond["col"])
                op = cond["op"]
                try:
                    if op in [">", "<", ">=", "<=", "==", "!="]:
                        expr = f"col_val {op} {repr(val)}"
                        results.append(eval(expr))
                    elif op == "包含":
                        results.append(str(val) in str(col_val))
                    elif op == "開頭是":
                        results.append(str(col_val).startswith(str(val)))
                    elif op == "結尾是":
                        results.append(str(col_val).endswith(str(val)))
                    else:
                        results.append(False)
                except:
                    results.append(False)
            passed = all(results) if rule["logic"] == "AND" else any(results)
            if passed:
                return rule["result"]
        return "Other"

    # 顯示套用結果
    if st.session_state.rules:
        df["結果"] = df.apply(lambda row: apply_rules(row, st.session_state.rules), axis=1)
        st.subheader("📈 套用結果")
        st.dataframe(df)

        st.download_button(
            "下載結果 Excel",
            data=to_excel_download(df),
            file_name="規則結果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("請先在左側上傳 Excel 檔案。")
