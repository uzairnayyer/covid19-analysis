import pandas as pd
import numpy as np

def get_name_col(df):
    return 'location' if 'location' in df.columns else 'iso_code'

def get_top_countries_by_cases(df, n=10):
    name_col = get_name_col(df)
    latest = df.groupby(name_col)['total_cases'].max().reset_index()
    latest.columns = ['country', 'total_cases']
    latest = latest.dropna(subset=['total_cases'])
    top = latest.nlargest(n, 'total_cases')
    return top

def get_top_countries_by_deaths(df, n=10):
    name_col = get_name_col(df)
    latest = df.groupby(name_col)['total_deaths'].max().reset_index()
    latest.columns = ['country', 'total_deaths']
    latest = latest.dropna(subset=['total_deaths'])
    top = latest.nlargest(n, 'total_deaths')
    return top

def get_death_rate_comparison(df, n=20):
    name_col = get_name_col(df)
    
    idx = df.groupby(name_col)['date'].idxmax()
    latest = df.loc[idx].copy()
    latest = latest.reset_index(drop=True)
    
    latest = latest[latest['total_cases'] > 100000]
    latest['death_rate'] = np.where(
        latest['total_cases'] > 0,
        (latest['total_deaths'] / latest['total_cases'] * 100).round(2),
        0
    )
    
    top = latest.nlargest(n, 'death_rate')[[name_col, 'death_rate', 'total_cases', 'total_deaths']].copy()
    top = top.rename(columns={name_col: 'country'})
    return top

def get_continent_comparison(df):
    name_col = get_name_col(df)
    
    if 'continent' not in df.columns:
        return pd.DataFrame()
    
    idx = df.groupby(name_col)['date'].idxmax()
    latest = df.loc[idx].copy()
    latest = latest.reset_index(drop=True)
    
    continent_stats = latest.groupby('continent').agg({
        'total_cases': 'sum',
        'total_deaths': 'sum',
        'population': 'sum'
    }).reset_index()
    
    continent_stats['cases_per_million'] = np.where(
        continent_stats['population'] > 0,
        (continent_stats['total_cases'] / continent_stats['population'] * 1000000).round(2),
        0
    )
    continent_stats['deaths_per_million'] = np.where(
        continent_stats['population'] > 0,
        (continent_stats['total_deaths'] / continent_stats['population'] * 1000000).round(2),
        0
    )
    continent_stats['death_rate'] = np.where(
        continent_stats['total_cases'] > 0,
        (continent_stats['total_deaths'] / continent_stats['total_cases'] * 100).round(2),
        0
    )
    
    return continent_stats

def get_country_timeline(df, country):
    name_col = get_name_col(df)
    country_df = df[df[name_col] == country].copy()
    country_df = country_df.sort_values('date')
    
    cols_to_keep = ['date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths']
    if 'stringency_index' in country_df.columns:
        cols_to_keep.append('stringency_index')
    
    available_cols = [c for c in cols_to_keep if c in country_df.columns]
    country_df = country_df[available_cols].copy()
    
    country_df['total_cases'] = pd.to_numeric(country_df['total_cases'], errors='coerce').fillna(0)
    country_df['total_deaths'] = pd.to_numeric(country_df['total_deaths'], errors='coerce').fillna(0)
    country_df['new_cases'] = pd.to_numeric(country_df['new_cases'], errors='coerce').fillna(0)
    country_df['new_deaths'] = pd.to_numeric(country_df['new_deaths'], errors='coerce').fillna(0)
    
    return country_df

def get_correlation_analysis(df):
    name_col = get_name_col(df)
    
    idx = df.groupby(name_col)['date'].idxmax()
    latest = df.loc[idx].copy()
    latest = latest.reset_index(drop=True)
    
    analysis_cols = ['total_cases_per_million', 'total_deaths_per_million',
                     'population_density', 'median_age', 'gdp_per_capita',
                     'life_expectancy', 'aged_65_older']
    
    available_cols = [c for c in analysis_cols if c in latest.columns]
    
    if len(available_cols) < 2:
        return {'columns': [], 'values': []}
    
    correlation_data = latest[available_cols].copy()
    
    for col in available_cols:
        correlation_data[col] = pd.to_numeric(correlation_data[col], errors='coerce')
    
    correlation_data = correlation_data.dropna()
    
    if len(correlation_data) < 5:
        return {'columns': [], 'values': []}
    
    correlation_matrix = correlation_data.corr()
    
    result = {
        'columns': correlation_matrix.columns.tolist(),
        'values': correlation_matrix.values.tolist()
    }
    
    return result

def get_monthly_trends(df, country):
    name_col = get_name_col(df)
    country_df = df[df[name_col] == country].copy()
    country_df['month'] = country_df['date'].dt.to_period('M')
    
    monthly = country_df.groupby('month').agg({
        'new_cases': 'sum',
        'new_deaths': 'sum'
    }).reset_index()
    
    monthly['month'] = monthly['month'].astype(str)
    monthly['new_cases'] = pd.to_numeric(monthly['new_cases'], errors='coerce').fillna(0)
    monthly['new_deaths'] = pd.to_numeric(monthly['new_deaths'], errors='coerce').fillna(0)
    return monthly

def get_comparison_data(df, countries):
    name_col = get_name_col(df)
    filtered = df[df[name_col].isin(countries)].copy()
    filtered = filtered.sort_values(['date'])
    
    for col in ['total_cases', 'total_deaths', 'new_cases', 'new_deaths',
                'total_cases_per_million', 'total_deaths_per_million']:
        if col in filtered.columns:
            filtered[col] = pd.to_numeric(filtered[col], errors='coerce').fillna(0)
    
    return filtered, name_col

def get_world_map_data(df):
    name_col = get_name_col(df)
    
    idx = df.groupby(name_col)['date'].idxmax()
    latest = df.loc[idx].copy()
    latest = latest.reset_index(drop=True)
    
    return latest