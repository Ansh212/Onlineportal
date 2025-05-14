import os
import json
import datetime
import numpy as np 
from collections import defaultdict
import math

def parse_timestamp(ts_str):
    # Handles the 'Z' suffix for UTC
    if ts_str is None:
        return None
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    try:
        return datetime.datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        print(f"Warning: Could not parse timestamp {ts_str}")
        return None

# --- Function to Process Single User's Logs for Batch Stats ---
def _process_single_session_logs_for_batch_stats(session_log_events, questions_data_map):
    """
    Parses a single user's session_log_events to extract per-question metrics.
    Uses the provided questions_data_map for correct answer lookup.
    """
    if not session_log_events:
        return {}

    session_metrics = defaultdict(lambda: {
        "time_spent": 0.0,
        "answered_correctly": None, # None=Not answered, 0=Incorrect, 1=Correct
        "answer_changes": 0,
        "tab_switches": 0
    })

    last_q_selection_time = None
    current_q_id = None
    final_answer_for_q = {} 

    parsed_logs = []
    for log in session_log_events: 
        ts = parse_timestamp(log.get("timestamp"))
        if ts:
            parsed_logs.append({**log, "timestamp_dt": ts})

    if not parsed_logs:
        return {}
        
    parsed_logs.sort(key=lambda x: x["timestamp_dt"])

    for i, log in enumerate(parsed_logs):
        activity = log.get("activity_text", "")
        timestamp = log["timestamp_dt"]
        location = log.get("location")

        if activity.startswith("Selected question") or activity == "Test Started":
            if current_q_id and last_q_selection_time:
                time_diff = (timestamp - last_q_selection_time).total_seconds()
                session_metrics[current_q_id]["time_spent"] += max(0, time_diff)
            current_q_id = location
            last_q_selection_time = timestamp
        elif activity == "Submitted Test" or i == len(parsed_logs) - 1:
            if current_q_id and last_q_selection_time:
                time_diff = (timestamp - last_q_selection_time).total_seconds()
                session_metrics[current_q_id]["time_spent"] += max(0, time_diff)
            current_q_id = None
            last_q_selection_time = None

        if current_q_id:
            if activity == "Tab Switched":
                 session_metrics[current_q_id]["tab_switches"] += 1
            elif activity.startswith("Cleared option"):
                 session_metrics[current_q_id]["answer_changes"] += 1
                 final_answer_for_q[current_q_id] = None
            elif activity.startswith("Selected option"):
                 try:
                     option_str = activity.split(" ")[2]
                     option_idx = int(option_str)
                     final_answer_for_q[current_q_id] = option_idx
                 except (IndexError, ValueError):
                     final_answer_for_q[current_q_id] = None

    for q_id, last_answer_idx in final_answer_for_q.items():
        if q_id in questions_data_map and last_answer_idx is not None: 
            question_info = questions_data_map.get(q_id, {}) 
            correct_answer = question_info.get("correct_answer") 
            if correct_answer is not None:
                 session_metrics[q_id]["answered_correctly"] = 1 if last_answer_idx == correct_answer else 0
            else:
                 session_metrics[q_id]["answered_correctly"] = None 
        elif q_id in questions_data_map: 
            session_metrics[q_id]["answered_correctly"] = None


    return {
        q_id: metrics for q_id, metrics in session_metrics.items()
        if q_id in questions_data_map and metrics["time_spent"] > 0.1
    }


def compute_batch_global_stats(all_user_logs_with_ids, questions_data_map):
    """
    Computes global statistics for a batch of user logs.
    Args:
        all_user_logs_with_ids: List of dicts, e.g., [{'userId': 'id1', 'session_log_events': [...]}, ...]
        questions_data_map: Dict mapping question_id to question details.
    Returns:
        A dictionary batch_global_stats where keys are question_ids.
    """
    accumulated_times = defaultdict(list)
    accumulated_correctness = defaultdict(list)
    accumulated_tab_switches = defaultdict(list)
    accumulated_answer_changes = defaultdict(list)

    if not questions_data_map:
        print("Warning: compute_batch_global_stats called with empty questions_data_map.")
        return {}

    for user_log_data in all_user_logs_with_ids:
        session_log_events = user_log_data.get('session_log_events')
        if not session_log_events:
            # print(f"Skipping user {user_log_data.get('userId')} due to missing session_log_events.")
            continue

        session_metrics = _process_single_session_logs_for_batch_stats(session_log_events, questions_data_map)

        for q_id, metrics in session_metrics.items():
            if q_id in questions_data_map:
                if metrics.get("time_spent", 0) > 0.1 : # Only consider attempted questions for time stats
                    accumulated_times[q_id].append(metrics["time_spent"])
                if metrics.get("answered_correctly") is not None:
                    accumulated_correctness[q_id].append(metrics["answered_correctly"])
                if metrics.get("time_spent", 0) > 0.1 :
                     accumulated_tab_switches[q_id].append(metrics.get("tab_switches", 0))
                     accumulated_answer_changes[q_id].append(metrics.get("answer_changes", 0))


    batch_global_stats = {}

    for q_id in questions_data_map.keys():
        times = accumulated_times.get(q_id, [])
        correctness = accumulated_correctness.get(q_id, [])
        switches = accumulated_tab_switches.get(q_id, [])
        changes = accumulated_answer_changes.get(q_id, [])

        attempt_count = len(times) 

        avg_time = float(np.mean(times)) if times else 0.0
        std_dev_time = float(np.std(times)) if len(times) > 1 else 0.0
        
        accuracy = float(np.mean(correctness)) if correctness else 0.0 
        
        avg_tab_switches = float(np.mean(switches)) if switches else 0.0
        avg_answer_changes = float(np.mean(changes)) if changes else 0.0

        batch_global_stats[q_id] = {
            "global_avg_time": round(avg_time, 3),
            "global_std_dev_time": round(std_dev_time, 3),
            "global_accuracy": round(accuracy, 3), 
            "global_avg_tab_switches": round(avg_tab_switches, 3), 
            "global_avg_answer_changes": round(avg_answer_changes, 3), 
            "global_attempt_count": attempt_count, 
        }
    return batch_global_stats
