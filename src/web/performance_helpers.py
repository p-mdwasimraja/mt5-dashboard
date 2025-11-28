"""
Helper functions for EA and Trading Pairs performance analysis
"""
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
from dash import html
import dash_bootstrap_components as dbc


def get_last_week_data(transactions):
    """Get last complete week's data (Monday to Sunday)"""
    today = datetime.now().date()
    # Find last Sunday
    days_since_sunday = (today.weekday() + 1) % 7
    if days_since_sunday == 0:
        days_since_sunday = 7
    last_sunday = today - timedelta(days=days_since_sunday)
    last_monday = last_sunday - timedelta(days=6)
    
    # Filter transactions for last week
    transactions['Date'] = transactions['TimeOpen'].dt.date
    last_week_trans = transactions[
        (transactions['Date'] >= last_monday) & 
        (transactions['Date'] <= last_sunday)
    ]
    
    return last_week_trans, last_monday, last_sunday


def get_this_week_data(transactions):
    """Get this week's data (Monday to today)"""
    today = datetime.now().date()
    days_since_monday = today.weekday()
    this_monday = today - timedelta(days=days_since_monday)
    
    # Filter transactions for this week
    transactions['Date'] = transactions['TimeOpen'].dt.date
    this_week_trans = transactions[transactions['Date'] >= this_monday]
    
    return this_week_trans, this_monday, today


def create_top_ea_this_week(transactions):
    """Create top EA performers for this week"""
    if transactions.empty:
        return html.Div("No data available", className="text-center text-muted")
    
    this_week_trans, start_date, end_date = get_this_week_data(transactions)
    
    if this_week_trans.empty:
        return html.Div("No data for this week yet", className="text-center text-muted")
    
    # Group by EA
    ea_stats = this_week_trans.groupby('EA_Name')['Profit'].agg([
        ('Total Profit', 'sum'),
        ('Trades', 'count'),
        ('Avg Profit', 'mean'),
        ('Win Rate', lambda x: (x > 0).sum() / len(x) * 100 if len(x) > 0 else 0)
    ]).reset_index()
    
    # Sort by total profit
    ea_stats = ea_stats.sort_values('Total Profit', ascending=False)
    
    # Create cards for top 3
    cards = []
    medals = ['🥇', '🥈', '🥉']
    colors = ['gold', 'silver', '#cd7f32']
    
    for idx, (_, row) in enumerate(ea_stats.head(3).iterrows()):
        card = dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Span(medals[idx], style={'fontSize': '24px', 'marginRight': '10px'}),
                    html.Strong(row['EA_Name'])
                ], style={'backgroundColor': colors[idx] if idx < 3 else 'white'}),
                dbc.CardBody([
                    html.H4(f"${row['Total Profit']:.2f}", 
                           className="text-center mb-2",
                           style={'color': 'green' if row['Total Profit'] > 0 else 'red'}),
                    html.Hr(),
                    html.P([
                        html.Strong("Trades: "),
                        f"{int(row['Trades'])}"
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Win Rate: "),
                        f"{row['Win Rate']:.1f}%"
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Avg Profit: "),
                        f"${row['Avg Profit']:.2f}"
                    ], className="mb-0")
                ])
            ], className="shadow h-100")
        ], width=12, md=4, className="mb-3")
        cards.append(card)
    
    return html.Div([
        html.P(f"Week: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}", 
               className="text-muted mb-3"),
        dbc.Row(cards)
    ])


