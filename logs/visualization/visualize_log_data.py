import os
import json
import datetime
import numpy as np
import pandas as pd
from collections import defaultdict
import math
import time
import random
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go one level up to the 'logs' directory to find generated_logs_2
LOGS_PARENT_DIR = os.path.dirname(SCRIPT_DIR) 
LOGS_SOURCE_DIR = os.path.join(LOGS_PARENT_DIR, "generated_logs_2") # Source of detailed normal logs
VIZ_OUTPUT_DIR = os.path.join(SCRIPT_DIR) # Output for plots (save in current dir)
MAX_FILES_TO_PROCESS = 1000 # Sample N files to avoid slow processing

# --- Question Data ---
# (Ensure this is the same as used in generation scripts)
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
question_details_lookup = {q["id"]: q for q in questions_data}
difficulty_order = ["Easy", "Medium", "Hard"]
# Define order, including the new persona
persona_order = [
    # Normal Personas
    "topper", "average", "cheater_slow_careful","pre_knowledge", 
    "cheater_tab_switcher", "cheater_smart", "slow_careful", "overconfident", "struggler", 
    # Cheating Personas
    
]

# --- Helper Functions ---
def parse_timestamp(ts_str):
    if not ts_str: return None
    if ts_str.endswith('Z'): ts_str = ts_str[:-1] + '+00:00'
    try: return datetime.datetime.fromisoformat(ts_str)
    except (ValueError, TypeError): return None

def extract_persona_from_filename(filename):
    """Extracts the persona string from the filename, handling multi-word personas."""
    cleaned_filename = filename.replace(".json", "")
    # Iterate through the defined personas and check if one exists in the filename
    for persona in persona_order: 
        # Check if the persona name is present, surrounded by underscores or at the end 
        # to ensure we match the whole word (e.g., avoid matching 'aver' in 'average')
        # This handles cases like _topper_ , _slow_careful_, etc.
        if f"_{persona}_" in f"_{cleaned_filename}" or cleaned_filename.endswith(f"_{persona}"):
             return persona
    return "unknown" # Fallback

def process_log_file_for_viz(log_data, question_details_lookup, filename):
    """Extracts relevant metrics for visualization from a single log file."""
    logs = log_data.get("logs", [])
    label = log_data.get("label", "unknown")
    persona = extract_persona_from_filename(filename)
    
    if not logs: return None, None

    # --- Basic Session Info ---
    parsed_logs = []
    for log in logs:
        ts = parse_timestamp(log.get("timestamp"))
        if ts: parsed_logs.append({**log, "timestamp_dt": ts})
    if not parsed_logs: return None, None
    parsed_logs.sort(key=lambda x: x["timestamp_dt"])
    
    start_time = parsed_logs[0]["timestamp_dt"]
    end_time = parsed_logs[-1]["timestamp_dt"]
    session_duration = (end_time - start_time).total_seconds()
    
    # --- Per Question Metrics ---
    q_metrics = defaultdict(lambda: {"time_spent": 0.0, "correct": None, "changes": 0})
    last_q_selection_time = None
    current_q_id = None
    final_answer_for_q = {}

    for i, log in enumerate(parsed_logs):
        activity = log.get("activity_text", "")
        timestamp = log["timestamp_dt"]
        location = log.get("location") 

        is_q_selection = activity.startswith("Selected question")
        is_test_start = activity == "Test Started"

        if is_q_selection or is_test_start:
            new_q_id = location
            if current_q_id and last_q_selection_time:
                q_metrics[current_q_id]["time_spent"] += max(0, (timestamp - last_q_selection_time).total_seconds())
            last_q_selection_time = timestamp
            current_q_id = new_q_id
        elif activity == "Submitted Test" or i == len(parsed_logs) - 1:
             if current_q_id and last_q_selection_time:
                q_metrics[current_q_id]["time_spent"] += max(0, (timestamp - last_q_selection_time).total_seconds())
             current_q_id = None 
             last_q_selection_time = None

        if current_q_id:
            if activity.startswith("Cleared option"):
                 q_metrics[current_q_id]["changes"] += 1
                 final_answer_for_q[current_q_id] = None 
            elif activity.startswith("Selected option"):
                 try: final_answer_for_q[current_q_id] = int(activity.split(" ")[2])
                 except: final_answer_for_q[current_q_id] = None 

    # Determine correctness and collect per-question data rows
    per_question_data = []
    attempted_count = 0
    correct_count = 0
    total_changes = 0

    for q_id, metrics in q_metrics.items():
        if q_id not in question_details_lookup or metrics["time_spent"] < 0.1: continue # Skip invalid or non-attempted

        details = question_details_lookup[q_id]
        last_answer = final_answer_for_q.get(q_id)
        correct_ref = details.get("correct_answer")
        is_correct = None
        if last_answer is not None and correct_ref is not None:
            is_correct = 1 if last_answer == correct_ref else 0
            attempted_count += 1
            if is_correct == 1: correct_count +=1
        
        total_changes += metrics["changes"]

        per_question_data.append({
            "session_id": filename,
            "persona": persona,
            "q_id": q_id,
            "difficulty": details.get("difficulty", "Unknown"),
            "time_spent": metrics["time_spent"],
            "answered_correctly": is_correct,
            "answer_changes": metrics["changes"]
        })

    overall_accuracy = (correct_count / attempted_count) if attempted_count > 0 else 0.0
    session_summary = {
        "session_id": filename,
        "persona": persona,
        "total_duration": session_duration,
        "overall_accuracy": overall_accuracy,
        "total_answer_changes": total_changes,
        "questions_attempted": attempted_count
    }

    return pd.DataFrame(per_question_data), session_summary

