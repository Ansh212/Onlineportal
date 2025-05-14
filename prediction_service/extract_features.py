import os
import json
import datetime
import numpy as np
import pandas as pd
from collections import defaultdict
import math

FEATURE_NAMES_IN_ORDER = [
    # Overall Timing
    "total_duration", 
    "time_until_first_answer", 
    "time_between_last_answer_and_submit",

    # Aggregated Timings
    "mean_time_per_question", 
    "std_dev_time_per_question", 
    "median_time_per_question", 
    "min_time_per_question", 
    "max_time_per_question",

    # Activity Counts
    "num_tab_switches", 
    "num_answer_changes", 
    "num_revisits",

    # Navigation / Attempt Rate
    "num_questions_attempted", 

    # Performance
    "accuracy", 

    # Deviation Features
    "mean_time_z_score", 
    "min_time_z_score", 
    "max_time_z_score", 
    "std_dev_time_z_score",
    "accuracy_deviation", 
    "tab_switch_deviation", 
    "answer_change_deviation",

    # Proportions
    "proportion_questions_fast", 
    "proportion_questions_correct_and_fast",
    "proportion_questions_with_tab_switch", 
    "answer_change_rate"
]

# --- Helper Functions ---
def parse_timestamp(ts_str):
    if not ts_str: return None
    if ts_str.endswith('Z'): ts_str = ts_str[:-1] + '+00:00'
    try: return datetime.datetime.fromisoformat(ts_str)
    except (ValueError, TypeError): 
        # print(f"Warning: Could not parse timestamp {ts_str}") # Silenced for library use
        return None

def calculate_time_z_score(user_time, q_id, batch_or_global_stats):

    if q_id not in batch_or_global_stats: return 0.0

    stats = batch_or_global_stats[q_id]

    mean = stats.get("global_avg_time", 0.0) 
    std_dev = stats.get("global_std_dev_time", 0.0)

    if std_dev > 1e-6:
        return (user_time - mean) / std_dev
    elif user_time > mean + 1e-6:
        return 5.0 
    elif user_time < mean - 1e-6:
        return -5.0
    else:
        return 0.0

