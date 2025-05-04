import random
import datetime
import time
import json
import math
import numpy as np # Using numpy for potentially better random number generation if needed later

# --- Data Provided by User ---
# (questions_data remains the same as before)
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

# --- Simulation Parameters ---
TIME_LIMIT_SECONDS = 60 * 60 # 60 minutes
NUM_QUESTIONS = len(questions_data)
MIN_TIME_PER_ACTION = 1.0 # Minimum seconds for any action like selection

# Scenario 1: Normal User Params
NORMAL_TIME_PARAMS = { # Mean, Std Dev (seconds)
    "Easy": (50, 10),
    "Medium": (90, 20),
    "Hard": (170, 30),
}
NORMAL_ACCURACY_PARAMS = { # Probability of correct answer
    "Easy": 0.90,
    "Medium": 0.75,
    "Hard": 0.55,
}
NORMAL_CHANGE_ANSWER_PROB = 0.15 # <-- INCREASED from 0.05
NORMAL_JUMP_PROB = 0.10 # <-- Increased probability to jump from sequential
NORMAL_TAB_SWITCH_PROB = 0.01 # Very low chance per test

# --- Helper Functions --- (Keep get_random_time, get_timestamp, select_answer_normal as before)
def get_random_time(mean, std_dev, min_time=MIN_TIME_PER_ACTION):
    """Gets a random time based on Normal distribution, ensuring minimum."""
    time_val = random.normalvariate(mean, std_dev)
    return max(min_time, time_val)

def get_timestamp(current_time_s):
    """Converts seconds since start to ISO timestamp."""
    start_datetime = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
    current_datetime = start_datetime + datetime.timedelta(seconds=current_time_s)
    return current_datetime.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def select_answer_normal(question):
    """Simulates answer selection for a normal user based on difficulty."""
    difficulty = question["difficulty"]
    correct_prob = NORMAL_ACCURACY_PARAMS[difficulty]

    if random.random() < correct_prob:
        return question["correct_answer"]
    else:
        num_options = len(question["options"])
        wrong_options = [i for i in range(num_options) if i != question["correct_answer"]]
        if not wrong_options:
             return question["correct_answer"]
        return random.choice(wrong_options)

# --- Main Simulation Function ---

