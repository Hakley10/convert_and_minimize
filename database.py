import mysql.connector
from collections import defaultdict
from typing import Tuple, Set, Dict, Optional, List, FrozenSet

class AutomataDB:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'Automata',
            'autocommit': True
        }

    def connect(self) -> Optional[mysql.connector.MySQLConnection]:
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            return None

    def fetch_nfas(self) -> List[Tuple[int, str]]:
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, name FROM NFAs ORDER BY name")
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error fetching NFAs: {err}")
            return []

    def fetch_nfa(self, nfa_id: int) -> Tuple[Set[str], str, Set[str], Dict[str, Dict[str, Set[str]]]]:
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    # Get states
                    cursor.execute("""
                        SELECT state, is_start, is_final FROM NFA_States 
                        WHERE nfa_id = %s ORDER BY state
                    """, (nfa_id,))
                    
                    states = set()
                    start = ""
                    finals = set()
                    
                    for state, is_start, is_final in cursor:
                        states.add(state)
                        if is_start:
                            start = state
                        if is_final:
                            finals.add(state)

                    # Get transitions
                    cursor.execute("""
                        SELECT from_state, symbol, to_state 
                        FROM NFA_Transitions 
                        WHERE nfa_id = %s
                        ORDER BY from_state, symbol
                    """, (nfa_id,))
                    
                    transitions = defaultdict(lambda: defaultdict(set))
                    for from_state, symbol, to_state in cursor:
                        transitions[from_state][symbol].add(to_state)

                    return states, start, finals, dict(transitions)

        except mysql.connector.Error as err:
            print(f"Error fetching NFA {nfa_id}: {err}")
            return set(), "", set(), defaultdict(lambda: defaultdict(set))