def get_per_question_metrics(session_log_events, questions_data_map, current_batch_global_stats):
    """
    Processes logs for one session to get detailed metrics per question.
    Args:
        session_log_events (list): List of log event dictionaries for the session.
        questions_data_map (dict): Map of question_id to question details for the current test.
        current_batch_global_stats (dict): Global stats calculated for the current batch/test.
    Returns:
        pd.DataFrame: DataFrame with per-question metrics.
    """
    if not session_log_events: return pd.DataFrame()

    parsed_logs = []
    for log in session_log_events: 
        ts = parse_timestamp(log.get("timestamp"))
        if ts: parsed_logs.append({**log, "timestamp_dt": ts})
    
    if not parsed_logs: return pd.DataFrame() 
    parsed_logs.sort(key=lambda x: x["timestamp_dt"])

    q_metrics = defaultdict(lambda: {
        "q_id": None, "time_spent": 0.0, "answered_correctly": None,
        "answer_changes": 0, "tab_switches": 0, "is_attempted": False,
        "global_avg_time": None, "global_std_dev_time": None,
        "global_accuracy": None, "time_z_score": None, "is_revisit": False
    })

    last_q_selection_time = None
    current_q_id = None
    final_answer_for_q = {}
    visited_q_ids = set()
    last_selected_q_idx = -1

    for i, log in enumerate(parsed_logs):
        activity = log.get("activity_text", "")
        timestamp = log["timestamp_dt"]
        location = log.get("location")

        is_q_selection = activity.startswith("Selected question")
        is_test_start = activity == "Test Started"

        if is_q_selection or is_test_start:
            new_q_id = location
            if current_q_id and last_q_selection_time and current_q_id in questions_data_map:
                time_diff = max(0, (timestamp - last_q_selection_time).total_seconds())
                q_metrics[current_q_id]["time_spent"] += time_diff
            
            last_q_selection_time = timestamp
            current_q_id = new_q_id
            
            if is_q_selection and current_q_id in questions_data_map: # Process only if valid q_id
                q_metrics[current_q_id]["q_id"] = current_q_id
                if current_q_id in visited_q_ids:
                     q_metrics[current_q_id]["is_revisit"] = True
                visited_q_ids.add(current_q_id)
                try: last_selected_q_idx = int(activity.split()[-1]) # Not used
                except: pass

        elif activity == "Submitted Test" or i == len(parsed_logs) - 1:
             if current_q_id and last_q_selection_time and current_q_id in questions_data_map:
                time_diff = max(0, (timestamp - last_q_selection_time).total_seconds())
                q_metrics[current_q_id]["time_spent"] += time_diff
             current_q_id = None
             last_q_selection_time = None

        if current_q_id and current_q_id in questions_data_map: 
            if q_metrics[current_q_id]["q_id"] is None: 
                 q_metrics[current_q_id]["q_id"] = current_q_id
                 visited_q_ids.add(current_q_id)
            
            q_metrics[current_q_id]["is_attempted"] = True
            if activity == "Tab Switched":
                 q_metrics[current_q_id]["tab_switches"] += 1
            elif activity.startswith("Cleared option"):
                 q_metrics[current_q_id]["answer_changes"] += 1
                 final_answer_for_q[current_q_id] = None
            elif activity.startswith("Selected option"):
                 try:
                     option_idx = int(activity.split(" ")[2])
                     final_answer_for_q[current_q_id] = option_idx
                 except (IndexError, ValueError):
                      final_answer_for_q[current_q_id] = None

    processed_metrics = []
    for q_id_key, metrics_val in q_metrics.items():
        if not q_id_key or q_id_key not in questions_data_map: 
            continue 

        question_details_from_map = questions_data_map[q_id_key]
        metrics_val["q_id"] = q_id_key 

        last_answer = final_answer_for_q.get(q_id_key)
        correct_ref = question_details_from_map.get("correct_answer")
        if last_answer is not None and correct_ref is not None:
            metrics_val["answered_correctly"] = 1 if last_answer == correct_ref else 0
        else:
            metrics_val["answered_correctly"] = None 

        if q_id_key in current_batch_global_stats: 
            gs = current_batch_global_stats[q_id_key]
            metrics_val["global_avg_time"] = gs.get("global_avg_time")
            metrics_val["global_std_dev_time"] = gs.get("global_std_dev_time")
            metrics_val["global_accuracy"] = gs.get("global_accuracy") 
            metrics_val["time_z_score"] = calculate_time_z_score(metrics_val["time_spent"], q_id_key, current_batch_global_stats)
        
        if metrics_val["is_attempted"] or metrics_val["time_spent"] > 0.1:
            processed_metrics.append(metrics_val)

    return pd.DataFrame(processed_metrics)


