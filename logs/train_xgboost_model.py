import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
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
    "num_questions_attempted", # "sequential_transition_rate", # Excluded if mostly NaN
    # Performance
    "accuracy", 
    # Deviation Features
    "mean_time_z_score", "min_time_z_score", "max_time_z_score", "std_dev_time_z_score",
    "accuracy_deviation", "tab_switch_deviation", "answer_change_deviation",
    # Proportions
    "proportion_questions_fast", "proportion_questions_correct_and_fast",
    "proportion_questions_with_tab_switch", "answer_change_rate"
]

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

# 1. Handle Missing Values (Example: Fill NaN with 0 or median/mean)
# Check for NaNs first
print("\nChecking for missing values...")
print(df[FEATURE_COLUMNS].isnull().sum())
# Simple strategy: fill NaNs with 0. Consider more sophisticated imputation if needed.
# Example: df['sequential_transition_rate'].fillna(df['sequential_transition_rate'].median(), inplace=True)
df.fillna(0, inplace=True) 
print("Filled potential NaN values with 0.")

# 2. Separate Features (X) and Target (y)
X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]
print(f"\nFeatures shape: {X.shape}")
print(f"Target shape: {y.shape}")
print(f"Target classes: {y.unique()}")

# 3. Encode Target Labels
# XGBoost requires numerical labels (0, 1, 2...)
# We assume extract_features.py now produces 0 for Normal, 1 for Cheat
y_encoded = y # The label column should already be 0 or 1
print(f"Labels as loaded: {np.unique(y_encoded)}")

# Define the expected class names for reporting
binary_class_names = ["Normal", "Cheat"]

# 4. Split Data into Training and Testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, 
    test_size=0.2,      # 80% training, 20% testing
    random_state=42,    # For reproducibility
    stratify=y_encoded  # Ensure class distribution is similar in train/test splits
)
print(f"\nTraining set shape: X={X_train.shape}, y={y_train.shape}")
print(f"Testing set shape: X={X_test.shape}, y={y_test.shape}")

# 5. Scale Features 
# Good practice, especially if considering other models later
print("\nScaling features using StandardScaler...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train) # Fit only on training data
X_test_scaled = scaler.transform(X_test)       # Transform test data using the same scaler

# --- Model Training ---
print("\nTraining XGBoost Classifier for Binary Classification...")

# Initialize XGBoost Classifier for Binary task
model = xgb.XGBClassifier(
    objective='binary:logistic', # Objective for binary classification
    # num_class is not needed for binary classification
    n_estimators=100,          
    learning_rate=0.1,         
    max_depth=3,               
    use_label_encoder=False,   
    eval_metric='logloss',    # Common metric for binary classification probability
    random_state=42
)

# Train the model using scaled data
eval_set = [(X_train_scaled, y_train), (X_test_scaled, y_test)]
model.fit(X_train_scaled, y_train, 
          eval_set=eval_set, 
          verbose=False)

print("Training complete.")

# --- Model Evaluation ---
print("\nEvaluating model on the test set...")

# Make predictions (outputs 0 or 1)
y_pred = model.predict(X_test_scaled)
# Optional: Predict probabilities if needed
# y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] 

# Calculate Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Classification Report (Precision, Recall, F1-score for Normal/Cheat)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=binary_class_names))

# Confusion Matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
# Display with correct labels
print(pd.DataFrame(cm, index=binary_class_names, columns=binary_class_names))

# --- Feature Importance (Optional but insightful) ---
print("\nPlotting feature importances...")
try:
    fig, ax = plt.subplots(figsize=(10, 8)) # Adjust figure size if needed
    xgb.plot_importance(model, ax=ax, max_num_features=20) # Show top 20 features
    plt.title("XGBoost Feature Importance (Top 20)")
    plt.tight_layout()
    # Save the plot
    importance_plot_path = os.path.join(SCRIPT_DIR, "xgboost_feature_importance.png")
    plt.savefig(importance_plot_path)
    print(f"Feature importance plot saved to: {importance_plot_path}")
    # plt.show() # Uncomment to display plot directly if running interactively
except Exception as e:
    print(f"Could not plot feature importance: {e}")

print("\nScript finished.") 