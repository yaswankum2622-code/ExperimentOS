import os
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


EXCEL_PATH = Path("data/online_retail_II.xlsx")
DB_PATH = Path("data/events.db")
RNG_SEED = 42

ADD_TO_CART_PROBABILITY = {"A": 0.68, "B": 0.78}
VIEW_PROBABILITY = {"A": 0.72, "B": 0.80}
BROWSE_CART_PROBABILITY = 0.30
MIN_BROWSE_SESSIONS = 3
MAX_BROWSE_SESSIONS = 7

TARGET_OVERALL_CONVERSION_RATE = 0.35
TARGET_CART_TO_PURCHASE_RATE = 0.67


def load_transactions() -> pd.DataFrame:
    sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)
    transactions = pd.concat(sheets.values(), ignore_index=True)

    transactions = transactions.dropna(subset=["Customer ID"]).copy()
    transactions = transactions[
        (transactions["Quantity"] > 0) & (transactions["Price"] > 0)
    ].copy()

    transactions["user_id"] = transactions["Customer ID"].astype(int)
    transactions["timestamp"] = pd.to_datetime(transactions["InvoiceDate"])
    transactions["event_date"] = transactions["timestamp"].dt.date
    transactions["revenue"] = transactions["Quantity"] * transactions["Price"]
    transactions["country"] = transactions["Country"]
    transactions["product_id"] = transactions["StockCode"].astype(str)
    transactions["description"] = transactions["Description"]
    transactions["invoice_id"] = transactions["Invoice"].astype(str)
    transactions["variant"] = transactions["user_id"].apply(
        lambda user_id: "B" if user_id % 2 == 0 else "A"
    )

    return transactions


def build_invoices(transactions: pd.DataFrame) -> pd.DataFrame:
    invoices = (
        transactions.groupby("invoice_id", as_index=False)
        .agg(
            user_id=("user_id", "first"),
            timestamp=("timestamp", "first"),
            total_revenue=("revenue", "sum"),
            item_count=("Quantity", "sum"),
            country=("country", "first"),
            variant=("variant", "first"),
            product_id=("product_id", "first"),
        )
        .sort_values(["timestamp", "invoice_id"])
        .reset_index(drop=True)
    )

    return invoices


def build_users(transactions: pd.DataFrame) -> pd.DataFrame:
    users = (
        transactions.groupby("user_id", as_index=False)
        .agg(
            first_seen=("timestamp", "min"),
            country=("country", "first"),
            variant=("variant", "first"),
            total_orders=("invoice_id", "nunique"),
            total_revenue=("revenue", "sum"),
        )
        .sort_values("user_id")
        .reset_index(drop=True)
    )

    return users


def build_events(
    invoices: pd.DataFrame,
    users: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RNG_SEED)
    event_frames = []

    cart_probabilities = invoices["variant"].map(ADD_TO_CART_PROBABILITY).to_numpy()
    cart_mask = rng.random(len(invoices)) < cart_probabilities
    cart_invoices = invoices.loc[cart_mask].copy()
    cart_invoices["cart_offset_minutes"] = rng.integers(2, 16, size=len(cart_invoices))

    view_probabilities = cart_invoices["variant"].map(VIEW_PROBABILITY).to_numpy()
    view_mask = rng.random(len(cart_invoices)) < view_probabilities
    view_invoices = cart_invoices.loc[view_mask].copy()
    view_invoices["view_offset_minutes"] = rng.integers(3, 31, size=len(view_invoices))

    event_frames.append(
        _invoice_events(
            invoices,
            "purchase",
            pd.Timedelta(minutes=0),
            event_order=3,
            revenue_from_purchase=True,
        )
    )
    event_frames.append(
        _invoice_events(
            cart_invoices,
            "add_to_cart",
            "cart_offset_minutes",
            event_order=2,
        )
    )
    event_frames.append(
        _invoice_events(
            view_invoices,
            "view",
            "view_offset_minutes",
            event_order=1,
        )
    )
    event_frames.append(_real_user_browse_events(users, invoices, rng))

    events = pd.concat(event_frames, ignore_index=True)
    synthetic_events, synthetic_users = _anonymous_browse_events(events, users, rng)
    events = pd.concat([events, synthetic_events], ignore_index=True)

    events = events.sort_values(["timestamp", "event_order", "user_id"]).reset_index(
        drop=True
    )
    events.insert(0, "event_id", range(1, len(events) + 1))

    return (
        events[
            [
                "event_id",
                "user_id",
                "event_type",
                "timestamp",
                "invoice_id",
                "product_id",
                "revenue",
                "country",
                "variant",
            ]
        ],
        synthetic_users,
    )


