
import streamlit as st
import pandas as pd
import joblib

ROLLING_WINDOW = 7

home_stats = [
    'Ball_possession_home', 'Total_shots_home', 'Goalkeeper_saves_home',
    'Corner_kicks_home', 'Passes_home', 'Free_kicks_home'
]
away_stats = [
    'Ball_possession_away', 'Total_shots_away', 'Goalkeeper_saves_away',
    'Corner_kicks_away', 'Passes_away', 'Free_kicks_away'
]

# Predictors used by the model (rolling ones + manually inputted)
rolling_features = [
    'home_Ball_possession_home_rolling_7', 'home_Total_shots_home_rolling_7',
    'home_Goalkeeper_saves_home_rolling_7', 'home_Corner_kicks_home_rolling_7',
    'home_Passes_home_rolling_7', 'home_Free_kicks_home_rolling_7',
    'away_Total_shots_away_rolling_7', 'away_Goalkeeper_saves_away_rolling_7',
    'away_Corner_kicks_away_rolling_7', 'away_Passes_away_rolling_7',
    'away_Free_kicks_away_rolling_7'
]

predictors = ['date', 'home_team', 'away_team', 'home_team_code', 'away_team_code',
       'hour', 'day_code', 'Ball_possession_home', 'Total_shots_home',
       'Total_shots_away', 'Goalkeeper_saves_home', 'Goalkeeper_saves_away',
       'Corner_kicks_home', 'Corner_kicks_away', 'Passes_home', 'Passes_away',
       'Free_kicks_home', 'Free_kicks_away', 'result',
       'home_Ball_possession_home_rolling_7',
       'home_Total_shots_home_rolling_7',
       'home_Goalkeeper_saves_home_rolling_7',
       'home_Corner_kicks_home_rolling_7', 'home_Passes_home_rolling_7',
       'home_Free_kicks_home_rolling_7', 'away_Total_shots_away_rolling_7',
       'away_Goalkeeper_saves_away_rolling_7',
       'away_Corner_kicks_away_rolling_7', 'away_Passes_away_rolling_7',
       'away_Free_kicks_away_rolling_7']

# Load model and data
model = joblib.load('serie_a_predictor.pkl')
categories = joblib.load('team_categories.pkl')
matches = pd.read_csv('matches_processed.csv')

if 'Ball_possession_away' not in matches.columns:
    matches['Ball_possession_away'] = 1 - matches['Ball_possession_home']

teams = sorted(set(matches['home_team'].dropna()).union(set(matches['away_team'].dropna())))

def get_team_rolling_dict(df, team_name, venue, home_stats, away_stats, window=7):
    """
    Returns a dictionary of rolling average stats for a specific team and venue ('home' or 'away').
    
    Parameters:
        df (pd.DataFrame): Match data with date column
        team_name (str): Team name (e.g., 'AC Milan')
        venue (str): 'home' or 'away'
        home_stats (list): List of home stat column names
        away_stats (list): List of away stat column names
        window (int): Rolling window size
        
    Returns:
        dict: { 'home_Total_shots_home_rolling_7': value, ... }
    """
    assert venue in ["home", "away"], "Venue must be 'home' or 'away'."

    stat_list = home_stats if venue == 'home' else away_stats
    rolling_features = {}

    # Filter matches for the team
    if venue == "home":
        team_matches = df[df["home_team"] == team_name]
    else:
        team_matches = df[df["away_team"] == team_name]

    team_matches = team_matches.sort_values("date")

    for stat in stat_list:
        colname = f"{venue}_{stat}_rolling_{window}"
        values = team_matches[stat].rolling(window=window, min_periods=1).mean().shift(1)
        rolling_features[colname] = values.iloc[-1] if not values.empty else 0.0

    return rolling_features


def predict_match(home_team, away_team, user_inputs, categories, model):
    try:
        home_code = categories.index(home_team)
        away_code = categories.index(away_team)
    except ValueError:
        return "Team not found in dataset.", False

    input_data = {
        'home_team_code': home_code,
        'away_team_code': away_code,
        'hour': user_inputs['hour'],
        'day_code': user_inputs['day_code'],
        'Ball_possession_home': user_inputs['Ball_possession_home'],
        'Ball_possession_away': user_inputs['Ball_possession_away'],
        'Total_shots_home': user_inputs['Total_shots_home'],
        'Total_shots_away': user_inputs['Total_shots_away'],
        'Goalkeeper_saves_home': user_inputs['Goalkeeper_saves_home'],
        'Goalkeeper_saves_away': user_inputs['Goalkeeper_saves_away'],
        'Corner_kicks_home': user_inputs['Corner_kicks_home'],
        'Corner_kicks_away': user_inputs['Corner_kicks_away'],
        'Passes_home': user_inputs['Passes_home'],
        'Passes_away': user_inputs['Passes_away'],
        'Free_kicks_home': user_inputs['Free_kicks_home'],
        'Free_kicks_away': user_inputs['Free_kicks_away']
    }

    rolling_stats_home = get_team_rolling_dict(matches, home_team, 'home', home_stats, away_stats, window=7)
    rolling_stats_away = get_team_rolling_dict(matches, away_team, 'away', home_stats, away_stats, window=7)
    for key, value in rolling_stats_home.items():
        input_data[key] = value
    for key, value in rolling_stats_away.items():
        input_data[key] = value
    del input_data['away_Ball_possession_away_rolling_7']  # Not needed, we have the home one
    del input_data['Ball_possession_away']  # This is not needed as we have the home one

    input_df = pd.DataFrame([input_data])
    prediction = model.predict(input_df)[0]

    result_mapping = {1: "Home Win", -1: "Away Win"}
    ac_milan_win = (home_team == 'AC Milan' and prediction == 1) or (away_team == 'AC Milan' and prediction == -1)
    return result_mapping.get(prediction, "Unknown"), ac_milan_win

# --- Streamlit App ---
st.title("Will AC Milan Win? - Serie A Match Predictor")
col1, col2 = st.columns(2)
with col1:
    team_type = st.selectbox("Is AC Milan the Home or Away Team?", ["Home", "Away"])
with col2:
    if team_type == "Home":
        home_team = "AC Milan"
        away_team = st.selectbox("Away Team", [t for t in teams if t != "AC Milan"])
    else:
        away_team = "AC Milan"
        home_team = st.selectbox("Home Team", [t for t in teams if t != "AC Milan"])

st.header("Manually Input Match Stats")
user_inputs = {}
user_inputs['hour'] = st.number_input("Match Hour (24h)", 0, 23, 20)
user_inputs['day_code'] = st.selectbox("Day of Week", range(7), format_func=lambda x: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][x])

numeric_fields = {
    'Ball_possession_home': 0.5,
    'Ball_possession_away': 0.5,
    'Total_shots_home': 12,
    'Total_shots_away': 10,
    'Goalkeeper_saves_home': 3,
    'Goalkeeper_saves_away': 3,
    'Corner_kicks_home': 5,
    'Corner_kicks_away': 5,
    'Passes_home': 0.75,
    'Passes_away': 0.75,
    'Free_kicks_home': 15,
    'Free_kicks_away': 15
}

for field, default in numeric_fields.items():
    user_inputs[field] = st.number_input(field.replace("_", " ").title(), value=default)

if st.button("Predict Match"):
    prediction, ac_milan_win = predict_match(home_team, away_team, user_inputs, categories, model)
    st.success(f"Prediction: {prediction}")
    if ac_milan_win:
        st.balloons()
        st.write("🎉 AC Milan is predicted to win! 🎉")
    else:
        st.snow()
        st.write("AC Milan is not predicted to win.")
