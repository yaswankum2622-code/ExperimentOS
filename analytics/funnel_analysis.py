import sqlite3

import pandas as pd
import plotly.graph_objects as go


def compute_funnel(db_path: str, variant: str = None) -> tuple[go.Figure, dict]:
    sql = """
    SELECT user_id, event_type, variant
    FROM events
    """
    params = ()
    if variant is not None:
        sql += " WHERE variant = ?"
        params = (variant,)

    with sqlite3.connect(db_path) as conn:
        events = pd.read_sql_query(sql, conn, params=params)

    viewers = _count_users(events, "view")
    cart_adders = _count_users(events, "add_to_cart")
    purchasers = _count_users(events, "purchase")

    view_to_cart_rate = _rate(cart_adders, viewers)
    cart_to_purchase_rate = _rate(purchasers, cart_adders)
    overall_conversion_rate = _rate(purchasers, viewers)

    stats = {
        "view_to_cart_rate": view_to_cart_rate,
        "cart_to_purchase_rate": cart_to_purchase_rate,
        "overall_conversion_rate": overall_conversion_rate,
        "viewers": viewers,
        "cart_adders": cart_adders,
        "purchasers": purchasers,
    }

    stages = ["View", "Add to Cart", "Purchase"]
    counts = [viewers, cart_adders, purchasers]
    percentages = [
        100.0 if viewers else 0.0,
        view_to_cart_rate,
        overall_conversion_rate,
    ]
    text = [
        f"{count:,} users ({percentage:.1f}%)"
        for count, percentage in zip(counts, percentages)
    ]

    title = "Purchase Funnel" if variant is None else f"Funnel — Variant {variant}"
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=counts,
            text=text,
            textinfo="text",
            marker=dict(color=["steelblue", "steelblue", "steelblue"]),
            hovertemplate="%{y}: %{x:,} users<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_white",
    )

    return fig, stats


def _count_users(events: pd.DataFrame, event_type: str) -> int:
    if events.empty:
        return 0
    return int(events.loc[events["event_type"] == event_type, "user_id"].nunique())


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator * 100.0 / denominator
