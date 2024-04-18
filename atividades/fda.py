class FDA:
    def __init__(self, string: str="") -> None:
        self.string: str = string
        self.initial_state: str = None
        self.transitions: dict[str, dict[str, set[str]]] = {}
        self.final_states: set[str] = set()
        self.current_state: str = None
        self.states: set[str] = {'qm'}
        self.num_states: int = 0
        self.alphabet: set[chr] = set()
    
    def compute(self, symbol: chr) -> None:
        if self.current_state is None: self.current_state = self.initial_state
        if self.current_state == 'qm': return
        if self.current_state not in self.transitions or symbol not in self.transitions[self.current_state]:
            self.current_state = 'qm'
            return
        self.current_state = self.transitions[self.current_state][symbol]

    def extended_compute(self, string: str) -> bool:
        for symbol in string: self.compute(symbol)
        return self.current_state in self.final_states

    def parse(self) -> None:
        num_states, initial_state, final_states, alphabet, *transitions = self.string.split(';')
        self.num_states = int(num_states)
        self.initial_state = initial_state
        self.final_states = set(final_states[1:-1].split(','))
        self.alphabet = set(alphabet[1:-1].split(','))
        transitions = transitions[:-1]
        self.states.add(self.initial_state)
        self.states.update(self.final_states)
        for transition in transitions:
            state, symbol, next_state = transition.split(',')
            if state not in self.transitions: self.transitions[state] = {}
            if symbol not in self.transitions[state]: self.transitions[state][symbol] = set()
            self.transitions[state][symbol].add(next_state)
            self.states.add(state)
            self.states.add(next_state)

    def is_deterministic(self):
        for state in self.transitions:
            if "" in self.transitions[state]: return False
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]: continue
                if len(self.transitions[state][symbol]) > 1: return False
        return True

    def __str__(self) -> str:
        base = f"{self.num_states};{self.initial_state};{','.join(self.final_states)};{','.join(self.alphabet)};"
        trans = ""
        for state in self.transitions:
            for symbol in self.transitions[state]:
                for next_state in self.transitions[state][symbol]:
                    trans += f"{state},{symbol},{next_state};"

        return base + trans

    def deterministic_equivalent(self) -> 'FDA':
        def epsilon_closure(state: str, closure: set=None) -> set[str]:
            if closure is None: closure = set()
            closure.add(state)

            if state not in self.transitions: return closure
            if "" not in self.transitions[state]: return closure

            for reachable_state in self.transitions[state][""]:
                # closure.add(reachable_state)
                if reachable_state not in closure: closure.update(epsilon_closure(reachable_state, closure))
            return closure

        if self.is_deterministic(): return self.copy()
        deterministic = FDA()
        states_epsilon_closure: dict[str, set[str]] = {}
        for state in self.states.difference({'qm'}): states_epsilon_closure[state] = frozenset(epsilon_closure(state))

        deterministic.initial_state = frozenset(states_epsilon_closure[self.initial_state])
        deterministic.final_states = {frozenset(state) for state in states_epsilon_closure.values() if state.intersection(self.final_states)}
        deterministic.states.add(frozenset(deterministic.initial_state))
        deterministic.states.update(deterministic.final_states)
        
        deterministic.alphabet = self.alphabet.copy()
        deterministic.transitions = {}
        stack = [deterministic.initial_state]
        print(states_epsilon_closure)
        while stack:
            current_state = stack.pop()
            deterministic.transitions[current_state] = {}
            for symbol in deterministic.alphabet:
                next_state = set()
                for state in current_state:
                    if state not in self.transitions or symbol not in self.transitions[state]: continue
                    next_state.update(states_epsilon_closure[next_state_state] for next_state_state in self.transitions[state][symbol])
                if not next_state: continue
                next_state = frozenset().union(*next_state)
                if next_state not in deterministic.states: stack.append(next_state)
                deterministic.states.add(next_state)
                deterministic.transitions[current_state][symbol] = next_state

        return deterministic

    def copy(self) -> 'FDA':
        copy = FDA()
        copy.string = self.string
        copy.initial_state = self.initial_state
        copy.final_states = self.final_states.copy()
        copy.current_state = self.current_state
        copy.states = self.states.copy()
        copy.num_states = self.num_states
        copy.alphabet = self.alphabet.copy()
        copy.transitions = {state: {symbol: next_state.copy() for symbol, next_state in self.transitions[state].items()} for state in self.transitions}
        return copy
            
hm = FDA("2;q0;{q1};{a,b};q0,,q1;q1,a,q1;")
hm.parse()
print(hm.transitions)
print(hm.deterministic_equivalent().transitions)