def _invoice_events(
    invoices: pd.DataFrame,
    event_type: str,
    offset: pd.Timedelta | str,
    event_order: int,
    revenue_from_purchase: bool = False,
) -> pd.DataFrame:
    columns = [
        "user_id",
        "timestamp",
        "invoice_id",
        "product_id",
        "country",
        "variant",
        "total_revenue",
    ]
    if isinstance(offset, str):
        columns.append(offset)
    frame = invoices[columns].copy()
    frame["event_type"] = event_type
    if isinstance(offset, str):
        frame["timestamp"] = frame["timestamp"] - pd.to_timedelta(
            frame[offset],
            unit="m",
        )
    else:
        frame["timestamp"] = frame["timestamp"] - offset
    frame["revenue"] = frame["total_revenue"] if revenue_from_purchase else 0.0
    frame["event_order"] = event_order
    drop_columns = ["total_revenue"]
    if isinstance(offset, str):
        drop_columns.append(offset)
    return frame.drop(columns=drop_columns)


def _real_user_browse_events(
    users: pd.DataFrame,
    invoices: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    user_windows = (
        invoices.groupby("user_id", as_index=False)
        .agg(
            first_invoice=("timestamp", "min"),
            last_invoice=("timestamp", "max"),
        )
        .merge(users[["user_id", "country", "variant"]], on="user_id", how="left")
    )
    session_counts = rng.integers(
        MIN_BROWSE_SESSIONS,
        MAX_BROWSE_SESSIONS + 1,
        size=len(user_windows),
    )
    repeated_users = user_windows.loc[
        user_windows.index.repeat(session_counts),
        ["user_id", "country", "variant", "first_invoice", "last_invoice"],
    ].reset_index(drop=True)
    repeated_users["timestamp"] = _random_timestamps_between(
        repeated_users["first_invoice"],
        repeated_users["last_invoice"],
        rng,
    )
    repeated_users = repeated_users.drop(columns=["first_invoice", "last_invoice"])

    view_events = repeated_users.copy()
    view_events["event_type"] = "view"
    view_events["invoice_id"] = None
    view_events["product_id"] = "BROWSE"
    view_events["revenue"] = 0.0
    view_events["event_order"] = 1

    cart_mask = rng.random(len(repeated_users)) < BROWSE_CART_PROBABILITY
    cart_events = repeated_users.loc[cart_mask].copy()
    cart_events["timestamp"] = cart_events["timestamp"] + pd.Timedelta(minutes=3)
    cart_events["event_type"] = "add_to_cart"
    cart_events["invoice_id"] = None
    cart_events["product_id"] = "BROWSE"
    cart_events["revenue"] = 0.0
    cart_events["event_order"] = 2

    return pd.concat([view_events, cart_events], ignore_index=True)


def _anonymous_browse_events(
    events: pd.DataFrame,
    users: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    purchasers = events.loc[events["event_type"] == "purchase", "user_id"].nunique()
    target_viewers = round(purchasers / TARGET_OVERALL_CONVERSION_RATE)
    target_cart_adders = round(purchasers / TARGET_CART_TO_PURCHASE_RATE)

    current_viewers = events.loc[events["event_type"] == "view", "user_id"].nunique()
    current_cart_adders = events.loc[
        events["event_type"] == "add_to_cart",
        "user_id",
    ].nunique()

    extra_viewers = max(0, target_viewers - current_viewers)
    extra_cart_adders = max(0, target_cart_adders - current_cart_adders)
    extra_cart_adders = min(extra_cart_adders, extra_viewers)

    if extra_viewers == 0:
        return pd.DataFrame(columns=events.columns), pd.DataFrame(columns=users.columns)

    start_user_id = int(users["user_id"].max()) + 1
    user_ids = np.arange(start_user_id, start_user_id + extra_viewers)
    timestamps = _random_timestamps(
        events["timestamp"].min(),
        events["timestamp"].max(),
        extra_viewers,
        rng,
    )
    countries = rng.choice(users["country"].dropna().to_numpy(), size=extra_viewers)

    synthetic_users = pd.DataFrame(
        {
            "user_id": user_ids,
            "first_seen": timestamps,
            "country": countries,
            "variant": np.where(user_ids % 2 == 0, "B", "A"),
            "total_orders": 0,
            "total_revenue": 0.0,
        }
    )

    view_events = synthetic_users[
        ["user_id", "country", "variant"]
    ].copy()
    view_events["timestamp"] = timestamps
    view_events["event_type"] = "view"
    view_events["invoice_id"] = None
    view_events["product_id"] = "BROWSE"
    view_events["revenue"] = 0.0
    view_events["event_order"] = 1

    cart_events = view_events.iloc[:extra_cart_adders].copy()
    cart_events["timestamp"] = cart_events["timestamp"] + pd.Timedelta(minutes=3)
    cart_events["event_type"] = "add_to_cart"
    cart_events["event_order"] = 2

    return pd.concat([view_events, cart_events], ignore_index=True), synthetic_users


def _random_timestamps(
    start: pd.Timestamp,
    end: pd.Timestamp,
    count: int,
    rng: np.random.Generator,
) -> pd.Series:
    start_second = pd.Timestamp(start).value // 1_000_000_000
    end_second = pd.Timestamp(end).value // 1_000_000_000
    random_seconds = rng.integers(start_second, end_second + 1, size=count)
    return pd.to_datetime(random_seconds, unit="s")


def _random_timestamps_between(
    starts: pd.Series,
    ends: pd.Series,
    rng: np.random.Generator,
) -> pd.Series:
    start_seconds = pd.to_datetime(starts).astype("int64") // 1_000_000_000
    end_seconds = pd.to_datetime(ends).astype("int64") // 1_000_000_000
    span_seconds = np.maximum(end_seconds - start_seconds, 0)
    random_seconds = start_seconds + np.floor(
        rng.random(len(starts)) * (span_seconds + 1)
    ).astype("int64")
    return pd.to_datetime(random_seconds, unit="s")


def write_sqlite(events: pd.DataFrame, users: pd.DataFrame, invoices: pd.DataFrame) -> None:
    os.makedirs(DB_PATH.parent, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        events.to_sql("events", connection, if_exists="replace", index=False)
        users.to_sql("users", connection, if_exists="replace", index=False)
        invoices[
            [
                "invoice_id",
                "user_id",
                "timestamp",
                "total_revenue",
                "item_count",
                "country",
                "variant",
            ]
        ].to_sql("invoices", connection, if_exists="replace", index=False)


def main() -> None:
    transactions = load_transactions()
    invoices = build_invoices(transactions)
    real_users = build_users(transactions)
    events, synthetic_users = build_events(invoices, real_users)
    users = pd.concat([real_users, synthetic_users], ignore_index=True)

    write_sqlite(events, users, invoices)

    n_users = len(users)
    n_invoices = len(invoices)
    n_events = len(events)
    a_users = (users["variant"] == "A").sum()
    b_users = (users["variant"] == "B").sum()
    min_date = transactions["event_date"].min()
    max_date = transactions["event_date"].max()
    n_countries = transactions["country"].nunique()

    print(f"Loaded {n_users} users | {n_invoices} invoices | {n_events} events")
    print(f"Variant A: {a_users} users | Variant B: {b_users} users")
    print(f"Date range: {min_date} to {max_date}")
    print(f"Countries: {n_countries}")
    print(f"Saved to: {DB_PATH}")


if __name__ == "__main__":
    main()
