"""
app.py
QueryMind AI — main entry point.

Wires together every module (database, ai_engine, sql_generator, dashboard,
charts, analysis, cleaning, report_generator, authentication, history) into
a single-page-app style Streamlit UI with a persistent sidebar navigation,
matching the requested "Home / Upload / DB Connection / AI Chat / SQL
Generator / SQL Executor / Dashboard / Charts / Cleaning / Analysis /
Insights / History / Saved / Reports / Settings / Profile" page set.

Run locally:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np

from config import configure_page, NAV_PAGES, AVAILABLE_MODELS, DEFAULT_MODEL_LABEL, GROQ_API_KEY
from utils import init_session_state, inject_css, page_header, kpi_card, human_number, dataframe_from_upload, safe_run
from authentication import auth_gate, logout
import database as db
import ai_engine
import sql_generator as sg
import dashboard as dash
import charts as ch
import analysis as an
import cleaning as cl
import report_generator as rg
import history as hist

# ---------------------------------------------------------------------------
# Page config + session bootstrap
# ---------------------------------------------------------------------------
configure_page()
init_session_state()
inject_css()

# ---------------------------------------------------------------------------
# Auth gate — everything below only renders once logged in
# ---------------------------------------------------------------------------
if not auth_gate():
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
def sidebar():
    with st.sidebar:
        st.markdown(
            f'<div style="font-size:1.4rem;font-weight:800;">🧠 QueryMind AI</div>'
            f'<div class="qm-subtle">Chat with your data. Instantly.</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        st.text_input("🔍 Search pages", key="nav_search", placeholder="Type to filter...")
        search = st.session_state.get("nav_search", "").lower()

        for icon, name in NAV_PAGES:
            if search and search not in name.lower():
                continue
            if st.button(f"{icon}  {name}", use_container_width=True, key=f"nav_{name}"):
                st.session_state["active_page"] = name

        st.divider()
        st.selectbox(
            "AI Model", list(AVAILABLE_MODELS.keys()),
            index=list(AVAILABLE_MODELS.keys()).index(DEFAULT_MODEL_LABEL),
            key="selected_model_label",
        )
        theme_choice = st.radio("Theme", ["dark", "light"], horizontal=True,
                                 index=0 if st.session_state["theme"] == "dark" else 1)
        if theme_choice != st.session_state["theme"]:
            st.session_state["theme"] = theme_choice
            st.rerun()

        st.caption(f"👤 Logged in as **{st.session_state.get('username')}**")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

        if not GROQ_API_KEY:
            st.warning("No GROQ_API_KEY set — AI features (Chat, SQL generation, "
                       "Insights) are disabled until you add one in Settings/.env.")


sidebar()
page = st.session_state["active_page"]


# ---------------------------------------------------------------------------
# Helpers shared across pages
# ---------------------------------------------------------------------------
def require_data():
    if st.session_state.get("df") is None and st.session_state.get("engine") is None:
        st.info("No dataset loaded yet. Go to **📂 Upload Data** or **🔗 Database Connection** first.")
        return False
    return True


def active_dataframe():
    """Return the best-effort current DataFrame, pulling from the engine if needed."""
    if st.session_state.get("df") is not None:
        return st.session_state["df"]
    if st.session_state.get("engine") is not None and st.session_state.get("df_name"):
        try:
            return db.load_table_preview(st.session_state["engine"], st.session_state["df_name"], limit=100000)
        except Exception:
            return None
    return None


# ---------------------------------------------------------------------------
# 🏠 Home
# ---------------------------------------------------------------------------
if page == "Home":
    page_header("🏠 Welcome to QueryMind AI", "Chat with your data. Instantly.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Datasets Loaded", "1" if st.session_state.get("df") is not None or st.session_state.get("engine") else "0")
    with c2:
        kpi_card("Queries Run", str(len(st.session_state.get("query_history", []))))
    with c3:
        kpi_card("Saved Queries", str(len(st.session_state.get("saved_queries", []))))
    with c4:
        kpi_card("AI Model", st.session_state.get("selected_model_label") or DEFAULT_MODEL_LABEL)

    st.write("")
    st.markdown("#### Get started")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown('<div class="qm-card">📂 <b>Upload Data</b><br><span class="qm-subtle">CSV, Excel, or a SQLite .db file.</span></div>', unsafe_allow_html=True)
    with g2:
        st.markdown('<div class="qm-card">💬 <b>AI Chat</b><br><span class="qm-subtle">Ask questions in plain English.</span></div>', unsafe_allow_html=True)
    with g3:
        st.markdown('<div class="qm-card">📊 <b>Dashboard</b><br><span class="qm-subtle">Instant KPIs & charts.</span></div>', unsafe_allow_html=True)

    if active_dataframe() is not None:
        st.write("")
        st.markdown("#### Current dataset preview")
        st.dataframe(active_dataframe().head(20), use_container_width=True)


# ---------------------------------------------------------------------------
# 📂 Upload Data
# ---------------------------------------------------------------------------
elif page == "Upload Data":
    page_header("📂 Upload Data", "CSV, Excel (.xlsx), or SQLite (.db) files.")
    uploaded = st.file_uploader("Drop a file here", type=["csv", "xlsx", "xls", "db", "sqlite", "sqlite3"])

    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith((".db", ".sqlite", ".sqlite3")):
                engine = db.engine_from_sqlite_upload(uploaded)
                schema = db.get_schema(engine)
                st.session_state["engine"] = engine
                st.session_state["schema"] = schema
                st.session_state["df"] = None
                tables = list(schema.keys())
                st.session_state["df_name"] = tables[0] if tables else None
                st.success(f"Connected to SQLite file with {len(tables)} table(s): {', '.join(tables)}")
            else:
                df = dataframe_from_upload(uploaded)
                table_name = uploaded.name.rsplit(".", 1)[0].replace(" ", "_").replace("-", "_")
                engine = db.engine_from_dataframe(df, table_name=table_name)
                st.session_state["df"] = df
                st.session_state["df_name"] = table_name
                st.session_state["engine"] = engine
                st.session_state["schema"] = db.get_schema(engine)
                st.success(f"Loaded **{uploaded.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns.")
        except Exception as e:
            st.error(f"Failed to load file: {e}")

    if active_dataframe() is not None:
        st.write("")
        st.markdown("##### Preview")
        st.dataframe(active_dataframe().head(50), use_container_width=True)
        st.markdown("##### Detected schema")
        st.code(db.schema_to_prompt_string(st.session_state["schema"]) or "No schema detected.")
    else:
        st.caption("No file uploaded yet. Try the sample dataset in `sample_data/sample_sales.csv`.")


# ---------------------------------------------------------------------------
# 🔗 Database Connection
# ---------------------------------------------------------------------------
elif page == "Database Connection":
    page_header("🔗 Database Connection", "Connect to a live MySQL or PostgreSQL database.")
    with st.form("db_conn_form"):
        col1, col2 = st.columns(2)
        with col1:
            db_type = st.selectbox("Database Type", ["MySQL", "PostgreSQL"])
            host = st.text_input("Host", "localhost")
            port = st.text_input("Port", "3306" if db_type == "MySQL" else "5432")
        with col2:
            database_name = st.text_input("Database name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("🔌 Test & Connect", use_container_width=True)

    if submitted:
        try:
            engine = db.engine_from_credentials(db_type, host, port, database_name, username, password)
            ok, msg = db.test_connection(engine)
            if ok:
                schema = db.get_schema(engine)
                st.session_state["engine"] = engine
                st.session_state["schema"] = schema
                st.session_state["df"] = None
                tables = list(schema.keys())
                st.session_state["df_name"] = tables[0] if tables else None
                st.session_state["connections"].append(
                    {"type": db_type, "host": host, "database": database_name, "username": username}
                )
                st.success(f"{msg} Found {len(tables)} table(s).")
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"Connection error: {e}")

    if st.session_state.get("connections"):
        st.markdown("##### Recent connections")
        st.dataframe(pd.DataFrame(st.session_state["connections"]), use_container_width=True)

    if st.session_state.get("schema"):
        st.markdown("##### Live schema")
        st.code(db.schema_to_prompt_string(st.session_state["schema"]))


# ---------------------------------------------------------------------------
# 💬 AI Chat
# ---------------------------------------------------------------------------
elif page == "AI Chat":
    page_header("💬 AI Chat", "Ask questions about your data in plain English.")
    if not require_data():
        pass
    else:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        question = st.chat_input("e.g. Show top 5 customers by revenue")
        if question:
            st.session_state["chat_history"].append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                try:
                    schema_prompt = db.schema_to_prompt_string(st.session_state["schema"])
                    sql = sg.natural_language_to_sql(
                        question, schema_prompt, st.session_state["engine"],
                        chat_history=st.session_state["chat_history"],
                    )
                    st.code(sql, language="sql")
                    result_df = db.execute_sql(st.session_state["engine"], sql)
                    st.dataframe(result_df, use_container_width=True)
                    hist.log_query(st.session_state["username"], question, sql)
                    st.session_state["query_history"].append({"question": question, "sql": sql})
                    st.session_state["last_sql"] = sql
                    st.session_state["last_result"] = result_df
                    reply = f"```sql\n{sql}\n```\nReturned **{len(result_df)}** row(s)."
                except Exception as e:
                    reply = f"⚠️ I couldn't run that query: {e}"
                    st.error(reply)
                st.session_state["chat_history"].append({"role": "assistant", "content": reply})


# ---------------------------------------------------------------------------
# 📝 SQL Generator
# ---------------------------------------------------------------------------
elif page == "SQL Generator":
    page_header("📝 SQL Generator", "English → SQL, SQL → English, optimize, explain, fix, format.")
    if not require_data():
        pass
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["English → SQL", "Explain SQL", "Optimize SQL", "Fix SQL Error", "Format SQL"]
        )
        schema_prompt = db.schema_to_prompt_string(st.session_state["schema"])

        with tab1:
            question = st.text_area("Describe what you want in plain English",
                                     placeholder="Monthly sales trend for 2024")
            if st.button("Generate SQL", key="gen_sql_btn"):
                with st.spinner("Generating SQL..."):
                    sql = sg.natural_language_to_sql(question, schema_prompt, st.session_state["engine"])
                    st.session_state["last_sql"] = sql
                st.code(sql, language="sql")

        with tab2:
            sql_in = st.text_area("Paste SQL to explain", key="explain_in")
            if st.button("Explain", key="explain_btn"):
                with st.spinner("Explaining..."):
                    st.markdown(sg.explain_sql(sql_in))

        with tab3:
            sql_in2 = st.text_area("Paste SQL to optimize", key="optimize_in")
            if st.button("Optimize", key="optimize_btn"):
                with st.spinner("Analyzing..."):
                    st.markdown(sg.optimize_sql(sql_in2, dialect=db._dialect_name(st.session_state["engine"])))

        with tab4:
            sql_in3 = st.text_area("Paste failing SQL", key="fix_in")
            err_in = st.text_area("Paste the error message", key="fix_err")
            if st.button("Fix it", key="fix_btn"):
                with st.spinner("Fixing..."):
                    fixed = sg.fix_sql_error(sql_in3, err_in, schema_prompt)
                st.code(fixed, language="sql")

        with tab5:
            sql_in4 = st.text_area("Paste SQL to format", key="format_in")
            if st.button("Format", key="format_btn"):
                st.code(sg.format_sql(sql_in4), language="sql")


# ---------------------------------------------------------------------------
# ▶ SQL Executor
# ---------------------------------------------------------------------------
elif page == "SQL Executor":
    page_header("▶ SQL Executor", "Run raw SQL directly against the connected data source.")
    if not require_data():
        pass
    else:
        allow_writes = st.toggle("⚠️ Allow write statements (INSERT/UPDATE/DELETE/DDL)", value=False)
        sql_text = st.text_area("SQL query", value=st.session_state.get("last_sql", ""), height=160)
        c1, c2 = st.columns([1, 1])
        with c1:
            run_clicked = st.button("▶ Run Query", use_container_width=True, type="primary")
        with c2:
            save_clicked = st.button("⭐ Save Query", use_container_width=True)

        if save_clicked and sql_text.strip():
            hist.save_query(st.session_state["username"], sql_text.strip().split("\n")[0][:60], sql_text)
            st.success("Saved to Saved Queries.")

        if run_clicked and sql_text.strip():
            try:
                result = db.execute_sql(st.session_state["engine"], sql_text, allow_writes=allow_writes)
                st.session_state["last_sql"] = sql_text
                st.session_state["last_result"] = result
                hist.log_query(st.session_state["username"], "(manual SQL)", sql_text)
                st.session_state["query_history"].append({"question": "(manual SQL)", "sql": sql_text})
                st.success(f"Returned {len(result)} row(s).")
                st.dataframe(result, use_container_width=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.download_button("⬇ CSV", rg.to_csv_bytes(result), "query_result.csv", "text/csv")
                with c2:
                    st.download_button("⬇ Excel", rg.to_excel_bytes(result), "query_result.xlsx")
                with c3:
                    st.download_button("⬇ SQL", rg.to_sql_file(sql_text), "query.sql")
            except Exception as e:
                st.error(f"Query failed: {e}")


# ---------------------------------------------------------------------------
# 📊 Dashboard
# ---------------------------------------------------------------------------
elif page == "Dashboard":
    page_header("📊 Dashboard", "Auto-generated executive dashboard.")
    if not require_data():
        pass
    else:
        df = active_dataframe()
        if df is None or df.empty:
            st.info("No rows to display.")
        else:
            dash.render_dashboard(df)


# ---------------------------------------------------------------------------
# 📈 Charts
# ---------------------------------------------------------------------------
elif page == "Charts":
    page_header("📈 Charts", "Build any of 20 chart types interactively.")
    if not require_data():
        pass
    else:
        df = active_dataframe()
        chart_type = st.selectbox("Chart type", list(ch.CHART_REGISTRY.keys()))
        cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

        fig = None
        try:
            if chart_type in ["Bar Chart", "Line Chart", "Area Chart", "Time Series"]:
                x = st.selectbox("X axis", cols)
                y = st.selectbox("Y axis", numeric_cols or cols)
                color = st.selectbox("Color (optional)", [None] + cols)
                fig = ch.CHART_REGISTRY[chart_type](df, x, y, color=color, title=chart_type)
            elif chart_type in ["Pie Chart", "Donut Chart"]:
                names = st.selectbox("Category column", cols)
                values = st.selectbox("Value column", numeric_cols or cols)
                fig = ch.CHART_REGISTRY[chart_type](df, names, values, title=chart_type)
            elif chart_type in ["Scatter Plot", "Bubble Chart"]:
                x = st.selectbox("X axis", numeric_cols or cols)
                y = st.selectbox("Y axis", numeric_cols or cols)
                if chart_type == "Bubble Chart":
                    size = st.selectbox("Size", numeric_cols or cols)
                    fig = ch.bubble_chart(df, x, y, size, title=chart_type)
                else:
                    fig = ch.scatter_plot(df, x, y, title=chart_type)
            elif chart_type in ["Histogram", "Distribution Plot"]:
                x = st.selectbox("Column", numeric_cols or cols)
                fig = ch.CHART_REGISTRY[chart_type](df, x, title=chart_type)
            elif chart_type in ["Box Plot", "Violin Plot"]:
                y = st.selectbox("Value column", numeric_cols or cols)
                x = st.selectbox("Group by (optional)", [None] + cols)
                fig = ch.CHART_REGISTRY[chart_type](df, x=x, y=y, title=chart_type)
            elif chart_type in ["Heatmap", "Correlation Matrix"]:
                fig = ch.CHART_REGISTRY[chart_type](df, title=chart_type)
            elif chart_type in ["Treemap", "Sunburst"]:
                path = st.multiselect("Hierarchy path (1-3 columns)", cols, default=cols[:1])
                values = st.selectbox("Value column", numeric_cols or cols)
                if path:
                    fig = ch.CHART_REGISTRY[chart_type](df, path, values, title=chart_type)
            elif chart_type == "Waterfall Chart":
                x = st.selectbox("X (category)", cols)
                y = st.selectbox("Y (value)", numeric_cols or cols)
                fig = ch.waterfall(df, x, y, title=chart_type)
            elif chart_type == "Funnel Chart":
                x = st.selectbox("Stage", cols)
                y = st.selectbox("Value", numeric_cols or cols)
                fig = ch.funnel_chart(df, x, y, title=chart_type)
            elif chart_type == "Geo Map":
                locations = st.selectbox("Location column (country names)", cols)
                color = st.selectbox("Color value", numeric_cols or cols)
                fig = ch.geo_map(df, locations, color, title=chart_type)
            elif chart_type == "Pair Plot":
                dims = st.multiselect("Dimensions", numeric_cols, default=numeric_cols[:4])
                if dims:
                    fig = ch.pair_plot(df, dims, title=chart_type)

            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
                try:
                    png = rg.fig_to_png_bytes(fig)
                    st.download_button("⬇ Download chart as PNG", png, f"{chart_type.replace(' ', '_')}.png")
                except Exception:
                    st.caption("PNG export needs the `kaleido` package installed.")
        except Exception as e:
            st.warning(f"Couldn't render this chart with the current selections: {e}")


# ---------------------------------------------------------------------------
# 🧹 Data Cleaning
# ---------------------------------------------------------------------------
elif page == "Data Cleaning":
    page_header("🧹 Data Cleaning", "One-click cleaning operations. Nothing is applied until you click a button.")
    if not require_data():
        pass
    else:
        df = active_dataframe()
        working = st.session_state.get("cleaned_df", df).copy()

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Remove Duplicates", use_container_width=True):
                working = cl.remove_duplicates(working)
        with c2:
            null_strategy = st.selectbox("Fill nulls strategy", ["mean", "median", "mode", "ffill", "bfill", "constant"])
        with c3:
            if st.button("Apply Fill Nulls", use_container_width=True):
                working = cl.fill_nulls(working, strategy=null_strategy)

        c4, c5, c6 = st.columns(3)
        with c4:
            if st.button("Drop Rows With Any Nulls", use_container_width=True):
                working = cl.drop_nulls(working)
        with c5:
            if st.button("Normalize Text Columns", use_container_width=True):
                working = cl.normalize_text(working)
        with c6:
            outlier_col = st.selectbox("Outlier column (IQR)", working.select_dtypes(include=np.number).columns.tolist() or ["-"])
            if st.button("Remove Outliers", use_container_width=True) and outlier_col != "-":
                working = cl.remove_outliers_iqr(working, outlier_col)

        st.markdown("##### Rename a column")
        rc1, rc2, rc3 = st.columns([2, 2, 1])
        with rc1:
            old_name = st.selectbox("Column", working.columns.tolist())
        with rc2:
            new_name = st.text_input("New name", value=old_name)
        with rc3:
            st.write("")
            if st.button("Rename"):
                working = cl.rename_columns(working, {old_name: new_name})

        st.markdown("##### Convert data type")
        tc1, tc2, tc3 = st.columns([2, 2, 1])
        with tc1:
            type_col = st.selectbox("Column ", working.columns.tolist(), key="type_col")
        with tc2:
            new_type = st.selectbox("New type", ["numeric", "string", "datetime", "category", "boolean"])
        with tc3:
            st.write("")
            if st.button("Convert"):
                try:
                    working = cl.convert_dtype(working, type_col, new_type)
                except Exception as e:
                    st.error(str(e))

        st.markdown("##### Drop columns")
        drop_cols = st.multiselect("Columns to drop", working.columns.tolist())
        if st.button("Drop selected columns") and drop_cols:
            working = cl.drop_columns(working, drop_cols)

        st.session_state["cleaned_df"] = working
        st.write("")
        st.markdown(f"##### Preview ({working.shape[0]:,} rows × {working.shape[1]} columns)")
        st.dataframe(working.head(50), use_container_width=True)

        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button("⬇ Download cleaned CSV", rg.to_csv_bytes(working), "cleaned_data.csv")
        with d2:
            st.download_button("⬇ Download cleaned Excel", rg.to_excel_bytes(working), "cleaned_data.xlsx")
        with d3:
            if st.button("✅ Use cleaned data as active dataset"):
                st.session_state["df"] = working
                st.session_state["engine"] = db.engine_from_dataframe(working, table_name=st.session_state.get("df_name", "data"))
                st.session_state["schema"] = db.get_schema(st.session_state["engine"])
                st.success("Active dataset updated.")


# ---------------------------------------------------------------------------
# 📉 Data Analysis
# ---------------------------------------------------------------------------
elif page == "Data Analysis":
    page_header("📉 Data Analysis", "Automatic EDA, correlation, trend, and category analysis.")
    if not require_data():
        pass
    else:
        df = active_dataframe()
        tabs = st.tabs(["Statistical Summary", "Correlation", "Missing Values", "Duplicates",
                        "Outliers", "Trend Detection", "Category Breakdown", "Feature Importance"])

        with tabs[0]:
            stats = an.statistical_summary(df)
            st.dataframe(stats, use_container_width=True) if not stats.empty else st.info("No numeric columns.")

        with tabs[1]:
            corr = an.correlation_analysis(df)
            st.dataframe(corr, use_container_width=True) if not corr.empty else st.info("No strong correlations found.")
            if df.select_dtypes(include=np.number).shape[1] >= 2:
                st.plotly_chart(ch.correlation_matrix(df), use_container_width=True)

        with tabs[2]:
            missing = an.missing_value_report(df)
            st.dataframe(missing, use_container_width=True) if not missing.empty else st.success("No missing values 🎉")

        with tabs[3]:
            dups = an.find_duplicate_records(df)
            st.dataframe(dups, use_container_width=True) if not dups.empty else st.success("No duplicate rows 🎉")

        with tabs[4]:
            with st.spinner("Running Isolation Forest..."):
                outliers = an.detect_outliers(df)
            st.dataframe(outliers, use_container_width=True) if not outliers.empty else st.info("No significant outliers detected.")

        with tabs[5]:
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            if numeric_cols:
                val_col = st.selectbox("Value column", numeric_cols)
                trend = an.trend_detection(df, val_col)
                if not trend.empty:
                    time_col = trend.columns[0]
                    st.plotly_chart(ch.time_series(trend, time_col, val_col, title=f"{val_col} Trend"), use_container_width=True)
                    st.dataframe(trend, use_container_width=True)
                else:
                    st.info("No date/time column detected for trend analysis.")

        with tabs[6]:
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            if cat_cols and numeric_cols:
                cc = st.selectbox("Category column", cat_cols)
                vc = st.selectbox("Value column", numeric_cols)
                breakdown = an.category_breakdown(df, cc, vc)
                st.plotly_chart(ch.bar_chart(breakdown, cc, vc, title=f"{vc} by {cc}"), use_container_width=True)
                st.dataframe(breakdown, use_container_width=True)
            else:
                st.info("Need at least one categorical and one numeric column.")

        with tabs[7]:
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            if numeric_cols:
                target = st.selectbox("Target (numeric) column", numeric_cols)
                if st.button("Compute Feature Importance"):
                    with st.spinner("Training a quick Random Forest..."):
                        fi = an.feature_importance(df, target)
                    if not fi.empty:
                        st.plotly_chart(ch.bar_chart(fi, "feature", "importance", title="Feature Importance"),
                                         use_container_width=True)
                    else:
                        st.info("Could not compute feature importance for this target/data.")


# ---------------------------------------------------------------------------
# 🧠 AI Insights
# ---------------------------------------------------------------------------
elif page == "AI Insights":
    page_header("🧠 AI Insights", "Automatic business insights generated by the LLM.")
    if not require_data():
        pass
    else:
        df = active_dataframe()
        if st.button("✨ Generate Insights", type="primary"):
            with st.spinner("Analyzing your data..."):
                summary = an.build_text_summary(df)
                try:
                    insights = ai_engine.generate_insights(summary)
                    st.session_state["last_insights"] = insights
                except Exception as e:
                    st.error(str(e))
        if st.session_state.get("last_insights"):
            st.markdown(st.session_state["last_insights"])


# ---------------------------------------------------------------------------
# 📜 Query History
# ---------------------------------------------------------------------------
elif page == "Query History":
    page_header("📜 Query History", "Every query you've run, persisted across sessions.")
    history_df = hist.get_history(st.session_state["username"])
    if history_df.empty:
        st.info("No queries run yet.")
    else:
        st.dataframe(history_df, use_container_width=True)


# ---------------------------------------------------------------------------
# ⭐ Saved Queries
# ---------------------------------------------------------------------------
elif page == "Saved Queries":
    page_header("⭐ Saved Queries", "Favorited queries for quick reuse.")
    saved_df = hist.get_saved_queries(st.session_state["username"])
    if saved_df.empty:
        st.info("No saved queries yet. Save one from the SQL Executor page.")
    else:
        for _, row in saved_df.iterrows():
            with st.expander(f"⭐ {row['label']}  —  {row['created_at']}"):
                st.code(row["sql"], language="sql")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("▶ Load into SQL Executor", key=f"load_{row['id']}"):
                        st.session_state["last_sql"] = row["sql"]
                        st.session_state["active_page"] = "SQL Executor"
                        st.rerun()
                with c2:
                    if st.button("🗑 Delete", key=f"del_{row['id']}"):
                        hist.delete_saved_query(row["id"])
                        st.rerun()


# ---------------------------------------------------------------------------
# 📄 Reports
# ---------------------------------------------------------------------------
elif page == "Reports":
    page_header("📄 Reports", "Export a polished PDF report of the current dataset.")
    if not require_data():
        pass
    else:
        df = active_dataframe()
        title = st.text_input("Report title", f"{st.session_state.get('df_name') or 'Dataset'} — Analytics Report")
        include_insights = st.checkbox("Include AI insights (requires GROQ_API_KEY)", value=bool(GROQ_API_KEY))

        if st.button("📄 Generate PDF Report", type="primary"):
            with st.spinner("Building report..."):
                profile = an.basic_profile(df)
                stats = an.statistical_summary(df)
                insights_text = ""
                if include_insights:
                    try:
                        insights_text = ai_engine.generate_insights(an.build_text_summary(df))
                    except Exception as e:
                        st.warning(f"Skipped AI insights: {e}")
                pdf_bytes = rg.build_pdf_report(title, profile, stats, insights_text)
            st.success("Report ready.")
            st.download_button("⬇ Download PDF", pdf_bytes, "queymind_report.pdf", "application/pdf")


# ---------------------------------------------------------------------------
# ⚙ Settings
# ---------------------------------------------------------------------------
elif page == "Settings":
    page_header("⚙ Settings", "App preferences and API configuration.")
    st.markdown("##### AI Configuration")
    st.text_input("GROQ_API_KEY (set via .env or Streamlit secrets — not editable here for security)",
                  value="•" * 12 if GROQ_API_KEY else "", disabled=True)
    st.caption("To set your key: create a `.env` file with `GROQ_API_KEY=your_key_here`, "
               "or add it under `.streamlit/secrets.toml` when deploying to Streamlit Cloud.")

    st.markdown("##### Query Safety")
    st.write("Write statements (INSERT/UPDATE/DELETE/DDL) are blocked by default in the "
             "SQL Executor and can be enabled per-query with the 'Allow write statements' toggle.")

    st.markdown("##### Data Reset")
    if st.button("🗑 Clear loaded dataset / connection"):
        for k in ["df", "engine", "schema", "df_name", "cleaned_df", "chat_history"]:
            st.session_state[k] = None if k != "chat_history" else []
        st.success("Cleared.")


# ---------------------------------------------------------------------------
# 👤 Profile
# ---------------------------------------------------------------------------
elif page == "Profile":
    page_header("👤 Profile", "Your account details.")
    st.markdown(f"**Username:** {st.session_state.get('username')}")
    st.markdown(f"**Queries run this session:** {len(st.session_state.get('query_history', []))}")
    st.markdown(f"**Saved queries:** {len(hist.get_saved_queries(st.session_state['username']))}")
    if st.button("🚪 Logout", key="profile_logout"):
        logout()
        st.rerun()
