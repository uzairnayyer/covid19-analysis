import pandas as pd
import numpy as np

def clean_data(df):
    df = df.copy()
    
    print("Original columns:", df.columns.tolist())
    
    df['date'] = pd.to_datetime(df['date'])
    
    if 'location' not in df.columns and 'iso_code' in df.columns:
        df['location'] = df['iso_code']
    
    if 'iso_code' in df.columns:
        df = df[df['iso_code'].str.len() == 3]
    
    if 'continent' in df.columns:
        df = df[df['continent'].notna()]
    
    numeric_columns = ['total_cases', 'new_cases', 'total_deaths', 'new_deaths',
                       'total_cases_per_million', 'new_cases_per_million',
                       'total_deaths_per_million', 'new_deaths_per_million',
                       'population', 'population_density', 'median_age',
                       'gdp_per_capita', 'life_expectancy', 'stringency_index']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    sort_col = 'location' if 'location' in df.columns else 'iso_code'
    df = df.sort_values([sort_col, 'date'])
    
    df['death_rate'] = np.where(
        df['total_cases'] > 0,
        (df['total_deaths'] / df['total_cases'] * 100).round(2),
        0
    )
    
    print("Cleaned columns:", df.columns.tolist())
    print("Sample data shape:", df.shape)
    
    return df

def get_latest_data(df):
    name_col = 'location' if 'location' in df.columns else 'iso_code'
    
    idx = df.groupby(name_col)['date'].idxmax()
    latest = df.loc[idx].copy()
    latest = latest.reset_index(drop=True)
    
    return latest

def fill_missing_for_country(df, country):
    name_col = 'location' if 'location' in df.columns else 'iso_code'
    country_df = df[df[name_col] == country].copy()
    country_df = country_df.sort_values('date')
    
    fill_cols = ['total_cases', 'total_deaths', 'new_cases', 'new_deaths']
    for col in fill_cols:
        if col in country_df.columns:
            country_df[col] = country_df[col].ffill().fillna(0)
    
    return country_df