from typing import Set, Dict, Tuple, FrozenSet
from collections import defaultdict

def minimize_dfa(
    states: Set[FrozenSet[str]],
    start: FrozenSet[str],
    finals: Set[FrozenSet[str]],
    transitions: Dict[Tuple[FrozenSet[str], str], FrozenSet[str]]
) -> Tuple[Set[FrozenSet[str]], FrozenSet[str], Set[FrozenSet[str]], Dict[Tuple[FrozenSet[str], str], FrozenSet[str]]]:
    
    # Initial partition
    partitions = {frozenset(finals), frozenset(states - finals)}
    waiting = set(partitions)
    
    while waiting:
        current = waiting.pop()
        
        # Get all transition symbols
        symbols = {sym for (_, sym) in transitions.keys()}
        
        for symbol in symbols:
            # Find states that transition into current set
            inverse = defaultdict(set)
            for (from_state, sym), to_state in transitions.items():
                if sym == symbol:
                    for part in partitions:
                        if to_state in part:
                            inverse[part].add(from_state)
                            break
            
            # Refine partitions
            new_partitions = set()
            for part in partitions:
                split1 = part & inverse.get(part, set())
                split2 = part - inverse.get(part, set())
                
                if split1 and split2:
                    new_partitions.add(frozenset(split1))
                    new_partitions.add(frozenset(split2))
                    
                    if part in waiting:
                        waiting.remove(part)
                        waiting.add(frozenset(split1))
                        waiting.add(frozenset(split2))
                    else:
                        waiting.add(frozenset(split1) if len(split1) <= len(split2) else waiting.add(frozenset(split2)))
                else:
                    new_partitions.add(part)
            
            partitions = new_partitions
    
    # Create state mapping
    state_map = {state: part for part in partitions for state in part}
    
    # Build new transitions
    new_transitions = {
        (state_map[from_state], sym): state_map[to_state]
        for (from_state, sym), to_state in transitions.items()
    }
    
    new_start = state_map[start]
    new_finals = {state_map[state] for state in finals}
    
    return set(partitions), new_start, new_finals, new_transitions