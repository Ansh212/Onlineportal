# Tool Input
# Creating a new file: batch_generate_logs.py
# Need to make sure the generation scripts (`normal_user.py`, `generate_pre_knowledge_logs.py`)
# have the main generation logic cleanly encapsulated in functions that can be imported.
# Assuming `normal_user.py` has a function `generate_synthetic_log()` that returns `(logs, "normal")`
# and `generate_pre_knowledge_logs.py` has a function `generate_synthetic_log()` that returns `(logs, "pre_knowledge")`

# Let's refine the generator scripts first to ensure they are importable.

# Refinement for normal_user.py (only relevant parts shown)
# ----------------------------------------------------------
# import ... (all necessary imports)
# questions_data = [...] (full list)
# TIME_LIMIT_SECONDS = ...
# NORMAL_TIME_PARAMS = ...
# ... (other params and helper functions) ...

# def generate_normal_log(questions, time_limit): # Renamed and encapsulated
#     # ... (existing logic from generate_synthetic_log for 'normal') ...
#     return logs, "normal"

# if __name__ == "__main__":
#     # ... (example usage remains here) ...
#     normal_logs, label = generate_normal_log(questions_data, TIME_LIMIT_SECONDS)
#     # ... (print statements) ...
# ----------------------------------------------------------

# Refinement for generate_pre_knowledge_logs.py (only relevant parts shown)
# ----------------------------------------------------------
# import ... (all necessary imports)
# questions_data = [...] (full list)
# TIME_LIMIT_SECONDS = ...
# PRE_KNOWLEDGE_TIME_PER_Q = ...
# ... (helper functions) ...

# def generate_pre_knowledge_log(questions, time_limit): # Renamed and encapsulated
#     # ... (existing logic from generate_synthetic_log for 'pre_knowledge') ...
#     return logs, "pre_knowledge"

# if __name__ == "__main__":
#     # ... (example usage remains here) ...
#     preknow_logs, label = generate_pre_knowledge_log(questions_data, TIME_LIMIT_SECONDS)
#     # ... (print statements) ...
# ----------------------------------------------------------

# Now, create batch_generate_logs.py

import json
import os
import time
from tqdm import tqdm  # For progress bar

# --- Define questions_data and time limit centrally ---
# (Copied from normal_user.py for consistency)
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
TIME_LIMIT_SECONDS = 60 * 60 # 60 minutes

# --- Import the actual generator function using aliases ---
try:
    # Import the function that takes scenario_type as the first arg
    from normal_user import generate_synthetic_log as generate_normal_synthetic
    from generate_pre_knowledge_logs import generate_synthetic_log as generate_pre_knowledge_synthetic
    # Import generate_active_cheat_log if needed later
    # from generate_active_cheat_logs import generate_synthetic_log as generate_active_cheat_synthetic

except ImportError as e:
    print(f"Error importing generator functions: {e}")
    print("Please ensure 'normal_user.py', 'generate_pre_knowledge_logs.py' etc. are in the same directory")
    print("and contain the function 'generate_synthetic_log'.")
    exit(1)

# --- Configuration ---
NUM_LOGS_PER_SCENARIO = 500
OUTPUT_DIR = "generated_logs_2"

# --- Main Generation Logic ---
def generate_and_save_logs(scenario_name, generator_func, num_logs):
    """Generates and saves logs for a given scenario, passing the scenario name."""
    print(f"\nGenerating {num_logs} logs for scenario: {scenario_name}...")
    
    try:
        iterator = tqdm(range(num_logs), desc=scenario_name)
    except NameError: # If tqdm is not imported/installed
        iterator = range(num_logs)
        print("(Consider installing 'tqdm' for a progress bar: pip install tqdm)")

    # Determine the base output directory relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__)) 
    full_output_dir = os.path.join(script_dir, OUTPUT_DIR)

    for i in iterator:
        # Generate the log data, passing the scenario_name as the first argument
        # The generator functions from the original files expect this.
        logs, label = generator_func(scenario_name, questions_data, TIME_LIMIT_SECONDS) 
        
        output_data = {
            "label": label, # Use the label returned by the function
            "logs": logs
        }
        
        filename = os.path.join(full_output_dir, f"{scenario_name}_{i+1:04d}.json") 
        
        try:
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=2)
        except IOError as e:
            print(f"\nError saving file {filename}: {e}")

if __name__ == "__main__":
    start_time = time.time()

    script_dir = os.path.dirname(os.path.abspath(__file__)) 
    full_output_dir = os.path.join(script_dir, OUTPUT_DIR)

    if not os.path.exists(full_output_dir):
        print(f"Creating output directory: {full_output_dir}")
        os.makedirs(full_output_dir)
    else:
        print(f"Using existing output directory: {full_output_dir}")

    # --- Generate Normal Logs ---
    # Pass the alias for the function from normal_user.py
    #generate_and_save_logs("normal", generate_normal_synthetic, NUM_LOGS_PER_SCENARIO) 

    # --- Generate Pre-Knowledge Logs ---
    # Pass the alias for the function from generate_pre_knowledge_logs.py
    generate_and_save_logs("pre_knowledge", generate_pre_knowledge_synthetic, NUM_LOGS_PER_SCENARIO) 
    
    # --- Generate Active Cheat Logs (Optional - Add if needed) ---
    # try:
    #     # Import the actual function name using an alias
    #     from generate_active_cheat_logs import generate_synthetic_log as generate_active_cheat_synthetic 
    #     generate_and_save_logs("active_cheat", generate_active_cheat_synthetic, NUM_LOGS_PER_SCENARIO)
    # except ImportError:
    #     print("\nSkipping active_cheat logs: Could not import 'generate_active_cheat_logs.py' or function.")
    # except NameError:
    #      print("\nSkipping active_cheat logs: function 'generate_active_cheat_synthetic' not defined.")


    end_time = time.time()
    total_time = end_time - start_time
    total_files_generated = len([name for name in os.listdir(full_output_dir) if os.path.isfile(os.path.join(full_output_dir, name))]) # Count actual files
    
    print(f"\nFinished generating logs.")
    print(f"Total files created in this run (approx): {NUM_LOGS_PER_SCENARIO * 2}") # Adjust if generating scenario 3
    print(f"Total files now in directory: {total_files_generated}")
    print(f"Output directory: {full_output_dir}")
    print(f"Total time taken: {total_time:.2f} seconds")