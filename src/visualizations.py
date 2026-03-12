import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json

def plot_top_countries_cases(df):
    df_sorted = df.sort_values('total_cases', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['country'],
        x=df_sorted['total_cases'],
        orientation='h',
        marker=dict(
            color=df_sorted['total_cases'],
            colorscale='viridis'
        ),
        text=df_sorted['total_cases'].apply(lambda x: f'{x/1e6:.2f}M'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Cases: %{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Top 10 Countries by Total COVID-19 Cases',
        xaxis_title='Total Cases',
        yaxis_title='Country',
        height=500,
        margin=dict(l=20, r=120, t=50, b=50)
    )
    
    return json.loads(fig.to_json())

def plot_top_countries_deaths(df):
    df_sorted = df.sort_values('total_deaths', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['country'],
        x=df_sorted['total_deaths'],
        orientation='h',
        marker=dict(
            color=df_sorted['total_deaths'],
            colorscale='reds'
        ),
        text=df_sorted['total_deaths'].apply(lambda x: f'{x/1e6:.2f}M'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Deaths: %{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Top 10 Countries by Total COVID-19 Deaths',
        xaxis_title='Total Deaths',
        yaxis_title='Country',
        height=500,
        margin=dict(l=20, r=120, t=50, b=50)
    )
    
    return json.loads(fig.to_json())

def plot_death_rate_comparison(df):
    df_sorted = df.sort_values('death_rate', ascending=True).copy()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['country'],
        x=df_sorted['death_rate'],
        orientation='h',
        marker=dict(
            color=df_sorted['death_rate'],
            colorscale='RdYlGn_r',
            cmin=df_sorted['death_rate'].min(),
            cmax=df_sorted['death_rate'].max()
        ),
        text=df_sorted['death_rate'].apply(lambda x: f'{x:.2f}%'),
        textposition='outside',
        customdata=np.column_stack([
            df_sorted['total_cases'],
            df_sorted['total_deaths']
        ]),
        hovertemplate=(
            '<b>%{y}</b><br>' +
            'Death Rate: %{x:.2f}%<br>' +
            'Total Cases: %{customdata[0]:,.0f}<br>' +
            'Total Deaths: %{customdata[1]:,.0f}<extra></extra>'
        )
    ))
    
    fig.update_layout(
        title='COVID-19 Death Rate by Country (Min 100K Cases)',
        xaxis_title='Death Rate (%)',
        yaxis_title='Country',
        height=600,
        margin=dict(l=20, r=100, t=50, b=50),
        xaxis=dict(
            ticksuffix='%',
            range=[0, df_sorted['death_rate'].max() * 1.15]
        )
    )
    
    return json.loads(fig.to_json())

def plot_continent_comparison(df):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No continent data available", showarrow=False)
        return json.loads(fig.to_json())
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Total Cases by Continent',
            'Total Deaths by Continent',
            'Cases per Million by Continent',
            'Death Rate (%) by Continent'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    colors = px.colors.qualitative.Set2
    
    fig.add_trace(
        go.Bar(
            x=df['continent'],
            y=df['total_cases'],
            marker_color=colors[:len(df)],
            text=df['total_cases'].apply(lambda x: f'{x/1e6:.1f}M'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Total Cases: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df['continent'],
            y=df['total_deaths'],
            marker_color=colors[:len(df)],
            text=df['total_deaths'].apply(lambda x: f'{x/1e6:.2f}M'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Total Deaths: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=df['continent'],
            y=df['cases_per_million'],
            marker_color=colors[:len(df)],
            text=df['cases_per_million'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Cases/Million: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df['continent'],
            y=df['death_rate'],
            marker_color=colors[:len(df)],
            text=df['death_rate'].apply(lambda x: f'{x:.2f}%'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Death Rate: %{y:.2f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text='Continental COVID-19 Comparison',
        height=700,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="Total Cases", row=1, col=1)
    fig.update_yaxes(title_text="Total Deaths", row=1, col=2)
    fig.update_yaxes(title_text="Cases per Million", row=2, col=1)
    fig.update_yaxes(title_text="Death Rate (%)", row=2, col=2)
    
    return json.loads(fig.to_json())

def plot_country_timeline(df, country):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"No data available for {country}", showarrow=False)
        return json.loads(fig.to_json())
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Total Cases Over Time',
            'Daily New Cases',
            'Total Deaths Over Time',
            'Daily New Deaths'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['total_cases'],
            mode='lines',
            fill='tozeroy',
            line=dict(color='#1f77b4', width=2),
            fillcolor='rgba(31, 119, 180, 0.3)',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Cases: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['new_cases'],
            marker_color='#ff7f0e',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>New Cases: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['total_deaths'],
            mode='lines',
            fill='tozeroy',
            line=dict(color='#d62728', width=2),
            fillcolor='rgba(214, 39, 40, 0.3)',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Deaths: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['new_deaths'],
            marker_color='#9467bd',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>New Deaths: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text=f'COVID-19 Timeline: {country}',
        height=700,
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            bgcolor='white',
            activecolor='lightblue'
        ),
        row=1, col=1
    )
    
    return json.loads(fig.to_json())

def plot_correlation_heatmap(corr_data):
    if corr_data is None or len(corr_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough data for correlation analysis",
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(height=400)
        return json.loads(fig.to_json())
    
    if isinstance(corr_data, dict):
        columns = corr_data.get('columns', [])
        values = corr_data.get('values', [])
    elif isinstance(corr_data, pd.DataFrame):
        columns = corr_data.columns.tolist()
        values = corr_data.values.tolist()
    else:
        fig = go.Figure()
        fig.add_annotation(text="Invalid correlation data", showarrow=False)
        fig.update_layout(height=400)
        return json.loads(fig.to_json())
    
    if len(columns) == 0 or len(values) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No correlation data available", showarrow=False)
        fig.update_layout(height=400)
        return json.loads(fig.to_json())
    
    short_names = {
        'total_cases_per_million': 'Cases/M',
        'total_deaths_per_million': 'Deaths/M',
        'population_density': 'Pop Density',
        'median_age': 'Median Age',
        'gdp_per_capita': 'GDP/Capita',
        'life_expectancy': 'Life Exp',
        'aged_65_older': 'Age 65+'
    }
    
    display_names = [short_names.get(col, col) for col in columns]
    
    values_array = np.array(values, dtype=float)
    
    text_matrix = []
    for row in values_array:
        text_row = []
        for val in row:
            if np.isnan(val):
                text_row.append('')
            else:
                text_row.append(f'{val:.2f}')
        text_matrix.append(text_row)
    
    fig = go.Figure(data=go.Heatmap(
        z=values_array,
        x=display_names,
        y=display_names,
        colorscale='RdBu_r',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=text_matrix,
        texttemplate='%{text}',
        textfont={"size": 11, "color": "black"},
        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>',
        colorbar=dict(
            title=dict(text='Correlation'),
            thickness=15,
            len=0.7,
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=['-1.0', '-0.5', '0.0', '0.5', '1.0']
        )
    ))
    
    fig.update_layout(
        title=dict(
            text='Correlation Matrix: COVID-19 Metrics vs Country Characteristics',
            font=dict(size=16)
        ),
        height=550,
        width=750,
        xaxis=dict(
            tickangle=45,
            side='bottom'
        ),
        yaxis=dict(
            autorange='reversed'
        ),
        margin=dict(l=120, r=50, t=80, b=120)
    )
    
    return json.loads(fig.to_json())

def plot_monthly_trends(df, country):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"No monthly data available for {country}", showarrow=False)
        return json.loads(fig.to_json())
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=df['month'],
            y=df['new_cases'],
            name='New Cases',
            marker_color='#1f77b4',
            hovertemplate='Month: %{x}<br>Cases: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['month'],
            y=df['new_deaths'],
            name='New Deaths',
            mode='lines+markers',
            line=dict(color='#d62728', width=3),
            marker=dict(size=8),
            hovertemplate='Month: %{x}<br>Deaths: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title=f'Monthly COVID-19 Trends: {country}',
        xaxis_title='Month',
        height=500,
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="New Cases", secondary_y=False)
    fig.update_yaxes(title_text="New Deaths", secondary_y=True)
    fig.update_xaxes(tickangle=45)
    
    return json.loads(fig.to_json())

def plot_multi_country_comparison(df, countries, name_col):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No comparison data available", showarrow=False)
        return json.loads(fig.to_json())
    
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    fig = go.Figure()
    
    for i, country in enumerate(countries):
        country_data = df[df[name_col] == country].copy()
        country_data = country_data.sort_values('date')
        
        if country_data.empty:
            continue
        
        color = colors[i % len(colors)]
        
        country_data['new_cases_avg'] = country_data['new_cases'].rolling(window=7, min_periods=1).mean()
        
        fig.add_trace(
            go.Scatter(
                x=country_data['date'],
                y=country_data['new_cases_avg'],
                mode='lines',
                name=country,
                line=dict(color=color, width=2.5),
                hovertemplate=f'<b>{country}</b><br>Date: %{{x|%Y-%m-%d}}<br>New Cases (7-day avg): %{{y:,.0f}}<extra></extra>'
            )
        )
    
    fig.update_layout(
        title=dict(
            text='COVID-19 Daily New Cases Comparison (7-Day Average)',
            font=dict(size=18)
        ),
        xaxis_title='Date',
        yaxis_title='New Cases (7-Day Average)',
        height=550,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return json.loads(fig.to_json())

def plot_world_map(df):
    if 'iso_code' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="ISO codes not available for world map", showarrow=False)
        fig.update_layout(height=400)
        return json.loads(fig.to_json())
    
    df_clean = df.copy()
    
    df_clean = df_clean[df_clean['iso_code'].notna()]
    df_clean = df_clean[df_clean['iso_code'].astype(str).str.len() == 3]
    df_clean = df_clean[~df_clean['iso_code'].astype(str).str.startswith('OWID')]
    
    name_col = 'location' if 'location' in df_clean.columns else 'iso_code'
    
    numeric_cols = ['total_cases', 'total_deaths', 'total_cases_per_million', 
                    'total_deaths_per_million', 'population']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
    
    if 'total_cases' in df_clean.columns and 'total_deaths' in df_clean.columns:
        df_clean['death_rate'] = np.where(
            df_clean['total_cases'] > 0,
            (df_clean['total_deaths'] / df_clean['total_cases'] * 100).round(2),
            0
        )
    else:
        df_clean['death_rate'] = 0
    
    country_names = []
    total_cases_list = []
    total_deaths_list = []
    cases_per_m_list = []
    deaths_per_m_list = []
    death_rate_list = []
    population_list = []
    iso_codes = []
    
    for idx, row in df_clean.iterrows():
        iso_codes.append(str(row['iso_code']))
        country_names.append(str(row[name_col]) if pd.notna(row[name_col]) else str(row['iso_code']))
        total_cases_list.append(float(row.get('total_cases', 0)))
        total_deaths_list.append(float(row.get('total_deaths', 0)))
        cases_per_m_list.append(float(row.get('total_cases_per_million', 0)))
        deaths_per_m_list.append(float(row.get('total_deaths_per_million', 0)))
        death_rate_list.append(float(row.get('death_rate', 0)))
        population_list.append(float(row.get('population', 0)))
    
    color_values = cases_per_m_list if any(v > 0 for v in cases_per_m_list) else total_cases_list
    
    fig = go.Figure(data=go.Choropleth(
        locations=iso_codes,
        z=color_values,
        customdata=np.column_stack([
            country_names,
            total_cases_list,
            total_deaths_list,
            cases_per_m_list,
            deaths_per_m_list,
            death_rate_list,
            population_list
        ]),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "━━━━━━━━━━━━━━━━<br>" +
            "Total Cases: %{customdata[1]:,.0f}<br>" +
            "Total Deaths: %{customdata[2]:,.0f}<br>" +
            "Cases/Million: %{customdata[3]:,.0f}<br>" +
            "Deaths/Million: %{customdata[4]:,.0f}<br>" +
            "Death Rate: %{customdata[5]:.2f}%<br>" +
            "Population: %{customdata[6]:,.0f}" +
            "<extra></extra>"
        ),
        colorscale=[
            [0, '#ffffcc'],
            [0.1, '#ffeda0'],
            [0.2, '#fed976'],
            [0.3, '#feb24c'],
            [0.5, '#fd8d3c'],
            [0.7, '#fc4e2a'],
            [0.85, '#e31a1c'],
            [1, '#800026']
        ],
        autocolorscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar=dict(
            title=dict(text='Cases/Million'),
            thickness=15,
            len=0.7,
            tickformat=',',
            tickfont=dict(size=10)
        )
    ))
    
    fig.update_layout(
        title=dict(
            text='🌍 Global COVID-19 - Hover Over Countries for Details',
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        height=650,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='gray',
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            showocean=True,
            oceancolor='rgb(220, 235, 255)',
            showcountries=True,
            countrycolor='rgb(180, 180, 180)',
            countrywidth=0.5
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        hoverlabel=dict(
            bgcolor='white',
            font_size=13,
            font_family='Arial',
            bordercolor='#333'
        )
    )
    
    return json.loads(fig.to_json())

def plot_daily_trends_with_average(df, country):
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    df_copy = df_copy.sort_values('date')
    
    if df_copy.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"No daily data available for {country}", showarrow=False)
        return json.loads(fig.to_json())
    
    df_copy['cases_7day_avg'] = df_copy['new_cases'].rolling(window=7, min_periods=1).mean()
    df_copy['deaths_7day_avg'] = df_copy['new_deaths'].rolling(window=7, min_periods=1).mean()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Cases with 7-Day Average', 'Daily Deaths with 7-Day Average'),
        vertical_spacing=0.12
    )
    
    fig.add_trace(
        go.Bar(
            x=df_copy['date'],
            y=df_copy['new_cases'],
            name='Daily Cases',
            marker_color='rgba(31, 119, 180, 0.4)',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Cases: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_copy['date'],
            y=df_copy['cases_7day_avg'],
            mode='lines',
            name='7-Day Average (Cases)',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='Date: %{x|%Y-%m-%d}<br>7-Day Avg: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df_copy['date'],
            y=df_copy['new_deaths'],
            name='Daily Deaths',
            marker_color='rgba(214, 39, 40, 0.4)',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Deaths: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_copy['date'],
            y=df_copy['deaths_7day_avg'],
            mode='lines',
            name='7-Day Average (Deaths)',
            line=dict(color='#d62728', width=3),
            hovertemplate='Date: %{x|%Y-%m-%d}<br>7-Day Avg: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title_text=f'Daily Trends with 7 Day Moving Average: {country}',
        height=700,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all", label="All")
            ])
        ),
        row=1, col=1
    )
    
    return json.loads(fig.to_json())