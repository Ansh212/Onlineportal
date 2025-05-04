import os
import json
import datetime
import numpy as np # For mean/std calculations
from collections import defaultdict
import math
import time 

# --- Configuration ---
# Assumes this script is in the 'logs' directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
LOGS_DIR = os.path.join(SCRIPT_DIR, "generated_logs_2") # Input directory
OUTPUT_STATS_FILE = os.path.join(SCRIPT_DIR, "global_stats.json") # Output file

# --- Question Data (Essential for correct answer lookup) ---
# Needs to be consistent with the data used for generation
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

# Create a lookup dictionary for faster access to question details
question_details = {q["id"]: q for q in questions_data}

# --- Helper Function to Parse Timestamps ---
def parse_timestamp(ts_str):
    # Handles the 'Z' suffix for UTC
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    try:
        return datetime.datetime.fromisoformat(ts_str)
    except ValueError:
        # Handle potential variations if necessary
        print(f"Warning: Could not parse timestamp {ts_str}")
        return None

# --- Function to Process a Single Log File ---
def process_log_file(log_data):
    """Parses logs to extract per-question metrics for one session."""
    logs = log_data.get("logs", [])
    if not logs:
        return {} # Skip if no logs

    session_metrics = defaultdict(lambda: {
        "time_spent": 0.0,
        "answered_correctly": None, # None=Not answered, 0=Incorrect, 1=Correct
        "answer_changes": 0,
        "tab_switches": 0
    })
    
    last_q_selection_time = None
    current_q_id = None
    final_answer_for_q = {} # Store the last selected option index for each question

    # Convert timestamps to datetime objects first
    parsed_logs = []
    for log in logs:
        ts = parse_timestamp(log.get("timestamp"))
        if ts:
            parsed_logs.append({**log, "timestamp_dt": ts})
        else:
            print(f"Skipping log due to invalid timestamp: {log}")
    
    # Sort logs by timestamp just in case
    parsed_logs.sort(key=lambda x: x["timestamp_dt"])

    for i, log in enumerate(parsed_logs):
        activity = log.get("activity_text", "")
        timestamp = log["timestamp_dt"]
        location = log.get("location") # This is the question ID

        # --- Track Time Intervals ---
        if activity.startswith("Selected question") or activity == "Test Started":
            # If we were tracking a previous question, finalize its interval time
            if current_q_id and last_q_selection_time:
                time_diff = (timestamp - last_q_selection_time).total_seconds()
                # Add this time difference to the question that was just completed
                session_metrics[current_q_id]["time_spent"] += max(0, time_diff) # Ensure non-negative time
            
            # Start tracking the new question interval
            current_q_id = location 
            last_q_selection_time = timestamp
            # Note: Initial "Selected question 0" might happen right after "Test Started"
            # We correctly associate time starting from the selection event.

        elif activity == "Submitted Test" or i == len(parsed_logs) - 1:
             # Finalize time for the last question being worked on
             if current_q_id and last_q_selection_time:
                time_diff = (timestamp - last_q_selection_time).total_seconds()
                session_metrics[current_q_id]["time_spent"] += max(0, time_diff)
             current_q_id = None # Stop tracking after submit/end
             last_q_selection_time = None

        # --- Track Other Metrics within the Current Question's Interval ---
        if current_q_id: # Only track if we are focused on a question
            if activity == "Tab Switched":
                 # Simple association: attribute switch to the currently selected question
                 session_metrics[current_q_id]["tab_switches"] += 1
            elif activity.startswith("Cleared option"):
                 session_metrics[current_q_id]["answer_changes"] += 1
                 # Also clear the final answer record if needed
                 final_answer_for_q[current_q_id] = None 
            elif activity.startswith("Selected option"):
                 # Record the latest selected option for this question
                 try:
                     # Extract option index (e.g., "Selected option 3 for question 5")
                     option_str = activity.split(" ")[2] 
                     option_idx = int(option_str)
                     final_answer_for_q[current_q_id] = option_idx
                 except (IndexError, ValueError):
                     # Handle cases like "Selected option unclear..." or parsing errors
                     # We could log a warning, but for now, we just don't record an answer index
                     final_answer_for_q[current_q_id] = None 

    # --- Determine Correctness After Processing All Logs ---
    for q_id, last_answer_idx in final_answer_for_q.items():
        if q_id in question_details and last_answer_idx is not None:
            correct_answer = question_details[q_id].get("correct_answer")
            if last_answer_idx == correct_answer:
                session_metrics[q_id]["answered_correctly"] = 1
            else:
                session_metrics[q_id]["answered_correctly"] = 0
        else:
             session_metrics[q_id]["answered_correctly"] = None # Not answered or invalid data


    # Filter out metrics for potentially invalid locations (e.g., None)
    # and ensure time spent is reasonable (e.g., filter out near-zero times if needed)
    final_metrics = {
        q_id: metrics for q_id, metrics in session_metrics.items() 
        if q_id in question_details and metrics["time_spent"] > 0.1 # Only include actual attempts with some time
    }

    return final_metrics


