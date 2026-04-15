import sqlite3

import pandas as pd
import plotly.graph_objects as go


def compute_retention(db_path: str) -> go.Figure:
    with sqlite3.connect(db_path) as conn:
        purchases = pd.read_sql_query(
            """
            SELECT user_id, timestamp
            FROM events
            WHERE event_type = 'purchase'
            """,
            conn,
        )

    if purchases.empty:
        return _build_heatmap(
            retention=pd.DataFrame(0.0, index=range(1, 7), columns=range(9)),
        )

    purchases["timestamp"] = pd.to_datetime(purchases["timestamp"])
    purchases["purchase_date"] = purchases["timestamp"].dt.normalize()

    first_purchase = (
        purchases.groupby("user_id", as_index=False)["purchase_date"]
        .min()
        .rename(columns={"purchase_date": "first_purchase_date"})
    )
    dataset_start = purchases["purchase_date"].min()

    cohort_users = first_purchase.copy()
    cohort_users["cohort_week"] = (
        (cohort_users["first_purchase_date"] - dataset_start).dt.days // 7
    ) + 1

    purchases = purchases.merge(cohort_users, on="user_id", how="inner")
    purchases["weeks_since_first_purchase"] = (
        (purchases["purchase_date"] - purchases["first_purchase_date"]).dt.days // 7
    )
    purchases = purchases[
        purchases["weeks_since_first_purchase"].between(0, 8)
    ].copy()

    cohort_sizes = cohort_users.groupby("cohort_week")["user_id"].nunique()
    retained_users = (
        purchases.groupby(["cohort_week", "weeks_since_first_purchase"])["user_id"]
        .nunique()
        .reset_index(name="retained_users")
    )

    max_cohort_week = max(int(cohort_users["cohort_week"].max()), 6)
    retention = pd.DataFrame(0.0, index=range(1, max_cohort_week + 1), columns=range(9))

    for row in retained_users.itertuples(index=False):
        cohort_week = int(row.cohort_week)
        week = int(row.weeks_since_first_purchase)
        cohort_size = cohort_sizes.get(cohort_week, 0)
        if cohort_size:
            retention.loc[cohort_week, week] = row.retained_users * 100.0 / cohort_size

    return _build_heatmap(retention)


def _build_heatmap(retention: pd.DataFrame) -> go.Figure:
    cohort_matrix = retention.tail(16)
    cohort_matrix = cohort_matrix.iloc[:, :9]
    cohort_matrix = cohort_matrix.round(1)
    cohort_matrix.index = [f"Week {week}" for week in cohort_matrix.index]

    fig = go.Figure(
        data=go.Heatmap(
            z=cohort_matrix.values,
            x=[f"Week {i}" for i in range(9)],
            y=cohort_matrix.index.tolist(),
            text=cohort_matrix.values,
            texttemplate="%{text:.1f}%",
            colorscale=[
                [0.0, "#F7F8FA"],
                [0.3, "#EEEDFE"],
                [0.7, "#7F77DD"],
                [1.0, "#26215C"],
            ],
            showscale=True,
            colorbar=dict(
                title="Retention %",
                ticksuffix="%",
                tickfont=dict(size=11),
            ),
            hoverongaps=False,
            xgap=2,
            ygap=2,
        )
    )

    fig.update_layout(
        height=520,
        title="Weekly cohort retention — last 16 cohorts (%)",
        xaxis_title="Weeks since first purchase",
        yaxis_title="Acquisition cohort",
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
    )

    return fig
