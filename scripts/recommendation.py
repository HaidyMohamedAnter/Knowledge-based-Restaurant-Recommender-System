#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

class RestaurantRecommender:
    """Restaurant recommendation engine using knowledge-based filtering."""
    
    def __init__(self, data_path: str = "data/processed/restaurants.csv"):
        self.data_path = data_path
        self.df = self._load_data()
        self.cuisines = sorted(self._extract_unique_cuisines())
        self.cities = sorted(self.df['City'].unique()) if 'City' in self.df.columns else []
        self.localities = sorted(self.df['Locality'].unique()) if 'Locality' in self.df.columns else []
        
    def _load_data(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.data_path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Processed data file not found at {self.data_path}. Run data_preprocessing.py first."
            )
    
    def _extract_unique_cuisines(self) -> list:
        if 'Cuisines' not in self.df.columns:
            return []
        all_cuisines = []
        for cuisine_list in self.df['Cuisines'].dropna():
            if isinstance(cuisine_list, str):
                cuisines = [c.strip() for c in cuisine_list.split(',')]
                all_cuisines.extend(cuisines)
        return sorted(list(set(all_cuisines)))
    
    def filter_and_rank(self, 
                        cuisines=None, 
                        budget_category=None,
                        location=None,
                        city=None,
                        min_rating=0,
                        top_n=10) -> pd.DataFrame:
        filtered_df = self.df.copy()
        
        if cuisines and len(cuisines) > 0:
            cuisine_mask = filtered_df['Cuisines'].apply(
                lambda x: any(cuisine.lower() in str(x).lower() for cuisine in cuisines)
            )
            filtered_df = filtered_df[cuisine_mask]
        
        if budget_category and 'Budget Category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Budget Category'] == budget_category.lower()]
        
        if location and 'Locality' in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df['Locality'].str.lower().str.contains(location.lower()) |
                filtered_df['Locality Verbose'].str.lower().str.contains(location.lower())
                if 'Locality Verbose' in filtered_df.columns else False
            ]
        
        if city and 'City' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['City'].str.lower() == city.lower()]
        
        if min_rating > 0 and 'Aggregate rating' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Aggregate rating'] >= min_rating]
        
        if filtered_df.empty:
            return pd.DataFrame()
        
        if 'Popularity Score' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('Popularity Score', ascending=False)
        elif 'Aggregate rating' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('Aggregate rating', ascending=False)
        
        if 'Explanation' not in filtered_df.columns:
            filtered_df['Explanation'] = filtered_df.apply(
                lambda row: self.generate_explanation(row, cuisines, budget_category, location),
                axis=1
            )
        
        return filtered_df.head(top_n)
    
    def generate_explanation(self, row, cuisines=None, budget=None, location=None) -> str:
        explanation_parts = []
        
        if cuisines and 'Cuisines' in row and isinstance(row['Cuisines'], str):
            matched_cuisines = [c for c in cuisines if c.lower() in row['Cuisines'].lower()]
            if matched_cuisines:
                cuisine_str = ", ".join(matched_cuisines)
                explanation_parts.append(f"matches your preference for {cuisine_str} cuisine")
        
        if budget and 'Budget Category' in row:
            explanation_parts.append(f"fits your {budget} budget")
        
        if 'Aggregate rating' in row and row['Aggregate rating'] > 0:
            explanation_parts.append(f"has a rating of {row['Aggregate rating']:.1f}/5")
        
        if 'Votes' in row and row['Votes'] > 0:
            explanation_parts.append(f"has {int(row['Votes'])} reviews")
        
        if explanation_parts:
            return "This restaurant " + ", ".join(explanation_parts) + "."
        else:
            return "This restaurant might be a good match for you."

    def get_budget_options(self) -> list:
        if 'Budget Category' in self.df.columns:
            return sorted(self.df['Budget Category'].unique().tolist())
        return ['low', 'medium', 'high']

