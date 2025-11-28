"""Risk insights per EA: longest consecutive loss streaks, worst streak loss, etc."""

from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

from web.helpers import load_transactions


def _get_tx():
    tx = load_transactions()
    if tx is None or tx.empty:
        return pd.DataFrame()
    return tx


def _make_table(df: pd.DataFrame):
    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        size="sm",
        responsive=True,
        class_name="mt-2 mb-0",
    )


def _compute_streaks_for_series(profits: pd.Series):
    """Given a profit series sorted by time, return list of loss streaks.

    Each streak is a dict with:
      - count: number of consecutive loss trades
      - loss_sum: total profit (negative) over the streak
    """
    streaks = []
    in_streak = False
    count = 0
    loss_sum = 0.0

    for p in profits:
        if p < 0:
            if not in_streak:
                in_streak = True
                count = 1
                loss_sum = float(p)
            else:
                count += 1
                loss_sum += float(p)
        else:
            if in_streak:
                streaks.append({"count": count, "loss_sum": loss_sum})
                in_streak = False
                count = 0
                loss_sum = 0.0

    if in_streak:
        streaks.append({"count": count, "loss_sum": loss_sum})

    return streaks


def create_ea_risk_insights(tx_filtered=None):
    """Create risk insights table per EA.

    If tx_filtered is provided, use it; otherwise load all transactions.
    """
    if tx_filtered is None:
        tx = _get_tx()
    else:
        tx = tx_filtered.copy()

    if tx is None or tx.empty or "Profit" not in tx.columns or "EA_Name" not in tx.columns:
        return html.Div("No risk data available.", className="text-muted")

    # ensure datetime sort column
    time_col = "TimeClose" if "TimeClose" in tx.columns else "TimeOpen"
    if time_col not in tx.columns:
        return html.Div("No time column found for risk analysis.", className="text-muted")

    rows = []

    for ea, sub in tx.groupby("EA_Name"):
        sub = sub.sort_values(time_col)
        profits = sub["Profit"].astype(float)

        streaks = _compute_streaks_for_series(profits)

        if not streaks:
            max_count = 0
            worst_loss = 0.0
            total_streaks = 0
            avg_loss = 0.0
        else:
            counts = [s["count"] for s in streaks]
            losses = [s["loss_sum"] for s in streaks]  # negative numbers
            max_count = max(counts)
            worst_loss = min(losses)  # most negative
            total_streaks = len(streaks)
            avg_loss = sum(losses) / total_streaks

        rows.append(
            {
                "EA Name": ea,
                "Max Loss Streak (trades)": max_count,
                "Worst Streak Loss": worst_loss,
                "Total Loss Streaks": total_streaks,
                "Avg Loss Per Streak": avg_loss,
            }
        )

    df = pd.DataFrame(rows)

    # sort by Max Loss Streak desc, then Worst Streak Loss asc (most negative)
    df = df.sort_values(
        ["Max Loss Streak (trades)", "Worst Streak Loss"],
        ascending=[False, True],
    )

    # format display
    disp = df.copy()
    disp["Worst Streak Loss"] = disp["Worst Streak Loss"].map(lambda v: f"${v:,.2f}")
    disp["Avg Loss Per Streak"] = disp["Avg Loss Per Streak"].map(lambda v: f"${v:,.2f}")

    header = html.Div(
        html.H4(
            "📉 Risk Insights per EA (Consecutive Loss Streaks)",
            className="mb-0 fw-bold",
        ),
        style={
            "background": "#eef3ff",
            "borderLeft": "6px solid #2a6ad3",
            "padding": "12px 18px",
            "marginTop": "30px",
            "borderRadius": "6px",
        },
    )

    return html.Div([header, _make_table(disp)])