# --- Plotting Functions ---

def plot_time_distribution(df, output_dir):
    """Plots time spent per question by difficulty and persona."""
    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x="difficulty", y="time_spent", hue="persona", 
                order=difficulty_order, hue_order=persona_order, showfliers=False) # Hide outliers for clarity
    plt.title("Time Spent per Question by Difficulty and Persona")
    plt.ylabel("Time Spent (seconds)")
    plt.xlabel("Question Difficulty")
    plt.ylim(0, 400) # Adjust ylim if needed based on data
    plt.legend(title="Persona", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "time_distribution_persona_difficulty.png"))
    plt.close()

def plot_accuracy(df, output_dir):
     """Plots average accuracy by persona and difficulty."""
     # Accuracy by Persona
     plt.figure(figsize=(10, 6))
     acc_persona = df.groupby("persona")["answered_correctly"].mean().reindex(persona_order).reset_index()
     sns.barplot(data=acc_persona, x="persona", y="answered_correctly")
     plt.title("Average Accuracy per Persona")
     plt.ylabel("Accuracy")
     plt.xlabel("Persona")
     plt.ylim(0, 1)
     plt.tight_layout()
     plt.savefig(os.path.join(output_dir, "accuracy_by_persona.png"))
     plt.close()

     # Accuracy by Difficulty
     plt.figure(figsize=(10, 6))
     acc_difficulty = df.groupby("difficulty")["answered_correctly"].mean().reindex(difficulty_order).reset_index()
     sns.barplot(data=acc_difficulty, x="difficulty", y="answered_correctly")
     plt.title("Average Accuracy per Difficulty")
     plt.ylabel("Accuracy")
     plt.xlabel("Difficulty")
     plt.ylim(0, 1)
     plt.tight_layout()
     plt.savefig(os.path.join(output_dir, "accuracy_by_difficulty.png"))
     plt.close()
     
def plot_session_summary(df_summary, output_dir):
    """Plots overall session duration vs accuracy."""
    plt.figure(figsize=(10, 7))
    sns.scatterplot(data=df_summary, x="total_duration", y="overall_accuracy", hue="persona", hue_order=persona_order, alpha=0.7)
    plt.title("Session Duration vs. Overall Accuracy by Persona")
    plt.xlabel("Total Duration (seconds)")
    plt.ylabel("Overall Accuracy")
    plt.legend(title="Persona", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "duration_vs_accuracy_persona.png"))
    plt.close()