def create_ea_last_week_performance(transactions):
    """Create last week EA performance"""
    if transactions.empty:
        return html.Div("No data available", className="text-center text-muted")
    
    last_week_trans, start_date, end_date = get_last_week_data(transactions)
    
    if last_week_trans.empty:
        return html.Div("No data for last week", className="text-center text-muted")
    
    # Group by EA
    ea_stats = last_week_trans.groupby('EA_Name')['Profit'].agg([
        'sum', 'count', 'mean'
    ]).reset_index()
    ea_stats.columns = ['EA Name', 'Total Profit', 'Trades', 'Avg Profit']
    ea_stats = ea_stats.sort_values('Total Profit', ascending=False)
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ea_stats['EA Name'],
        y=ea_stats['Total Profit'],
        marker_color=['green' if x > 0 else 'red' for x in ea_stats['Total Profit']],
        text=ea_stats['Total Profit'].apply(lambda x: f'${x:.2f}'),
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"Last Week Performance ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})",
        xaxis_title="Expert Advisor",
        yaxis_title="Profit ($)",
        template='plotly_white',
        height=300
    )
    
    # Create summary table
    ea_stats['Total Profit'] = ea_stats['Total Profit'].apply(lambda x: f"${x:.2f}")
    ea_stats['Avg Profit'] = ea_stats['Avg Profit'].apply(lambda x: f"${x:.2f}")
    ea_stats['Trades'] = ea_stats['Trades'].astype(int)
    
    return dbc.Row([
        dbc.Col([
            dcc.Graph(figure=fig)
        ], width=12, lg=8),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Summary"),
                dbc.CardBody([
                    dbc.Table.from_dataframe(
                        ea_stats,
                        striped=True,
                        bordered=True,
                        hover=True,
                        size='sm',
                        className="mb-0"
                    )
                ])
            ], className="shadow-sm h-100")
        ], width=12, lg=4)
    ])


# Similar functions for Trading Pairs
def create_top_pairs_this_week(transactions):
    """Create top trading pairs for this week"""
    if transactions.empty or 'Symbol' not in transactions.columns:
        return html.Div("No data available", className="text-center text-muted")
    
    this_week_trans, start_date, end_date = get_this_week_data(transactions)
    
    if this_week_trans.empty:
        return html.Div("No data for this week yet", className="text-center text-muted")
    
    # Group by Symbol
    symbol_stats = this_week_trans.groupby('Symbol')['Profit'].agg([
        ('Total Profit', 'sum'),
        ('Trades', 'count'),
        ('Avg Profit', 'mean'),
        ('Win Rate', lambda x: (x > 0).sum() / len(x) * 100 if len(x) > 0 else 0)
    ]).reset_index()
    
    # Sort by total profit
    symbol_stats = symbol_stats.sort_values('Total Profit', ascending=False)
    
    # Create cards for top 3
    cards = []
    medals = ['🥇', '🥈', '🥉']
    colors = ['gold', 'silver', '#cd7f32']
    
    for idx, (_, row) in enumerate(symbol_stats.head(3).iterrows()):
        card = dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Span(medals[idx], style={'fontSize': '24px', 'marginRight': '10px'}),
                    html.Strong(row['Symbol'])
                ], style={'backgroundColor': colors[idx] if idx < 3 else 'white'}),
                dbc.CardBody([
                    html.H4(f"${row['Total Profit']:.2f}", 
                           className="text-center mb-2",
                           style={'color': 'green' if row['Total Profit'] > 0 else 'red'}),
                    html.Hr(),
                    html.P([
                        html.Strong("Trades: "),
                        f"{int(row['Trades'])}"
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Win Rate: "),
                        f"{row['Win Rate']:.1f}%"
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Avg Profit: "),
                        f"${row['Avg Profit']:.2f}"
                    ], className="mb-0")
                ])
            ], className="shadow h-100")
        ], width=12, md=4, className="mb-3")
        cards.append(card)
    
    return html.Div([
        html.P(f"Week: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}", 
               className="text-muted mb-3"),
        dbc.Row(cards)
    ])


def create_pairs_last_week_performance(transactions):
    """Create last week trading pairs performance"""
    if transactions.empty or 'Symbol' not in transactions.columns:
        return html.Div("No data available", className="text-center text-muted")
    
    last_week_trans, start_date, end_date = get_last_week_data(transactions)
    
    if last_week_trans.empty:
        return html.Div("No data for last week", className="text-center text-muted")
    
    # Group by Symbol
    symbol_stats = last_week_trans.groupby('Symbol')['Profit'].agg([
        'sum', 'count', 'mean'
    ]).reset_index()
    symbol_stats.columns = ['Trading Pair', 'Total Profit', 'Trades', 'Avg Profit']
    symbol_stats = symbol_stats.sort_values('Total Profit', ascending=False)
    
    # Get top 10
    symbol_stats = symbol_stats.head(10)
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=symbol_stats['Trading Pair'],
        y=symbol_stats['Total Profit'],
        marker_color=['green' if x > 0 else 'red' for x in symbol_stats['Total Profit']],
        text=symbol_stats['Total Profit'].apply(lambda x: f'${x:.2f}'),
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"Last Week Performance - Top 10 ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})",
        xaxis_title="Trading Pair",
        yaxis_title="Profit ($)",
        template='plotly_white',
        height=300,
        xaxis={'tickangle': -45}
    )
    
    return dbc.Row([
        dbc.Col([
            dcc.Graph(figure=fig)
        ], width=12)
    ])


