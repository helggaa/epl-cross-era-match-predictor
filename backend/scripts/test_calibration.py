import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.dixon_coles import DixonColesModel

model = DixonColesModel()

test_cases = [
    ("Equal Teams (1500 vs 1500)", 1500, 1500),
    ("Slight Advantage (1600 vs 1500)", 1600, 1500),
    ("Moderate Advantage (1750 vs 1500)", 1750, 1500),
    ("Strong Advantage (1850 vs 1450)", 1850, 1450),
    ("Dominant Advantage (1950 vs 1350)", 1950, 1350),
    ("Extreme Advantage (2000 vs 1300)", 2000, 1300),
]

print("=== DIXON-COLES PROBABILITY CALIBRATION TEST ===")
for name, elo_a, elo_b in test_cases:
    res = model.predict_matchup(elo_a, elo_b)
    total = res["home_win_prob"] + res["draw_prob"] + res["away_win_prob"]
    print(f"\n{name}:")
    print(f"  Home Win: {res['home_win_prob']*100:.1f}% | Draw: {res['draw_prob']*100:.1f}% | Away Win: {res['away_win_prob']*100:.1f}% | Total: {total*100:.2f}%")
    print(f"  Expected Scoreline: {res['predicted_home_goals']:.2f} - {res['predicted_away_goals']:.2f}")
