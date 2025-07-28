import streamlit as st
import pandas as pd
import json

st.title("📊 多條件規則編輯器")

# 範例資料
df = pd.DataFrame({
    "數值": [120, 90, 150, 130],
    "等級": ["A", "B", "C", "A"]
})
st.subheader("📄 原始資料")
st.dataframe(df)

# 初始化 session state
if "current_conditions" not in st.session_state:
    st.session_state.current_conditions = []

if "rules" not in st.session_state:
    st.session_state.rules = []

# 新增條件區
st.subheader("➕ 建立條件 (會組成一個規則)")
col1, col2, col3 = st.columns(3)
with col1:
    selected_col = st.selectbox("欄位", df.columns)
with col2:
    selected_op = st.selectbox("運算子", [">", "<", ">=", "<=", "==", "!="])
with col3:
    input_val = st.text_input("值")

add_cond_btn = st.button("加入條件")

def parse_val(v):
    try:
        return float(v)
    except:
        return v.strip()

if add_cond_btn:
    condition = {
        "col": selected_col,
        "op": selected_op,
        "val": parse_val(input_val)
    }
    st.session_state.current_conditions.append(condition)

# 顯示目前正在編輯的條件們
if st.session_state.current_conditions:
    st.markdown("**目前條件組**")
    for cond in st.session_state.current_conditions:
        st.write(f"{cond['col']} {cond['op']} {cond['val']}")

    logic = st.radio("條件邏輯運算（多條件）", ["AND", "OR"])
    rule_result = st.text_input("當符合時的結果")

    if st.button("✅ 建立規則"):
        new_rule = {
            "logic": logic,
            "conditions": st.session_state.current_conditions.copy(),
            "result": rule_result
        }
        st.session_state.rules.append(new_rule)
        st.session_state.current_conditions.clear()

# 顯示所有規則
st.subheader("🧠 所有規則")
if st.session_state.rules:
    for i, rule in enumerate(st.session_state.rules):
        st.markdown(f"**規則 {i+1}: ({rule['logic']}) → {rule['result']}**")
        for c in rule["conditions"]:
            st.write(f"- {c['col']} {c['op']} {c['val']}")

# 套用規則
def apply_rules(row, rules):
    for rule in rules:
        results = []
        for cond in rule["conditions"]:
            try:
                expr = f"row['{cond['col']}'] {cond['op']} {repr(cond['val'])}"
                results.append(eval(expr))
            except:
                results.append(False)
        passed = all(results) if rule["logic"] == "AND" else any(results)
        if passed:
            return rule["result"]
    return "Other"

if st.session_state.rules:
    df["結果"] = df.apply(lambda row: apply_rules(row, st.session_state.rules), axis=1)
    st.subheader("📈 結果資料")
    st.dataframe(df)

# 儲存 / 載入規則
st.subheader("💾 儲存 / 載入規則")
col4, col5 = st.columns(2)

with col4:
    if st.download_button(
        label="📥 下載規則 JSON",
        data=json.dumps(st.session_state.rules, ensure_ascii=False, indent=2),
        file_name="rules.json",
        mime="application/json"
    ):
        st.success("規則已匯出")

with col5:
    uploaded_file = st.file_uploader("上傳規則 JSON", type="json")
    if uploaded_file:
        rules_from_file = json.load(uploaded_file)
        st.session_state.rules = rules_from_file
        st.success("已載入規則")
