import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sqlite3
import sys
import os
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.bayesian_ab import BayesianABTest
from experiments.cuped import CUPEDAnalysis
from analytics.cohort_retention import compute_retention
from analytics.funnel_analysis import compute_funnel
from memo.decision_memo import generate_memo


DB_PATH = "data/events.db"


def ensure_database(db_path: str) -> None:
    """Create events.db from the workbook when the DB is missing."""
    if os.path.exists(db_path):
        return
    if not os.path.exists("data/online_retail_II.xlsx"):
        return
    subprocess.run([sys.executable, "data/loader.py"], check=False)


ensure_database(DB_PATH)


st.set_page_config(
    page_title="ExperimentOS",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root tokens ── */
:root {
  --bg:       #0F1117;
  --surface:  #1A1D27;
  --surface2: #22263A;
  --border:   #2E3250;
  --accent:   #6C63FF;
  --accent2:  #FF6B6B;
  --green:    #00D4AA;
  --amber:    #FFB347;
  --text:     #E8E9F0;
  --muted:    #8B8FA8;
  --font:     'DM Sans', sans-serif;
  --mono:     'DM Mono', monospace;
}

/* ── App background ── */
.stApp {
  background: var(--bg);
  font-family: var(--font);
  color: var(--text);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { font-family: var(--font) !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.2rem 1.4rem;
  transition: border-color 0.2s;
}
[data-testid="metric-container"]:hover { border-color: var(--accent); }
[data-testid="stMetricValue"] {
  font-size: 2rem !important;
  font-weight: 700 !important;
  font-family: var(--mono) !important;
  color: var(--text) !important;
}
[data-testid="stMetricLabel"] {
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: var(--muted) !important;
}
[data-testid="stMetricDelta"] { font-family: var(--mono) !important; }

/* ── Buttons ── */
.stButton > button {
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.4rem;
  font-family: var(--font);
  font-weight: 600;
  font-size: 0.9rem;
  letter-spacing: 0.02em;
  transition: all 0.2s;
  width: 100%;
}
.stButton > button:hover {
  background: #7C74FF;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(108, 99, 255, 0.4);
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
  font-family: var(--font);
  font-weight: 500;
  font-size: 0.85rem;
  color: var(--muted);
  border-radius: 6px 6px 0 0;
  padding: 0.6rem 1.2rem;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--accent);
  border-bottom: 2px solid var(--accent);
}

/* ── Info / success / warning boxes ── */
.stAlert {
  border-radius: 10px;
  border-left: 4px solid var(--accent);
  background: rgba(108, 99, 255, 0.08) !important;
  font-family: var(--font);
}

/* ── Code blocks ── */
.stCode { font-family: var(--mono) !important; font-size: 0.82rem; }

/* ── Selectbox, radio ── */
.stSelectbox > div, .stRadio > div {
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Page title component ── */
.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
  margin-bottom: 0.2rem;
}
.page-subtitle {
  font-size: 0.9rem;
  color: var(--muted);
  margin-bottom: 2rem;
}

/* ── Recommendation badge ── */
.badge {
  display: inline-block;
  padding: 0.3rem 0.9rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
  font-family: var(--mono);
}
.badge-green  { background: rgba(0,212,170,0.15); color: #00D4AA; border: 1px solid rgba(0,212,170,0.3); }
.badge-red    { background: rgba(255,107,107,0.15); color: #FF6B6B; border: 1px solid rgba(255,107,107,0.3); }
.badge-amber  { background: rgba(255,179,71,0.15); color: #FFB347; border: 1px solid rgba(255,179,71,0.3); }
.badge-purple { background: rgba(108,99,255,0.15); color: #6C63FF; border: 1px solid rgba(108,99,255,0.3); }

/* ── Stat row card ── */
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.2rem;
  text-align: center;
}
.stat-number {
  font-family: var(--mono);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--accent);
}
.stat-label {
  font-size: 0.72rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin-top: 0.2rem;
}

/* ── Memo output ── */
.memo-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 4px solid var(--green);
  border-radius: 10px;
  padding: 1.5rem;
  line-height: 1.8;
  font-size: 0.95rem;
  color: var(--text);
}

/* ── Plotly dark override ── */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""",
    unsafe_allow_html=True,
)


def load_data(db_path: str) -> dict:
    """Read sidebar and variant summary stats from SQLite."""
    if not os.path.exists(db_path):
        return {}

    conn = sqlite3.connect(db_path)
    variant_df = pd.read_sql(
        """
        SELECT
            variant,
            COUNT(DISTINCT user_id)                                   AS users,
            COUNT(DISTINCT CASE WHEN event_type='purchase'
                  THEN user_id END)                                   AS purchasers,
            ROUND(SUM(CASE WHEN event_type='purchase'
                  THEN revenue ELSE 0 END), 2)                        AS revenue,
            ROUND(COUNT(DISTINCT CASE WHEN event_type='purchase'
                  THEN user_id END) * 100.0 /
                  NULLIF(COUNT(DISTINCT user_id),0), 2)               AS conv_rate
        FROM events GROUP BY variant
        """,
        conn,
    )

    stats = pd.read_sql(
        """
        SELECT
            COUNT(DISTINCT user_id)  AS total_users,
            COUNT(DISTINCT CASE WHEN event_type='purchase' THEN user_id END) AS total_purchasers,
            MIN(DATE(timestamp))     AS start_date,
            MAX(DATE(timestamp))     AS end_date,
            COUNT(DISTINCT country)  AS countries
        FROM events
        """,
        conn,
    ).iloc[0].to_dict()

    conn.close()
    return {"variants": variant_df, "stats": stats}


def plotly_dark_layout() -> dict:
    """Return the dark Plotly layout used across dashboard charts."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,29,39,0.6)",
        font=dict(family="DM Sans, sans-serif", color="#E8E9F0", size=13),
        xaxis=dict(
            gridcolor="#2E3250",
            zerolinecolor="#2E3250",
            tickfont=dict(color="#8B8FA8"),
        ),
        yaxis=dict(
            gridcolor="#2E3250",
            zerolinecolor="#2E3250",
            tickfont=dict(color="#8B8FA8"),
        ),
        legend=dict(bgcolor="rgba(26,29,39,0.8)", bordercolor="#2E3250", borderwidth=1),
        margin=dict(l=40, r=30, t=50, b=40),
        hoverlabel=dict(
            bgcolor="#22263A",
            bordercolor="#2E3250",
            font=dict(family="DM Mono, monospace", color="#E8E9F0"),
        ),
    )


def badge_html(recommendation: str) -> str:
    """Return badge HTML for the current recommendation."""
    mapping = {
        "Ship B": ("badge-green", "✓ Ship B"),
        "Keep A": ("badge-red", "✗ Keep A"),
        "Run longer": ("badge-amber", "⏳ Run Longer"),
        "Inconclusive": ("badge-purple", "? Inconclusive"),
    }
    for key, (cls, label) in mapping.items():
        if key in recommendation:
            return f'<span class="badge {cls}">{label}</span>'
    return f'<span class="badge badge-purple">{recommendation}</span>'


def db_missing_warning():
    st.error(
        "**Database not found.** Run `python data/loader.py` first to load "
        "the Online Retail II dataset into SQLite.",
        icon="🗄️",
    )
    st.code("python data/loader.py", language="bash")
    st.stop()


def get_variant_row(variants: pd.DataFrame, variant: str) -> pd.Series:
    rows = variants[variants["variant"] == variant]
    if rows.empty:
        st.error(f"Variant {variant} was not found in the events database.")
        st.stop()
    return rows.iloc[0]


def sidebar_stat(label: str, value: str) -> None:
    st.sidebar.markdown(
        f"""
        <div style='background:#22263A;border:1px solid #2E3250;border-radius:8px;
                    padding:0.75rem 0.9rem;margin-bottom:0.55rem'>
          <div style='font-size:0.68rem;color:#8B8FA8;text-transform:uppercase;
                      letter-spacing:0.08em'>{label}</div>
          <div style='font-family:DM Mono,monospace;color:#E8E9F0;font-size:0.95rem;
                      margin-top:0.15rem'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.sidebar.markdown(
    """
<div style='padding: 0.5rem 0 1.5rem'>
  <div style='font-size:1.5rem;font-weight:700;color:#E8E9F0;letter-spacing:-0.02em'>
    🧪 ExperimentOS
  </div>
  <div style='font-size:0.75rem;color:#8B8FA8;margin-top:0.2rem;
              font-family:DM Mono,monospace;letter-spacing:0.05em'>
    BAYESIAN EXPERIMENTATION PLATFORM
  </div>
</div>
""",
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigation",
    options=[
        "📊  A/B Test Engine",
        "🔄  Cohort Retention",
        "🔽  Conversion Funnel",
        "📋  Metric Registry",
        "📝  Decision Memo",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()

if os.path.exists(DB_PATH):
    sidebar_data = load_data(DB_PATH)
    sidebar_stats = sidebar_data.get("stats", {})
    sidebar_stat("Total Users", f"{int(sidebar_stats.get('total_users', 0)):,}")
    sidebar_stat(
        "Date Range",
        f"{sidebar_stats.get('start_date', '—')} → {sidebar_stats.get('end_date', '—')}",
    )
    sidebar_stat("Countries", f"{int(sidebar_stats.get('countries', 0)):,}")

st.sidebar.divider()
st.sidebar.markdown(
    """
<div style='font-size:0.72rem;color:#8B8FA8;line-height:1.8'>
  Built by <b style='color:#6C63FF'>Yashwanth</b><br>
  Dataset: Online Retail II (UCI)<br>
  Stack: PyMC · dbt · Gemini · SQLite
</div>
""",
    unsafe_allow_html=True,
)


if "A/B Test" in page:
    st.markdown('<div class="page-title">A/B Test Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Bayesian Beta-Binomial model · Real Online Retail II data</div>',
        unsafe_allow_html=True,
    )

    if not os.path.exists(DB_PATH):
        db_missing_warning()

    data = load_data(DB_PATH)
    variants = data["variants"]
    a = get_variant_row(variants, "A")
    b = get_variant_row(variants, "B")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Variant A — Users", f"{int(a['users']):,}")
    col2.metric("Variant A — Conversion", f"{a['conv_rate']:.2f}%")
    col3.metric("Variant A — Revenue", f"£{a['revenue']:,.0f}")
    col4.metric("Variant B — Users", f"{int(b['users']):,}")
    col5.metric(
        "Variant B — Conversion",
        f"{b['conv_rate']:.2f}%",
        delta=f"{b['conv_rate'] - a['conv_rate']:+.2f}%",
    )
    col6.metric(
        "Variant B — Revenue",
        f"£{b['revenue']:,.0f}",
        delta=f"£{b['revenue'] - a['revenue']:+,.0f}",
    )

    st.divider()

    ab = BayesianABTest()
    with st.spinner("Running Bayesian analysis..."):
        results = ab.run_test(
            int(a["purchasers"]),
            int(a["users"]),
            int(b["purchasers"]),
            int(b["users"]),
        )

    r1, r2, r3, r4 = st.columns(4)
    prob = results["prob_treatment_better"]
    prob_color = "#00D4AA" if prob > 80 else "#FF6B6B" if prob < 20 else "#FFB347"

    r1.markdown(
        f"""
    <div class='stat-card'>
      <div class='stat-number' style='color:{prob_color}'>{prob:.1f}%</div>
      <div class='stat-label'>P(B &gt; A)</div>
    </div>""",
        unsafe_allow_html=True,
    )

    r2.markdown(
        f"""
    <div class='stat-card'>
      <div class='stat-number'>{results['expected_lift_pct']:+.2f}%</div>
      <div class='stat-label'>Expected Lift</div>
    </div>""",
        unsafe_allow_html=True,
    )

    r3.markdown(
        f"""
    <div class='stat-card'>
      <div class='stat-number' style='font-size:1.1rem'>
        [{results['ci_low']:+.1f}%, {results['ci_high']:+.1f}%]
      </div>
      <div class='stat-label'>95% Credible Interval</div>
    </div>""",
        unsafe_allow_html=True,
    )

    r4.markdown(
        f"""
    <div class='stat-card'>
      {badge_html(results['recommendation'])}
      <div class='stat-label' style='margin-top:0.6rem'>Recommendation</div>
    </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    fig = ab.plot_posteriors(results)
    fig.update_layout(**plotly_dark_layout())
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📉  CUPED Variance Reduction Analysis", expanded=False):
        with st.spinner("Computing CUPED adjustment..."):
            cuped = CUPEDAnalysis()
            cuped_results = cuped.run_analysis(DB_PATH)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Variance Reduction", f"{cuped_results['variance_reduction_pct']:.1f}%")
        c2.metric(
            "Sample Size Reduction",
            f"{cuped_results['sample_size_reduction_pct']:.1f}%",
        )
        c3.metric("Original Required N", f"{cuped_results['original_required_n']:,}")
        c4.metric(
            "CUPED Required N",
            f"{cuped_results['cuped_required_n']:,}",
            delta=f"{cuped_results['cuped_required_n'] - cuped_results['original_required_n']:,}",
        )

        fig_v = go.Figure()
        fig_v.add_trace(
            go.Bar(
                x=["Original Variance", "CUPED Variance"],
                y=[cuped_results["original_variance"], cuped_results["cuped_variance"]],
                marker_color=["#FF6B6B", "#00D4AA"],
                text=[
                    f"{cuped_results['original_variance']:.4f}",
                    f"{cuped_results['cuped_variance']:.4f}",
                ],
                textposition="outside",
                textfont=dict(family="DM Mono, monospace", color="#E8E9F0"),
            )
        )
        fig_v.update_layout(
            **plotly_dark_layout(),
            title="Variance Before vs After CUPED",
            height=280,
            showlegend=False,
        )
        st.plotly_chart(fig_v, use_container_width=True)

        st.info(
            f"**CUPED saved {cuped_results['days_saved']:.0f} experiment days.** "
            "By adjusting for pre-experiment user behaviour, we reduced variance "
            f"by {cuped_results['variance_reduction_pct']:.1f}%, meaning you need "
            f"{cuped_results['sample_size_reduction_pct']:.1f}% fewer users to "
            "detect the same effect.",
            icon="💡",
        )

elif "Cohort" in page:
    st.markdown('<div class="page-title">Cohort Retention</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Weekly retention by acquisition cohort · Online Retail II</div>',
        unsafe_allow_html=True,
    )

    if not os.path.exists(DB_PATH):
        db_missing_warning()

    with st.spinner("Computing cohort matrix..."):
        fig = compute_retention(DB_PATH)

    fig.update_layout(
        **plotly_dark_layout(),
        height=480,
        title=dict(text="Weekly Cohort Retention (%)", font=dict(size=16, color="#E8E9F0")),
    )
    fig.update_traces(
        textfont=dict(family="DM Mono, monospace", size=11),
        colorscale=[
            [0.0, "#1A1D27"],
            [0.3, "#2E3A6E"],
            [0.6, "#5B5BCE"],
            [1.0, "#6C63FF"],
        ],
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Key Insights")
    ki1, ki2, ki3 = st.columns(3)
    ki1.info(
        "**Week 1 retention** is your most critical metric — users who return in week 1 are 3x more likely to become long-term customers.",
        icon="📌",
    )
    ki2.info(
        "**Cohort comparison** shows whether your product is improving — later cohorts should retain better than earlier ones.",
        icon="📈",
    )
    ki3.info(
        "**Plateau point** — when the curve flattens, that is your loyal user base. Anything above this is your engagement floor.",
        icon="📊",
    )

elif "Funnel" in page:
    st.markdown('<div class="page-title">Conversion Funnel</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">View → Add to Cart → Purchase · by variant</div>',
        unsafe_allow_html=True,
    )

    if not os.path.exists(DB_PATH):
        db_missing_warning()

    tab_all, tab_a, tab_b, tab_compare = st.tabs(
        ["Overall", "Variant A", "Variant B", "A vs B Comparison"]
    )

    with tab_all:
        fig_all, stats_all = compute_funnel(DB_PATH)
        fig_all.update_layout(**plotly_dark_layout(), height=400)
        st.plotly_chart(fig_all, use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("View → Cart", f"{stats_all['view_to_cart_rate']:.1f}%")
        m2.metric("Cart → Purchase", f"{stats_all['cart_to_purchase_rate']:.1f}%")
        m3.metric("Overall Conversion", f"{stats_all['overall_conversion_rate']:.1f}%")

    with tab_a:
        fig_a, stats_a = compute_funnel(DB_PATH, variant="A")
        fig_a.update_layout(**plotly_dark_layout(), height=400)
        st.plotly_chart(fig_a, use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("View → Cart", f"{stats_a['view_to_cart_rate']:.1f}%")
        m2.metric("Cart → Purchase", f"{stats_a['cart_to_purchase_rate']:.1f}%")
        m3.metric("Overall Conversion", f"{stats_a['overall_conversion_rate']:.1f}%")

    with tab_b:
        fig_b, stats_b = compute_funnel(DB_PATH, variant="B")
        fig_b.update_layout(**plotly_dark_layout(), height=400)
        st.plotly_chart(fig_b, use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("View → Cart", f"{stats_b['view_to_cart_rate']:.1f}%")
        m2.metric("Cart → Purchase", f"{stats_b['cart_to_purchase_rate']:.1f}%")
        m3.metric("Overall Conversion", f"{stats_b['overall_conversion_rate']:.1f}%")

    with tab_compare:
        _, stats_a = compute_funnel(DB_PATH, variant="A")
        _, stats_b = compute_funnel(DB_PATH, variant="B")

        stages = ["View → Cart", "Cart → Purchase", "Overall"]
        rates_a = [
            stats_a["view_to_cart_rate"],
            stats_a["cart_to_purchase_rate"],
            stats_a["overall_conversion_rate"],
        ]
        rates_b = [
            stats_b["view_to_cart_rate"],
            stats_b["cart_to_purchase_rate"],
            stats_b["overall_conversion_rate"],
        ]

        fig_cmp = go.Figure()
        fig_cmp.add_trace(
            go.Bar(
                name="Control (A)",
                x=stages,
                y=rates_a,
                marker_color="#6C63FF",
                opacity=0.85,
                text=[f"{v:.1f}%" for v in rates_a],
                textposition="outside",
                textfont=dict(family="DM Mono, monospace"),
            )
        )
        fig_cmp.add_trace(
            go.Bar(
                name="Treatment (B)",
                x=stages,
                y=rates_b,
                marker_color="#00D4AA",
                opacity=0.85,
                text=[f"{v:.1f}%" for v in rates_b],
                textposition="outside",
                textfont=dict(family="DM Mono, monospace"),
            )
        )
        fig_cmp.update_layout(
            **plotly_dark_layout(),
            barmode="group",
            height=400,
            title="Variant A vs B — Stage-by-Stage Conversion Rates",
            yaxis_title="Conversion Rate (%)",
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

        deltas = {
            "Stage": stages,
            "Variant A": [f"{value:.2f}%" for value in rates_a],
            "Variant B": [f"{value:.2f}%" for value in rates_b],
            "Δ Lift": [f"{b_rate - a_rate:+.2f}%" for a_rate, b_rate in zip(rates_a, rates_b)],
        }
        st.dataframe(pd.DataFrame(deltas), use_container_width=True, hide_index=True)

elif "Metric" in page:
    st.markdown('<div class="page-title">Metric Registry</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Canonical metric definitions · Governed via GitHub Actions PR gate</div>',
        unsafe_allow_html=True,
    )

    st.warning(
        "**Governance active.** Any PR modifying `metric_definitions.yml` "
        "is automatically blocked by GitHub Actions until approved by the data team lead.",
        icon="🔒",
    )

    metrics = [
        {
            "name": "conversion_rate",
            "label": "Purchase Conversion Rate",
            "definition": "Purchasers ÷ Viewers",
            "type": "Ratio",
            "owner": "data_team",
            "tags": ["core", "revenue"],
            "modified": "2026-04-15",
        },
        {
            "name": "retention_rate_week1",
            "label": "Week 1 Retention Rate",
            "definition": "% of users active in week 1 after first purchase",
            "type": "Percentage",
            "owner": "data_team",
            "tags": ["retention", "engagement"],
            "modified": "2026-04-15",
        },
        {
            "name": "revenue_per_user",
            "label": "Revenue Per User",
            "definition": "Total Revenue ÷ Unique Users",
            "type": "Ratio",
            "owner": "data_team",
            "tags": ["core", "revenue"],
            "modified": "2026-04-15",
        },
    ]

    for metric in metrics:
        tags_html = "".join(
            f'<span style="background:rgba(0,212,170,0.1);color:#00D4AA;border:1px solid rgba(0,212,170,0.25);border-radius:4px;padding:0.15rem 0.5rem;font-size:0.7rem;font-family:DM Mono,monospace">{tag}</span>'
            for tag in metric["tags"]
        )
        with st.container():
            st.markdown(
                f"""
            <div style='background:#1A1D27;border:1px solid #2E3250;
                        border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem'>
              <div style='display:flex;justify-content:space-between;align-items:center'>
                <div>
                  <code style='font-family:DM Mono,monospace;color:#6C63FF;
                               font-size:0.9rem'>{metric['name']}</code>
                  <span style='color:#E8E9F0;font-weight:600;font-size:1rem;
                               margin-left:0.8rem'>{metric['label']}</span>
                </div>
                <span style='background:rgba(108,99,255,0.12);color:#6C63FF;
                             border:1px solid rgba(108,99,255,0.25);border-radius:6px;
                             padding:0.2rem 0.7rem;font-size:0.75rem;
                             font-family:DM Mono,monospace'>{metric['type']}</span>
              </div>
              <div style='color:#8B8FA8;font-size:0.87rem;margin-top:0.5rem'>
                {metric['definition']}
              </div>
              <div style='display:flex;gap:0.5rem;margin-top:0.7rem;flex-wrap:wrap'>
                {tags_html}
                <span style='color:#8B8FA8;font-size:0.72rem;margin-left:auto;
                             font-family:DM Mono,monospace'>
                  owner: {metric['owner']} · modified: {metric['modified']}
                </span>
              </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("#### Raw YAML Definition")
    try:
        with open("dbt_project/models/metrics/metric_definitions.yml", encoding="utf-8") as file:
            yaml_content = file.read()
        st.code(yaml_content, language="yaml")
    except FileNotFoundError:
        st.code("# Run dbt project setup first", language="yaml")

elif "Memo" in page:
    st.markdown(
        '<div class="page-title">Decision Memo Generator</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">Powered by Google Gemini 2.5 Flash Lite · Plain English for product teams</div>',
        unsafe_allow_html=True,
    )

    if not os.path.exists(DB_PATH):
        db_missing_warning()

    data = load_data(DB_PATH)
    variants = data["variants"]
    a = get_variant_row(variants, "A")
    b = get_variant_row(variants, "B")

    ab = BayesianABTest()
    results = ab.run_test(
        int(a["purchasers"]),
        int(a["users"]),
        int(b["purchasers"]),
        int(b["users"]),
    )

    st.markdown("#### Current Experiment Summary")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Control Rate", f"{results['control_rate']:.2%}")
    s2.metric(
        "Treatment Rate",
        f"{results['treatment_rate']:.2%}",
        delta=f"{results['expected_lift_pct']:+.1f}%",
    )
    s3.metric("P(B > A)", f"{results['prob_treatment_better']:.1f}%")
    s4.markdown(
        f"""
    <div style='padding:0.8rem 0'>
      {badge_html(results['recommendation'])}
    </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("✨  Generate Decision Memo", type="primary"):
        with st.spinner("Gemini is writing your memo..."):
            memo_input = {
                "prob_treatment_better": results["prob_treatment_better"],
                "expected_lift_pct": results["expected_lift_pct"],
                "control_rate": results["control_rate"],
                "treatment_rate": results["treatment_rate"],
                "recommendation": results["recommendation"],
                "control_n": int(a["users"]),
                "treatment_n": int(b["users"]),
                "ci_low": results["ci_low"],
                "ci_high": results["ci_high"],
            }
            memo_text = generate_memo(memo_input)

        st.success("Memo generated", icon="✅")
        st.markdown(
            f"""
        <div class="memo-box">
          {memo_text.replace(chr(10), '<br>')}
        </div>
        """,
            unsafe_allow_html=True,
        )

        col_dl, col_copy = st.columns([1, 3])
        col_dl.download_button(
            "⬇  Download Memo",
            memo_text,
            file_name="decision_memo.txt",
            mime="text/plain",
        )

        st.caption(
            "Generated by Google Gemini 2.5 Flash Lite · "
            "Based on real Online Retail II data · "
            "ExperimentOS v1.0"
        )
    else:
        st.info(
            "Click **Generate Decision Memo** to get a plain-English "
            "ship/kill recommendation written for your product team.",
            icon="📝",
        )
