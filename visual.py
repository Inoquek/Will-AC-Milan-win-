import streamlit as st
import pandas as pd
import joblib
predictors = ['home_team_code', 'away_team_code', 'hour', 'day_code', 
              'Ball_possession_home', 
              'Total_shots_home', 'Total_shots_away',
              'Goalkeeper_saves_home', 'Goalkeeper_saves_away', 
              'Corner_kicks_home', 'Corner_kicks_away',
              'Passes_home', 'Passes_away',
              'Free_kicks_home', 'Free_kicks_away'] 

# Load model and team categories
model = joblib.load('serie_a_predictor.pkl')
categories = joblib.load('team_categories.pkl')

# Load dataset for team names
matches = pd.read_csv('matches_processed.csv')
teams = sorted(set(matches['home_team'].dropna()).union(set(matches['away_team'].dropna())))

# Filter predictors to available columns
predictors_available = [p for p in predictors if p in matches.columns or p in ['home_team_code', 'away_team_code', 'hour', 'day_code']]

# Function to calculate rolling averages for a team
def get_team_rolling_averages(team, df, stat_cols, n_matches=5):
    """
    Calculate rolling averages for a team over their last n_matches for given stats.
    Combines home and away stats (e.g., home_team's Ball_possession_home with away_team's Ball_possession_away).
    """
    team_matches = df[(df['home_team'] == team) | (df['away_team'] == team)].sort_values('date').tail(n_matches)
    averages = {}
    for stat in stat_cols:
        stat_away = stat.replace('_home','_away')
        if 'home' in stat and stat_away in df.columns:
            stat_values = pd.concat([
                team_matches[team_matches['home_team'] == team][stat],
                team_matches[team_matches['away_team'] == team][stat.replace('_home', '_away')]
            ])
        elif 'away' in stat and stat.replace('_away', '_home') in df.columns:
            stat_values = pd.concat([
                team_matches[team_matches['away_team'] == team][stat],
                team_matches[team_matches['home_team'] == team][stat.replace('_away', '_home')]
            ])
        else:
            stat_values = pd.Series([])
        averages[stat] = stat_values.mean() if len(stat_values) > 0 else 0
    return averages

# Prediction function
def predict_match(home_team, away_team, match_stats, categories, model, predictors):
    try:
        home_code = categories.index(home_team)
        away_code = categories.index(away_team)
    except ValueError:
        return "Team not found in dataset.", False
    
    input_data = pd.DataFrame({
        'home_team_code': [home_code],
        'away_team_code': [away_code],
        'hour': [match_stats.get('hour', 20)],
        'day_code': [match_stats.get('day_code', 5)],
        'ball_possession_home': [match_stats.get('ball_possession_home', 0.5)],
        'ball_possession_away': [match_stats.get('ball_possession_away', 0.5)],
        'total_shots_home': [match_stats.get('total_shots_home', 12)],
        'total_shots_away': [match_stats.get('total_shots_away', 10)],
        'goalkeeper_saves_home': [match_stats.get('goalkeeper_saves_home', 3)],
        'goalkeeper_saves_away': [match_stats.get('goalkeeper_saves_away', 3)],
        'corner_kicks_home': [match_stats.get('corner_kicks_home', 5)],
        'corner_kicks_away': [match_stats.get('corner_kicks_away', 5)],
        'passes_home': [match_stats.get('passes_home', 0.75)],
        'passes_away': [match_stats.get('passes_away', 0.75)],
        'free_kicks_home': [match_stats.get('free_kicks_home', 15)],
        'free_kicks_away': [match_stats.get('free_kicks_away', 15)]
    }, columns=predictors)
    
    input_data = input_data.fillna(input_data.median(numeric_only=True))
    prediction = model.predict(input_data)[0]
    result_mapping = {1: "Home Win", 0: "Draw", -1: "Away Win"}
    ac_milan_win = (home_team == 'AC Milan' and prediction == 1) or (away_team == 'AC Milan' and prediction == -1)
    return result_mapping.get(prediction, "Unknown"), ac_milan_win

# Streamlit app
st.title("Will AC Milan Win? - Serie A Match Predictor")
st.header("Predict an AC Milan Match")
col1, col2 = st.columns(2)
with col1:
    team_type = st.selectbox("Is AC Milan the Home or Away Team?", ["Home", "Away"])
with col2:
    if team_type == "Home":
        home_team = "AC Milan"
        away_team = st.selectbox("Away Team", [t for t in teams if t != "AC Milan"], key="away_team")
    else:
        away_team = "AC Milan"
        home_team = st.selectbox("Home Team", [t for t in teams if t != "AC Milan"], key="home_team")

st.subheader("Match Details")
st.write("Select the match time and day. Statistics are automatically calculated based on recent team performance (last 5 matches).")
match_stats = {}
match_stats['hour'] = st.number_input("Match Hour (24h)", min_value=0, max_value=23, value=20, step=1)
match_stats['day_code'] = st.selectbox("Day of Week", options=list(range(7)), format_func=lambda x: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][x], index=5)

# Display rolling averages for transparency
stat_cols = [p for p in predictors if p not in ['home_team_code', 'away_team_code', 'hour', 'day_code']]
home_averages = get_team_rolling_averages(home_team, matches, [s for s in stat_cols if 'home' in s])
away_averages = get_team_rolling_averages(away_team, matches, [s for s in stat_cols if 'away' in s])
st.write(f"**{home_team} Recent Form (Last 5 Matches):**")
for stat, value in home_averages.items():
    display_stat = stat.replace('_home', '').replace('_', ' ').title()
    st.write(f"{display_stat}: {value:.2f}")
st.write(f"**{away_team} Recent Form (Last 5 Matches):**")
for stat, value in away_averages.items():
    display_stat = stat.replace('_away', '').replace('_', ' ').title()
    st.write(f"{display_stat}: {value:.2f}")

if st.button("Predict Match"):
    prediction, ac_milan_win = predict_match(home_team, away_team, match_stats, categories, model, predictors_available)
    if prediction in ["Home Win", "Away Win"]:
        st.success(f"Prediction: {prediction}")
        if ac_milan_win:
            st.balloons()
            st.write("🎉 AC Milan is predicted to win! 🎉")
        else:
            st.snow()
            st.write("AC Milan is not predicted to win.")
    else:
        st.error(prediction)

# Upcoming matches
st.header("Upcoming AC Milan Matches Predictions")
st.write("Hypothetical upcoming matches involving AC Milan with predicted outcomes.")
upcoming_matches = [
    ('AC Milan', 'Inter', {'hour': 20, 'day_code': 5}),
    ('Napoli', 'AC Milan', {'hour': 18, 'day_code': 6})
]

upcoming_data = []
progress_bar = st.progress(0)
for i, (home, away, stats) in enumerate(upcoming_matches):
    prediction, ac_milan_win, _, _ = predict_match(home, away, stats, categories, model, predictors_available, matches)
    upcoming_data.append({
        'Home Team': home,
        'Away Team': away,
        'Prediction': prediction,
        'AC Milan Wins?': 'Yes' if ac_milan_win else 'No'
    })
    progress_bar.progress((i + 1) / len(upcoming_matches))
st.table(pd.DataFrame(upcoming_data))