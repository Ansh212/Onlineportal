import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier # Changed import
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler # Optional but keep for consistency
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt # For plotting feature importance
import os

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(SCRIPT_DIR, "features_dataset.csv")
TARGET_COLUMN = "label"
# Define feature columns explicitly (excluding identifiers and label)
FEATURE_COLUMNS = [
    # Overall Timing
    "total_duration", "time_until_first_answer", "time_between_last_answer_and_submit",
    # Aggregated Timings
    "mean_time_per_question", "std_dev_time_per_question", "median_time_per_question",
    "min_time_per_question", "max_time_per_question",
    # Activity Counts
    "num_tab_switches", "num_answer_changes", "num_revisits",
    # Navigation / Attempt Rate
    "num_questions_attempted",
    # Performance
    "accuracy",
    # Deviation Features
    "mean_time_z_score", "min_time_z_score", "max_time_z_score", "std_dev_time_z_score",
    "accuracy_deviation", "tab_switch_deviation", "answer_change_deviation",
    # Proportions
    "proportion_questions_fast", "proportion_questions_correct_and_fast",
    "proportion_questions_with_tab_switch", "answer_change_rate"
]
# Define the expected class names for reporting
binary_class_names = ["Normal", "Cheat"]

# --- Load Data ---
print(f"Loading dataset from: {DATASET_PATH}")
try:
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
except FileNotFoundError:
    print(f"Error: Dataset file not found at {DATASET_PATH}")
    print("Please run extract_features.py first.")
    exit(1)
except Exception as e:
     print(f"Error loading dataset: {e}")
     exit(1)

# --- Preprocessing ---
print("\\nChecking for missing values (and filling with 0)...")
print(df[FEATURE_COLUMNS].isnull().sum().loc[lambda x : x > 0])
df.fillna(0, inplace=True)
print("Filled potential NaN values with 0.")

# Separate Features (X) and Target (y)
X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN] # Should be 0 or 1
print(f"\\nFeatures shape: {X.shape}")
print(f"Target shape: {y.shape}")
print(f"Target classes: {y.unique()}")
if not all(item in [0, 1] for item in y.unique()):
    print("Warning: Target column contains values other than 0 and 1.")

# Split Data into Training and Testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
print(f"\\nTraining set shape: X={X_train.shape}, y={y_train.shape}")
print(f"Testing set shape: X={X_test.shape}, y={y_test.shape}")

# Scale Features (Optional for RF, but kept for consistency if comparing models)
print("\\nScaling features using StandardScaler...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- Model Training ---
print("\\nTraining Random Forest Classifier...")
# Using default parameters (e.g., n_estimators=100). Can be tuned.
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1) # n_jobs=-1 uses all processors
# Use scaled data for consistency, though RF is less sensitive to scaling
model.fit(X_train_scaled, y_train)
print("Training complete.")

# --- Model Evaluation ---
print("\\nEvaluating model on the test set...")
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=binary_class_names))
print("\\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(pd.DataFrame(cm, index=binary_class_names, columns=binary_class_names))

# --- Feature Importance --- 
print("\\nPlotting feature importances...")
importances = model.feature_importances_
indices = np.argsort(importances)[::-1] # Get indices of features sorted by importance
num_features_to_plot = 20

try:
    plt.figure(figsize=(10, 8))
    plt.title(f"Random Forest Feature Importance (Top {num_features_to_plot})")
    plt.bar(range(num_features_to_plot), importances[indices[:num_features_to_plot]], align='center')
    plt.xticks(range(num_features_to_plot), [FEATURE_COLUMNS[i] for i in indices[:num_features_to_plot]], rotation=90)
    plt.xlim([-1, num_features_to_plot])
    plt.ylabel("Importance (Gini Impurity Reduction)")
    plt.tight_layout()
    # Save the plot
    importance_plot_path = os.path.join(SCRIPT_DIR, "random_forest_feature_importance.png")
    plt.savefig(importance_plot_path)
    print(f"Feature importance plot saved to: {importance_plot_path}")
except Exception as e:
    print(f"Could not plot feature importance: {e}")

print("\\nScript finished.") 