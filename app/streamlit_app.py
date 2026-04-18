# app/streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DATA_PROCESSED, MODELS_DIR, DB_URL

st.set_page_config(page_title="Olist Delivery Analytics", page_icon="📦", layout="wide", initial_sidebar_state="expanded")

# Custom CSS (same as before – keep it)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #13162B; }
    .css-1d391kg { background-color: #1C2040; border-right: 1px solid #2d3360; }
    .kpi-card {
        background-color: #1C2040;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        border: 1px solid #2d3360;
        text-align: center;
        transition: all 0.2s;
    }
    .kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.4); border-color: #7C3AED; }
    .kpi-value { font-size: 2.2rem; font-weight: 700; color: #E4E6F0; line-height: 1.2; }
    .kpi-label { font-size: 0.85rem; color: #a0a4c0; letter-spacing: 0.5px; margin-top: 0.5rem; }
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #E4E6F0;
        border-left: 4px solid #7C3AED;
        padding-left: 0.75rem;
        margin: 1rem 0 0.25rem 0;
    }
    .section-caption {
        color: #a0a4c0;
        font-size: 0.8rem;
        margin-bottom: 1rem;
        margin-left: 0.75rem;
    }
    .stButton button {
        background-color: #7C3AED;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 500;
        width: 100%;
    }
    .stButton button:hover { background-color: #6d28d9; }
    .stSelectbox label { color: #E4E6F0 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return joblib.load(MODELS_DIR / "model.pkl")

@st.cache_data
def load_feature_data():
    df = pd.read_csv(DATA_PROCESSED / "feature_engineered_data.csv")
    df['is_late'] = df['is_late'].astype(int)
    return df

@st.cache_data
def load_sales_summary():
    engine = create_engine(DB_URL)
    return pd.read_sql("SELECT * FROM sales_summary ORDER BY month", engine)

@st.cache_data
def load_top_cities():
    engine = create_engine(DB_URL)
    return pd.read_sql("""
        SELECT customer_city, COUNT(*) as count
        FROM customer_summary
        GROUP BY customer_city
        ORDER BY count DESC
        LIMIT 10
    """, engine)

@st.cache_data
def load_rfm_data():
    engine = create_engine(DB_URL)
    df = pd.read_sql("""
        SELECT 
            c.customer_unique_id,
            MAX(o.order_purchase_timestamp) as last_order_date,
            COUNT(o.order_id) as frequency,
            SUM(p.payment_value) as monetary
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN payments p ON o.order_id = p.order_id
        GROUP BY c.customer_unique_id
    """, engine)
    today = pd.Timestamp.now()
    df['recency'] = (today - df['last_order_date']).dt.days
    df = df[df['frequency'] > 0].copy()
    return df

def reset_filters():
    st.session_state["cat_filter"] = "All"
    st.session_state["state_filter"] = "All"
    st.session_state["month_filter"] = "All"

def compute_rfm_segments(df):
    df['r_score'] = pd.qcut(df['recency'], q=4, labels=['4','3','2','1'])
    df['f_score'] = pd.qcut(df['frequency'].rank(method='first'), q=4, labels=['1','2','3','4'])
    df['m_score'] = pd.qcut(df['monetary'].rank(method='first'), q=4, labels=['1','2','3','4'])
    
    def rfm_segment(row):
        r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
        if r >= 3 and f >= 3 and m >= 3:
            return 'Champions'
        elif r >= 3 and f >= 2 and m >= 2:
            return 'Loyal Customers'
        elif r >= 2 and f >= 2 and m >= 2:
            return 'Potential Loyalists'
        elif r >= 3 and f == 1:
            return 'New Customers'
        elif r == 1 and f >= 2 and m >= 2:
            return 'At Risk'
        elif r == 1 and f == 1 and m == 1:
            return 'Lost'
        else:
            return 'Others'
    
    df['segment'] = df.apply(rfm_segment, axis=1)
    return df

def main():
    df = load_feature_data()
    model = load_model()
    df_sales = load_sales_summary()
    df_cities = load_top_cities()
    df_rfm_raw = load_rfm_data()
    df_rfm = compute_rfm_segments(df_rfm_raw)
    
    # Sidebar filters (top 5)
    cat_counts = df['main_category'].value_counts().head(5).index.tolist()
    state_cols = [c for c in df.columns if c.startswith("state_")]
    state_volumes = {c.replace("state_", ""): df[c].sum() for c in state_cols}
    top_states = sorted(state_volumes, key=state_volumes.get, reverse=True)[:5]
    months = sorted(df['purchase_month'].unique())
    
    with st.sidebar:
        st.markdown("### 📦 Olist Analytics")
        st.markdown("**Delivery Performance & Business Insights**")
        st.markdown("---")
        st.markdown("#### 🔍 Filters")
        st.selectbox("Product Category (Top 5)", ["All"] + cat_counts, index=0, key="cat_filter")
        st.selectbox("Customer State (Top 5)", ["All"] + top_states, index=0, key="state_filter")
        st.selectbox("Purchase Month", ["All"] + [str(m) for m in months], index=0, key="month_filter")
        st.markdown("---")
        st.button("🗑️ Clear All Filters", on_click=reset_filters)
        st.markdown("---")
        st.markdown("**Model version:** XGBoost v1.0")
        st.markdown("**Last updated:** 2025-01-15")
    
    # Apply filters to delivery data only
    filtered = df.copy()
    if st.session_state["cat_filter"] != "All":
        filtered = filtered[filtered['main_category'] == st.session_state["cat_filter"]]
    if st.session_state["state_filter"] != "All":
        state_col = f"state_{st.session_state['state_filter']}"
        if state_col in filtered.columns:
            filtered = filtered[filtered[state_col] == 1]
    if st.session_state["month_filter"] != "All":
        filtered = filtered[filtered['purchase_month'] == int(st.session_state["month_filter"])]
    
    # ---------- KPI Cards (global, not filtered) ----------
    total_orders = len(filtered)
    late_pct = filtered['is_late'].mean() * 100
    avg_items = filtered['total_items'].mean()
    avg_freight = filtered['total_freight_value'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{total_orders:,}</div><div class="kpi-label">TOTAL ORDERS (filtered)</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{late_pct:.1f}%</div><div class="kpi-label">LATE DELIVERY RATE (filtered)</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{avg_items:.1f}</div><div class="kpi-label">AVG ITEMS PER ORDER (filtered)</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">R$ {avg_freight:.2f}</div><div class="kpi-label">AVG FREIGHT (filtered)</div></div>""", unsafe_allow_html=True)
    
    # ==================== DELIVERY EDA (FILTERED) ====================
    st.markdown('<div class="section-header">📊 Delivery Performance Analysis (Filtered)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">These charts update based on your filters above.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        monthly_late = filtered.groupby('purchase_month')['is_late'].mean() * 100
        fig_ts = px.line(x=monthly_late.index, y=monthly_late.values, markers=True,
                         labels={'x': 'Month', 'y': 'Late Rate (%)'},
                         title='Late Delivery Rate by Month', template='plotly_dark')
        fig_ts.update_traces(line=dict(color='#7C3AED', width=2))
        fig_ts.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ts, use_container_width=True)
    with col2:
        cat_late = filtered.groupby('main_category')['is_late'].mean().sort_values(ascending=False).head(5) * 100
        fig_cat = px.bar(x=cat_late.values, y=cat_late.index, orientation='h',
                         labels={'x': 'Late Rate (%)', 'y': 'Category Code'},
                         text=cat_late.round(1).astype(str)+'%',
                         color=cat_late.values, color_continuous_scale='Reds',
                         template='plotly_dark')
        fig_cat.update_layout(height=350, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        fig_cat.update_traces(textposition='outside')
        st.plotly_chart(fig_cat, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        state_late = {}
        for col in state_cols:
            state = col.replace("state_", "")
            mask = filtered[col] == 1
            if mask.sum() > 0:
                rate = filtered[mask]['is_late'].mean() * 100
                state_late[state] = rate
        state_df = pd.DataFrame(list(state_late.items()), columns=['state', 'late_rate'])
        state_df = state_df.sort_values('late_rate', ascending=False).head(5)
        fig_state = px.bar(state_df, x='state', y='late_rate', color='late_rate',
                           labels={'late_rate': 'Late Rate (%)', 'state': 'State'},
                           title='Top 5 States with Highest Late Rate',
                           color_continuous_scale='Reds', template='plotly_dark')
        fig_state.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_state, use_container_width=True)
    with col2:
        numeric_cols = filtered.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in numeric_cols if not c.startswith("state_") and c != 'is_late']
        if len(numeric_cols) > 1:
            corr_with_target = filtered[numeric_cols + ['is_late']].corr()[['is_late']].drop('is_late').sort_values('is_late', ascending=False)
            fig_corr = px.bar(x=corr_with_target['is_late'], y=corr_with_target.index, orientation='h',
                              labels={'x': 'Correlation with Late Delivery', 'y': 'Feature'},
                              title='Feature Correlation with Late Delivery',
                              color=corr_with_target['is_late'], color_continuous_scale='RdBu_r',
                              template='plotly_dark')
            fig_corr.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Not enough numeric features for correlation.")
    
    # ==================== MODEL PERFORMANCE (FILTERED) ====================
    st.markdown('<div class="section-header">🤖 Model Performance (on filtered test set)</div>', unsafe_allow_html=True)
    target = 'is_late'
    X = filtered.drop(columns=[target])
    y = filtered[target]
    if len(X) < 100:
        st.warning("Not enough data after filters to evaluate model.")
    else:
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        
        col1, col2 = st.columns(2)
        with col1:
            z = [[tn, fp], [fn, tp]]
            fig_cm = px.imshow(z, text_auto=True, labels=dict(x="", y="", color="Count"),
                               x=['Pred On Time', 'Pred Late'], y=['Actual On Time', 'Actual Late'],
                               color_continuous_scale='Blues', template='plotly_dark')
            fig_cm.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_cm, use_container_width=True)
        with col2:
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f'ROC (AUC = {roc_auc:.3f})',
                                         line=dict(color='#7C3AED', width=2)))
            fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random',
                                         line=dict(dash='dash', color='gray')))
            fig_roc.update_layout(xaxis_title='False Positive Rate', yaxis_title='True Positive Rate',
                                  height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_roc, use_container_width=True)
        
        st.markdown('<div class="section-header">📈 Key Model Metrics (filtered)</div>', unsafe_allow_html=True)
        mc = st.columns(4)
        with mc[0]:
            st.metric("Recall (Late caught)", f"{tp/(tp+fn):.1%}" if (tp+fn)>0 else "N/A")
        with mc[1]:
            st.metric("Precision (Late)", f"{tp/(tp+fp):.1%}" if (tp+fp)>0 else "N/A")
        with mc[2]:
            st.metric("False Alarm Rate", f"{fp/(tn+fp):.1%}" if (tn+fp)>0 else "N/A")
        with mc[3]:
            st.metric("Overall Accuracy", f"{(tp+tn)/(tp+tn+fp+fn):.1%}")
        
        st.info(f"""
        **What this means for the filtered data:**  
        - Out of orders that were actually **on time**, the model incorrectly flagged **{fp/(tn+fp):.1%}** as late (false alarms).  
        - Out of orders that were actually **late**, the model caught **{tp/(tp+fn):.1%}** (recall).  
        - AUC = **{roc_auc:.3f}**.
        """)
    
    st.markdown("---")
    # ==================== BUSINESS INSIGHTS (GLOBAL) ====================
    st.markdown('<div class="section-header">📈 Business Performance (Global Metrics)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">These charts show overall business performance across all orders – they do not change with filters.</div>', unsafe_allow_html=True)

    # RFM segmentation
    segment_counts = df_rfm['segment'].value_counts().reset_index()
    segment_counts.columns = ['segment', 'count']
    avg_monetary = df_rfm.groupby('segment')['monetary'].mean().sort_values(ascending=False).reset_index()
    fig_rfm = make_subplots(rows=1, cols=2, specs=[[{'type':'pie'}, {'type':'bar'}]],
                            subplot_titles=('Customer Segments', 'Average Spend by Segment'))
    fig_rfm.add_trace(go.Pie(labels=segment_counts['segment'], values=segment_counts['count'],
                             hole=0.3, textinfo='percent+label', name='Segments'), row=1, col=1)
    fig_rfm.add_trace(go.Bar(x=avg_monetary['segment'], y=avg_monetary['monetary'],
                             marker_color=avg_monetary['monetary'], marker_colorscale='Viridis',
                             showlegend=False, name='Avg Spend'), row=1, col=2)
    fig_rfm.update_layout(height=500, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
    fig_rfm.update_yaxes(title_text='Avg Total Spend (R$)', row=1, col=2)
    st.plotly_chart(fig_rfm, use_container_width=True)    
    # Sales performance
    fig_sales = make_subplots(rows=2, cols=2,
                              subplot_titles=('Monthly Revenue (R$)', 'Monthly Orders',
                                              'Avg Order Payment (R$)', 'Monthly Items Sold'))
    fig_sales.add_trace(go.Scatter(x=df_sales['month'], y=df_sales['total_payment_revenue'],
                                   mode='lines+markers', name='Revenue', line=dict(color='#7C3AED')), row=1, col=1)
    fig_sales.add_trace(go.Scatter(x=df_sales['month'], y=df_sales['total_orders'],
                                   mode='lines+markers', name='Orders', line=dict(color='#FFA07A')), row=1, col=2)
    fig_sales.add_trace(go.Scatter(x=df_sales['month'], y=df_sales['avg_order_payment'],
                                   mode='lines+markers', name='Avg Payment', line=dict(color='#2ECC71')), row=2, col=1)
    fig_sales.add_trace(go.Scatter(x=df_sales['month'], y=df_sales['total_items_sold'],
                                   mode='lines+markers', name='Items Sold', line=dict(color='#E74C3C')), row=2, col=2)
    fig_sales.update_layout(height=600, template='plotly_dark', showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    fig_sales.update_xaxes(title_text='Month', tickangle=-45)
    fig_sales.update_yaxes(title_text='Revenue (R$)', row=1, col=1)
    fig_sales.update_yaxes(title_text='Orders', row=1, col=2)
    fig_sales.update_yaxes(title_text='Avg Payment (R$)', row=2, col=1)
    fig_sales.update_yaxes(title_text='Items Sold', row=2, col=2)
    st.plotly_chart(fig_sales, use_container_width=True)
    
    # Top 10 cities
    fig_cities = px.bar(df_cities, x='customer_city', y='count',
                        title='Top 10 Cities by Customer Count',
                        labels={'customer_city': 'City', 'count': 'Number of Customers'},
                        color='count', color_continuous_scale='Blues',
                        template='plotly_dark')
    fig_cities.update_layout(xaxis_tickangle=-45, height=400, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_cities, use_container_width=True)
    

        
    st.markdown("<center style='color:#a0a4c0; font-size:0.8rem'>Author: Younes Benali | Data source: Olist Brazilian E‑commerce | Built with Streamlit</center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()