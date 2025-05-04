import random
import datetime
import time
import json

# --- Data Provided by User ---
questions_data = [
    {"id": "q1", "subject": "Maths", "difficulty": "Easy", "text": "If x^2 - 5x + 6 = 0, find x.", "options": ["1 and 6", "2 and 3", "3 and 4", "None"], "correct_answer": 1},
    {"id": "q2", "subject": "Maths", "difficulty": "Easy", "text": "Derivative of sin(x)?", "options": ["cos(x)", "-cos(x)", "-sin(x)", "sin(x)"], "correct_answer": 0},
    {"id": "q3", "subject": "Maths", "difficulty": "Easy", "text": "Distance between (1,2) and (4,6)?", "options": ["5", "4", "3", "2"], "correct_answer": 0},
    {"id": "q4", "subject": "Maths", "difficulty": "Medium", "text": "If det(A) = 5, what is det(2A)?", "options": ["10", "20", "25", "40"], "correct_answer": 1},
    {"id": "q5", "subject": "Maths", "difficulty": "Medium", "text": "Evaluate ∫x^2 dx.", "options": ["x^2/2", "x^3/3", "x^3", "x^2"], "correct_answer": 1},
    # Add remaining questions here...
]

# --- Simulation Parameters ---
TIME_LIMIT_SECONDS = 60 * 60 # 60 minutes
NUM_QUESTIONS = len(questions_data)
MIN_TIME_PER_ACTION = 0.5 # Can be slightly lower for cheaters potentially

# Scenario 2: Pre-Knowledge Cheating Params
PRE_KNOWLEDGE_TIME_PER_Q = (30, 5) # Mean, Std Dev (seconds) - very fast & consistent

# --- Helper Functions ---
def get_random_time(mean, std_dev, min_time=MIN_TIME_PER_ACTION):
    """Gets a random time based on Normal distribution, ensuring minimum."""
    time_val = random.normalvariate(mean, std_dev)
    return max(min_time, time_val)

def get_timestamp(current_time_s):
    """Converts seconds since start to ISO timestamp."""
    # Using a fixed start date for consistency in generated timestamps
    start_datetime = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
    current_datetime = start_datetime + datetime.timedelta(seconds=current_time_s)
    return current_datetime.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

# --- Main Simulation Function ---
def generate_synthetic_log(scenario_type, questions, time_limit, accuracy=0.95):
    """Generates a synthetic log array for the pre-knowledge cheating scenario with human error."""
    
    logs = []
    current_time_s = 0.0
    current_question_idx = 0
    last_real_interaction_idx = 0 # Track last question interacted with

    # Start Test Log
    first_question_id = questions[0]["id"]
    current_time_s += get_random_time(1.5, 0.5) # Small delay to start
    logs.append({
        "location": first_question_id,
        "timestamp": get_timestamp(current_time_s),
        "activity_text": "Test Started"
    })

    # Log initial selection of Q0
    nav_time = get_random_time(2.0, 0.5, min_time=0.5) # Increased navigation time
    current_time_s += nav_time
    logs.append({
        "location": questions[current_question_idx]["id"],
        "timestamp": get_timestamp(current_time_s),
        "activity_text": f"Selected question {current_question_idx}"
    })

    # --- Pre-Knowledge Cheating Logic ---
    time_mean, time_std = PRE_KNOWLEDGE_TIME_PER_Q
    
    for idx in range(len(questions)):  # Iterate strictly sequentially
        current_question_idx = idx
        question = questions[current_question_idx]
        last_real_interaction_idx = current_question_idx  # Keep track of last Q

        # 1. Simulate selecting the question (if not the first one)
        if idx > 0:
            # Increased random navigation time
            nav_time = get_random_time(2.0, 0.5, min_time=0.5) 
            current_time_s += nav_time
            if current_time_s >= time_limit: break  # Should not happen here
            
            logs.append({
                "location": question["id"],
                "timestamp": get_timestamp(current_time_s),
                "activity_text": f"Selected question {current_question_idx}"
            })

        # 2. Simulate very short time 'thinking'/selecting answer
        answer_time = get_random_time(time_mean, time_std)
        current_time_s += answer_time
        if current_time_s >= time_limit: break  # Should not happen here

        # 3. Decide whether to select the correct answer or make an error (human error)
        if random.random() > accuracy:
            # Simulate a mistake: choose a random incorrect answer
            incorrect_answers = [i for i in range(len(question["options"])) if i != question["correct_answer"]]
            selected_option_idx = random.choice(incorrect_answers)
        else:
            # Select the correct answer
            selected_option_idx = question["correct_answer"]
        
        logs.append({
            "location": question["id"],
            "timestamp": get_timestamp(current_time_s),
            "activity_text": f"Selected option {selected_option_idx} for question {current_question_idx}"
        })
        
    # Final Submit Log (Always happens very quickly after last answer)
    final_q_id = questions[last_real_interaction_idx]["id"]
    if current_time_s < time_limit:  # Should always be true
        submit_delay = get_random_time(1.5, 0.5)
        current_time_s += submit_delay
        current_time_s = min(current_time_s, time_limit - 0.001)  # Cosmetic limit check
        logs.append({
            "location": final_q_id,
            "timestamp": get_timestamp(current_time_s),
            "activity_text": "Submitted Test"
        })

    return logs, "pre_knowledge"  # Return the label along with logs

# --- Example Usage --- 
if __name__ == "__main__":
    # --- Generate Pre-Knowledge Example with 90% accuracy ---
    print(f"Generating log for scenario: pre_knowledge with human error")
    preknow_logs, label = generate_synthetic_log("pre_knowledge", questions_data, TIME_LIMIT_SECONDS, accuracy=0.95)    
    
    start_time = datetime.datetime.fromisoformat(preknow_logs[0]['timestamp'].replace('Z', '+00:00'))
    end_time = datetime.datetime.fromisoformat(preknow_logs[-1]['timestamp'].replace('Z', '+00:00'))
    total_duration_minutes = (end_time - start_time).total_seconds() / 60

    print(f"Generated {len(preknow_logs)} log entries.")
    print(f"Simulated test duration (pre-knowledge): {total_duration_minutes:.2f} minutes")    
    print(f"Label: {label}")
    # Optionally print the full log to a file or view sample
    # print(json.dumps(preknow_logs[:5] + preknow_logs[-5:], indent=2))
