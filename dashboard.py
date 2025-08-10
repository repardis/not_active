import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from datetime import datetime

df = pd.read_excel('notActive.xlsx')

df['lastfacture'] = pd.to_datetime(df['lastfacture'])
today = datetime.now()
df['how_many_days_with_nodata'] = (today - df['lastfacture']).dt.days

# Step 4: Calculate counts and metrics
# Count branches with both evaluation and club
both_eval_club = df[(df['SmartEvaluation'] == 1) & (df['SmartClub'] == 1)]
count_both_eval_club = len(both_eval_club)

# Count only evaluations (evaluation=1 but club=0)
count_only_eval = len(df[(df['SmartEvaluation'] == 1) & (df['SmartClub'] == 0)])

# Count only club (club=1 but evaluation=0)  
count_only_club = len(df[(df['SmartClub'] == 1) & (df['SmartEvaluation'] == 0)])

# For branches with both club and evaluation, calculate rates
# Branches with evaluation rate <= 5%
eval_rate_low = len(both_eval_club[both_eval_club['eval_ratio'] <= 0.05])

# Branches with club rate <= 5%
club_rate_low = len(both_eval_club[both_eval_club['Club_ratio'] <= 0.05])

# Branches with both rates <= 5%
both_rates_low = len(both_eval_club[(both_eval_club['eval_ratio'] <= 0.05) & (both_eval_club['Club_ratio'] <= 0.05)])

# Calculate shares compared to total branches with both club and evaluation
eval_rate_low_share = eval_rate_low / count_both_eval_club * 100 if count_both_eval_club > 0 else 0
club_rate_low_share = club_rate_low / count_both_eval_club * 100 if count_both_eval_club > 0 else 0
both_rates_low_share = both_rates_low / count_both_eval_club * 100 if count_both_eval_club > 0 else 0


app = dash.Dash(__name__)