def create_ea_daily_stats(transactions):
    """Create EA performance by day heatmap (last 14 days)"""
    if transactions.empty:
        return html.Div("No data available", className="text-center text-muted")
    
    transactions['Date'] = transactions['TimeOpen'].dt.date
    transactions['DateLabel'] = transactions['TimeOpen'].dt.strftime('%m/%d')
    
    unique_dates = sorted(transactions['Date'].unique())[-14:]
    transactions_filtered = transactions[transactions['Date'].isin(unique_dates)]
    
    if transactions_filtered.empty:
        return html.Div("No data for last 14 days", className="text-center text-muted")
    
    ea_daily_stats = transactions_filtered.groupby(['EA_Name', 'Date', 'DateLabel'])['Profit'].sum().reset_index()
    pivot_data = ea_daily_stats.pivot(index='EA_Name', columns='DateLabel', values='Profit')
    
    date_to_label = dict(zip(ea_daily_stats['Date'], ea_daily_stats['DateLabel']))
    sorted_labels = [date_to_label[d] for d in sorted(unique_dates) if d in date_to_label]
    pivot_data = pivot_data.reindex(columns=sorted_labels).fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='RdYlGn',
        text=pivot_data.values,
        texttemplate='$%{text:.0f}',
        textfont={"size": 9},
        colorbar=dict(title="Profit")
    ))
    
    fig.update_layout(
        title="EA Performance Heatmap (Last 14 Days)",
        xaxis_title="Date",
        yaxis_title="EA",
        template='plotly_white',
        height=250 + (len(pivot_data) * 40),
        xaxis={'tickangle': -45}
    )
    
    return dcc.Graph(figure=fig)


def create_ea_dow_patterns(transactions):
    """Create EA day of week patterns"""
    if transactions.empty:
        return html.Div("No data available", className="text-center text-muted")
    
    transactions['DayOfWeek'] = transactions['TimeOpen'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    dow_stats = transactions.groupby(['EA_Name', 'DayOfWeek'])['Profit'].sum().reset_index()
    dow_pivot = dow_stats.pivot(index='EA_Name', columns='DayOfWeek', values='Profit')
    dow_pivot = dow_pivot.reindex(columns=day_order).fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=dow_pivot.values,
        x=dow_pivot.columns,
        y=dow_pivot.index,
        colorscale='RdYlGn',
        text=dow_pivot.values,
        texttemplate='$%{text:.0f}',
        textfont={"size": 9},
        colorbar=dict(title="Profit")
    ))
    
    fig.update_layout(
        title="EA Performance by Day of Week (All Time)",
        xaxis_title="Day",
        yaxis_title="EA",
        template='plotly_white',
        height=250 + (len(dow_pivot) * 40)
    )
    
    return dcc.Graph(figure=fig)