def generate_synthetic_log(scenario_type, questions, time_limit):
    logs = []
    current_time_s = 0.0
    current_question_idx = 0 # Start at the first question
    selected_options = [None] * len(questions)
    # Keep track of which questions have been visited/attempted
    visited_mask = [False] * len(questions)
    questions_remaining = len(questions)
    last_real_interaction_idx = 0 # Track last question interacted with for final submit log

    # Start Test Log
    first_question_id = questions[0]["id"]
    current_time_s += get_random_time(2, 1) # Small delay to start
    logs.append({
        "location": first_question_id,
        "timestamp": get_timestamp(current_time_s),
        "activity_text": "Test Started"
    })
    # Log initial selection of Q0
    nav_time = get_random_time(1.5, 0.5)
    current_time_s += nav_time
    logs.append({
        "location": questions[current_question_idx]["id"],
        "timestamp": get_timestamp(current_time_s),
        "activity_text": f"Selected question {current_question_idx}"
    })


    if scenario_type == "normal":
        # Simulate Normal User behavior with refined navigation/changes
        
        # Simulate rare tab switch for the whole test
        did_tab_switch = random.random() < NORMAL_TAB_SWITCH_PROB
        tab_switch_time = 0
        if did_tab_switch:
            tab_switch_time = get_random_time(15, 5) # Duration of switch

        while current_time_s < time_limit and questions_remaining > 0:
            # --- Process Current Question ---
            if not visited_mask[current_question_idx]: # Only process if not yet visited
                question = questions[current_question_idx]
                last_real_interaction_idx = current_question_idx

                # 2. Simulate thinking/answering time based on difficulty
                think_time_mean, think_time_std = NORMAL_TIME_PARAMS[question["difficulty"]]
                think_time = get_random_time(think_time_mean, think_time_std)
                current_time_s += think_time
                if current_time_s >= time_limit: break

                # 3. Select an answer
                selected_option_idx = select_answer_normal(question)
                selected_options[current_question_idx] = selected_option_idx
                
                click_time = get_random_time(1.5, 0.5)
                current_time_s += click_time
                if current_time_s >= time_limit: break

                logs.append({
                    "location": question["id"],
                    "timestamp": get_timestamp(current_time_s),
                    "activity_text": f"Selected option {selected_option_idx} for question {current_question_idx}"
                })

                # 4. Simulate occasional answer change (with increased probability)
                if random.random() < NORMAL_CHANGE_ANSWER_PROB:
                    change_delay = get_random_time(10, 5)
                    current_time_s += change_delay
                    if current_time_s >= time_limit: break

                    logs.append({
                        "location": question["id"],
                        "timestamp": get_timestamp(current_time_s),
                        "activity_text": f"Cleared option for question {current_question_idx}"
                    })
                    selected_options[current_question_idx] = None 

                    new_selection_delay = get_random_time(5, 2)
                    current_time_s += new_selection_delay
                    if current_time_s >= time_limit: break
                    
                    new_selected_option_idx = select_answer_normal(question) 
                    selected_options[current_question_idx] = new_selected_option_idx

                    logs.append({
                        "location": question["id"],
                        "timestamp": get_timestamp(current_time_s),
                        "activity_text": f"Selected option {new_selected_option_idx} for question {current_question_idx}"
                    })
                
                # Mark as visited and decrement remaining count
                visited_mask[current_question_idx] = True
                questions_remaining -= 1


            # --- Decide Next Question ---
            if questions_remaining == 0: break # Exit if all questions done

            jump = random.random() < NORMAL_JUMP_PROB
            next_question_idx = -1

            if jump:
                # Try to jump to a random *unvisited* question
                unvisited_indices = [i for i, visited in enumerate(visited_mask) if not visited]
                if unvisited_indices:
                    next_question_idx = random.choice(unvisited_indices)
                else:
                    # If somehow all are visited (shouldn't happen here), just break or move sequentially
                    jump = False # Force sequential if jump fails

            if not jump:
                # Try to move sequentially to the next unvisited question
                temp_idx = (current_question_idx + 1) % len(questions)
                checked_count = 0
                while visited_mask[temp_idx] and checked_count < len(questions):
                    temp_idx = (temp_idx + 1) % len(questions)
                    checked_count += 1
                
                if not visited_mask[temp_idx]:
                    next_question_idx = temp_idx
                # If all remaining are visited (shouldn't happen if questions_remaining > 0), loop will exit

            if next_question_idx != -1 and next_question_idx != current_question_idx:
                 # Log the navigation to the new question
                 current_question_idx = next_question_idx
                 nav_time = get_random_time(1.5, 0.5)
                 current_time_s += nav_time
                 if current_time_s >= time_limit: break
                 
                 logs.append({
                     "location": questions[current_question_idx]["id"],
                     "timestamp": get_timestamp(current_time_s),
                     "activity_text": f"Selected question {current_question_idx}"
                 })
            elif questions_remaining == 0:
                 break # All questions visited
            # else: continue loop to re-evaluate state if no next index found

            # 5. Insert tab switch logs if it happened (can happen between questions)
            if did_tab_switch and questions_remaining < len(questions) / 2 : # Inject roughly halfway
                 switch_start_time = current_time_s
                 current_time_s += tab_switch_time 
                 if current_time_s >= time_limit: break
                 
                 logs.append({"location": None, "timestamp": get_timestamp(switch_start_time), "activity_text": "Tab Switched"})
                 logs.append({"location": None, "timestamp": get_timestamp(current_time_s), "activity_text": "Returned to Test Tab"})
                 did_tab_switch = False # Only once

    elif scenario_type == "pre_knowledge":
        # TODO: Implement Scenario 2 Logic
        pass
    elif scenario_type == "active_cheat":
        # TODO: Implement Scenario 3 Logic
        pass
    else:
        raise ValueError("Unknown scenario_type")

    # Final Submit Log
    final_q_id = questions[last_real_interaction_idx]["id"]
    if current_time_s < time_limit:
        submit_delay = get_random_time(1.5, 0.5)
        current_time_s += submit_delay
        # Make sure submit time doesn't exceed limit (cosmetic)
        current_time_s = min(current_time_s, time_limit - 0.001) 
        logs.append({
            "location": final_q_id,
            "timestamp": get_timestamp(current_time_s),
            "activity_text": "Submitted Test"
        })
    # else: User ran out of time, no explicit submit log

    return logs, scenario_type

# --- Example Usage --- (remains the same)
if __name__ == "__main__":
    print(f"Generating log for scenario: normal")
    normal_logs, label = generate_synthetic_log("normal", questions_data, TIME_LIMIT_SECONDS)
    
    # Calculate total time from logs
    start_time = datetime.datetime.fromisoformat(normal_logs[0]['timestamp'].replace('Z', '+00:00'))
    end_time = datetime.datetime.fromisoformat(normal_logs[-1]['timestamp'].replace('Z', '+00:00'))
    total_duration_minutes = (end_time - start_time).total_seconds() / 60

    print(f"Generated {len(normal_logs)} log entries.")
    print(f"Simulated test duration: {total_duration_minutes:.2f} minutes")
    print(json.dumps(normal_logs, indent=2))
    
    # print("\n--- Sample Logs (Normal Scenario - Refined) ---")
    # print(json.dumps(normal_logs[:5], indent=2))
    # print("...")
    # print(json.dumps(normal_logs[-5:], indent=2))
    # print(f"Label: {label}")

    # Check navigation pattern (simple check: count unique 'Selected question' indices)
    selected_q_indices = set()
    for log in normal_logs:
        if log['activity_text'].startswith('Selected question'):
            try:
                idx = int(log['activity_text'].split()[-1])
                selected_q_indices.add(idx)
            except: pass # Ignore if parsing fails
    print(f"\nNavigation check: Visited {len(selected_q_indices)} unique question indices via 'Selected question' logs.")
