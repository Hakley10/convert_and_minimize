import mysql.connector
from collections import defaultdict
from typing import Tuple, Set, Dict, Optional, List, FrozenSet

class AutomataDB:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'FiniteAutomatonDBV2',
            'autocommit': True
        }
        self.initialize_database()

    def initialize_database(self):
        try:
            temp_config = {k: v for k, v in self.config.items() if k != 'database'}
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS FiniteAutomatonDBV2")
            cursor.execute("USE FiniteAutomatonDBV2")

            # NFA Tables
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

            # DFA Tables
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
                 finals: Set[FrozenSet[str]], 
                 transitions: Dict[Tuple[FrozenSet[str], str], FrozenSet[str]], 
                 source_nfa_id: Optional[int] = None) -> int:
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO DFAs (name, source_nfa_id)
                        VALUES (%s, %s)
                    """, (name, source_nfa_id))
                    dfa_id = cursor.lastrowid

                    def frozenset_to_str(fs: FrozenSet) -> str:
                        if not fs:
                            return "{}"
                        if isinstance(next(iter(fs)), frozenset):
                            return '{' + ','.join(sorted(frozenset_to_str(s) for s in fs)) + '}'
                        else:
                            return '{' + ','.join(sorted(fs)) + '}'

                    state_map = {}
                    for state in states:
                        state_str = frozenset_to_str(state)
                        state_map[state] = state_str
                        is_start = (state == start)
                        is_final = (state in finals)
                        cursor.execute("""
                            INSERT INTO DFA_States (dfa_id, state, is_start, is_final)
                            VALUES (%s, %s, %s, %s)
                        """, (dfa_id, state_str, is_start, is_final))

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
            return -1

    def save_nfa(self, name: str, states: Set[str], start: str, finals: Set[str], transitions: Dict[str, Dict[str, Set[str]]]) -> int:
        """Saves an NFA to the database."""
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO NFAs (name) VALUES (%s)", (name,))
                    nfa_id = cursor.lastrowid

                    for state in states:
                        is_start = state == start
                        is_final = state in finals
                        cursor.execute("""
                            INSERT INTO NFA_States (nfa_id, state, is_start, is_final)
                            VALUES (%s, %s, %s, %s)
                        """, (nfa_id, state, is_start, is_final))

                    for from_state, sym_trans in transitions.items():
                        for symbol, to_states in sym_trans.items():
                            for to_state in to_states:
                                cursor.execute("""
                                    INSERT INTO NFA_Transitions (nfa_id, from_state, symbol, to_state)
                                    VALUES (%s, %s, %s, %s)
                                """, (nfa_id, from_state, symbol, to_state))
                    
                    conn.commit()
                    return nfa_id

        except mysql.connector.Error as err:
            print(f"Error saving NFA: {err}")
            return -1

def insert_sample_nfas(db: AutomataDB):
    """Inserts two sample NFAs into the database."""
    nfas = db.fetch_nfas()
    if not nfas:
        # Sample NFA 1: a, b
        nfa1_states = {'q0', 'q1', 'q2'}
        nfa1_start = 'q0'
        nfa1_finals = {'q2'}
        nfa1_transitions = {
            'q0': {'a': {'q0'}, 'b': {'q0', 'q1'}},
            'q1': {'b': {'q2'}},
            'q2': {'a': {'q2'}, 'b': {'q2'}}
        }
        db.save_nfa("Sample NFA 1", nfa1_states, nfa1_start, nfa1_finals, nfa1_transitions)
        
        # Sample NFA 2: b, ε
        nfa2_states = {'s0', 's1', 's2'}
        nfa2_start = 's0'
        nfa2_finals = {'s2'}
        nfa2_transitions = {
            's0': {'b': {'s0'}, 'ε': {'s1'}},
            's1': {'b': {'s1'}, 'ε': {'s2'}},
            's2': {'b': {'s2'}}
        }
        db.save_nfa("Sample NFA 2", nfa2_states, nfa2_start, nfa2_finals, nfa2_transitions)
        
        print("\nSample NFAs have been added to the database.\n")