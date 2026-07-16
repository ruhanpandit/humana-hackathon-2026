import streamlit as st
from tools.business_impact import calculate_business_impact

def render_business_impact_dashboard():
    """
    Renders the Business Impact dashboard using Streamlit components.
    This can be called from a main Streamlit app.
    """
    st.header("📈 Business Impact Analysis")
    st.markdown("Comparing Traditional vs. AI-Powered Healthcare Workflows")
    
    data = calculate_business_impact()
    
    # KPI Cards
    st.subheader("Key Performance Indicators")
    cols = st.columns(len(data['kpis']))
    for i, kpi in enumerate(data['kpis']):
        with cols[i]:
            st.metric(
                label=kpi['label'],
                value=kpi['value'],
                delta=kpi['delta'],
                help=kpi['description']
            )
            
    st.divider()
    
    # Financial Impact
    st.subheader("Estimated Annual Impact")
    f1, f2, f3 = st.columns(3)
    financials = data['financials']
    f1.metric("Annual Financial Savings", f"${financials['annual_financial_savings']:,.2f}")
    f2.metric("Annual Agent Hours Reclaimed", f"{financials['annual_hours_saved']:,.0f} hrs")
    f3.metric("Operating Cost Reduction", f"{financials['cost_reduction_pct']}%")
    
    st.divider()
    
    # Workflow Comparison Chart
    st.subheader("Workflow Stage Breakdown (Seconds)")
    stages = data['workflow_comparison']['stages']
    
    # Prepare data for horizontal bar chart
    # Streamlit's native bar_chart is a bit limited for grouped bars, 
    # but we can use st.dataframe or st.bar_chart with prepared data.
    chart_labels = [s['stage'] for s in stages]
    trad_times = [s['traditional'] for s in stages]
    ai_times = [s['ai_assisted'] for s in stages]
    
    # For a horizontal bar chart in Streamlit, we often use Plotly or Altair,
    # but since we want to avoid extra dependencies if possible, we'll suggest using Altair.
    try:
        import pandas as pd
        import altair as alt
        
        df = pd.DataFrame({
            'Stage': chart_labels * 2,
            'Duration (s)': trad_times + ai_times,
            'Type': ['Traditional'] * len(chart_labels) + ['AI-Assisted'] * len(chart_labels)
        })
        
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y('Stage:N', sort=None),
            x='Duration (s):Q',
            color='Type:N',
            row='Type:N'
        ).properties(height=150, width=600)
        
        st.altair_chart(chart, use_container_width=True)
        
    except ImportError:
        # Fallback to simple bar charts if pandas/altair are missing
        st.write("Traditional Workflow Duration")
        st.bar_chart(dict(zip(chart_labels, trad_times)))
        st.write("AI-Assisted Workflow Duration")
        st.bar_chart(dict(zip(chart_labels, ai_times)))

    # Detail Table
    with st.expander("View Workflow Assumption Details"):
        st.table(stages)

if __name__ == "__main__":
    # Mocking st for local testing without streamlit installed
    class MockSt:
        def __getattr__(self, name):
            def mock_func(*args, **kwargs):
                print(f"ST.{name.upper()}: {args} {kwargs}")
            return mock_func
    st = MockSt()
    render_business_impact_dashboard()
