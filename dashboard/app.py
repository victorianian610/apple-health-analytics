import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import anthropic
from dotenv import load_dotenv
import os

load_dotenv('/Users/victoria/Desktop/DE/DS/Project/apple_health_export/apple_health_analysis/.env')

# ── Page config ────────────────────────────────────
st.set_page_config(
    page_title="My Health Dashboard",
    page_icon="🏃",
    layout="wide"
)

# ── Load data ──────────────────────────────────────
@st.cache_data
def load_data():
    base = '/Users/victoria/Desktop/DE/DS/Project/apple_health_export/apple_health_analysis/data'
    master    = pd.read_csv(f'{base}/master_daily.csv', parse_dates=['date'])
    anomalies = pd.read_csv(f'{base}/anomaly_results.csv', parse_dates=['date'])
    yearly    = pd.read_csv(f'{base}/yearly_summary.csv')
    return master, anomalies, yearly

master, anomalies, yearly = load_data()

# ── Header ─────────────────────────────────────────
st.title("🏃 Personal Health Analytics Dashboard")
st.markdown("*9 years of Apple Health data — 2017 to 2026*")
st.divider()

# ── Top KPI cards ──────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Avg Daily Steps",    f"{master['steps'].mean():,.0f}",      "Goal: 10,000")
col2.metric("Days Hit 10k Steps", f"{(master['steps']>=10000).mean()*100:.1f}%", "of all days")
col3.metric("Avg Sleep",          f"{master['sleep_hrs'].mean():.1f} hrs", "Goal: 8hrs")
col4.metric("Avg Heart Rate",     f"{master['hr_avg'].mean():.1f} bpm",  "Healthy: 60-100")
col5.metric("Total Days Tracked", f"{len(master):,}",                    "days")

st.divider()

# ── Sidebar filters ────────────────────────────────
st.sidebar.header("🔧 Filters")
years = sorted(master['date'].dt.year.unique())
selected_years = st.sidebar.multiselect("Select Years", years, default=years)
filtered = master[master['date'].dt.year.isin(selected_years)]

# ── Tab layout ─────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Steps & Activity", 
    "😴 Sleep", 
    "❤️ Heart Rate",
    "🔗 Correlations",
    "🚨 Anomalies",
    "🤖 AI Health Agent"
])

# ────────────────────────────────────────────────────
# TAB 1: Steps
# ────────────────────────────────────────────────────
with tab1:
    st.subheader("Steps & Activity Over Time")
    
    # Rolling avg
    filtered = filtered.copy()
    filtered['steps_30d'] = filtered['steps'].rolling(30).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered['date'], y=filtered['steps'],
        mode='lines', name='Daily Steps',
        line=dict(color='steelblue', width=0.8),
        opacity=0.4
    ))
    fig.add_trace(go.Scatter(
        x=filtered['date'], y=filtered['steps_30d'],
        mode='lines', name='30-day Avg',
        line=dict(color='darkblue', width=2.5)
    ))
    fig.add_hline(y=10000, line_dash='dash', line_color='red',
                  annotation_text='10k Goal')
    fig.update_layout(height=400, xaxis_title='Date', yaxis_title='Steps')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        # By day of week
        dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        dow = filtered.groupby('weekday')['steps'].mean().reindex(dow_order).reset_index()
        fig2 = px.bar(dow, x='weekday', y='steps',
                      title='Avg Steps by Day of Week',
                      color='steps', color_continuous_scale='Blues')
        fig2.add_hline(y=10000, line_dash='dash', line_color='red')
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Yearly trend
        fig3 = px.bar(yearly, x='year', y='avg_steps',
                      title='Yearly Average Steps',
                      color='avg_steps', color_continuous_scale='Blues')
        fig3.add_hline(y=10000, line_dash='dash', line_color='red')
        st.plotly_chart(fig3, use_container_width=True)

