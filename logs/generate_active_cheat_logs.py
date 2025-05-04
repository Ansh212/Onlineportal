import random
import datetime
import time
import json
import math
# import numpy as np 

# --- Data Provided by User ---
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
MIN_TIME_PER_ACTION = 1.0 

# Scenario 3: Active Cheat (Tab Switching) Params
ACTIVE_CHEAT_SEARCH_PROB = { # Probability of searching (tab switch) per difficulty
    "Easy": 0.05, 
    "Medium": 0.30,
    "Hard": 0.60, 
}
ACTIVE_CHEAT_SEARCH_TIME = (30, 15) # Mean, Std Dev (seconds) for tab switch duration
ACTIVE_CHEAT_BASE_TIME = { # Base time spent on question *when not searching*
    "Easy": (15, 5),
    "Medium": (25, 8),
    "Hard": (40, 12),
}
ACTIVE_CHEAT_ACCURACY = { # Probability of correct answer
    "searching": 0.95, # High accuracy if they searched
    "not_searching_easy": 0.70, # Lower base accuracy if not searching
    "not_searching_medium": 0.50,
    "not_searching_hard": 0.30,
}
ACTIVE_CHEAT_JUMP_PROB = 0.05 # Low chance to jump questions
ACTIVE_CHEAT_CHANGE_ANSWER_PROB = 0.02 # Very low chance to change answer

# --- Helper Functions ---
def get_random_time(mean, std_dev, min_time=MIN_TIME_PER_ACTION):
    """Gets a random time based on Normal distribution, ensuring minimum."""
    time_val = random.normalvariate(mean, std_dev)
    return max(min_time, time_val)

def get_timestamp(current_time_s):
    """Converts seconds since start to ISO timestamp."""
    start_datetime = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
    current_datetime = start_datetime + datetime.timedelta(seconds=current_time_s)
    return current_datetime.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def select_answer_active_cheat(question, did_search):
    """Simulates answer selection for active cheater based on search status."""
    if did_search:
        correct_prob = ACTIVE_CHEAT_ACCURACY["searching"]
    else:
        difficulty_key = f"not_searching_{question['difficulty'].lower()}"
        correct_prob = ACTIVE_CHEAT_ACCURACY[difficulty_key]
    
    if random.random() < correct_prob:
        return question["correct_answer"]
    else:
        # Select a random wrong answer
        num_options = len(question["options"])
        wrong_options = [i for i in range(num_options) if i != question["correct_answer"]]
        if not wrong_options: return question["correct_answer"]
        return random.choice(wrong_options)

# --- Main Simulation Function ---

