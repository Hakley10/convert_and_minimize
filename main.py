from database import AutomataDB
from nfa_to_dfa import convert_nfa_to_dfa
from dfa_minimizer import minimize_dfa
from display import display_automaton, print_automaton

def main():
    db = AutomataDB()
    
    while True:
        print("\nAutomata Toolkit")
        print("1. Convert NFA to DFA")
        print("2. Minimize DFA")
        print("3. Exit")
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            convert_nfa(db)
        elif choice == '2':
            minimize_dfa_interactive(db)
        elif choice == '3':
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
        
        show_png = input("Would you like to show the visualization? (y/n): ").lower()
        if show_png == 'y':
            display_automaton(dfa_states, dfa_start, dfa_finals, dfa_trans, "DFA")
            
        save = input("Would you like to save this DFA? (y/n): ").lower()
        if save == 'y':
            name = input("Enter a name for this DFA: ")
            db.save_dfa(name, dfa_states, dfa_start, dfa_finals, dfa_trans, nfa_id)
            print("DFA saved successfully!")
        
    except ValueError:
        print("Please enter a valid number")

def minimize_dfa_interactive(db: AutomataDB):
    dfas = db.fetch_dfas()
    if not dfas:
        print("No DFAs found in database. Would you like to convert an NFA to DFA first?")
        choice = input("Enter 'y' to convert NFA to DFA or any key to cancel: ").lower()
        if choice == 'y':
            convert_nfa(db)
        return
    
    print("\nAvailable DFAs:")
    for id, name in dfas:
        print(f"{id}. {name}")
    
    try:
        dfa_id = int(input("\nSelect DFA ID to minimize: "))
        states, start, finals, transitions = db.fetch_dfa(dfa_id)
        
        if not states:
            print("Invalid DFA selected")
            return
        
        # Convert to frozen sets for minimization
        frozen_states = {frozenset({s}) for s in states}
        frozen_start = frozenset({start})
        frozen_finals = {frozenset({f}) for f in finals}
        frozen_transitions = {(frozenset({f}), s): frozenset({t}) 
                            for (f, s), t in transitions.items()}
        
        print("\nMinimizing DFA...")
        min_states, min_start, min_finals, min_trans = minimize_dfa(
            frozen_states, frozen_start, frozen_finals, frozen_transitions)
        
        print_automaton(min_states, min_start, min_finals, min_trans, "Minimized DFA")
        
        show_png = input("Would you like to show the visualization? (y/n): ").lower()
        if show_png == 'y':
            display_automaton(min_states, min_start, min_finals, min_trans, "Minimized_DFA")
        
        save = input("Would you like to save this minimized DFA? (y/n): ").lower()
        if save == 'y':
            name = input("Enter a name for this minimized DFA: ")
            db.save_dfa(name, min_states, min_start, min_finals, min_trans)
            print("Minimized DFA saved successfully!")
        
    except ValueError:
        print("Please enter a valid number")

if __name__ == "__main__":
    main()