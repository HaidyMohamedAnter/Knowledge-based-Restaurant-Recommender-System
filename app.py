#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import streamlit as st
import pandas as pd
import numpy as np
import os
import csv
import time
from datetime import datetime
from pathlib import Path
from scripts import data_preprocessing
from scripts.recommendation import RestaurantRecommender

# Page configuration
st.set_page_config(
    page_title="Restaurant Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
DATA_PATH = "data/processed/restaurants.csv"
RAW_DATA_PATH = "data/raw/zomato.csv"
FEEDBACK_FILE = r"C:\Users\hidoz\Desktop\Knowledge-based Restaurant Recommender System\feedback\user_feedback.csv"

# Ensure feedback file exists with headers
def ensure_feedback_file():
    feedback_dir = os.path.dirname(FEEDBACK_FILE)
    if feedback_dir and not os.path.exists(feedback_dir):
        try:
            os.makedirs(feedback_dir, exist_ok=True)
        except Exception as e:
            st.error(f"⚠️ Could not create feedback directory. Reason: {e}")
            return

    # If the file does not exist, create it with the necessary headers
    if not os.path.isfile(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "User", "Restaurant", "Feedback", "Rating", "Comment"])
        except Exception as e:
            st.error(f"⚠️ Could not create feedback file. Reason: {e}")

ensure_feedback_file()

# Custom CSS for better styling
st.markdown("""
<style>
    .restaurant-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .restaurant-name {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.2em;
    }
    .restaurant-detail {
        margin: 5px 0;
    }
    .explanation {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        font-style: italic;
    }
    .rating-high { color: #2e7d32; font-weight: bold; }
    .rating-medium { color: #ff9800; font-weight: bold; }
    .rating-low { color: #d32f2f; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_recommender():
    try:
        return RestaurantRecommender(DATA_PATH)
    except FileNotFoundError:
        st.error(f"Processed data not found at {DATA_PATH}")
        if os.path.exists(RAW_DATA_PATH):
            st.info("Raw data found. Please run preprocessing.")
            if st.button("Run Preprocessing"):
                with st.spinner("Processing data..."):
                    data_preprocessing.main()
                    st.success("Data processed! Reloading...")
                    time.sleep(2)
                    st.experimental_rerun()
        else:
            st.error(f"Raw data not found at {RAW_DATA_PATH}")
            st.markdown("[Download Zomato Dataset](https://www.kaggle.com/datasets/shrutimehta/zomato-restaurants-data)")
        st.stop()

def save_feedback(restaurant_name, feedback, comment, user_name=None, rating=None):
    feedback_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User": user_name or "Anonymous",
        "Restaurant": restaurant_name,
        "Feedback": feedback,
        "Rating": rating,
        "Comment": comment
    }
    try:
        with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=feedback_data.keys())
            writer.writerow(feedback_data)
    except Exception as e:
        st.error(f"⚠️ Could not save feedback. Reason: {e}")

def render_restaurant_card(restaurant, index=None):
    name = restaurant.get('Restaurant Name', 'Unknown')
    cuisines = restaurant.get('Cuisines', 'Various')
    rating = restaurant.get('Aggregate rating', 0)
    votes = int(restaurant.get('Votes', 0))
    cost = restaurant.get('Average Cost for two', 'Unknown')
    currency = restaurant.get('Currency', '')
    locality = restaurant.get('Locality Verbose', restaurant.get('Locality', 'Unknown'))
    explanation = restaurant.get('Explanation', '')

    rating_class = (
        "rating-high" if rating >= 4 else
        "rating-medium" if rating >= 3 else
        "rating-low"
    )

    st.markdown(f"""
    <div class="restaurant-card">
        <div class="restaurant-name">{name}</div>
        <div class="restaurant-detail">🍴 <b>Cuisine:</b> {cuisines}</div>
        <div class="restaurant-detail">⭐ <b>Rating:</b> <span class="{rating_class}">{rating}/5</span> ({votes} votes)</div>
        <div class="restaurant-detail">💰 <b>Cost for Two:</b> {currency}{cost}</div>
        <div class="restaurant-detail">📍 <b>Location:</b> {locality}</div>
        <div class="explanation">✨ {explanation}</div>
    </div>
    """, unsafe_allow_html=True)

    # Feedback section
    st.markdown("#### Feedback on this restaurant:")

    user_name = st.text_input("Your Name (optional):", key=f"user_name_{index}")
    rating_given = st.slider("Your Rating (1 to 5):", 1, 5, 3, 1, key=f"user_rating_{index}")

    feedback = st.radio(
        f"Was MYRECOMMENDER helpful?", 
        options=["Yes", "No", "Not sure"], 
        key=f"feedback_radio_{index}"
    )

    comment = st.text_area("Any additional feedback?", key=f"comment_{index}")

    if st.button(f"Submit Feedback for {name}", key=f"submit_{index}"):
        save_feedback(name, feedback, comment, user_name, rating_given)
        st.success(f"Thank you for your feedback on {name}!")
        if user_name:
            st.write(f"User: {user_name}")
        st.write(f"Rating: {rating_given}/5")
        st.write(f"Feedback: {feedback}")
        if comment:
            st.write(f"Comment: {comment}")

def main():
    st.title("🍽️ Restaurant Recommender")

    recommender = load_recommender()

    tab1, tab2 = st.tabs(["Recommendations", "Dataset Insights"])

    with tab1:
        st.markdown("Find restaurants based on your preferences.")

        st.sidebar.title("Your Preferences")
        cuisines = st.sidebar.multiselect("Select Cuisines", options=recommender.cuisines)

        city = st.sidebar.selectbox("City", options=["Any"] + recommender.cities)
        city = None if city == "Any" else city

        budget = st.sidebar.selectbox("Budget", options=["Any"] + recommender.get_budget_options())
        budget = None if budget == "Any" else budget

        min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.5, 0.5)
        num_recommendations = st.sidebar.slider("Number of Recommendations", 1, 20, 5, 1)

        search_button = st.sidebar.button("Find Restaurants")

        if search_button or st.session_state.get("show_recommendations", False):
            st.session_state["show_recommendations"] = True
            with st.spinner("Finding restaurants..."):
                results = recommender.filter_and_rank(
                    cuisines=cuisines,
                    budget_category=budget,
                    location=None,
                    city=city,
                    min_rating=min_rating,
                    top_n=num_recommendations
                )

            if not results.empty:
                st.subheader(f"Found {len(results)} Restaurants:")
                for idx, (_, row) in enumerate(results.iterrows()):
                    render_restaurant_card(row, index=idx)
            else:
                st.error("No restaurants match your criteria.")

    with tab2:
        st.subheader("📊 Dataset Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Restaurants", f"{len(recommender.df):,}")
        with col2:
            st.metric("Cuisines Available", f"{len(recommender.cuisines):,}")
        with col3:
            st.metric("Cities Covered", f"{len(recommender.cities):,}")

        st.markdown("### Sample Restaurants")
        sample = recommender.df.sample(min(5, len(recommender.df)))
        for idx, (_, row) in enumerate(sample.iterrows()):
            render_restaurant_card(row, index=f"sample_{idx}")

if __name__ == "__main__":
    main()
