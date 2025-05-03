#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path

def create_directories():
    """Create necessary directories if they don't exist."""
    Path("data/processed").mkdir(parents=True, exist_ok=True)

def load_data():
    """
    Load the raw Zomato dataset with encoding handling.
    Tries multiple encodings to handle potential encoding issues.
    """
    file_path = "data/raw/zomato.csv"
    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            exit(1)
    exit(1)

def clean_data(df):
    """Clean the dataset by removing duplicates and handling missing values."""
    df = df.drop_duplicates()
    relevant_columns = [
        'Restaurant ID', 'Restaurant Name', 'Country Code', 'City', 'Address',
        'Locality', 'Locality Verbose', 'Cuisines', 'Price range', 'Currency',
        'Average Cost for two', 'Aggregate rating', 'Rating text', 'Votes'
    ]
    df = df[[col for col in relevant_columns if col in df.columns]]
    df = df.dropna(subset=['Restaurant Name', 'Cuisines'])
    df['Aggregate rating'] = df['Aggregate rating'].fillna(0)
    df['Votes'] = df['Votes'].fillna(0)
    df['Average Cost for two'] = df['Average Cost for two'].fillna(df['Average Cost for two'].median())
    return df

def normalize_categories(df):
    """Normalize categorical values."""
    df['Cuisines'] = df['Cuisines'].str.lower().str.strip()
    df['Primary Cuisine'] = df['Cuisines'].apply(lambda x: x.split(',')[0].strip() if isinstance(x, str) else x)
    df['City'] = df['City'].str.lower().str.strip()
    return df

def engineer_features(df):
    """Create additional features for recommendation."""
    df['Average Cost for two'] = pd.to_numeric(df['Average Cost for two'], errors='coerce').fillna(df['Average Cost for two'].median())
    df['Aggregate rating'] = pd.to_numeric(df['Aggregate rating'], errors='coerce').fillna(0)
    df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce').fillna(0)

    cost_percentiles = df['Average Cost for two'].quantile([0.33, 0.66]).values
    def categorize_cost(cost):
        if cost <= cost_percentiles[0]: return 'low'
        elif cost <= cost_percentiles[1]: return 'medium'
        else: return 'high'
    df['Budget Category'] = df['Average Cost for two'].apply(categorize_cost)

    if df['Aggregate rating'].max() > 5:
        df['Aggregate rating'] = df['Aggregate rating'] / 2

    df['Normalized Votes'] = np.log1p(df['Votes'])
    max_votes = df['Normalized Votes'].max()
    if max_votes > 0:
        df['Normalized Votes'] = df['Normalized Votes'] / max_votes
    df['Popularity Score'] = 0.7 * df['Aggregate rating'] / 5 + 0.3 * df['Normalized Votes']
    return df

def save_processed_data(df, output_path="data/processed/restaurants.csv"):
    """Save the processed dataframe to CSV."""
    try:
        df.to_csv(output_path, index=False, encoding='utf-8')
    except:
        df.to_csv(output_path, index=False, encoding='latin1')

def main():
    """Main function to orchestrate the data preprocessing pipeline."""
    create_directories()
    df = load_data()
    df = clean_data(df)
    df = normalize_categories(df)
    df = engineer_features(df)
    save_processed_data(df)

if __name__ == "__main__":
    main()
