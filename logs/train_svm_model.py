import pandas as pd
import numpy as np
from sklearn.svm import SVC # Changed import
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler # Keep scaling
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
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

# Scale Features (Important for SVM)
print("\\nScaling features using StandardScaler...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- Model Training ---
print("\\nTraining Support Vector Machine (SVM) Classifier...")
# Using default parameters (RBF kernel, C=1.0). Consider tuning these.
model = SVC(random_state=42, probability=True) # probability=True for predict_proba if needed
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

# --- Feature Importance (Not directly available like tree models) ---
# For SVM, importance is less direct. Can use techniques like permutation importance
# or examining coefficients for linear kernels, but not shown here for simplicity.
print("\\n(SVM feature importance is less direct and not calculated here)")

print("\\nScript finished.") 