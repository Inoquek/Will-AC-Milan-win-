import pandas as pd
def compute_rolling_features(df, home_stats, away_stats, window):
    df = df.sort_values("date").reset_index(drop=True)

    def calc_rolling(df, team_col, stat_cols, prefix):
        all_teams = []
        for team_id in df[team_col].unique():
            team_df = df[df[team_col] == team_id].copy()
            team_df = team_df.sort_values("date")

            for stat in stat_cols:
                colname = f"{prefix}_{stat}_rolling_{window}"
                team_df[colname] = (
                    team_df[stat].rolling(window=window, min_periods=1).mean().shift(1)
                )

            all_teams.append(team_df)

        return pd.concat(all_teams)

    df = calc_rolling(df, "home_team_code", home_stats, "home")
    df = calc_rolling(df, "away_team_code", away_stats, "away")

    return df
