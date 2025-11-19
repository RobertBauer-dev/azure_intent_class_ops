import sys
from pathlib import Path

# Set up project path before importing config
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import numpy as np
import json
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn

import config

# Logging starten
mlflow.set_experiment("intent_classification")

# Daten laden
embeddings = np.load(config.PROJECT_ROOT / "data/embeddings/embeddings.npy")
with open(config.PROJECT_ROOT / "data/embeddings/labels.json") as f:
    labels = json.load(f)

# Labels encoden
le = LabelEncoder()
y = le.fit_transform(labels)
"""
# Example-mapping (alphabetically sorted):
"account_changes"     → 0
"delivery"            → 1
"general_question"    → 2
"login_problems"      → 3
"payment_issues"      → 4
"product_info"        → 5
"returns"             → 6
"security"            → 7
"subscription"        → 8
"technical_error"     → 9
"""

X_train, X_test, y_train, y_test = train_test_split(
    embeddings, y, test_size=0.2, random_state=42
)

with mlflow.start_run():
    
    # Hyperparameters
    C = 1.0
    penalty = "l2" # Ridge Regression
    
    mlflow.log_param("C", C)
    mlflow.log_param("penalty", penalty)

    # Modell
    # LR fast, stable, worked well for Embeddings, easy to serve
    clf = LogisticRegression(
        C=C,
        penalty=penalty,
        max_iter=2000,
        solver="liblinear" # liblinear is a good choice for small datasets (saga=better for large datasets)
    )
    clf.fit(X_train, y_train)

    # Evaluation
    acc = clf.score(X_test, y_test)
    mlflow.log_metric("accuracy", acc)

    print(f"✅ Test Accuracy: {acc:.3f}")

    # Speichern
    joblib.dump(clf, config.PROJECT_ROOT / "model/artifacts/model.pkl")
    joblib.dump(le, config.PROJECT_ROOT / "model/artifacts/label_encoder.pkl")

    mlflow.sklearn.log_model(clf, name="sklearn-model")

print("✅ Modell + LabelEncoder gespeichert")