import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.title("📊 Excel 規則引擎系統（含多條件 & 字串判斷）")

# 初始化 session state
for key in ["rules", "current_conditions", "df"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key != "df" else None

# ========== 📥 上傳 Excel 資料 ========== #
st.subheader("📂 載入 Excel 資料")
uploaded_data = st.file_uploader("上傳 Excel 檔 (.xlsx)", type="xlsx")

if uploaded_data:
    df = pd.read_excel(uploaded_data)
    st.session_state.df = df.copy()
    st.success("資料已載入")

if st.session_state.df is not None:
    df = st.session_state.df
    st.subheader("📄 預覽資料")
    st.dataframe(df)

    # ========== ➕ 新增條件與規則 ========== #
    st.divider()
    st.subheader("➕ 建立條件規則")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_col = st.selectbox("欄位", df.columns)
    with col2:
        selected_op = st.selectbox("運算子", [">", "<", ">=", "<=", "==", "!=", "包含", "開頭是", "結尾是"])
    with col3:
        input_val = st.text_input("值")

    if st.button("加入條件"):
        def parse_val(v):
            try:
                return float(v)
            except:
                return v.strip()

        condition = {
            "col": selected_col,
            "op": selected_op,
            "val": parse_val(input_val)
        }
        st.session_state.current_conditions.append(condition)

    # 顯示目前條件組
    if st.session_state.current_conditions:
        st.markdown("**🧩 目前條件組：**")
        for cond in st.session_state.current_conditions:
            st.write(f"- {cond['col']} {cond['op']} {cond['val']}")

        logic = st.radio("邏輯（條件之間）", ["AND", "OR"])
        result = st.text_input("符合時的結果")

        if st.button("✅ 建立規則"):
            st.session_state.rules.append({
                "logic": logic,
                "conditions": st.session_state.current_conditions.copy(),
                "result": result
            })
            st.session_state.current_conditions.clear()
            st.success("規則已新增")

    # 顯示目前所有規則
    if st.session_state.rules:
        st.subheader("🧠 所有規則")
        for i, rule in enumerate(st.session_state.rules):
            st.markdown(f"**規則 {i+1}: ({rule['logic']}) → {rule['result']}**")
            for c in rule["conditions"]:
                st.write(f"- {c['col']} {c['op']} {c['val']}")

    # ========== 🔁 套用規則邏輯（含字串判斷） ========== #
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

    if st.session_state.rules:
        df["結果"] = df.apply(lambda row: apply_rules(row, st.session_state.rules), axis=1)
        st.subheader("📈 套用結果")
        st.dataframe(df)

        # ========== 💾 匯出結果 Excel ========== #
        def to_excel_download(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="結果")
            return output.getvalue()

        st.download_button(
            label="📤 下載結果 Excel",
            data=to_excel_download(df),
            file_name="規則結果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ========== 💾 規則儲存與載入 ========== #
st.divider()
st.subheader("📁 儲存 / 載入規則")

col1, col2 = st.columns(2)

with col1:
    if st.session_state.rules:
        st.download_button(
            label="📥 下載規則 JSON",
            data=json.dumps(st.session_state.rules, ensure_ascii=False, indent=2),
            file_name="rules.json",
            mime="application/json"
        )

with col2:
    uploaded_rules = st.file_uploader("📤 上傳規則 JSON", type="json")
    if uploaded_rules:
        try:
            st.session_state.rules = json.load(uploaded_rules)
            st.success("規則已載入")
        except Exception as e:
            st.error(f"讀取失敗：{e}")
