# Will AC Milan win?
I've been a fan of Milan since I was nine years old, and while I take great pride in their legacy, I can't say I'm proud of their current situation. With this project, I hope to predict that Milan(AC, not Inter...) wins all the matches(and other teams don't).

The app is built with **Streamlit** and allows users to interactively input match details and see live predictions.

## Features

- Predict match outcomes for AC Milan vs. any Serie A opponent
- Rolling average stats over the last 7 matches
- Interactive web app built with Streamlit
- Includes both manual and auto-predicted stats
- Model trained using `RandomForestClassifier`

## How to Set It Up

### 1. Clone the Repository

```bash
git clone https://github.com/Inoquek/Will-AC-Milan-win-.git
cd Will-AC-Milan-win-
```

### 2. Set Up Your Environment

**Option A: Using Conda**

```bash
conda env create -f environment.yml
conda activate Prediction_proj
```

**Option B: Using pip**

```bash
pip install -r requirements.txt
```

> Make sure you have Python 3.9+ installed.

### Run the App

```bash
streamlit run visual.py
```

### Predict Matches

- Choose if AC Milan is playing **home** or **away**
- Select the opponent
- Fill in match time and other stats
- Click "Predict Match" to see the result

## Project Structure

- `ml_final.ipynb` and `ml.ipynb` – Notebook where the model is trained and saved
- `matches_processed.csv` – Historical match dataset with engineered features
- `visual.py` – Streamlit app for predicting match results
- `serie_a_predictor.pkl` – Trained ML model
- `team_categories.pkl` – Encoded team list for model input

## Example Features Used

- Ball possession
- Total shots
- Goalkeeper saves
- Passes
- Free kicks
- Corner kicks
- Rolling averages of the above over last 7 matches

## Model Info

- Algorithm: RandomForestClassifier
- Evaluation metrics: Accuracy, Precision, F1-score
- Window size for rolling averages: 7 matches