# Create dashboard layout
app.layout = html.Div([
    # Header
    html.H1("Business Analytics Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Dropdowns
    html.Div([
        html.Div([
            html.Label("Select Salesperson:"),
            dcc.Dropdown(
                id='salesperson-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + 
                        [{'label': sp, 'value': sp} for sp in df['salesman'].dropna().unique()],
                value='All'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
        
        html.Div([
            html.Label("Select City:"),
            dcc.Dropdown(
                id='city-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + 
                        [{'label': city, 'value': city} for city in df['city'].dropna().unique()],
                value='All'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
        
        html.Div([
            html.Label("Select Branch Status:"),
            dcc.Dropdown(
                id='status-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + 
                        [{'label': status, 'value': status} for status in df['BranchStatus'].dropna().unique()],
                value='All'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'})
    ]),
    
    # KPI Cards
    html.Div(id='kpi-cards', style={'margin': '20px'}),
    
    # Charts Row 1
    html.Div([
        html.Div([
            dcc.Graph(id='city-deactive-eval')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='city-deactive-club')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    
    # Charts Row 2
    html.Div([
        html.Div([
            dcc.Graph(id='salesperson-deactive')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='deactive-pie')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    
    # Charts Row 3 - Branch Status Analysis
    html.Div([
        html.Div([
            dcc.Graph(id='branch-status-eval')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='branch-status-club')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    
    # Charts Row 4 - Additional Metrics
    html.Div([
        html.Div([
            dcc.Graph(id='orders-per-day-hist')
        ], style={'width': '33%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='avg-revenue-hist')
        ], style={'width': '33%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='subscription-hist')
        ], style={'width': '33%', 'display': 'inline-block'})
    ]),
    
    # Charts Row 5
    html.Div([
        html.Div([
            dcc.Graph(id='negative-charge-pie')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='no-data-days-pie')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    
    # Histogram
    html.Div([
        dcc.Graph(id='tenure-histogram')
    ], style={'margin': '20px'})
])

# Callback for updating all charts
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('city-deactive-eval', 'figure'),
     Output('city-deactive-club', 'figure'),
     Output('salesperson-deactive', 'figure'),
     Output('deactive-pie', 'figure'),
     Output('branch-status-eval', 'figure'),
     Output('branch-status-club', 'figure'),
     Output('orders-per-day-hist', 'figure'),
     Output('avg-revenue-hist', 'figure'),
     Output('subscription-hist', 'figure'),
     Output('negative-charge-pie', 'figure'),
     Output('no-data-days-pie', 'figure'),
     Output('tenure-histogram', 'figure')],
    [Input('salesperson-dropdown', 'value'),
     Input('city-dropdown', 'value'),
     Input('status-dropdown', 'value')]
)
def update_dashboard(selected_salesperson, selected_city, selected_status):
    # Filter data based on selections
    filtered_df = df.copy()
    if selected_salesperson != 'All':
        filtered_df = filtered_df[filtered_df['salesman'] == selected_salesperson]
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['city'] == selected_city]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['BranchStatus'] == selected_status]
    
    # Calculate KPIs for filtered data
    both_eval_club_f = filtered_df[(filtered_df['SmartEvaluation'] == 1) & (filtered_df['SmartClub'] == 1)]
    count_both_f = len(both_eval_club_f)
    count_only_eval_f = len(filtered_df[(filtered_df['SmartEvaluation'] == 1) & (filtered_df['SmartClub'] == 0)])
    count_only_club_f = len(filtered_df[(filtered_df['SmartClub'] == 1) & (filtered_df['SmartEvaluation'] == 0)])
    eval_rate_low_f = len(both_eval_club_f[both_eval_club_f['eval_ratio'] <= 0.05])
    club_rate_low_f = len(both_eval_club_f[both_eval_club_f['Club_ratio'] <= 0.05])
    both_rates_low_f = len(both_eval_club_f[(both_eval_club_f['eval_ratio'] <= 0.05) & (both_eval_club_f['Club_ratio'] <= 0.05)])
    
    # KPI Cards
    kpi_cards = html.Div([
        html.Div([
            html.H3(str(count_both_f)),
            html.P("Both Eval & Club")
        ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'textAlign': 'center', 
                                      'border': '1px solid #ddd', 'margin': '5px', 'padding': '10px'}),
        
        html.Div([
            html.H3(str(count_only_eval_f)),
            html.P("Only Evaluation")
        ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'textAlign': 'center',
                                      'border': '1px solid #ddd', 'margin': '5px', 'padding': '10px'}),
        
        html.Div([
            html.H3(str(count_only_club_f)),
            html.P("Only Club")
        ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'textAlign': 'center',
                                      'border': '1px solid #ddd', 'margin': '5px', 'padding': '10px'}),
        
        html.Div([
            html.H3(str(eval_rate_low_f)),
            html.P("Low Eval Rate (≤5%)")
        ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'textAlign': 'center',
                                      'border': '1px solid #ddd', 'margin': '5px', 'padding': '10px'}),
        
        html.Div([
            html.H3(str(club_rate_low_f)),
            html.P("Low Club Rate (≤5%)")
        ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'textAlign': 'center',
                                      'border': '1px solid #ddd', 'margin': '5px', 'padding': '10px'}),
        
        html.Div([
            html.H3(str(both_rates_low_f)),
            html.P("Both Rates Low (≤5%)")
        ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'textAlign': 'center',
                                      'border': '1px solid #ddd', 'margin': '5px', 'padding': '10px'})
    ])
    
    # City with most deactive evaluation (show top 10 counts, not percentages)
    eval_branches = filtered_df[filtered_df['SmartEvaluation'] == 1]
    if len(eval_branches) > 0:
        city_eval = eval_branches.groupby('city').agg({
            'eval_ratio': lambda x: (x <= 0.05).sum()
        }).reset_index()
        city_eval.columns = ['city', 'deactive_eval_count']
        city_eval = city_eval.sort_values('deactive_eval_count', ascending=False).head(10)
        fig_city_eval = px.bar(city_eval, x='city', y='deactive_eval_count',
                              title='Top 10 Cities with Most Deactive Evaluation (Count)')
    else:
        fig_city_eval = px.bar(title='No Evaluation Data Available')
    
    # City with most deactive club (show top 10 counts, not percentages)
    club_branches = filtered_df[filtered_df['SmartClub'] == 1]
    if len(club_branches) > 0:
        city_club = club_branches.groupby('city').agg({
            'Club_ratio': lambda x: (x <= 0.05).sum()
        }).reset_index()
        city_club.columns = ['city', 'deactive_club_count']
        city_club = city_club.sort_values('deactive_club_count', ascending=False).head(10)
        fig_city_club = px.bar(city_club, x='city', y='deactive_club_count',
                              title='Top 10 Cities with Most Deactive Club (Count)')
    else:
        fig_city_club = px.bar(title='No Club Data Available')
    
    # Salesperson with most deactive
    if len(both_eval_club_f) > 0:
        sales_deactive = both_eval_club_f.groupby('salesman').agg({
            'eval_ratio': lambda x: (x <= 0.05).sum(),
            'Club_ratio': lambda x: (x <= 0.05).sum()
        }).reset_index()
        sales_deactive['total_deactive'] = sales_deactive['eval_ratio'] + sales_deactive['Club_ratio']
        sales_deactive = sales_deactive.sort_values('total_deactive', ascending=False).head(10)
        fig_salesperson = px.bar(sales_deactive, x='salesman', y='total_deactive',
                                title='Salesperson with Most Deactive Club & Evaluation')
    else:
        fig_salesperson = px.bar(title='No Data Available for Both Club & Evaluation')

    # Branch Status with deactive evaluation counts
    eval_branches_status = filtered_df[filtered_df['SmartEvaluation'] == 1]
    if len(eval_branches_status) > 0:
        status_eval = eval_branches_status.groupby('BranchStatus').agg({
            'eval_ratio': lambda x: (x <= 0.05).sum()
        }).reset_index()
        status_eval.columns = ['BranchStatus', 'deactive_eval_count']
        status_eval = status_eval.sort_values('deactive_eval_count', ascending=False)
        fig_branch_status_eval = px.bar(status_eval, x='BranchStatus', y='deactive_eval_count',
                                       title='Deactive Evaluation Count by Branch Status')
        # Rotate x-axis labels for better readability
        fig_branch_status_eval.update_layout(xaxis_tickangle=-45)
    else:
        fig_branch_status_eval = px.bar(title='No Evaluation Data Available')
    
    # Branch Status with deactive club counts
    club_branches_status = filtered_df[filtered_df['SmartClub'] == 1]
    if len(club_branches_status) > 0:
        status_club = club_branches_status.groupby('BranchStatus').agg({
            'Club_ratio': lambda x: (x <= 0.05).sum()
        }).reset_index()
        status_club.columns = ['BranchStatus', 'deactive_club_count']
        status_club = status_club.sort_values('deactive_club_count', ascending=False)
        fig_branch_status_club = px.bar(status_club, x='BranchStatus', y='deactive_club_count',
                                       title='Deactive Club Count by Branch Status')
        # Rotate x-axis labels for better readability
        fig_branch_status_club.update_layout(xaxis_tickangle=-45)
    else:
        fig_branch_status_club = px.bar(title='No Club Data Available')

    # Orders per day histogram with custom bins
    filtered_orders = filtered_df[(filtered_df['orderCount'] > 0) & (filtered_df['fDays'] > 0)]
    if len(filtered_orders) > 0:
        filtered_orders_copy = filtered_orders.copy()
        filtered_orders_copy['orders_per_day'] = filtered_orders_copy['orderCount'] / filtered_orders_copy['fDays']
        
        # Create custom bins for orders per day
        bins = [0, 101, 201, 301, 501, float('inf')]
        labels = ['0-100', '101-200', '201-300', '301-500', '500+']
        
        # Cut the data into bins
        orders_binned = pd.cut(filtered_orders_copy['orders_per_day'], bins=bins, labels=labels, right=False, include_lowest=True)
        orders_counts = orders_binned.value_counts().reindex(labels, fill_value=0)
        
        # Create bar chart
        fig_orders_per_day = px.bar(x=labels, y=orders_counts.values,
                                   title='Orders Per Day Distribution (Custom Bins)')
        fig_orders_per_day.update_xaxes(title='Orders Per Day Range')
        fig_orders_per_day.update_yaxes(title='Count')
        
        # Calculate statistics
        avg_orders = filtered_orders_copy['orders_per_day'].mean()
        median_orders = filtered_orders_copy['orders_per_day'].median()
        
        # Add prominent statistical annotations
        fig_orders_per_day.add_annotation(
            x=0.2, y=0.95,
            xref="paper", yref="paper",
            text=f"<b style='color:red'>AVG: {avg_orders:.1f}</b>",
            showarrow=False,
            align="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="red",
            borderwidth=2,
            font=dict(size=16, color="red")
        )
        
        fig_orders_per_day.add_annotation(
            x=0.8, y=0.95,
            xref="paper", yref="paper",
            text=f"<b style='color:blue'>MEDIAN: {median_orders:.1f}</b>",
            showarrow=False,
            align="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="blue",
            borderwidth=2,
            font=dict(size=16, color="blue")
        )
    else:
        fig_orders_per_day = px.bar(title='No Order Data Available')
    
    # Revenue per day statistics table
    revenue_data = filtered_df[filtered_df['revenue'] > 0]
    if len(revenue_data) > 0:
        revenue_per_day = revenue_data['revenue'] / revenue_data['fDays']
        
        # Calculate statistics
        avg_rev = revenue_per_day.mean()
        p25_rev = revenue_per_day.quantile(0.25)
        p50_rev = revenue_per_day.quantile(0.50)
        p75_rev = revenue_per_day.quantile(0.75)
        
        # Create a table-like display
        table_data = {
            'Statistic': ['Average', '25th Percentile', '50th Percentile (Median)', '75th Percentile'],
            'Value': [f'{avg_rev:,.0f}', f'{p25_rev:,.0f}', f'{p50_rev:,.0f}', f'{p75_rev:,.0f}']
        }
        
        fig_avg_revenue = px.bar(x=table_data['Statistic'], y=[1, 1, 1, 1],
                                title='Revenue Per Day Statistics',
                                text=[f"<b>{val}</b>" for val in table_data['Value']])
        
        fig_avg_revenue.update_traces(
            textposition='inside',
            textfont=dict(size=14, color='white'),
            marker=dict(color=['#ff4444', '#4444ff', '#44ff44', '#ff44ff'])
        )
        
        fig_avg_revenue.update_layout(
            showlegend=False,
            yaxis={'visible': False, 'range': [0, 1.2]},
            xaxis={'title': ''},
            height=300
        )
    else:
        fig_avg_revenue = px.bar(title='No Revenue Data Available')
    
    # Subscription histogram with custom bins (like client tenure)
    subscription_data = filtered_df[filtered_df['subscription'].notna()]  # Only exclude NaN values, include 0
    if len(subscription_data) > 0:
        # Create custom bins for subscription (0-50%, 50-70%, 70-90%, 90%+)
        bins = [0, 0.5, 0.7, 0.9, float('inf')]
        labels = ['0-50%', '50-70%', '70-90%', '90%+']
        
        # Cut the data into bins
        subscription_binned = pd.cut(subscription_data['subscription'], bins=bins, labels=labels, right=False, include_lowest=True)
        subscription_counts = subscription_binned.value_counts().reindex(labels, fill_value=0)
        
        # Create bar chart
        fig_subscription = px.bar(x=labels, y=subscription_counts.values,
                                 title='Subscription Distribution (Custom Bins)')
        fig_subscription.update_xaxes(title='Subscription Range')
        fig_subscription.update_yaxes(title='Count')
        
        # Calculate statistics
        avg_subscription = subscription_data['subscription'].mean()
        median_subscription = subscription_data['subscription'].median()
        
        # Add prominent statistical annotations (like tenure chart)
        fig_subscription.add_annotation(
            x=0.15, y=0.90,
            xref="paper", yref="paper",
            text=f"<b style='color:red'>AVERAGE: {avg_subscription:.1%}</b>",
            showarrow=False,
            align="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="red",
            borderwidth=2,
            font=dict(size=14, color="red")
        )
        
        fig_subscription.add_annotation(
            x=0.85, y=0.90,
            xref="paper", yref="paper",
            text=f"<b style='color:blue'>MEDIAN: {median_subscription:.1%}</b>",
            showarrow=False,
            align="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="blue",
            borderwidth=2,
            font=dict(size=14, color="blue")
        )
    else:
        fig_subscription = px.bar(title='No Subscription Data Available')

    # Pie chart for deactive status
    if len(both_eval_club_f) > 0:
        deactive_only_eval = len(both_eval_club_f[(both_eval_club_f['eval_ratio'] <= 0.05) & (both_eval_club_f['Club_ratio'] > 0.05)])
        deactive_only_club = len(both_eval_club_f[(both_eval_club_f['eval_ratio'] > 0.05) & (both_eval_club_f['Club_ratio'] <= 0.05)])
        deactive_both = len(both_eval_club_f[(both_eval_club_f['eval_ratio'] <= 0.05) & (both_eval_club_f['Club_ratio'] <= 0.05)])
        active_both = len(both_eval_club_f[(both_eval_club_f['eval_ratio'] > 0.05) & (both_eval_club_f['Club_ratio'] > 0.05)])
        
        fig_deactive_pie = px.pie(values=[deactive_only_eval, deactive_only_club, deactive_both, active_both],
                                 names=['Only Deactive Eval', 'Only Deactive Club', 'Both Deactive', 'Both Active'],
                                 title='Deactive Status Distribution')
    else:
        fig_deactive_pie = px.pie(values=[1], names=['No Data'], title='No Data Available')
    
    # Negative charge days pie
    neg_0 = len(filtered_df[filtered_df['HowManydayschargeisNegetive'] == 0])
    neg_1_7 = len(filtered_df[(filtered_df['HowManydayschargeisNegetive'] > 0) & (filtered_df['HowManydayschargeisNegetive'] <= 7)])
    neg_8_30 = len(filtered_df[(filtered_df['HowManydayschargeisNegetive'] >= 8) & (filtered_df['HowManydayschargeisNegetive'] <= 30)])
    neg_30_plus = len(filtered_df[filtered_df['HowManydayschargeisNegetive'] > 30])
    
    fig_neg_charge = px.pie(values=[neg_0, neg_1_7, neg_8_30, neg_30_plus],
                           names=['0 days', '1-7 days', '8-30 days', '30+ days'],
                           title='Negative Charge Days Distribution')
    
    # No data days pie
    nodata_0 = len(filtered_df[filtered_df['how_many_days_with_nodata'] == 0])
    nodata_1_7 = len(filtered_df[(filtered_df['how_many_days_with_nodata'] > 0) & (filtered_df['how_many_days_with_nodata'] <= 7)])
    nodata_8_30 = len(filtered_df[(filtered_df['how_many_days_with_nodata'] >= 8) & (filtered_df['how_many_days_with_nodata'] <= 30)])
    nodata_30_plus = len(filtered_df[filtered_df['how_many_days_with_nodata'] > 30])
    
    fig_nodata_pie = px.pie(values=[nodata_0, nodata_1_7, nodata_8_30, nodata_30_plus],
                           names=['0 days', '1-7 days', '8-30 days', '30+ days'],
                           title='Days with No Data Distribution')
    
    # Tenure histogram with custom bins and statistical lines
    tenure_data = filtered_df['client_tenure_days\n'].dropna()
    if len(tenure_data) > 0:
        # Create custom bins
        bins = [0, 31, 61, 91, 181, 366, float('inf')]
        labels = ['0-30', '31-60', '61-90', '91-180', '181-365', '365+']
        
        # Cut the data into bins
        tenure_binned = pd.cut(tenure_data, bins=bins, labels=labels, right=False, include_lowest=True)
        tenure_counts = tenure_binned.value_counts().reindex(labels, fill_value=0)
        
        # Create bar chart with custom bins
        fig_tenure = px.bar(x=labels, y=tenure_counts.values,
                           title='Client Tenure Days Distribution (Custom Bins)')
        fig_tenure.update_xaxes(title='Tenure Days Range')
        fig_tenure.update_yaxes(title='Count')
        
        # Calculate statistics
        avg_tenure = tenure_data.mean()
        median_tenure = tenure_data.median()
        p75_tenure = tenure_data.quantile(0.75)
        
        # Add multiple prominent statistical annotations
        max_count = tenure_counts.max()
        
        # Average line annotation (as a red horizontal line for reference)
        fig_tenure.add_annotation(
            x=0.15, y=0.95,
            xref="paper", yref="paper",
            text=f"<b style='color:red'>AVERAGE: {avg_tenure:.0f} days</b>",
            showarrow=False,
            align="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="red",
            borderwidth=2,
            font=dict(size=14, color="red")
        )
        
        # Median annotation
        fig_tenure.add_annotation(
            x=0.5, y=0.95,
            xref="paper", yref="paper",
            text=f"<b style='color:blue'>MEDIAN: {median_tenure:.0f} days</b>",
            showarrow=False,
            align="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="blue",
            borderwidth=2,
            font=dict(size=14, color="blue")
        )
        
        # 75th percentile annotation
        fig_tenure.add_annotation(
            x=0.85, y=0.95,
            xref="paper", yref="paper",
            text=f"<b style='color:green'>75th %: {p75_tenure:.0f} days</b>",
            showarrow=False,
            align="center",
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="green",
            borderwidth=2,
            font=dict(size=14, color="green")
        )
        
        # Add which bin each statistic falls into
        def get_bin_for_value(value):
            if value <= 30:
                return "0-30"
            elif value <= 60:
                return "31-60"
            elif value <= 90:
                return "61-90"
            elif value <= 180:
                return "91-180"
            elif value <= 365:
                return "181-365"
            else:
                return "365+"
        
        # Add arrows pointing to the bins where statistics fall
        avg_bin = get_bin_for_value(avg_tenure)
        median_bin = get_bin_for_value(median_tenure)
        p75_bin = get_bin_for_value(p75_tenure)
        
        # Summary box at the bottom
        fig_tenure.add_annotation(
            x=0.5, y=0.02,
            xref="paper", yref="paper",
            text=f"<b>Summary:</b> Avg falls in {avg_bin} bin | Median falls in {median_bin} bin | 75% falls in {p75_bin} bin",
            showarrow=False,
            align="center",
            bgcolor="rgba(240,240,240,0.95)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=12)
        )
        
    else:
        fig_tenure = px.bar(title='No Tenure Data Available')
    
    return (kpi_cards, fig_city_eval, fig_city_club, fig_salesperson, fig_deactive_pie, 
            fig_branch_status_eval, fig_branch_status_club, fig_orders_per_day, fig_avg_revenue, 
            fig_subscription, fig_neg_charge, fig_nodata_pie, fig_tenure)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)