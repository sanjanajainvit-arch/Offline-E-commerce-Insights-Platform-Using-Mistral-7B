import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import requests
import json

st.set_page_config(page_title="E-commerce Insights", layout="wide")
st.title("📊 E-commerce AI Dashboard")

query = st.text_input("Ask a question about your data:", "What is the conversion rate on 2025-06-01?")

# 🔍 Optional Filters
# with st.expander("🔧 Advanced Filters"):
#     date_range = st.date_input("Filter by date range", [])
#     category = st.text_input("Filter by category (if applicable)", "")

if st.button("Submit Query"):
    with st.spinner("Thinking..."):
        try:
            res = requests.post("http://localhost:8000/query", json={"question": query})
            res_json = res.json()

            st.subheader("🧠 AI Answer")
            if isinstance(res_json["answer"], dict):
                st.write(res_json["answer"].get("answer", "No answer"))
                rows = res_json["answer"].get("results", [])
                sql_query = res_json["answer"].get("sql", None)
            else:
                st.write(res_json["answer"])
                rows = []
                sql_query = None

            # ✅ Show generated SQL query
            if sql_query:
                with st.expander("📄 View Generated SQL"):
                    st.code(sql_query, language="sql")

            if rows:
                df = pd.DataFrame(rows)
                st.markdown("---")
                st.subheader("📈 Visualization")

                if df.shape[0] == 1 and df.shape[1] == 1:
                    # Single value case - use gauge and bar
                    col_name = df.columns[0]
                    val = df.iloc[0, 0]

                    # Display value
                    st.metric(label=col_name.replace("_", " ").title(), value=val)

                    # Gauge Chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=val,
                        title={'text': col_name.replace("_", " ").title()},
                        gauge={'axis': {'range': [None, val * 2]}, 'bar': {'color': "#636EFA"}}
                    ))
                    st.plotly_chart(fig, use_container_width=True)

                    # Optional Bar Chart
                    single_df = pd.DataFrame({col_name: [val], "Label": [col_name]})
                    chart = alt.Chart(single_df).mark_bar(size=80).encode(
                        x=alt.X('Label', title='Metric'),
                        y=alt.Y(f'{col_name}:Q', title='Value', scale=alt.Scale(domain=[0, val * 1.2])),
                        color=alt.value('#1f77b4'),
                        tooltip=['Label', col_name]
                    ).properties(title=f"{col_name.replace('_', ' ').title()} as Bar")
                    st.altair_chart(chart, use_container_width=True)

                elif df.shape[0] >= 1:
                    col_names = df.columns.tolist()
                    value_col = [col for col in col_names if col not in ['item_id', 'date']][-1]

                    # Choose line or bar chart based on data type
                    if 'date' in col_names:
                        chart = alt.Chart(df).mark_line(point=True).encode(
                            x=alt.X('date:T', title='Date'),
                            y=alt.Y(f'{value_col}:Q', title=value_col.replace('_', ' ').title()),
                            tooltip=col_names
                        ).properties(title=f"{value_col.replace('_', ' ').title()} Over Time")
                    else:
                        chart = alt.Chart(df).mark_bar().encode(
                            x=alt.X('item_id:O', title='Item ID'),
                            y=alt.Y(f'{value_col}:Q', title=value_col.replace('_', ' ').title()),
                            tooltip=['item_id', value_col]
                        ).properties(title=f"{value_col.replace('_', ' ').title()} per Item")

                    st.altair_chart(chart, use_container_width=True)
                    st.dataframe(df)

            else:
                st.warning("No results returned for this question.")

        except Exception as e:
            st.error(f"🚨 Error: {e}")
