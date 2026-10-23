# Model Selection and Evaluation

This document explains how the workout-plan model is chosen and evaluated. All numbers come from `train_model.py` (model selection) and `evaluate_model.py` (held-out evaluation and feature analysis). Both save their output in `artifacts/model_metadata.json` and `reports/evaluation_results.json`. The runs used Python 3.13.2 and scikit-learn 1.7.2.

## Task and data

The task is a 9-class classification. The inputs are weight, height, BMI, goal and experience, and the output is one of nine workout plans. The training data is the synthetic dataset described in [DATASET_CARD.md](DATASET_CARD.md). Its labels are a fixed function of goal and experience. The questions the evaluation answers are:

1. Does a learned model reproduce the plan mapping on unseen rows?
2. Which inputs actually carry information?
3. What is the simplest model that does the job?

The evaluation is not a measure of real-world recommendation quality, because there are no real outcomes to measure against.

## Method

| Step | Implementation |
|---|---|
| Validation | `validate_dataset` checks schema, types, categories, ranges and BMI consistency; exact duplicates are dropped |
| Split | Stratified 80/20 train/test split, seed 42 (1,520 / 380 rows) |
| Preprocessing | One-hot encoding for `Goal` and `Experience` with fixed category lists; numeric columns passed through (standardised for logistic regression). The encoder lives inside a scikit-learn `Pipeline`, so it is fitted on training folds only and saved with the model. |
| Model selection | Stratified 5-fold cross-validation on the training split only |
| Selection rule | Highest mean macro-F1 among learned candidates. Scores within 0.005 count as a tie, and the simplest tied candidate wins. Candidates are ordered by number of input features, then single tree, linear model, 100-tree forest. |
| Final check | The selected model is fitted on the training split and evaluated once on the test split |
| Main metric | Macro-F1, which weights all nine classes equally. Accuracy, macro precision and macro recall are also reported. |

Encoding `Goal` as an integer (for example Bulk=0, Cut=1, Maintain=2) would invent an order the categories don't have, which is why one-hot encoding is used. `Experience` has a natural order, but each level maps to its own template, so one-hot encoding avoids assuming the levels are evenly spaced.

## Model selection (5-fold CV on the training split)

| Candidate | Type | Features | Macro-F1 (mean ± std) | Accuracy |
|---|---|---|---|---|
| Most-frequent class | baseline | none | 0.0243 ± 0.0003 | 0.1230 |
| Stratified random guess | baseline | none | 0.1080 ± 0.0103 | 0.1079 |
| Rule lookup | baseline | goal, experience | 1.0000 ± 0.0000 | 1.0000 |
| **Decision tree** | learned | goal, experience | **1.0000 ± 0.0000** | 1.0000 |
| Logistic regression | learned | goal, experience | 1.0000 ± 0.0000 | 1.0000 |
| Random forest | learned | goal, experience | 1.0000 ± 0.0000 | 1.0000 |
| Random forest | learned | weight, height, BMI | 0.0607 ± 0.0128 | 0.0618 |
| Logistic regression | learned | all five | 1.0000 ± 0.0000 | 1.0000 |
| Random forest | learned | all five | 1.0000 ± 0.0000 | 1.0000 |

Every learned model that sees goal and experience ties at 1.0. The selection rule picks the **decision tree on goal and experience**. Adding weight, height and BMI does not improve the score. Given only those three features, a random forest does worse than random guessing, because it fits noise.

## Selected model

The saved model is a `DecisionTreeClassifier` with depth 4 and 9 leaves, one leaf per plan. Its learned rules are shown condensed below; the full text is in `reports/evaluation_results.json` under `deployed_model.rules`:

```text
Experience_Beginner <= 0.5
├── Goal_Cut <= 0.5
│   ├── Goal_Bulk <= 0.5   → Experience_Advanced ? Maintenance_Advanced : Maintenance_Intermediate
│   └── Goal_Bulk  > 0.5   → Experience_Intermediate ? MuscleGain_Intermediate : MuscleGain_Advanced
└── Goal_Cut  > 0.5        → Experience_Advanced ? FatLoss_Advanced : FatLoss_Intermediate
Experience_Beginner > 0.5
├── Goal_Maintain > 0.5    → Maintenance_Beginner
└── Goal_Cut ? FatLoss_Beginner : MuscleGain_Beginner
```

The model is fully readable: it reproduces the goal × experience mapping and nothing else.

## Held-out test set (380 rows, evaluated once)

| Model | Accuracy | Macro precision | Macro recall | Macro-F1 |
|---|---|---|---|---|
| Decision tree (served) | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Rule lookup | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Stratified random guess | 0.1000 | 0.0995 | 0.1001 | 0.0989 |

- Each class has 37–47 test rows, and every class scores precision, recall and F1 of 1.00.
- The confusion matrix is diagonal.
- The served model agrees with the rule lookup on 100% of test rows.

## Feature relevance

To check whether body measurements carry any signal, `evaluate_model.py` fits a random forest on **all five** features (training split) and measures each feature's contribution on the test split.

| | Weight | Height | BMI | Goal | Experience |
|---|---|---|---|---|---|
| Permutation importance (macro-F1 drop, 20 repeats) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.6699 ± 0.0229 | 0.6697 ± 0.0184 |
| Impurity importance | 0.0047 | 0.0047 | 0.0062 | 0.15–0.16 per category | 0.16–0.19 per category |

- **Grouped permutation:** shuffling weight, height and BMI together, which keeps their correlation intact, also lowers macro-F1 by 0.0000.
- **Impurity importance is small but non-zero:** a forest still splits on noise features, which is why permutation importance on held-out data is the measure used to make decisions.
- **Positive control:** `tests/test_training.py` builds a label that really depends on BMI and checks that the same permutation method detects it. So the zero result above reflects the data, not a broken measurement.
- **Input sweep:** the served model was evaluated on every goal × experience combination across the full range the API accepts, from 20 to 300 kg and 100 to 250 cm in steps of 2. That is 96,444 inputs. No prediction differs from the rule lookup.

## Interpretation

- **The 1.0 scores show the model learned the plan mapping, not that it predicts well.** The labels are defined by goal and experience, so any model that sees those two fields can score perfectly.
- **A lookup table performs identically.** A trained model is used so the project demonstrates a complete train → evaluate → serve workflow, and the decision tree is the closest learned equivalent of that table.
- **The inputs that matter are goal and experience.** Weight, height and BMI add no information in this data.
- **Real-world evidence is still missing.** Showing that recommendations are personalized or effective would require real data with outcomes that are not already determined by the inputs, such as progress, adherence or coach-assigned plans.

## Reproducing

```bash
cd ml-service
pip install -r requirements-dev.txt
python generate_synthetic_data.py
python train_model.py
python evaluate_model.py
python -m pytest -q
```

Seed 42 is used for the data generator, the split, the CV folds, the models and permutation importance. With the pinned versions in `requirements.txt`, the dataset and `artifacts/workout_pipeline.joblib` rebuild byte-for-byte. `model_metadata.json` records the dataset hash, library versions and a training timestamp.