# ────────────────────────────────────────────────────
# TAB 2: Sleep
# ────────────────────────────────────────────────────
with tab2:
    st.subheader("Sleep Analysis")
    sleep_clean = filtered[filtered['sleep_hrs'].between(1, 14)].copy()

    fig = px.scatter(sleep_clean, x='date', y='sleep_hrs',
                     opacity=0.4, color='sleep_hrs',
                     color_continuous_scale='Purples',
                     title='Sleep Duration Over Time')
    sleep_clean['sleep_30d'] = sleep_clean['sleep_hrs'].rolling(30).mean()
    fig.add_trace(go.Scatter(
        x=sleep_clean['date'], y=sleep_clean['sleep_30d'],
        mode='lines', name='30-day Avg',
        line=dict(color='darkviolet', width=2.5)
    ))
    fig.add_hline(y=8, line_dash='dash', line_color='red',
                  annotation_text='8hr Goal')
    fig.add_hline(y=7, line_dash='dash', line_color='orange',
                  annotation_text='7hr Min')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.histogram(sleep_clean, x='sleep_hrs', nbins=40,
                            title='Sleep Duration Distribution',
                            color_discrete_sequence=['purple'])
        fig2.add_vline(x=8, line_dash='dash', line_color='red')
        fig2.add_vline(x=sleep_clean['sleep_hrs'].mean(),
                       line_dash='dash', line_color='green')
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        dow_sleep = sleep_clean.groupby('weekday')['sleep_hrs'].mean().reindex(dow_order).reset_index()
        fig3 = px.bar(dow_sleep, x='weekday', y='sleep_hrs',
                      title='Avg Sleep by Day of Week',
                      color='sleep_hrs', color_continuous_scale='Purples')
        fig3.add_hline(y=8, line_dash='dash', line_color='red')
        st.plotly_chart(fig3, use_container_width=True)

# ────────────────────────────────────────────────────
# TAB 3: Heart Rate
# ────────────────────────────────────────────────────
with tab3:
    st.subheader("Heart Rate Analysis")
    hr_clean = filtered[filtered['hr_avg'].between(40, 120)].copy()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hr_clean['date'], y=hr_clean['hr_avg'],
        mode='markers', name='Daily HR',
        marker=dict(color='crimson', size=4, opacity=0.4)
    ))
    hr_clean['hr_30d'] = hr_clean['hr_avg'].rolling(30).mean()
    fig.add_trace(go.Scatter(
        x=hr_clean['date'], y=hr_clean['hr_30d'],
        mode='lines', name='30-day Avg',
        line=dict(color='darkred', width=2.5)
    ))
    fig.add_hline(y=100, line_dash='dash', line_color='red',
                  annotation_text='High (100)')
    fig.add_hline(y=60, line_dash='dash', line_color='green',
                  annotation_text='Athletic (60)')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.histogram(hr_clean, x='hr_avg', nbins=40,
                            title='Heart Rate Distribution',
                            color_discrete_sequence=['crimson'])
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = px.scatter(hr_clean, x='steps', y='hr_avg',
                  title='Heart Rate vs Daily Steps',
                  opacity=0.4, color='hr_avg',
                  color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig3, use_container_width=True)

