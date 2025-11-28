
"""EA overview table component"""
import dash_bootstrap_components as dbc
import pandas as pd
from web.helpers import load_stats, load_deposits

def create_ea_overview():
    stats = load_stats()
    deposits = load_deposits()

    if not stats or 'eas' not in stats:
        return dbc.Alert("No EA data available", color="light", className="text-center text-muted")

    ea_deposits = {}
    if not deposits.empty:
        for ea_name in deposits['EA_Name'].unique():
            ea_deposit_data = deposits[deposits['EA_Name'] == ea_name]
            total_deposit = ea_deposit_data['Profit'].sum() if 'Profit' in ea_deposit_data.columns else 0
            ea_deposits[ea_name] = total_deposit

    table_data = []
    for ea_name, ea_data in stats['eas'].items():
        deposit_amount = float(ea_deposits.get(ea_name, 0) or 0)
        current_balance = float(ea_data.get('balance', 0) or 0)
        equity = float(ea_data.get('equity', 0) or 0)
        profit = current_balance - deposit_amount
        percentage = (profit / deposit_amount * 100) if deposit_amount > 0 else 0

        table_data.append({
            'EA Name': ea_name,
            'Currency': ea_data.get('currency', 'USD'),
            'Deposit': f"${deposit_amount:,.0f}",
            'Balance': f"${current_balance:,.2f}",
            'Equity': f"${equity:,.2f}",
            'Profit': f"${profit:,.2f}",
            'Percentage': f"{percentage:.2f}%"
        })

    df = pd.DataFrame(table_data)
    column_order = ['EA Name', 'Currency', 'Deposit', 'Balance', 'Equity', 'Profit', 'Percentage']
    df = df[column_order]

    return dbc.Card([
        dbc.CardBody([
            dbc.Table.from_dataframe(
                df,
                striped=True,
                bordered=True,
                hover=True,
                responsive=True,
                className="mb-0"
            )
        ])
    ], className="shadow-sm")