def create_pairs_daily_stats(transactions):
    """Create trading pairs performance by day (last 14 days)"""
    if transactions.empty or 'Symbol' not in transactions.columns:
        return html.Div("No data available", className="text-center text-muted")
    
    transactions['Date'] = transactions['TimeOpen'].dt.date
    transactions['DateLabel'] = transactions['TimeOpen'].dt.strftime('%m/%d')
    
    unique_dates = sorted(transactions['Date'].unique())[-14:]
    transactions_filtered = transactions[transactions['Date'].isin(unique_dates)]
    
    if transactions_filtered.empty:
        return html.Div("No data for last 14 days", className="text-center text-muted")
    
    # Get top 10 symbols by total profit
    top_symbols = transactions_filtered.groupby('Symbol')['Profit'].sum().sort_values(ascending=False).head(10).index
    transactions_filtered = transactions_filtered[transactions_filtered['Symbol'].isin(top_symbols)]
    
    symbol_daily_stats = transactions_filtered.groupby(['Symbol', 'Date', 'DateLabel'])['Profit'].sum().reset_index()
    pivot_data = symbol_daily_stats.pivot(index='Symbol', columns='DateLabel', values='Profit')
    
    date_to_label = dict(zip(symbol_daily_stats['Date'], symbol_daily_stats['DateLabel']))
    sorted_labels = [date_to_label[d] for d in sorted(unique_dates) if d in date_to_label]
    pivot_data = pivot_data.reindex(columns=sorted_labels).fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='RdYlGn',
        text=pivot_data.values,
        texttemplate='$%{text:.0f}',
        textfont={"size": 9},
        colorbar=dict(title="Profit")
    ))
    
    fig.update_layout(
        title="Top 10 Trading Pairs - Heatmap (Last 14 Days)",
        xaxis_title="Date",
        yaxis_title="Symbol",
        template='plotly_white',
        height=300,
        xaxis={'tickangle': -45}
    )
    
    return dcc.Graph(figure=fig)


def create_pairs_dow_patterns(transactions):
    """Create trading pairs day of week patterns"""
    if transactions.empty or 'Symbol' not in transactions.columns:
        return html.Div("No data available", className="text-center text-muted")
    
    transactions['DayOfWeek'] = transactions['TimeOpen'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Get top 10 symbols
    top_symbols = transactions.groupby('Symbol')['Profit'].sum().sort_values(ascending=False).head(10).index
    transactions_filtered = transactions[transactions['Symbol'].isin(top_symbols)]
    
    dow_stats = transactions_filtered.groupby(['Symbol', 'DayOfWeek'])['Profit'].sum().reset_index()
    dow_pivot = dow_stats.pivot(index='Symbol', columns='DayOfWeek', values='Profit')
    dow_pivot = dow_pivot.reindex(columns=day_order).fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=dow_pivot.values,
        x=dow_pivot.columns,
        y=dow_pivot.index,
        colorscale='RdYlGn',
        text=dow_pivot.values,
        texttemplate='$%{text:.0f}',
        textfont={"size": 9},
        colorbar=dict(title="Profit")
    ))
    
    fig.update_layout(
        title="Top 10 Trading Pairs by Day of Week (All Time)",
        xaxis_title="Day",
        yaxis_title="Symbol",
        template='plotly_white',
        height=300
    )
    
    return dcc.Graph(figure=fig)

def create_ea_performance_table(transactions):
    """Create EA performance dashboard table"""
    if transactions.empty:
        return html.Div("No transaction data available", className="text-center text-muted")
    
    # Create analysis data for all EAs
    analysis_data = []
    
    for ea_name in transactions['EA_Name'].unique():
        ea_trans = transactions[transactions['EA_Name'] == ea_name].copy()
        
        total_trades = len(ea_trans)
        winning_trades = len(ea_trans[ea_trans['Profit'] > 0])
        losing_trades = len(ea_trans[ea_trans['Profit'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_profit = ea_trans['Profit'].sum()
        avg_profit = ea_trans['Profit'].mean()
        max_profit = ea_trans['Profit'].max()
        max_loss = ea_trans['Profit'].min()
        
        analysis_data.append({
            'EA Name': ea_name,
            'Total Trades': total_trades,
            'Win Rate': f"{win_rate:.1f}%",
            'Winning Trades': winning_trades,
            'Losing Trades': losing_trades,
            'Total Profit': f"${total_profit:.2f}",
            'Avg Profit': f"${avg_profit:.2f}",
            'Max Profit': f"${max_profit:.2f}",
            'Max Loss': f"${max_loss:.2f}"
        })
    
    # Create DataFrame for table
    import pandas as pd
    df = pd.DataFrame(analysis_data)
    
    # Sort by Total Profit (descending)
    df = df.sort_values('Total Profit', ascending=False)
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Table.from_dataframe(
                df,
                striped=True,
                bordered=True,
                hover=True,
                responsive=True,
                className="mb-0",
                style={'fontSize': '14px'}
            )
        ])
    ], className="shadow-sm")

# Import this in dashboard.py
from dash import dcc
