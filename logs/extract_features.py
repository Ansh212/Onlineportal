import os
import json
import datetime
import numpy as np
import pandas as pd
from collections import defaultdict
import math
import time

# --- Configuration ---
# Assumes this script is in the 'logs' directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(SCRIPT_DIR, "generated_logs_2") # Input logs directory
GLOBAL_STATS_FILE = os.path.join(SCRIPT_DIR, "global_stats.json") # Input global stats
OUTPUT_CSV_FILE = os.path.join(SCRIPT_DIR, "features_dataset.csv") # Output dataset

# --- Define Cheating Persona Keywords ---
# Add any other keywords that identify cheating logs
CHEAT_KEYWORDS = ["pre_knowledge", "cheater_tab_switcher", "cheater_smart", "cheater_slow_careful"]
NORMAL_PERSONAS = ["topper", "average", "slow_careful", "overconfident", "struggler"]

# --- Load Static Data ---

# Question Data (Needs to be consistent with generation/global stats)
questions_data = [
    # Maths
    {"id": "q1", "subject": "Maths", "difficulty": "Easy", "text": "If x^2 - 5x + 6 = 0, find x.", "options": ["1 and 6", "2 and 3", "3 and 4", "None"], "correct_answer": 1},
    {"id": "q2", "subject": "Maths", "difficulty": "Easy", "text": "Derivative of sin(x)?", "options": ["cos(x)", "-cos(x)", "-sin(x)", "sin(x)"], "correct_answer": 0},
    {"id": "q3", "subject": "Maths", "difficulty": "Easy", "text": "Distance between (1,2) and (4,6)?", "options": ["5", "4", "3", "2"], "correct_answer": 0},
    {"id": "q4", "subject": "Maths", "difficulty": "Medium", "text": "If det(A) = 5, what is det(2A)?", "options": ["10", "20", "25", "40"], "correct_answer": 1},
    {"id": "q5", "subject": "Maths", "difficulty": "Medium", "text": "Evaluate ∫x^2 dx.", "options": ["x^2/2", "x^3/3", "x^3", "x^2"], "correct_answer": 1},
    {"id": "q6", "subject": "Maths", "difficulty": "Medium", "text": "If z = 1+i, find |z|.", "options": ["1", "√2", "2", "√3"], "correct_answer": 1},
    {"id": "q7", "subject": "Maths", "difficulty": "Medium", "text": "Find equation of line: slope 2 through (1,3).", "options": ["y=2x+1", "y-3=2(x-1)", "y=x+2", "y=2x-3"], "correct_answer": 1},
    {"id": "q8", "subject": "Maths", "difficulty": "Hard", "text": "Solve sin(2x)=√3/2.", "options": ["x=30°,150°", "x=45°", "x=60°", "None"], "correct_answer": 0},
    {"id": "q9", "subject": "Maths", "difficulty": "Hard", "text": "Solve log(x^2-5x+6)=0.", "options": ["x=2,3", "x=1,6", "x=3,4", "x=1,2"], "correct_answer": 0},
    {"id": "q10", "subject": "Maths", "difficulty": "Hard", "text": "Area between y=x^2 and y=x (0 to 1)?", "options": ["1/6", "1/3", "1/2", "1"], "correct_answer": 0},
    {"id": "q11", "subject": "Physics", "difficulty": "Easy", "text": "Unit of Force?", "options": ["Joule", "Newton", "Pascal", "Watt"], "correct_answer": 1},
    {"id": "q12", "subject": "Physics", "difficulty": "Easy", "text": "g on Earth?", "options": ["8.9", "9.8", "10.2", "9"], "correct_answer": 1},
    {"id": "q13", "subject": "Physics", "difficulty": "Easy", "text": "Resistance if V=10V, I=2A?", "options": ["20Ω", "5Ω", "2Ω", "10Ω"], "correct_answer": 1},
    {"id": "q14", "subject": "Physics", "difficulty": "Medium", "text": "Law of electromagnetic induction?", "options": ["Lenz", "Newton", "Ohm", "Ampere"], "correct_answer": 0},
    {"id": "q15", "subject": "Physics", "difficulty": "Medium", "text": "Speed of light?", "options": ["3x10^8", "3x10^6", "3x10^5", "Both A & C"], "correct_answer": 0},
    {"id": "q16", "subject": "Physics", "difficulty": "Medium", "text": "Time to fall 20m (g=10)?", "options": ["2s", "3s", "4s", "2s"], "correct_answer": 0},
    {"id": "q17", "subject": "Physics", "difficulty": "Medium", "text": "Electric field at r from q?", "options": ["q/4πε₀r", "q/4πε₀r²", "q/r", "q/r²"], "correct_answer": 1},
    {"id": "q18", "subject": "Physics", "difficulty": "Hard", "text": "Block on incline θ=30°, L=5m, time?", "options": ["1s", "2s", "3s", "4s"], "correct_answer": 1},
    {"id": "q19", "subject": "Physics", "difficulty": "Hard", "text": "Freq LC circuit L=1H, C=1μF?", "options": ["50Hz", "5kHz", "159Hz", "159kHz"], "correct_answer": 3},
    {"id": "q20", "subject": "Physics", "difficulty": "Hard", "text": "Photon energy of 500nm light?", "options": ["3.98eV", "2.48eV", "1.24eV", "4.13eV"], "correct_answer": 1},
    {"id": "q21", "subject": "Chemistry", "difficulty": "Easy", "text": "Atomic number of Oxygen?", "options": ["6", "7", "8", "9"], "correct_answer": 2},
    {"id": "q22", "subject": "Chemistry", "difficulty": "Easy", "text": "Valency of Nitrogen?", "options": ["2", "3", "4", "5"], "correct_answer": 1},
    {"id": "q23", "subject": "Chemistry", "difficulty": "Easy", "text": "Hybridization in CH₄?", "options": ["sp", "sp²", "sp³", "dsp²"], "correct_answer": 2},
    {"id": "q24", "subject": "Chemistry", "difficulty": "Medium", "text": "Oxidizer in Zn + CuSO₄?", "options": ["Zn", "CuSO₄", "Cu", "ZnSO₄"], "correct_answer": 1},
    {"id": "q25", "subject": "Chemistry", "difficulty": "Medium", "text": "Identify nucleophile?", "options": ["NH₃", "H₂O", "NO₃⁻", "SO₄²⁻"], "correct_answer": 0},
    {"id": "q26", "subject": "Chemistry", "difficulty": "Medium", "text": "Moles in 22.4L at STP?", "options": ["1", "2", "0.5", "1.5"], "correct_answer": 0},
    {"id": "q27", "subject": "Chemistry", "difficulty": "Medium", "text": "pH of 0.01M HCl?", "options": ["1", "2", "3", "4"], "correct_answer": 0},
    {"id": "q28", "subject": "Chemistry", "difficulty": "Hard", "text": "ΔH with given bond energies?", "options": ["-184kJ", "-117kJ", "+184kJ", "+117kJ"], "correct_answer": 0},
    {"id": "q29", "subject": "Chemistry", "difficulty": "Hard", "text": "Lattice energy order?", "options": ["NaCl", "KCl", "RbCl", "CsCl"], "correct_answer": 0},
    {"id": "q30", "subject": "Chemistry", "difficulty": "Hard", "text": "Rate law (2nd order)?", "options": ["k[A]", "k[A]^2", "k[B]", "k[A][B]"], "correct_answer": 1},
]
question_details = {q["id"]: q for q in questions_data}