# --- Main Calculation ---
if __name__ == "__main__":
    print(f"Starting global stats calculation...")
    print(f"Reading logs from: {LOGS_DIR}")

    # Data accumulators
    # Store lists of values for each metric per question
    accumulated_times = defaultdict(list)
    accumulated_correctness = defaultdict(list) # Store 0s and 1s
    accumulated_tab_switches = defaultdict(list)
    accumulated_answer_changes = defaultdict(list)
    
    log_files = [f for f in os.listdir(LOGS_DIR) if f.endswith('.json')]
    print(f"Found {len(log_files)} log files.")

    if not log_files:
        print("No log files found. Exiting.")
        exit()
        
    # Optional: Use tqdm for progress
    try:
        from tqdm import tqdm
        file_iterator = tqdm(log_files, desc="Processing Logs")
    except ImportError:
        file_iterator = log_files
        print("(Install 'tqdm' for progress bar)")

    processed_files = 0
    for filename in file_iterator:
        filepath = os.path.join(LOGS_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                log_data = json.load(f)
            
            session_metrics = process_log_file(log_data)
            
            # Append metrics to global accumulators
            for q_id, metrics in session_metrics.items():
                accumulated_times[q_id].append(metrics["time_spent"])
                if metrics["answered_correctly"] is not None:
                    accumulated_correctness[q_id].append(metrics["answered_correctly"])
                accumulated_tab_switches[q_id].append(metrics["tab_switches"])
                accumulated_answer_changes[q_id].append(metrics["answer_changes"])
            processed_files += 1

        except json.JSONDecodeError:
            print(f"\nWarning: Skipping invalid JSON file: {filename}")
        except Exception as e:
            print(f"\nWarning: Error processing file {filename}: {e}")

    print(f"\nProcessed {processed_files} log files.")
    if processed_files == 0:
        print("No logs were successfully processed. Cannot calculate stats.")
        exit()

    # --- Calculate Final Statistics ---
    print("Calculating final statistics...")
    global_stats = {}

    all_q_ids = set(accumulated_times.keys()) | set(accumulated_correctness.keys()) | \
                set(accumulated_tab_switches.keys()) | set(accumulated_answer_changes.keys())

    for q_id in all_q_ids:
        if q_id not in question_details: 
            print(f"Warning: Found stats for unknown question ID '{q_id}'. Skipping.")
            continue # Skip if somehow an invalid q_id appears

        times = accumulated_times.get(q_id, [])
        correctness = accumulated_correctness.get(q_id, [])
        switches = accumulated_tab_switches.get(q_id, [])
        changes = accumulated_answer_changes.get(q_id, [])
        
        attempt_count = len(times) # Use time entries count as attempt count

        # Use numpy for safe mean/std calculation
        avg_time = float(np.mean(times)) if times else 0.0
        std_dev_time = float(np.std(times)) if len(times) > 1 else 0.0 # Std dev requires > 1 point
        
        accuracy = float(np.mean(correctness)) if correctness else 0.0 # Avg of 0s and 1s
        
        avg_tab_switches = float(np.mean(switches)) if switches else 0.0
        avg_answer_changes = float(np.mean(changes)) if changes else 0.0
        
        global_stats[q_id] = {
            "global_avg_time": round(avg_time, 3),
            "global_std_dev_time": round(std_dev_time, 3),
            "global_accuracy": round(accuracy, 3),
            "global_avg_tab_switches": round(avg_tab_switches, 3),
            "global_avg_answer_changes": round(avg_answer_changes, 3),
            "global_attempt_count": attempt_count
        }

    # --- Save Statistics ---
    print(f"Saving global statistics to: {OUTPUT_STATS_FILE}")
    try:
        with open(OUTPUT_STATS_FILE, 'w') as f:
            json.dump(global_stats, f, indent=2)
        print("Successfully saved global statistics.")
    except IOError as e:
        print(f"Error saving statistics file: {e}")
    except Exception as e:
         print(f"An unexpected error occurred during saving: {e}") 