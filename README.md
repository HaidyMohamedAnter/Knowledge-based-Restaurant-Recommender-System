Here is the updated **README.md** with the correct link:

---

# Knowledge-Based Restaurant Recommender System

## Overview

The **Knowledge-Based Restaurant Recommender System** allows users to discover restaurants based on explicit preferences such as cuisine, budget, location, and rating. This rule-based system does not require historical user behavior, eliminating the cold-start problem typically seen in collaborative filtering models. The application is built using **Streamlit**, providing a sleek and interactive user interface, and leverages the **Zomato Restaurants dataset**.

## Features

* **Customizable Filters**: Users can filter restaurants based on:

  * Cuisine
  * Budget
  * Location
  * Rating
* **Rule-based Recommendations**: The system generates restaurant recommendations based on the user-defined filters.
* **Explainable Recommendations**: The system provides clear explanations for why a restaurant is recommended (e.g., "matched on cuisine and cost").
* **User Feedback Integration**: Users can provide feedback on recommendations, which is stored for future analysis.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/knowledge-based-restaurant-recommender.git
   cd knowledge-based-restaurant-recommender
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate  # For Windows
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application locally:

   ```bash
   streamlit run app.py
   ```

## Features and Functionality

### User Input

* **Filters**: Users can select preferences based on cuisine, budget, location, and rating.
* **Custom Popularity Score**: A restaurant's popularity is calculated using a custom score combining various factors like ratings and user reviews.

### Backend Logic

* **Recommendation Engine**: Restaurants are recommended by filtering the dataset according to user preferences using a rule-based system.
* **Feedback Collection**: After receiving recommendations, users can rate their experience through a feedback form. All responses are saved for future evaluation.

### Evaluation

* **User Feedback**: User feedback is collected via a simple form capturing:

  * Satisfaction Level
  * Relevance Score (0-10)
  * Open Comments (for suggestions)

* The feedback data is stored in a CSV file for future analysis.

## Project Structure

```
/knowledge-based-restaurant-recommender
│
├── app.py               # Main Streamlit application file
├── scripts/
│   ├── data_preprocessing.py  # Data cleaning and preprocessing
│   └── recommendation.py     # Recommendation engine logic
├── data/
│   ├── zomato_data.csv  # Raw Zomato dataset
│   └── processed_data.csv  # Preprocessed dataset for filtering
├── feedback/
│   └── user_feedback.csv  # Stores feedback data from users
├── requirements.txt     # List of dependencies
└── README.md            # Project documentation
```

## Deployment

The app is hosted on **Streamlit Cloud**, allowing users to access it directly via a browser. No installation is required.

**Live App**: [Click here to open the app](https://knowledge-based-restaurant-recommender-system-5njlubs95cyq9rfn.streamlit.app/)

## Future Enhancements

* **Map View**: Integrating an interactive map (using Folium or Streamlit Maps) to display restaurant locations.
* **Visual Elements**: Including restaurant images or icons to enhance the user interface.
* **User Feedback-based Ranking**: Implement a ranking system that highlights the best-rated restaurants based on user feedback.
* **Sorting Options**: Allow users to toggle between sorting recommendations by popularity or rating.
