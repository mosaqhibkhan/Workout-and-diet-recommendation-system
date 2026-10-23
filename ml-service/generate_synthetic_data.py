"""
Generate the SYNTHETIC experimental dataset used by the training pipeline.

THIS IS NOT REAL-WORLD FITNESS DATA. No person, coach or study is behind it.
See DATASET_CARD.md.

  * Weight: integer kg, uniform in [50, 100]
  * Height: integer cm, uniform in [150, 190]
  * BMI:    computed from Weight and Height, rounded to 2 decimals
  * Goal, Experience: uniform over the 3 x 3 categories
  * Plan:   the deterministic rule  GOAL_PREFIX + "_" + Experience
            (Cut -> FatLoss, Bulk -> MuscleGain, Maintain -> Maintenance)

Weight and Height are drawn independently, so many (Weight, Height) pairs are
physiologically unrealistic. Because the label is a pure function of Goal and
Experience, the numeric columns carry no information about the label by design.

Usage:  python generate_synthetic_data.py [--rows 2000] [--seed 42]
"""

import argparse

import numpy as np
import pandas as pd

from workout_ml import DATA_PATH, EXPERIENCES, FEATURES, GOALS, RANDOM_SEED, TARGET, compute_bmi, rule_based_plan


def generate(n_rows=2000, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    weight = rng.integers(50, 101, n_rows)
    height = rng.integers(150, 191, n_rows)
    goal = rng.choice(GOALS, n_rows)
    experience = rng.choice(EXPERIENCES, n_rows)
    df = pd.DataFrame({
        "Weight": weight.astype(float),
        "Height": height.astype(float),
        "BMI": compute_bmi(weight, height),
        "Goal": goal,
        "Experience": experience,
    })
    df[TARGET] = [rule_based_plan(g, e) for g, e in zip(goal, experience)]
    return df[FEATURES + [TARGET]]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rows", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--out", default=str(DATA_PATH))
    args = parser.parse_args()

    df = generate(args.rows, args.seed)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Fixed line endings so the file (and its SHA-256) is identical on every OS.
    df.to_csv(args.out, index=False, lineterminator="\n")
    print(f"Wrote {len(df)} SYNTHETIC rows to {args.out}")


if __name__ == "__main__":
    main()
