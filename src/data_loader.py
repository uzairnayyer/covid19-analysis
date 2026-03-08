import pandas as pd
import os

def load_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'owid-covid-data.csv')
    df = pd.read_csv(data_path)
    print("=" * 50)
    print("Dataset loaded successfully!")
    print("Columns found:", df.columns.tolist())
    print("Shape:", df.shape)
    print("=" * 50)
    return df

def get_countries(df):
    name_col = 'location' if 'location' in df.columns else 'iso_code'
    
    if 'iso_code' in df.columns:
        valid_df = df[df['iso_code'].str.len() == 3]
    else:
        valid_df = df
    
    countries = valid_df[name_col].dropna().unique()
    return sorted([str(c) for c in countries if pd.notna(c)])

def get_continents(df):
    if 'continent' not in df.columns:
        return []
    continents = df['continent'].dropna().unique()
    return sorted([str(c) for c in continents])

def get_country_name_column(df):
    if 'location' in df.columns:
        return 'location'
    return 'iso_code'