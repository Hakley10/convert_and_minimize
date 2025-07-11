from database import AutomataDB
from nfa_to_dfa import convert_nfa_to_dfa
from dfa_minimizer import minimize_dfa
from display import display_automaton, print_automaton

def main():
    db = AutomataDB()
    
    while True:
        print("\nAutomata Toolkit")
        print("1. List NFAs")
        print("2. Convert NFA to DFA")
        print("3. Minimize DFA")
        print("4. Exit")
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            list_nfas(db)
        elif choice == '2':
            convert_nfa(db)
        elif choice == '3':
            minimize_dfa_interactive(db)
        elif choice == '4':
            break
        else:
            print("Invalid choice")

def list_nfas(db: AutomataDB):
    nfas = db.fetch_nfas()
    if not nfas:
        print("No NFAs found in database")
        return
    
    print("\nAvailable NFAs:")
    for id, name in nfas:
        print(f"{id}. {name}")

def convert_nfa(db: AutomataDB):
    nfas = db.fetch_nfas()
    if not nfas:
        print("No NFAs available for conversion")
        return
    
    print("\nAvailable NFAs:")
    for id, name in nfas:
        print(f"{id}. {name}")
    
    try:
        nfa_id = int(input("\nSelect NFA ID to convert: "))
        states, start, finals, transitions = db.fetch_nfa(nfa_id)
        
        if not states:
            print("Invalid NFA selected")
            return
        
        print("\nConverting NFA to DFA...")
        dfa_states, dfa_start, dfa_finals, dfa_trans = convert_nfa_to_dfa(
            states, start, finals, transitions)
        
        print_automaton(dfa_states, dfa_start, dfa_finals, dfa_trans, "Converted DFA")
        display_automaton(dfa_states, dfa_start, dfa_finals, dfa_trans, "DFA")
        
    except ValueError:
        print("Please enter a valid number")

def minimize_dfa_interactive(db: AutomataDB):
    # Similar to convert_nfa but starts with a DFA
    pass

if __name__ == "__main__":
    main()