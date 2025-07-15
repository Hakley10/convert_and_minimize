from collections import deque
from typing import Set, Dict, FrozenSet, Tuple

def epsilon_closure(states: Set[str], transitions: Dict[str, Dict[str, Set[str]]]) -> FrozenSet[str]:
    closure = set(states)
    queue = deque(states)
    
    while queue:
        state = queue.popleft()
        for to_state in transitions.get(state, {}).get('ε', set()):
            if to_state not in closure:
                closure.add(to_state)
                queue.append(to_state)
    
    return frozenset(closure)

def convert_nfa_to_dfa(
    states: Set[str],
    start: str,
    finals: Set[str],
    transitions: Dict[str, Dict[str, Set[str]]]
) -> Tuple[Set[FrozenSet[str]], FrozenSet[str], Set[FrozenSet[str]], Dict[Tuple[FrozenSet[str], str], FrozenSet[str]]]:
    
    dfa_transitions = {}
    dfa_states = set()
    dfa_finals = set()
    
    initial_state = epsilon_closure({start}, transitions)
    queue = deque([initial_state])
    
    while queue:
        current = queue.popleft()
        
        if current in dfa_states:
            continue
            
        dfa_states.add(current)
        
        if any(s in finals for s in current):
            dfa_finals.add(current)
        
        # Find all unique symbols (excluding epsilon)
        symbols = {sym for state in current 
                    for sym in transitions.get(state, {}).keys()
                    if sym != 'ε'}
        
        for sym in symbols:
            next_states = set()
            for state in current:
                next_states.update(transitions.get(state, {}).get(sym, set()))
            
            if next_states:
                next_closure = epsilon_closure(next_states, transitions)
                dfa_transitions[(current, sym)] = next_closure
                
                if next_closure not in dfa_states:
                    queue.append(next_closure)
    
    return dfa_states, initial_state, dfa_finals, dfa_transitions