# Load Global Stats
try:
    with open(GLOBAL_STATS_FILE, 'r') as f:
        global_stats = json.load(f)
    print(f"Successfully loaded global stats from {GLOBAL_STATS_FILE}")
except FileNotFoundError:
    print(f"Error: Global stats file not found at {GLOBAL_STATS_FILE}")
    print("Please run calculate_global_stats.py first.")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {GLOBAL_STATS_FILE}")
    exit(1)

# --- Helper Functions ---
def parse_timestamp(ts_str):
    if not ts_str: return None
    if ts_str.endswith('Z'): ts_str = ts_str[:-1] + '+00:00'
    try: return datetime.datetime.fromisoformat(ts_str)
    except (ValueError, TypeError): return None

def calculate_time_z_score(user_time, q_id, global_stats):
    """Calculates the Z-score for time spent on a question."""
    if q_id not in global_stats: return 0.0 # Or handle as missing data
    
    stats = global_stats[q_id]
    mean = stats.get("global_avg_time", 0.0)
    std_dev = stats.get("global_std_dev_time", 0.0)
    
    if std_dev > 1e-6: # Avoid division by zero or near-zero
        return (user_time - mean) / std_dev
    elif user_time > mean + 1e-6: # If std dev is zero, return large positive if user is slower
        return 5.0 # Arbitrary large positive Z-score
    elif user_time < mean - 1e-6: # Return large negative if user is faster
        return -5.0 # Arbitrary large negative Z-score
    else:
        return 0.0 # User time matches the mean exactly