def aggregate_features(per_question_metrics_df, session_log_events, current_batch_global_stats, questions_data_map):
    """
    Calculates session-level features from per-question metrics.
    Args:
        per_question_metrics_df (pd.DataFrame): DataFrame from get_per_question_metrics.
        session_log_events (list): List of log event dictionaries for the session.
        current_batch_global_stats (dict): Global stats for the current batch/test.
        questions_data_map (dict): Map of question_id to question details for the current test.
    Returns:
        dict: Dictionary of aggregated session features.
    """
    features = {name: 0.0 for name in FEATURE_NAMES_IN_ORDER} # Initialize with defaults

    if not session_log_events:
        # print("Warning: aggregate_features called with no session_log_events.")
        return features # Return default initialized features

    parsed_logs = []
    for log_event in session_log_events: 
        ts = parse_timestamp(log_event.get("timestamp"))
        if ts: parsed_logs.append({**log_event, "timestamp_dt": ts})
    
    if not parsed_logs: 
        # print("Warning: aggregate_features found no parseable logs in session_log_events.")
        return features # Return default initialized features
        
    parsed_logs.sort(key=lambda x: x["timestamp_dt"])

    start_time = parsed_logs[0]["timestamp_dt"]
    end_time = parsed_logs[-1]["timestamp_dt"]
    features["total_duration"] = (end_time - start_time).total_seconds()

    first_answer_log = next((l for l in parsed_logs if l.get("activity_text", "").startswith("Selected option")), None)
    features["time_until_first_answer"] = (first_answer_log["timestamp_dt"] - start_time).total_seconds() if first_answer_log else features.get("total_duration", 0.0)

    submit_log = next((l for l in reversed(parsed_logs) if l.get("activity_text") == "Submitted Test"), None)
    last_answer_log = next((l for l in reversed(parsed_logs) if l.get("activity_text", "").startswith("Selected option")), None)
    if submit_log and last_answer_log and last_answer_log["timestamp_dt"] <= submit_log["timestamp_dt"]:
        features["time_between_last_answer_and_submit"] = (submit_log["timestamp_dt"] - last_answer_log["timestamp_dt"]).total_seconds()
    else:
         features["time_between_last_answer_and_submit"] = 0.0

    # Calculations based on per_question_metrics_df
    if not per_question_metrics_df.empty:
        valid_times = per_question_metrics_df["time_spent"].dropna()
        if not valid_times.empty:
            features["mean_time_per_question"] = valid_times.mean()
            features["median_time_per_question"] = valid_times.median()
            features["min_time_per_question"] = valid_times.min()
            features["max_time_per_question"] = valid_times.max()
        if len(valid_times) > 1:
            features["std_dev_time_per_question"] = valid_times.std()

        features["num_tab_switches"] = per_question_metrics_df["tab_switches"].sum()
        features["num_answer_changes"] = per_question_metrics_df["answer_changes"].sum()
        features["num_revisits"] = per_question_metrics_df["is_revisit"].sum()
        
        if 'is_attempted' in per_question_metrics_df.columns:
            features["num_questions_attempted"] = per_question_metrics_df["is_attempted"].sum()
        else: 
            features["num_questions_attempted"] = len(per_question_metrics_df["q_id"].unique())


        answered_correctly_series = per_question_metrics_df["answered_correctly"].dropna()
        features["accuracy"] = answered_correctly_series.mean() if not answered_correctly_series.empty else 0.0

        valid_z_scores = per_question_metrics_df["time_z_score"].dropna()
        if not valid_z_scores.empty:
            features["mean_time_z_score"] = valid_z_scores.mean()
            features["min_time_z_score"] = valid_z_scores.min()
            features["max_time_z_score"] = valid_z_scores.max()
        if len(valid_z_scores) > 1:
            features["std_dev_time_z_score"] = valid_z_scores.std()

        num_attempted = features["num_questions_attempted"]
        if num_attempted > 0:
            fast_threshold = -1.5 
            features["proportion_questions_fast"] = (valid_z_scores < fast_threshold).sum() / num_attempted
            
            temp_df_for_fast_correct = per_question_metrics_df.dropna(subset=['answered_correctly', 'time_z_score'])
            if not temp_df_for_fast_correct.empty:
                correct_and_fast_count = len(temp_df_for_fast_correct[
                    (temp_df_for_fast_correct["answered_correctly"] == 1) & 
                    (temp_df_for_fast_correct["time_z_score"] < fast_threshold)
                ])
                features["proportion_questions_correct_and_fast"] = correct_and_fast_count / num_attempted

            features["proportion_questions_with_tab_switch"] = (per_question_metrics_df["tab_switches"] > 0).sum() / num_attempted
            features["answer_change_rate"] = (per_question_metrics_df["answer_changes"] > 0).sum() / num_attempted

        # Deviation features using current_batch_global_stats
        attempted_q_ids = per_question_metrics_df["q_id"].dropna().unique()
        expected_accuracy_list = []
        for q_id in attempted_q_ids:
            if q_id in current_batch_global_stats and "global_accuracy" in current_batch_global_stats[q_id]:
                expected_accuracy_list.append(current_batch_global_stats[q_id]["global_accuracy"])
        
        avg_expected_accuracy_for_attempted = np.mean(expected_accuracy_list) if expected_accuracy_list else 0.0
        features["accuracy_deviation"] = features["accuracy"] - avg_expected_accuracy_for_attempted

        total_expected_switches = sum(current_batch_global_stats.get(qid, {}).get("global_avg_tab_switches", 0) for qid in attempted_q_ids)
        features["tab_switch_deviation"] = features["num_tab_switches"] - total_expected_switches

        total_expected_changes = sum(current_batch_global_stats.get(qid, {}).get("global_avg_answer_changes", 0) for qid in attempted_q_ids)
        features["answer_change_deviation"] = features["num_answer_changes"] - total_expected_changes
    

    for key in FEATURE_NAMES_IN_ORDER:
        value = features.get(key, 0.0) 
        if isinstance(value, (float, np.floating)) and not math.isnan(value) and not math.isinf(value):
            features[key] = round(value, 4)
        elif math.isnan(value) or math.isinf(value):
            features[key] = 0.0 
        else: 
            features[key] = round(float(value), 4)
            
    return features