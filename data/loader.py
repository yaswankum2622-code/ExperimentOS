import os
import sqlite3
from pathlib import Path

import pandas as pd


EXCEL_PATH = Path("data/online_retail_II.xlsx")
DB_PATH = Path("data/events.db")


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


def build_events(invoices: pd.DataFrame) -> pd.DataFrame:
    event_frames = []
    event_specs = [
        ("view", pd.Timedelta(minutes=10), 1),
        ("add_to_cart", pd.Timedelta(minutes=3), 2),
        ("purchase", pd.Timedelta(minutes=0), 3),
    ]

    for event_type, offset, event_order in event_specs:
        frame = invoices[
            [
                "user_id",
                "timestamp",
                "invoice_id",
                "product_id",
                "country",
                "variant",
                "total_revenue",
            ]
        ].copy()
        frame["event_type"] = event_type
        frame["timestamp"] = frame["timestamp"] - offset
        frame["revenue"] = frame["total_revenue"] if event_type == "purchase" else 0.0
        frame["event_order"] = event_order
        frame = frame.drop(columns=["total_revenue"])
        event_frames.append(frame)

    events = pd.concat(event_frames, ignore_index=True)
    events = events.sort_values(["timestamp", "invoice_id", "event_order"]).reset_index(
        drop=True
    )
    events.insert(0, "event_id", range(1, len(events) + 1))

    return events[
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
    ]


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
    users = build_users(transactions)
    events = build_events(invoices)

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