def get_label_from_filename(filename):
    """Determines binary label (0=Normal, 1=Cheat) based on filename keywords."""
    cleaned_filename = filename.lower().replace(".json", "")
    for keyword in CHEAT_KEYWORDS:
        if f"_{keyword}_" in f"_{cleaned_filename}" or cleaned_filename.endswith(f"_{keyword}"):
            return 1 # Cheat
    # Can optionally check if it's a known normal persona for robustness
    for persona in NORMAL_PERSONAS:
         if f"_{persona}_" in f"_{cleaned_filename}" or cleaned_filename.endswith(f"_{persona}"):
              return 0 # Normal
    # If neither cheat nor known normal, maybe return -1 or log warning?
    print(f"Warning: Could not determine label for {filename}, assuming Normal (0).") 
    return 0 # Default to Normal if unsure, or handle differently

# --- Step 1: Process Logs -> Per-Question Metrics Function ---
def get_per_question_metrics(log_data, global_stats, question_details):
    """Processes logs for one session to get detailed metrics per question."""
    logs = log_data.get("logs", [])
    if not logs: return pd.DataFrame() # Return empty DataFrame if no logs

    # Parse and sort logs
    parsed_logs = []
    for log in logs:
        ts = parse_timestamp(log.get("timestamp"))
        if ts: parsed_logs.append({**log, "timestamp_dt": ts})
    if not parsed_logs: return pd.DataFrame()
    parsed_logs.sort(key=lambda x: x["timestamp_dt"])

    # Initialize accumulators for this session
    q_metrics = defaultdict(lambda: {
        "q_id": None, "time_spent": 0.0, "answered_correctly": None, 
        "answer_changes": 0, "tab_switches": 0, "is_attempted": False,
        "difficulty": None, "global_avg_time": None, "global_std_dev_time": None,
        "global_accuracy": None, "time_z_score": None, "is_revisit": False
    })
    
    last_q_selection_time = None
    current_q_id = None
    final_answer_for_q = {}
    visited_q_ids = set() # Track visited questions for revisits
    last_selected_q_idx = -1 # For sequential check

    # Iterate through logs to calculate metrics
    for i, log in enumerate(parsed_logs):
        activity = log.get("activity_text", "")
        timestamp = log["timestamp_dt"]
        location = log.get("location") 

        is_q_selection = activity.startswith("Selected question")
        is_test_start = activity == "Test Started"

        if is_q_selection or is_test_start:
            new_q_id = location
            
            # Finalize time for previous question
            if current_q_id and last_q_selection_time:
                time_diff = max(0, (timestamp - last_q_selection_time).total_seconds())
                q_metrics[current_q_id]["time_spent"] += time_diff

            # Start new question interval
            last_q_selection_time = timestamp
            current_q_id = new_q_id

            if is_q_selection:
                q_metrics[current_q_id]["q_id"] = current_q_id # Ensure q_id is set
                # Check for revisit
                if current_q_id in visited_q_ids:
                     q_metrics[current_q_id]["is_revisit"] = True
                visited_q_ids.add(current_q_id)
                # Try to get index for sequential check
                try: last_selected_q_idx = int(activity.split()[-1])
                except: pass 

        elif activity == "Submitted Test" or i == len(parsed_logs) - 1:
             if current_q_id and last_q_selection_time:
                time_diff = max(0, (timestamp - last_q_selection_time).total_seconds())
                q_metrics[current_q_id]["time_spent"] += time_diff
             current_q_id = None 
             last_q_selection_time = None

        # Accumulate metrics for the currently active question
        if current_q_id and q_metrics[current_q_id]["q_id"] is None: 
             q_metrics[current_q_id]["q_id"] = current_q_id # Ensure q_id is set even if only Test Started points to it
             visited_q_ids.add(current_q_id) # Mark as visited

        if current_q_id:
            q_metrics[current_q_id]["is_attempted"] = True # Mark as attempted if any activity occurs
            if activity == "Tab Switched":
                 q_metrics[current_q_id]["tab_switches"] += 1
            elif activity.startswith("Cleared option"):
                 q_metrics[current_q_id]["answer_changes"] += 1
                 final_answer_for_q[current_q_id] = None 
            elif activity.startswith("Selected option"):
                 try:
                     option_idx = int(activity.split(" ")[2])
                     final_answer_for_q[current_q_id] = option_idx
                 except: final_answer_for_q[current_q_id] = None 

    # Post-process: Calculate correctness, add global stats, calculate Z-score
    processed_metrics = []
    for q_id, metrics in q_metrics.items():
        if not q_id or q_id not in question_details: continue # Skip if no valid question ID

        # Correctness
        last_answer = final_answer_for_q.get(q_id)
        correct_ref = question_details[q_id].get("correct_answer")
        if last_answer is not None and correct_ref is not None:
            metrics["answered_correctly"] = 1 if last_answer == correct_ref else 0
        
        # Difficulty
        metrics["difficulty"] = question_details[q_id].get("difficulty", "Unknown")

        # Global Stats & Z-Score
        if q_id in global_stats:
            gs = global_stats[q_id]
            metrics["global_avg_time"] = gs.get("global_avg_time")
            metrics["global_std_dev_time"] = gs.get("global_std_dev_time")
            metrics["global_accuracy"] = gs.get("global_accuracy")
            metrics["time_z_score"] = calculate_time_z_score(metrics["time_spent"], q_id, global_stats)
        
        processed_metrics.append(metrics)

    return pd.DataFrame(processed_metrics)


