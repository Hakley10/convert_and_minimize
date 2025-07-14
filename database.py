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
        self.initialize_database()

    def initialize_database(self):
        try:
            conn = mysql.connector.connect(**{k: v for k, v in self.config.items() if k != 'database'})
            cursor = conn.cursor()
            
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS Automata")
            cursor.execute("USE Automata")
            
            # Create NFA tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS NFAs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS NFA_States (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nfa_id INT NOT NULL,
                    state VARCHAR(255) NOT NULL,
                    is_start BOOLEAN DEFAULT FALSE,
                    is_final BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (nfa_id) REFERENCES NFAs(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS NFA_Transitions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nfa_id INT NOT NULL,
                    from_state VARCHAR(255) NOT NULL,
                    symbol VARCHAR(255) NOT NULL,
                    to_state VARCHAR(255) NOT NULL,
                    FOREIGN KEY (nfa_id) REFERENCES NFAs(id)
                )
            """)
            
            # Create DFA tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DFAs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    source_nfa_id INT,
                    FOREIGN KEY (source_nfa_id) REFERENCES NFAs(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DFA_States (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    dfa_id INT NOT NULL,
                    state VARCHAR(255) NOT NULL,
                    is_start BOOLEAN DEFAULT FALSE,
                    is_final BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (dfa_id) REFERENCES DFAs(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DFA_Transitions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    dfa_id INT NOT NULL,
                    from_state VARCHAR(255) NOT NULL,
                    symbol VARCHAR(255) NOT NULL,
                    to_state VARCHAR(255) NOT NULL,
                    FOREIGN KEY (dfa_id) REFERENCES DFAs(id)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            print(f"Database initialization failed: {err}")

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

    def fetch_dfas(self) -> List[Tuple[int, str]]:
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, name FROM DFAs ORDER BY name")
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error fetching DFAs: {err}")
            return []

    def fetch_dfa(self, dfa_id: int) -> Tuple[Set[str], str, Set[str], Dict[Tuple[str, str], str]]:
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    # Get states
                    cursor.execute("""
                        SELECT state, is_start, is_final FROM DFA_States 
                        WHERE dfa_id = %s ORDER BY state
                    """, (dfa_id,))
                    
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
                        FROM DFA_Transitions 
                        WHERE dfa_id = %s
                        ORDER BY from_state, symbol
                    """, (dfa_id,))
                    
                    transitions = {}
                    for from_state, symbol, to_state in cursor:
                        transitions[(from_state, symbol)] = to_state

                    return states, start, finals, transitions

        except mysql.connector.Error as err:
            print(f"Error fetching DFA {dfa_id}: {err}")
            return set(), "", set(), {}

    def save_dfa(self, name: str, states: Set[FrozenSet[str]], start: FrozenSet[str], 
                finals: Set[FrozenSet[str]], transitions: Dict[Tuple[FrozenSet[str], str], FrozenSet[str]], 
                source_nfa_id: Optional[int] = None) -> int:
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    # Save DFA metadata
                    cursor.execute("""
                        INSERT INTO DFAs (name, source_nfa_id)
                        VALUES (%s, %s)
                    """, (name, source_nfa_id))
                    dfa_id = cursor.lastrowid
                    
                    # Helper to convert frozenset of frozensets (or strings) to a single string
                    def frozenset_to_str(fs: FrozenSet) -> str:
                        if not fs:
                            return "{}"
                        # Check if the elements are frozensets (for minimized DFA states)
                        if isinstance(next(iter(fs)), frozenset):
                            # Recursively format inner frozensets and sort for consistent representation
                            return '{' + ','.join(sorted(frozenset_to_str(s) for s in fs)) + '}'
                        else:
                            # Assume it's a frozenset of strings
                            return '{' + ','.join(sorted(fs)) + '}'
                    
                    # Save states
                    state_map = {}  # Maps frozenset to string representation
                    for state in states:
                        state_str = frozenset_to_str(state)
                        state_map[state] = state_str
                        
                        is_start = (state == start)
                        is_final = (state in finals)
                        
                        cursor.execute("""
                            INSERT INTO DFA_States (dfa_id, state, is_start, is_final)
                            VALUES (%s, %s, %s, %s)
                        """, (dfa_id, state_str, is_start, is_final))
                    
                    # Save transitions
                    for (from_state, symbol), to_state in transitions.items():
                        from_str = state_map[from_state]
                        to_str = state_map[to_state]
                        
                        cursor.execute("""
                            INSERT INTO DFA_Transitions (dfa_id, from_state, symbol, to_state)
                            VALUES (%s, %s, %s, %s)
                        """, (dfa_id, from_str, symbol, to_str))
                    
                    conn.commit()
                    return dfa_id
                    
        except mysql.connector.Error as err:
            print(f"Error saving DFA: {err}")
            conn.rollback()
            return -1