def plot_answer_changes(df_summary, output_dir):
    """Plots distribution of total answer changes per session by persona."""
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df_summary, x="total_answer_changes", hue="persona", 
                 hue_order=persona_order, multiple="stack", bins=range(0, int(df_summary['total_answer_changes'].max())+2))
    plt.title("Distribution of Total Answer Changes per Session by Persona")
    plt.xlabel("Number of Answer Changes")
    plt.ylabel("Number of Sessions")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "answer_changes_distribution_persona.png"))
    plt.close()

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Starting log visualization...")
    
    # Create output directory
    if not os.path.exists(VIZ_OUTPUT_DIR):
        print(f"Creating visualization output directory: {VIZ_OUTPUT_DIR}")
        os.makedirs(VIZ_OUTPUT_DIR)

    # List and sample log files
    try:
        all_files_in_dir = [f for f in os.listdir(LOGS_SOURCE_DIR) if f.endswith('.json')]
        # Filter files to include only those matching known personas
        all_log_files = []
        for filename in all_files_in_dir:
             # Use the (fixed) extraction logic to see if it's a known persona file
             extracted_persona = extract_persona_from_filename(filename)
             if extracted_persona != "unknown":
                 all_log_files.append(filename)

        if not all_log_files:
            print(f"Error: No log files matching known personas found in {LOGS_SOURCE_DIR}")
            print(f"Looked for personas: {persona_order}")
            exit()
            
        if len(all_log_files) > MAX_FILES_TO_PROCESS:
            print(f"Sampling {MAX_FILES_TO_PROCESS} files out of {len(all_log_files)} found matching personas.")
            log_files_to_process = random.sample(all_log_files, MAX_FILES_TO_PROCESS)
        else:
            log_files_to_process = all_log_files
            print(f"Processing all {len(log_files_to_process)} found files matching personas.")
            
    except FileNotFoundError:
        print(f"Error: Log source directory not found: {LOGS_SOURCE_DIR}")
        exit()

    # Process logs and accumulate data
    all_per_question_data = []
    all_session_summaries = []
    
    print("Processing log files...")
    try:
        from tqdm import tqdm
        file_iterator = tqdm(log_files_to_process)
    except ImportError:
        file_iterator = log_files_to_process

    for filename in file_iterator:
        filepath = os.path.join(LOGS_SOURCE_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                log_data = json.load(f)
            
            per_q_df, session_summary = process_log_file_for_viz(log_data, question_details_lookup, filename)
            
            if per_q_df is not None and not per_q_df.empty:
                all_per_question_data.append(per_q_df)
            if session_summary is not None:
                 all_session_summaries.append(session_summary)

        except Exception as e:
            print(f"\nWarning: Error processing file {filename}: {e}")

    if not all_per_question_data or not all_session_summaries:
        print("Error: No data processed successfully. Cannot create visualizations.")
        exit()

    # Combine data into large DataFrames
    df_questions = pd.concat(all_per_question_data, ignore_index=True)
    df_sessions = pd.DataFrame(all_session_summaries)

    print(f"\nProcessed data from {len(df_sessions)} sessions.")
    
    # --- Add Check for Persona Mean Accuracies ---
    print("Checking calculated mean accuracies per persona (before plotting):")
    mean_acc_check = df_questions.groupby("persona")['answered_correctly'].mean()
    # Ensure all expected personas are checked, even if they had no valid data
    mean_acc_check = mean_acc_check.reindex(persona_order) 
    for persona, avg_acc in mean_acc_check.items():
        status = "OK"
        if pd.isna(avg_acc):
            status = "NaN - Will not appear in bar plot!"
        elif avg_acc == 0:
             status = "Zero (Should appear in bar plot)"
        print(f"  - {persona}: {avg_acc:.4f} ({status})" if not pd.isna(avg_acc) else f"  - {persona}: NaN ({status})")
    print("-" * 30)
    # --- End Check ---
    
    # Generate Plots
    print("Generating plots...")
    plot_time_distribution(df_questions, VIZ_OUTPUT_DIR)
    plot_accuracy(df_questions, VIZ_OUTPUT_DIR)
    plot_session_summary(df_sessions, VIZ_OUTPUT_DIR)
    plot_answer_changes(df_sessions, VIZ_OUTPUT_DIR)

    print(f"\nVisualizations saved to: {VIZ_OUTPUT_DIR}")
    print("Script finished.") 