# --- Step 2: Aggregate Per-Question Metrics -> Session Features Function ---
def aggregate_features(per_q_df, logs, global_stats, question_details):
    """Calculates session-level features from per-question metrics."""
    features = {}
    
    # Basic checks
    if per_q_df.empty or not logs:
        # Return default features if no valid data
        # Define a default structure based on expected features
        # This part needs careful definition of all expected output features
        return { "error": "No valid question metrics or logs" } 

    parsed_logs = []
    for log in logs:
        ts = parse_timestamp(log.get("timestamp"))
        if ts: parsed_logs.append({**log, "timestamp_dt": ts})
    parsed_logs.sort(key=lambda x: x["timestamp_dt"])
    
    # --- Overall Timing ---
    start_time = parsed_logs[0]["timestamp_dt"]
    end_time = parsed_logs[-1]["timestamp_dt"]
    features["total_duration"] = (end_time - start_time).total_seconds()
    
    first_answer_log = next((l for l in parsed_logs if l.get("activity_text", "").startswith("Selected option")), None)
    features["time_until_first_answer"] = (first_answer_log["timestamp_dt"] - start_time).total_seconds() if first_answer_log else features["total_duration"]
    
    submit_log = next((l for l in reversed(parsed_logs) if l.get("activity_text") == "Submitted Test"), None)
    last_answer_log = next((l for l in reversed(parsed_logs) if l.get("activity_text", "").startswith("Selected option")), None)
    if submit_log and last_answer_log:
        features["time_between_last_answer_and_submit"] = (submit_log["timestamp_dt"] - last_answer_log["timestamp_dt"]).total_seconds()
    else:
         features["time_between_last_answer_and_submit"] = 0.0

    # --- Aggregated Timings (from per_q_df) ---
    valid_times = per_q_df["time_spent"].dropna()
    features["mean_time_per_question"] = valid_times.mean() if not valid_times.empty else 0.0
    features["std_dev_time_per_question"] = valid_times.std() if len(valid_times) > 1 else 0.0
    features["median_time_per_question"] = valid_times.median() if not valid_times.empty else 0.0
    features["min_time_per_question"] = valid_times.min() if not valid_times.empty else 0.0
    features["max_time_per_question"] = valid_times.max() if not valid_times.empty else 0.0
    
    # --- Activity Counts ---
    features["num_tab_switches"] = per_q_df["tab_switches"].sum()
    features["num_answer_changes"] = per_q_df["answer_changes"].sum()
    features["num_revisits"] = per_q_df["is_revisit"].sum()

    # --- Navigation ---
    # Simple sequential check: count how many times q_idx+1 is selected after q_idx
    # Requires parsing 'Selected question N' logs again, or adding index to per_q_df
    # Simplified: Just use num_revisits as proxy for non-sequential
    features["num_questions_attempted"] = len(per_q_df)
    # Placeholder for sequential rate - needs more complex logic if required
    features["sequential_transition_rate"] = np.nan # Mark as not implemented yet

    # --- Performance ---
    answered_correctly = per_q_df["answered_correctly"].dropna()
    features["accuracy"] = answered_correctly.mean() if not answered_correctly.empty else 0.0

    # --- Deviation Features ---
    valid_z_scores = per_q_df["time_z_score"].dropna()
    features["mean_time_z_score"] = valid_z_scores.mean() if not valid_z_scores.empty else 0.0
    features["min_time_z_score"] = valid_z_scores.min() if not valid_z_scores.empty else 0.0
    features["max_time_z_score"] = valid_z_scores.max() if not valid_z_scores.empty else 0.0
    features["std_dev_time_z_score"] = valid_z_scores.std() if len(valid_z_scores) > 1 else 0.0

    # Proportions
    num_attempted = features["num_questions_attempted"]
    if num_attempted > 0:
        fast_threshold = -1.5 # Define what constitutes 'fast' Z-score
        features["proportion_questions_fast"] = (valid_z_scores < fast_threshold).mean()
        
        correct_mask = per_q_df["answered_correctly"] == 1
        fast_mask = per_q_df["time_z_score"] < fast_threshold
        # Ensure masks align - handle potential NaNs carefully if using direct boolean indexing
        correct_and_fast = per_q_df[correct_mask & fast_mask] 
        features["proportion_questions_correct_and_fast"] = len(correct_and_fast) / num_attempted
        
        features["proportion_questions_with_tab_switch"] = (per_q_df["tab_switches"] > 0).mean()
        features["answer_change_rate"] = (per_q_df["answer_changes"] > 0).mean() # Rate of questions with changes
    else:
        features["proportion_questions_fast"] = 0.0
        features["proportion_questions_correct_and_fast"] = 0.0
        features["proportion_questions_with_tab_switch"] = 0.0
        features["answer_change_rate"] = 0.0

    # Deviation from global accuracy/activity
    expected_accuracy = per_q_df["global_accuracy"].dropna().mean() if not per_q_df["global_accuracy"].dropna().empty else 0.0
    features["accuracy_deviation"] = features["accuracy"] - expected_accuracy

    total_expected_switches = sum(global_stats.get(qid, {}).get("global_avg_tab_switches", 0) for qid in per_q_df["q_id"])
    features["tab_switch_deviation"] = features["num_tab_switches"] - total_expected_switches
    
    total_expected_changes = sum(global_stats.get(qid, {}).get("global_avg_answer_changes", 0) for qid in per_q_df["q_id"])
    features["answer_change_deviation"] = features["num_answer_changes"] - total_expected_changes

    # Round features for cleaner output
    for key, value in features.items():
        if isinstance(value, (float, np.floating)):
            features[key] = round(value, 4)
            
    return features