# ────────────────────────────────────────────────────
# TAB 4: Correlations
# ────────────────────────────────────────────────────
with tab4:
    st.subheader("Health Metrics Correlations")

    col1, col2 = st.columns(2)
    with col1:
        corr_cols = ['steps', 'distance_km', 'calories', 'hr_avg', 'sleep_hrs']
        corr = filtered[corr_cols].corr().round(2)
        fig = px.imshow(corr, text_auto=True, aspect='auto',
                        color_continuous_scale='RdYlGn',
                        title='Correlation Heatmap', zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        valid = filtered[['sleep_hrs', 'steps']].dropna().copy()
        valid['next_day_steps'] = valid['steps'].shift(-1)
        valid = valid.dropna()
        corr_val = valid['sleep_hrs'].corr(valid['next_day_steps'])
        fig2 = px.scatter(valid, x='sleep_hrs', y='next_day_steps',
                  opacity=0.3,
                  title=f"Sleep → Next Day Steps (r={corr_val:.3f})")
        st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────────────────────────────
# TAB 5: Anomalies
# ────────────────────────────────────────────────────
with tab5:
    st.subheader("🚨 Anomaly Detection (Isolation Forest)")

    anom_filtered = anomalies[anomalies['date'].dt.year.isin(selected_years)]
    normal  = anom_filtered[~anom_filtered['is_anomaly']]
    anom    = anom_filtered[anom_filtered['is_anomaly']]

    st.info(f"Detected **{len(anom)}** anomalous days out of {len(anom_filtered)} total ({len(anom)/len(anom_filtered)*100:.1f}%)")

    for metric, label, color in zip(
        ['steps', 'hr_avg', 'sleep_hrs'],
        ['Daily Steps', 'Avg Heart Rate (BPM)', 'Sleep (hrs)'],
        ['steelblue', 'crimson', 'purple']
    ):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=normal['date'], y=normal[metric],
            mode='markers', name='Normal',
            marker=dict(color=color, size=4, opacity=0.3)
        ))
        fig.add_trace(go.Scatter(
            x=anom['date'], y=anom[metric],
            mode='markers', name='Anomaly',
            marker=dict(color='red', size=10,
                       symbol='x', line=dict(width=2))
        ))
        fig.update_layout(height=250, title=label,
                         xaxis_title='Date', yaxis_title=label)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Most Anomalous Days")
    top = anom_filtered[anom_filtered['is_anomaly']].nsmallest(10, 'anomaly_score')
    st.dataframe(top[['date', 'steps', 'hr_avg', 'sleep_hrs', 'anomaly_score']].round(2),
                 use_container_width=True)
    

# ────────────────────────────────────────────────────
# TAB 6: AI Health Agent
# ────────────────────────────────────────────────────
with tab6:
    st.subheader("🤖 Personal AI Health Agent")
    st.markdown("*Ask me anything about your health, training plans, or nutrition!*")

    # ── Build personal health context ──────────────
    recent = master.tail(30)
    avg_steps_30d   = recent['steps'].mean()
    avg_sleep_30d   = recent['sleep_hrs'].mean()
    avg_hr_30d      = recent['hr_avg'].mean()
    best_steps_ever = master['steps'].max()
    best_year       = master.loc[master['steps'].idxmax(), 'year']

    health_context = f"""
    You are a personal AI health coach. Here is the user's real Apple Health data:
    
    OVERALL STATS (9 years of data, 2017-2026):
    - Average daily steps: {master['steps'].mean():,.0f}
    - Days hitting 10k steps: {(master['steps']>=10000).mean()*100:.1f}%
    - Average sleep: {master['sleep_hrs'].mean():.1f} hrs
    - Average heart rate: {master['hr_avg'].mean():.1f} bpm
    - Best ever steps in a day: {best_steps_ever:,.0f}
    
    LAST 30 DAYS:
    - Average daily steps: {avg_steps_30d:,.0f}
    - Average sleep: {avg_sleep_30d:.1f} hrs
    - Average heart rate: {avg_hr_30d:.1f} bpm
    
    HEALTH INSIGHTS:
    - Peak activity year was 2023 (avg 12,223 steps/day)
    - Sleep has improved over the years from ~5.5hrs to ~8hrs
    - More active on weekdays than weekends
    - Sleep quality positively correlates with next day activity (r=0.29)
    
    Based on this data, give personalized, specific advice. 
    Always reference their actual numbers when relevant.
    Be encouraging but honest. Keep responses concise and actionable.
    """

    # ── Chat interface ──────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Suggested questions
    if len(st.session_state.messages) == 0:
        st.markdown("**💡 Try asking:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 How was my health this week?"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "How was my health this week based on my data?"
                })
                st.rerun()
        with col2:
            if st.button("🏃 Give me a 5-day training plan"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Give me a personalized 5-day training plan based on my fitness level"
                })
                st.rerun()
        with col3:
            if st.button("😴 How can I improve my sleep?"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Based on my sleep data, what can I do to improve my sleep quality?"
                })
                st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask your health agent anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    system=health_context,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )
                
                reply = response.content[0].text
                st.markdown(reply)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })

    # Clear chat button
    if len(st.session_state.messages) > 0:
        if st.button("🗑️ Clear chat"):
            st.session_state.messages = []
            st.rerun()