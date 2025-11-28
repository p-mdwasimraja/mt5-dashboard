
"""Recent transactions table component"""
import dash_bootstrap_components as dbc
from web.helpers import load_transactions

def create_transaction_table():
    transactions = load_transactions()

    if transactions.empty:
        return dbc.Alert("No transaction data available", color="light", className="text-center text-muted")

    display_transactions = transactions.copy()

    if 'TimeOpen' in display_transactions.columns:
        display_transactions['TimeOpen'] = display_transactions['TimeOpen'].dt.strftime('%Y-%m-%d %H:%M')
    if 'TimeClose' in display_transactions.columns:
        display_transactions['TimeClose'] = display_transactions['TimeClose'].dt.strftime('%Y-%m-%d %H:%M')
    if 'Profit' in display_transactions.columns:
        display_transactions['Profit'] = display_transactions['Profit'].apply(lambda x: f"${x:.2f}")

    columns = ['EA_Name', 'Symbol', 'Type', 'Volume', 'PriceOpen', 'PriceClose', 'Profit', 'TimeOpen', 'TimeClose']
    columns = [c for c in columns if c in display_transactions.columns]

    display_transactions = display_transactions[columns].tail(20)

    return dbc.Table.from_dataframe(
        display_transactions,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-0"
    )