# --- Main Feature Extraction Loop ---
if __name__ == "__main__":
    print(f"Starting feature extraction...")
    print(f"Reading logs from: {LOGS_DIR}")
    print(f"Using global stats: {GLOBAL_STATS_FILE}")

    log_files = [f for f in os.listdir(LOGS_DIR) if f.endswith('.json')]
    print(f"Found {len(log_files)} log files.")

    if not log_files:
        print("No log files found. Exiting.")
        exit()

    all_features_list = [] # List to hold feature dictionaries for each session

    try:
        from tqdm import tqdm
        file_iterator = tqdm(log_files, desc="Extracting Features")
    except ImportError:
        file_iterator = log_files
        print("(Install 'tqdm' for progress bar)")

    processed_count = 0
    error_count = 0
    for filename in file_iterator:
        filepath = os.path.join(LOGS_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                log_data = json.load(f)
            
            # Step 1: Get per-question metrics
            per_q_metrics_df = get_per_question_metrics(log_data, global_stats, question_details)
            
            # Step 2: Aggregate into session features
            if not per_q_metrics_df.empty:
                 session_features = aggregate_features(per_q_metrics_df, log_data.get("logs", []), global_stats, question_details)
                 session_features["log_file"] = filename # Add filename for reference
                 # Assign binary label based on filename
                 session_features["label"] = get_label_from_filename(filename)
                 all_features_list.append(session_features)
                 processed_count += 1
            else:
                 print(f"\nWarning: No valid per-question metrics extracted from {filename}. Skipping.")
                 error_count += 1

        except json.JSONDecodeError:
            print(f"\nWarning: Skipping invalid JSON file: {filename}")
            error_count += 1
        except Exception as e:
            print(f"\nWarning: Error processing file {filename}: {e}")
            import traceback
            traceback.print_exc() # Print detailed traceback for debugging
            error_count += 1
            
    print(f"\nFinished processing.")
    print(f"Successfully extracted features for {processed_count} sessions.")
    print(f"Skipped {error_count} files due to errors or no valid data.")

    if not all_features_list:
        print("No features were extracted. Cannot create dataset.")
        exit()

    # --- Create DataFrame and Save ---
    features_df = pd.DataFrame(all_features_list)

    # Define a good column order (optional but recommended)
    feature_columns = [
        # Overall Timing
        "total_duration", "time_until_first_answer", "time_between_last_answer_and_submit",
        # Aggregated Timings
        "mean_time_per_question", "std_dev_time_per_question", "median_time_per_question", 
        "min_time_per_question", "max_time_per_question",
        # Activity Counts
        "num_tab_switches", "num_answer_changes", "num_revisits",
        # Navigation / Attempt Rate
        "num_questions_attempted", # "sequential_transition_rate", # (Skipped for now)
        # Performance
        "accuracy", 
        # Deviation Features
        "mean_time_z_score", "min_time_z_score", "max_time_z_score", "std_dev_time_z_score",
        "accuracy_deviation", "tab_switch_deviation", "answer_change_deviation",
        # Proportions
        "proportion_questions_fast", "proportion_questions_correct_and_fast",
        "proportion_questions_with_tab_switch", "answer_change_rate"
    ]
    # Ensure all calculated feature columns are included, plus label and file
    final_columns = [col for col in feature_columns if col in features_df.columns] # Keep only existing cols
    final_columns = ["log_file", "label"] + final_columns # Add identifiers first

    # Reorder DataFrame
    features_df = features_df[final_columns]

    print(f"\nSaving dataset with {len(features_df)} rows and {len(features_df.columns)} columns to: {OUTPUT_CSV_FILE}")
    try:
        features_df.to_csv(OUTPUT_CSV_FILE, index=False)
        print("Successfully saved dataset.")
    except Exception as e:
        print(f"Error saving dataset to CSV: {e}") 