def generate_synthetic_log(questions, time_limit):
    """Generates a synthetic log array for the active cheating (tab switch) scenario."""
    
    logs = []
    current_time_s = 0.0
    current_question_idx = 0 
    selected_options = [None] * len(questions) # Track selected options
    visited_mask = [False] * len(questions)
    questions_remaining = len(questions)
    last_real_interaction_idx = 0 
    tab_switch_count = 0 # Track number of tab switches

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

    # --- Active Cheating Logic ---
    while current_time_s < time_limit and questions_remaining > 0:
        if not visited_mask[current_question_idx]: 
            question = questions[current_question_idx]
            last_real_interaction_idx = current_question_idx
            difficulty = question["difficulty"]
            did_search = False

            # 1. Decide whether to search (tab switch) based on difficulty
            if random.random() < ACTIVE_CHEAT_SEARCH_PROB[difficulty]:
                did_search = True
                tab_switch_count += 1
                
                # Log Tab Switched
                switch_start_time = current_time_s
                logs.append({"location": None, "timestamp": get_timestamp(switch_start_time), "activity_text": "Tab Switched"})
                
                # Add search time delay
                search_time_mean, search_time_std = ACTIVE_CHEAT_SEARCH_TIME
                search_delay = get_random_time(search_time_mean, search_time_std)
                current_time_s += search_delay
                if current_time_s >= time_limit: break

                # Log Returned to Test Tab
                logs.append({"location": None, "timestamp": get_timestamp(current_time_s), "activity_text": "Returned to Test Tab"})
                
                # Add small delay after returning before answering
                post_search_delay = get_random_time(2, 1)
                current_time_s += post_search_delay
                if current_time_s >= time_limit: break
            
            else: # Did not search
                # Use base thinking time
                base_time_mean, base_time_std = ACTIVE_CHEAT_BASE_TIME[difficulty]
                think_time = get_random_time(base_time_mean, base_time_std)
                current_time_s += think_time
                if current_time_s >= time_limit: break

            # 2. Select an answer (accuracy depends on whether search occurred)
            selected_option_idx = select_answer_active_cheat(question, did_search)
            selected_options[current_question_idx] = selected_option_idx                
            
            click_time = get_random_time(1.5, 0.5)
            current_time_s += click_time
            if current_time_s >= time_limit: break

            logs.append({
                "location": question["id"],
                "timestamp": get_timestamp(current_time_s),
                "activity_text": f"Selected option {selected_option_idx} for question {current_question_idx}"
            })

            # 3. Simulate very rare answer change (cheaters less likely to change)
            if random.random() < ACTIVE_CHEAT_CHANGE_ANSWER_PROB:
                change_delay = get_random_time(8, 4) # Shorter rethink time
                current_time_s += change_delay
                if current_time_s >= time_limit: break
                logs.append({"location": question["id"], "timestamp": get_timestamp(current_time_s), "activity_text": f"Cleared option for question {current_question_idx}"})
                selected_options[current_question_idx] = None 
                new_selection_delay = get_random_time(3, 1)
                current_time_s += new_selection_delay
                if current_time_s >= time_limit: break                    
                new_selected_option_idx = select_answer_active_cheat(question, did_search) # Re-select based on original search decision
                selected_options[current_question_idx] = new_selected_option_idx
                logs.append({"location": question["id"], "timestamp": get_timestamp(current_time_s), "activity_text": f"Selected option {new_selected_option_idx} for question {current_question_idx}"})                
            
            visited_mask[current_question_idx] = True
            questions_remaining -= 1

        # --- Decide Next Question (Similar navigation logic to Normal) ---
        if questions_remaining == 0: break 
        jump = random.random() < ACTIVE_CHEAT_JUMP_PROB
        next_question_idx = -1
        if jump:
            unvisited_indices = [i for i, visited in enumerate(visited_mask) if not visited]
            if unvisited_indices: next_question_idx = random.choice(unvisited_indices)
            else: jump = False 
        if not jump:
            temp_idx = (current_question_idx + 1) % len(questions)
            checked_count = 0
            while visited_mask[temp_idx] and checked_count < len(questions):
                temp_idx = (temp_idx + 1) % len(questions)
                checked_count += 1                
            if not visited_mask[temp_idx]: next_question_idx = temp_idx
        
        if next_question_idx != -1 and next_question_idx != current_question_idx:
             current_question_idx = next_question_idx
             nav_time = get_random_time(1.5, 0.5)
             current_time_s += nav_time
             if current_time_s >= time_limit: break                 
             logs.append({"location": questions[current_question_idx]["id"], "timestamp": get_timestamp(current_time_s), "activity_text": f"Selected question {current_question_idx}"})
        elif questions_remaining == 0: break 
        # No extra tab switch logic here, as switches are tied to questions

    # Final Submit Log
    final_q_id = questions[last_real_interaction_idx]["id"]
    if current_time_s < time_limit and not questions_remaining > 0 : # Only submit if finished
        submit_delay = get_random_time(1.5, 0.5)
        current_time_s += submit_delay
        current_time_s = min(current_time_s, time_limit - 0.001) 
        logs.append({
            "location": final_q_id, 
            "timestamp": get_timestamp(current_time_s),
            "activity_text": "Submitted Test"
        })

    return logs, "active_cheat" # Return the label

# --- Example Usage --- 
if __name__ == "__main__":
    # --- Generate Active Cheat Example ---
    print(f"Generating log for scenario: active_cheat")
    active_logs, label = generate_synthetic_log(questions_data, TIME_LIMIT_SECONDS)
    
    start_time = datetime.datetime.fromisoformat(active_logs[0]['timestamp'].replace('Z', '+00:00'))
    # Use the timestamp of the final log entry (might not be submit if time ran out)
    end_time = datetime.datetime.fromisoformat(active_logs[-1]['timestamp'].replace('Z', '+00:00'))
    total_duration_minutes = (end_time - start_time).total_seconds() / 60
    
    # Count tab switches from logs
    tab_switch_count_from_log = sum(1 for log in active_logs if log['activity_text'] == 'Tab Switched')

    print(f"Generated {len(active_logs)} log entries.")
    print(f"Simulated test duration (active cheat): {total_duration_minutes:.2f} minutes")
    print(f"Simulated tab switches: {tab_switch_count_from_log}")
    print(f"Label: {label}")
    #print full log
    print(json.dumps(active_logs, indent=2))
    
    # Optionally print sample logs or save to file
    # print("
    #--- Sample Logs (Active Cheat Scenario) ---")
    # # Find logs around a tab switch event
    # switch_indices = [i for i, log in enumerate(active_logs) if log['activity_text'] == 'Tab Switched']
    # if switch_indices:
    #     sample_idx = switch_indices[0] # Show logs around the first switch
    #     print(json.dumps(active_logs[max(0, sample_idx-3):min(len(active_logs), sample_idx+4)], indent=2))
    # else:
    #      print(json.dumps(active_logs[:5] + active_logs[-5:], indent=2))

    # To save to a file:
    # filename = f"active_cheat_log_{int(time.time())}.json"
    # with open(filename, 'w') as f:
    #     json.dump({"label": label, "logs": active_logs}, f, indent=2)
    # print(f"
#Saved log to {filename}") 