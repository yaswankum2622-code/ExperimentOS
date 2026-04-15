import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sqlite3
import os
import sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.bayesian_ab import BayesianABTest
from experiments.cuped import CUPEDAnalysis
from analytics.cohort_retention import compute_retention
from analytics.funnel_analysis import compute_funnel
from memo.decision_memo import generate_memo


DB_PATH = "data/events.db"


def ensure_database() -> None:
    if os.path.exists(DB_PATH):
        return
    if not os.path.exists("data/online_retail_II.xlsx"):
        return
    subprocess.run([sys.executable, "data/loader.py"], check=False)


ensure_database()


st.set_page_config(
    page_title="ExperimentOS",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #F7F8FA;
}

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1400px !important;
}

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #EBEBEB !important;
}

[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 0.5px solid #E8E8E8;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    transition: box-shadow 0.2s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: #1a1a18 !important;
    letter-spacing: -0.02em !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #888888 !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}

.stButton > button {
    background: #534AB7 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #443DA0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(83,74,183,0.3) !important;
}

[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    color: #888888 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #534AB7 !important;
    border-bottom: 2px solid #534AB7 !important;
}

[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 0.5px solid #E8E8E8 !important;
    border-radius: 10px !important;
}

[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}

[data-testid="stDataFrame"] {
    border-radius: 8px !important;
    overflow: hidden !important;
}

hr {
    border-color: #EBEBEB !important;
}

.page-title {
    font-size: 1.7rem;
    font-weight: 700;
    color: #1a1a18;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}
.page-subtitle {
    font-size: 0.82rem;
    color: #888888;
    font-weight: 400;
    margin-bottom: 1.5rem;
}

.result-card {
    background: #FFFFFF;
    border: 0.5px solid #E8E8E8;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.result-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.result-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #888888;
}

.rc-purple { border-top: 3px solid #534AB7 !important; }
.rc-teal   { border-top: 3px solid #1D9E75 !important; }
.rc-blue   { border-top: 3px solid #185FA5 !important; }
.rc-amber  { border-top: 3px solid #BA7517 !important; }

.rn-purple { color: #534AB7; }
.rn-teal   { color: #0F6E56; }
.rn-blue   { color: #185FA5; }
.rn-amber  { color: #854F0B; }
.rn-red    { color: #791F1F; }

.badge {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.badge-green  { background:#E1F5EE; color:#085041; border:0.5px solid #9FE1CB; }
.badge-red    { background:#FCEBEB; color:#791F1F; border:0.5px solid #F09595; }
.badge-amber  { background:#FAEEDA; color:#633806; border:0.5px solid #FAC775; }
.badge-purple { background:#EEEDFE; color:#26215C; border:0.5px solid #AFA9EC; }

.memo-box {
    background: #FFFFFF;
    border: 0.5px solid #E8E8E8;
    border-left: 4px solid #1D9E75;
    border-radius: 10px;
    padding: 1.5rem 1.6rem;
    line-height: 1.8;
    font-size: 0.93rem;
    color: #1a1a18;
}

.metric-card {
    background: #FFFFFF;
    border: 0.5px solid #E8E8E8;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.15s;
}
.metric-card:hover { border-color: #534AB7; }
</style>
""",
    unsafe_allow_html=True,
)


CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    font=dict(
        family="Inter, sans-serif",
        color="#1a1a18",
        size=12,
    ),
    xaxis=dict(
        gridcolor="#F0F0F0",
        linecolor="#E8E8E8",
        tickcolor="#888888",
        tickfont=dict(color="#888888", size=11),
    ),
    yaxis=dict(
        gridcolor="#F0F0F0",
        linecolor="#E8E8E8",
        tickcolor="#888888",
        tickfont=dict(color="#888888", size=11),
    ),
    legend=dict(
        bgcolor="#FFFFFF",
        bordercolor="#E8E8E8",
        borderwidth=1,
        font=dict(size=12, color="#1a1a18"),
    ),
    margin=dict(l=40, r=30, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#1a1a18",
        bordercolor="#1a1a18",
        font=dict(
            family="JetBrains Mono, monospace",
            color="#FFFFFF",
            size=11,
        ),
    ),
)


def db_check():
    if not os.path.exists(DB_PATH):
        st.error(
            "Database not found. Run `python data/loader.py` first.",
            icon="🗄️",
        )
        st.code("python data/loader.py", language="bash")
        st.stop()


def load_variant_stats() -> tuple:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """
        SELECT
            variant,
            COUNT(DISTINCT user_id)  AS users,
            COUNT(DISTINCT CASE WHEN event_type='purchase'
                  THEN user_id END)  AS purchasers,
            ROUND(SUM(CASE WHEN event_type='purchase'
                  THEN revenue ELSE 0 END), 2) AS revenue,
            ROUND(COUNT(DISTINCT CASE WHEN event_type='purchase'
                  THEN user_id END) * 100.0 /
                  NULLIF(COUNT(DISTINCT user_id), 0), 2) AS conv_rate
        FROM events GROUP BY variant
        ORDER BY variant
        """,
        conn,
    )
    conn.close()
    a = df[df.variant == "A"].iloc[0]
    b = df[df.variant == "B"].iloc[0]
    return a, b


def badge_html(rec: str) -> str:
    if "Ship" in rec:
        cls, txt = "badge-green", f"✓  {rec}"
    elif "Keep A" in rec:
        cls, txt = "badge-red", f"✗  {rec}"
    elif "Longer" in rec or "longer" in rec:
        cls, txt = "badge-amber", f"⏳  {rec}"
    else:
        cls, txt = "badge-purple", f"?  {rec}"
    return f'<span class="badge {cls}">{txt}</span>'


def section_header(title: str, subtitle: str):
    st.markdown(
        f'<div class="page-title">{title}</div>'
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        """
        <div style='padding:0.2rem 0 1.2rem'>
          <div style='font-size:1.3rem;margin-bottom:6px'>🧪</div>
          <div style='font-size:1.1rem;font-weight:700;color:#1a1a18;
                      letter-spacing:-0.02em'>ExperimentOS</div>
          <div style='font-size:0.7rem;color:#888;text-transform:uppercase;
                      letter-spacing:0.07em;margin-top:2px'>
            Experimentation Platform
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        [
            "📊  A/B Test Engine",
            "🔄  Cohort Retention",
            "🔽  Conversion Funnel",
            "📋  Metric Registry",
            "📝  Decision Memo",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        stats = pd.read_sql(
            """
            SELECT
                COUNT(DISTINCT user_id)      AS users,
                MIN(DATE(timestamp))         AS start_date,
                MAX(DATE(timestamp))         AS end_date,
                COUNT(DISTINCT country)      AS countries
            FROM events
            """,
            conn,
        ).iloc[0]
        conn.close()

        for label, value in [
            ("Total Users", f"{int(stats.users):,}"),
            ("Date Range", f"{stats.start_date} → {stats.end_date}"),
            ("Countries", str(int(stats.countries))),
        ]:
            st.markdown(
                f"""
                <div style='background:#F7F8FA;border-radius:8px;
                            padding:8px 12px;margin-bottom:8px'>
                  <div style='font-size:0.65rem;font-weight:600;
                              text-transform:uppercase;letter-spacing:.07em;
                              color:#888;margin-bottom:3px'>{label}</div>
                  <div style='font-size:0.88rem;font-weight:600;
                              color:#1a1a18;font-family:JetBrains Mono,monospace'>
                    {value}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown(
        """
        <div style='font-size:0.7rem;color:#aaa;line-height:1.8'>
          Built by <b style='color:#534AB7'>Yashwanth</b><br>
          UCI Online Retail II Dataset<br>
          PyMC · dbt · Gemini · SQLite
        </div>
        """,
        unsafe_allow_html=True,
    )


if "A/B" in page:
    db_check()
    section_header(
        "A/B Test Engine",
        "Bayesian Beta-Binomial model · UCI Online Retail II · Real data",
    )

    a, b = load_variant_stats()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("A — Users", f"{int(a.users):,}")
    c2.metric("A — Conversion", f"{a.conv_rate:.1f}%")
    c3.metric("A — Revenue", f"£{a.revenue / 1e6:.2f}M")
    c4.metric("B — Users", f"{int(b.users):,}")
    c5.metric(
        "B — Conversion",
        f"{b.conv_rate:.1f}%",
        delta=f"{b.conv_rate - a.conv_rate:+.1f}pp",
    )
    c6.metric(
        "B — Revenue",
        f"£{b.revenue / 1e6:.2f}M",
        delta=f"£{(b.revenue - a.revenue) / 1e3:+.0f}K",
    )

    st.divider()

    ab = BayesianABTest()
    with st.spinner("Running Bayesian analysis..."):
        results = ab.run_test(
            int(a.purchasers),
            int(a.users),
            int(b.purchasers),
            int(b.users),
        )

    r1, r2, r3, r4 = st.columns(4)

    prob = results["prob_treatment_better"]
    r1.markdown(
        f"""
        <div class="result-card rc-purple">
          <div class="result-number rn-purple">{prob:.1f}%</div>
          <div class="result-label">P(B &gt; A)</div>
        </div>""",
        unsafe_allow_html=True,
    )

    lift_sign = "rn-teal" if results["expected_lift_pct"] > 0 else "rn-red"
    r2.markdown(
        f"""
        <div class="result-card rc-teal">
          <div class="result-number {lift_sign}">{results['expected_lift_pct']:+.2f}pp</div>
          <div class="result-label">Expected Lift</div>
        </div>""",
        unsafe_allow_html=True,
    )

    r3.markdown(
        f"""
        <div class="result-card rc-blue">
          <div class="result-number rn-blue" style="font-size:1.1rem">
            [{results['ci_low']:+.1f}%, {results['ci_high']:+.1f}%]
          </div>
          <div class="result-label">95% Credible Interval</div>
        </div>""",
        unsafe_allow_html=True,
    )

    r4.markdown(
        f"""
        <div class="result-card rc-amber" style="padding-top:1.4rem">
          {badge_html(results['recommendation'])}
          <div class="result-label" style="margin-top:0.6rem">Recommendation</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    fig = ab.plot_posteriors(results)
    fig.update_layout(**CHART_THEME)
    fig.update_layout(height=360)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📉  CUPED Variance Reduction Analysis"):
        with st.spinner("Computing..."):
            cuped_r = CUPEDAnalysis().run_analysis(DB_PATH)

        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric(
            "Variance Reduction",
            f"{cuped_r['variance_reduction_pct']:.1f}%",
        )
        cc2.metric(
            "Sample Size Saved",
            f"{cuped_r['sample_size_reduction_pct']:.1f}%",
        )
        cc3.metric("Original N", f"{cuped_r['original_required_n']:,}")
        cc4.metric(
            "CUPED N",
            f"{cuped_r['cuped_required_n']:,}",
            delta=f"{cuped_r['sample_size_reduction_pct']:.0f}% fewer",
        )

        fig_v = go.Figure()
        fig_v.add_trace(
            go.Bar(
                x=["Original variance", "CUPED variance"],
                y=[cuped_r["original_variance"], cuped_r["cuped_variance"]],
                marker_color=["#F09595", "#9FE1CB"],
                marker_line=dict(color=["#E24B4A", "#1D9E75"], width=1.5),
                text=[
                    f"{cuped_r['original_variance']:.4f}",
                    f"{cuped_r['cuped_variance']:.4f}",
                ],
                textposition="outside",
                textfont=dict(
                    family="JetBrains Mono",
                    size=11,
                    color="#1a1a18",
                ),
                width=0.45,
            )
        )
        fig_v.update_layout(
            **CHART_THEME,
            title="Variance before vs after CUPED",
            height=260,
            showlegend=False,
        )
        st.plotly_chart(fig_v, use_container_width=True)

        st.info(
            f"CUPED reduced required sample size by "
            f"**{cuped_r['sample_size_reduction_pct']:.0f}%** "
            f"({cuped_r['original_required_n']:,} → "
            f"{cuped_r['cuped_required_n']:,} users). "
            f"At 300 new users per day, that is "
            f"**{cuped_r['days_saved']:.0f} fewer days** needed.",
            icon="💡",
        )


elif "Cohort" in page:
    db_check()
    section_header(
        "Cohort Retention",
        "Weekly retention by acquisition cohort · Online Retail II",
    )

    with st.spinner("Computing cohort matrix..."):
        fig = compute_retention(DB_PATH)

    fig.update_layout(**CHART_THEME, height=500)
    fig.update_layout(
        title=dict(
            text="Weekly cohort retention (%)",
            font=dict(size=15, color="#1a1a18", family="Inter"),
        )
    )
    fig.update_traces(
        colorscale=[
            [0.0, "#F7F8FA"],
            [0.25, "#EEEDFE"],
            [0.6, "#7F77DD"],
            [1.0, "#26215C"],
        ],
        textfont=dict(family="JetBrains Mono", size=10, color="#1a1a18"),
    )
    st.plotly_chart(fig, use_container_width=True)

    k1, k2, k3 = st.columns(3)
    k1.info(
        "**Week 1 retention** is your most critical metric. Users "
        "who return in week 1 are 3× more likely to become "
        "long-term customers.",
        icon="📌",
    )
    k2.info(
        "**Cohort trend** shows whether product quality is improving "
        "— later cohorts should retain better.",
        icon="📈",
    )
    k3.info(
        "**Plateau point** — where the curve flattens is your "
        "loyal user floor.",
        icon="📊",
    )


elif "Funnel" in page:
    db_check()
    section_header(
        "Conversion Funnel",
        "View → Add to Cart → Purchase · by variant",
    )

    tab_all, tab_a, tab_b, tab_cmp = st.tabs(
        ["Overall", "Variant A", "Variant B", "A vs B"]
    )

    FUNNEL_COLORS = {
        "all": ["#7F77DD", "#534AB7", "#26215C"],
        "A": ["#85B7EB", "#378ADD", "#0C447C"],
        "B": ["#9FE1CB", "#1D9E75", "#085041"],
    }

    def show_funnel_tab(variant=None, key="all"):
        fig, stats = compute_funnel(DB_PATH, variant=variant)
        fig.update_layout(**CHART_THEME, height=380)
        fig.update_traces(
            marker_color=FUNNEL_COLORS[key],
            textfont=dict(family="JetBrains Mono", size=12),
        )
        st.plotly_chart(fig, use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("View → Cart", f"{stats['view_to_cart_rate']:.1f}%")
        m2.metric("Cart → Purchase", f"{stats['cart_to_purchase_rate']:.1f}%")
        m3.metric("Overall Conversion", f"{stats['overall_conversion_rate']:.1f}%")
        return stats

    with tab_all:
        show_funnel_tab(key="all")
    with tab_a:
        show_funnel_tab(variant="A", key="A")
    with tab_b:
        show_funnel_tab(variant="B", key="B")

    with tab_cmp:
        _, sa = compute_funnel(DB_PATH, variant="A")
        _, sb = compute_funnel(DB_PATH, variant="B")

        stages = ["View → Cart", "Cart → Purchase", "Overall"]
        rates_a = [
            sa["view_to_cart_rate"],
            sa["cart_to_purchase_rate"],
            sa["overall_conversion_rate"],
        ]
        rates_b = [
            sb["view_to_cart_rate"],
            sb["cart_to_purchase_rate"],
            sb["overall_conversion_rate"],
        ]

        fig_c = go.Figure()
        fig_c.add_trace(
            go.Bar(
                name="Control A",
                x=stages,
                y=rates_a,
                marker_color="#7F77DD",
                opacity=0.9,
                text=[f"{v:.1f}%" for v in rates_a],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=11),
            )
        )
        fig_c.add_trace(
            go.Bar(
                name="Treatment B",
                x=stages,
                y=rates_b,
                marker_color="#1D9E75",
                opacity=0.9,
                text=[f"{v:.1f}%" for v in rates_b],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=11),
            )
        )
        fig_c.update_layout(
            **CHART_THEME,
            barmode="group",
            height=400,
            title="Variant A vs B — conversion rate by stage",
            yaxis_title="Conversion rate (%)",
        )
        st.plotly_chart(fig_c, use_container_width=True)

        delta_df = pd.DataFrame(
            {
                "Stage": stages,
                "Variant A": [f"{v:.2f}%" for v in rates_a],
                "Variant B": [f"{v:.2f}%" for v in rates_b],
                "Δ Lift": [
                    f"{b_rate - a_rate:+.2f}%"
                    for a_rate, b_rate in zip(rates_a, rates_b)
                ],
            }
        )
        st.dataframe(delta_df, use_container_width=True, hide_index=True)


elif "Metric" in page:
    section_header(
        "Metric Registry",
        "Canonical metric definitions · Governed via GitHub Actions PR gate",
    )

    st.warning(
        "**Governance active.** Any PR modifying `metric_definitions.yml` "
        "is automatically blocked by GitHub Actions until approved.",
        icon="🔒",
    )

    metrics = [
        (
            "conversion_rate",
            "Purchase Conversion Rate",
            "Viewers who complete a purchase",
            "Ratio",
            ["core", "revenue", "primary"],
            "#534AB7",
        ),
        (
            "add_to_cart_rate",
            "Add-to-Cart Rate",
            "Viewers who add at least one item to cart",
            "Ratio",
            ["funnel", "engagement"],
            "#185FA5",
        ),
        (
            "retention_rate_week1",
            "Week 1 Retention Rate",
            "Users active in week 1 after acquisition",
            "Percentage",
            ["retention", "ltv"],
            "#1D9E75",
        ),
        (
            "revenue_per_user",
            "Revenue Per User",
            "Total net revenue divided by unique users",
            "Ratio",
            ["core", "revenue", "guardrail"],
            "#BA7517",
        ),
        (
            "cart_abandonment_rate",
            "Cart Abandonment Rate",
            "Cart adders who did not complete purchase",
            "Ratio",
            ["funnel", "diagnostic"],
            "#993556",
        ),
    ]

    for name, label, desc, typ, tags, color in metrics:
        tag_pills = "".join(
            [
                f'<span style="background:#F0F0F8;color:#534AB7;'
                f'border:0.5px solid #C5C0F0;border-radius:4px;'
                f'padding:2px 8px;font-size:0.68rem;font-weight:600;'
                f'font-family:JetBrains Mono,monospace;margin-right:4px">'
                f"{tag}</span>"
                for tag in tags
            ]
        )
        st.markdown(
            f"""
            <div class="metric-card">
              <div style="display:flex;justify-content:space-between;
                          align-items:flex-start">
                <div>
                  <code style="font-family:JetBrains Mono,monospace;
                               color:{color};font-size:0.85rem;
                               font-weight:500">{name}</code>
                  <span style="font-weight:600;font-size:0.95rem;
                               color:#1a1a18;margin-left:10px">{label}</span>
                </div>
                <span style="background:#F7F8FA;color:#534AB7;
                             border:0.5px solid #C5C0F0;border-radius:6px;
                             padding:3px 10px;font-size:0.72rem;font-weight:600;
                             font-family:JetBrains Mono,monospace;
                             white-space:nowrap">{typ}</span>
              </div>
              <div style="color:#666;font-size:0.83rem;margin:6px 0 8px">
                {desc}
              </div>
              <div style="display:flex;justify-content:space-between;
                          align-items:center">
                <div>{tag_pills}</div>
                <span style="font-size:0.68rem;color:#aaa;
                             font-family:JetBrains Mono,monospace">
                  owner: data_team · modified: 2026-04-15
                </span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Raw YAML")
    try:
        with open(
            "dbt_project/models/metrics/metric_definitions.yml",
            encoding="utf-8",
        ) as file:
            yaml_content = file.read()
        st.code(yaml_content, language="yaml")
    except FileNotFoundError:
        st.info("dbt project files not found. Run dbt setup first.")


elif "Memo" in page:
    db_check()
    section_header(
        "Decision Memo",
        "AI-generated ship/kill recommendation · Powered by Google Gemini",
    )

    a, b = load_variant_stats()
    ab = BayesianABTest()
    results = ab.run_test(
        int(a.purchasers),
        int(a.users),
        int(b.purchasers),
        int(b.users),
    )

    st.markdown("#### Current experiment summary")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Control rate", f"{results['control_rate']:.2%}")
    s2.metric(
        "Treatment rate",
        f"{results['treatment_rate']:.2%}",
        delta=f"{results['expected_lift_pct']:+.2f}pp",
    )
    s3.metric("P(B > A)", f"{results['prob_treatment_better']:.1f}%")
    s4.markdown(
        f"""
        <div style='padding:1rem 0'>
          {badge_html(results['recommendation'])}
        </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("✨  Generate Decision Memo", type="primary"):
        with st.spinner("Gemini is writing your memo..."):
            memo_text = generate_memo(
                {
                    "prob_treatment_better": results["prob_treatment_better"],
                    "expected_lift_pct": results["expected_lift_pct"],
                    "control_rate": results["control_rate"],
                    "treatment_rate": results["treatment_rate"],
                    "recommendation": results["recommendation"],
                    "control_n": int(a.users),
                    "treatment_n": int(b.users),
                    "ci_low": results["ci_low"],
                    "ci_high": results["ci_high"],
                }
            )

        st.success("Memo generated", icon="✅")
        st.markdown(
            f'<div class="memo-box">'
            f'{memo_text.replace(chr(10), "<br>")}'
            f"</div>",
            unsafe_allow_html=True,
        )
        col_dl, _ = st.columns([1, 4])
        col_dl.download_button(
            "⬇  Download",
            memo_text,
            file_name="decision_memo.txt",
            mime="text/plain",
        )
        st.caption(
            "Generated by Google Gemini · "
            "Based on UCI Online Retail II data · "
            "ExperimentOS v1.0"
        )
    else:
        st.info(
            "Click the button above to generate a plain-English "
            "memo for your product team.",
            icon="📝",
        )
