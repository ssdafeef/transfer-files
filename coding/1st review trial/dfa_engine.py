"""
DFA Engine for Signature-based Intrusion Detection
Implements Deterministic Finite Automata for pattern matching in network traffic
"""

import logging

class DFA:
    """
    Deterministic Finite Automata implementation for pattern matching
    """
    def __init__(self, transitions, start_state, accept_states, pattern_name="unknown"):
        """
        Initialize DFA with transitions, start state, and accept states
        
        Args:
            transitions (dict): Dictionary of (state, char) -> next_state transitions
            start_state (int): Initial state of the DFA
            accept_states (set): Set of accepting/final states
            pattern_name (str): Name of the pattern for logging
        """
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.pattern_name = pattern_name
        self.logger = logging.getLogger(__name__)

    def match(self, text):
        """
        Check if the input text contains the DFA pattern
        
        Args:
            text (str): Input text to check against the pattern
            
        Returns:
            bool: True if pattern is matched, False otherwise
        """
        # Check for pattern anywhere in the text
        for i in range(len(text)):
            state = self.start_state
            for char in text[i:]:
                if (state, char) in self.transitions:
                    state = self.transitions[(state, char)]
                    if state in self.accept_states:
                        return True
                else:
                    break
        return False

    def check_and_log(self, text):
        """
        Check for pattern match and log if detected
        
        Args:
            text (str): Input text to check
            
        Returns:
            bool: True if pattern is matched, False otherwise
        """
        if self.match(text):
            self.logger.warning(f"[DFA ALERT] Pattern '{self.pattern_name}' detected in: {text}")
            return True
        return False


# Pre-defined DFA patterns for common intrusion signatures

# Pattern for detecting "attack"
ATTACK_TRANSITIONS = {
    (0, 'a'): 1,
    (1, 't'): 2,
    (2, 't'): 3,
    (3, 'a'): 4,
    (4, 'c'): 5,
    (5, 'k'): 6
}
DFA_ATTACK = DFA(ATTACK_TRANSITIONS, 0, {6}, "attack")

# Pattern for detecting "unauthorized"
UNAUTHORIZED_TRANSITIONS = {
    (0, 'u'): 1,
    (1, 'n'): 2,
    (2, 'a'): 3,
    (3, 'u'): 4,
    (4, 't'): 5,
    (5, 'h'): 6,
    (6, 'o'): 7,
    (7, 'r'): 8,
    (8, 'i'): 9,
    (9, 'z'): 10,
    (10, 'e'): 11,
    (11, 'd'): 12
}
DFA_UNAUTHORIZED = DFA(UNAUTHORIZED_TRANSITIONS, 0, {12}, "unauthorized access")

# Pattern for detecting "scan"
SCAN_TRANSITIONS = {
    (0, 's'): 1,
    (1, 'c'): 2,
    (2, 'a'): 3,
    (3, 'n'): 4
}
DFA_SCAN = DFA(SCAN_TRANSITIONS, 0, {4}, "scan attempt")

# Pattern for detecting "malware"
MALWARE_TRANSITIONS = {
    (0, 'm'): 1,
    (1, 'a'): 2,
    (2, 'l'): 3,
    (3, 'w'): 4,
    (4, 'a'): 5,
    (5, 'r'): 6,
    (6, 'e'): 7
}
DFA_MALWARE = DFA(MALWARE_TRANSITIONS, 0, {7}, "malware")

# Pattern for detecting "injection"
INJECTION_TRANSITIONS = {
    (0, 'i'): 1,
    (1, 'n'): 2,
    (2, 'j'): 3,
    (3, 'e'): 4,
    (4, 'c'): 5,
    (5, 't'): 6,
    (6, 'i'): 7,
    (7, 'o'): 8,
    (8, 'n'): 9
}
DFA_INJECTION = DFA(INJECTION_TRANSITIONS, 0, {9}, "injection")

# Pattern for detecting "bruteforce"
BRUTEFORCE_TRANSITIONS = {
    (0, 'b'): 1,
    (1, 'r'): 2,
    (2, 'u'): 3,
    (3, 't'): 4,
    (4, 'e'): 5,
    (5, 'f'): 6,
    (6, 'o'): 7,
    (7, 'r'): 8,
    (8, 'c'): 9,
    (9, 'e'): 10
}
DFA_BRUTEFORCE = DFA(BRUTEFORCE_TRANSITIONS, 0, {10}, "bruteforce")

# Pattern for detecting "ddos"
DDOS_TRANSITIONS = {
    (0, 'd'): 1,
    (1, 'd'): 2,
    (2, 'o'): 3,
    (3, 's'): 4
}
DFA_DDOS = DFA(DDOS_TRANSITIONS, 0, {4}, "ddos")

# Pattern for detecting "phishing"
PHISHING_TRANSITIONS = {
    (0, 'p'): 1,
    (1, 'h'): 2,
    (2, 'i'): 3,
    (3, 's'): 4,
    (4, 'h'): 5,
    (5, 'i'): 6,
    (6, 'n'): 7,
    (7, 'g'): 8
}
DFA_PHISHING = DFA(PHISHING_TRANSITIONS, 0, {8}, "phishing")

# Collection of all DFA patterns
DFA_PATTERNS = [
    DFA_ATTACK, 
    DFA_UNAUTHORIZED, 
    DFA_SCAN,
    DFA_MALWARE,
    DFA_INJECTION,
    DFA_BRUTEFORCE,
    DFA_DDOS,
    DFA_PHISHING
]


def check_all_patterns(text):
    """
    Check input text against all registered DFA patterns
    
    Args:
        text (str): Input text to check
        
    Returns:
        list: List of pattern names that were matched
    """
    detected_patterns = []
    for pattern in DFA_PATTERNS:
        if pattern.check_and_log(text):
            detected_patterns.append(pattern.pattern_name)
    return detected_patterns


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test the DFA patterns
    test_cases = [
        "attack detected",
        "unauthorized access attempt",
        "scan attempt detected",
        "normal traffic",
        "user login"
    ]
    
    for test in test_cases:
        print(f"Testing: {test}")
        detected = check_all_patterns(test)
        if detected:
            print(f"  Detected patterns: {detected}")
        else:
            print("  No patterns detected")
        print()
