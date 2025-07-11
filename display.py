from typing import Dict, Tuple, FrozenSet, Set, Optional
from collections import defaultdict
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("Note: Graphviz not installed - using text display only")

def display_automaton(
    states: Set[FrozenSet[str]],
    start: FrozenSet[str],
    finals: Set[FrozenSet[str]],
    transitions: Dict[Tuple[FrozenSet[str], str], FrozenSet[str]],
    name: str = "Automaton"
) -> Optional[Digraph]:
    """Visualize automaton using Graphviz or ASCII"""
    if not GRAPHVIZ_AVAILABLE:
        print("\nGraph visualization not available - here's the text representation:")
        print_automaton(states, start, finals, transitions, name)
        return None
        
    try:
        dot = Digraph()
        dot.attr(rankdir='LR')
        
        # Add states
        for state in states:
            label = ','.join(sorted(state))
            if state in finals:
                dot.node(label, shape='doublecircle', color='green')
            else:
                dot.node(label)
            
            if state == start:
                dot.node('start', shape='none', label='')
                dot.edge('start', label)
        
        # Add transitions
        for (from_state, symbol), to_state in transitions.items():
            from_label = ','.join(sorted(from_state))
            to_label = ','.join(sorted(to_state))
            dot.edge(from_label, to_label, label=symbol)
        
        output_path = dot.render(f'automaton_{name}', view=True, cleanup=True)
        print(f"Visualization saved to: {output_path}")
        return dot
    except Exception as e:
        print(f"Visualization error: {e}")
        return None

def print_automaton(
    states: Set[FrozenSet[str]],
    start: FrozenSet[str],
    finals: Set[FrozenSet[str]],
    transitions: Dict[Tuple[FrozenSet[str], str], FrozenSet[str]],
    title: str = "Automaton"
) -> None:
    """Print automaton details to console"""
    print(f"\n{title}:")
    print("States:", ', '.join('{' + ','.join(sorted(s)) + '}' for s in states))
    print("Start:", '{' + ','.join(sorted(start)) + '}')
    print("Final:", ', '.join('{' + ','.join(sorted(f)) + '}' for f in finals))
    
    print("\nTransitions:")
    for (from_state, symbol), to_state in sorted(transitions.items()):
        print(f"{{ {','.join(sorted(from_state))} }} -- {symbol} --> {{ {','.join(sorted(to_state))} }}")