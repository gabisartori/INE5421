class FDA:
    def __init__(self, string: str="") -> None:
        self.string: str = string
        self.initial_state: frozenset[str] = None
        self.transitions: dict[frozenset[str], dict[str, frozenset[frozenset[str]]]] = {}
        self.final_states: frozenset[frozenset[str]] = set()
        self.current_state: frozenset[str] = None
        self.states: frozenset[str] = {'qm'}
        self.num_states: int = 0
        self.alphabet: set[chr] = set()
        if self.string: self.parse()
    
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
        temp_states = set()
        num_states, initial_state, final_states, alphabet, *transitions = self.string.split(';')
        self.num_states = int(num_states)
        self.initial_state = frozenset(initial_state)
        self.final_states = frozenset(frozenset(state) for state in final_states[1:-1].split(','))
        self.alphabet = frozenset(alphabet[1:-1].split(','))
        transitions = [transition for transition in transitions if transition]
        temp_states.add(self.initial_state)
        temp_states.update(self.final_states)
        for transition in transitions:
            state, symbol, next_state = transition.split(',')
            if symbol == "": symbol = "&"
            if state not in self.transitions: self.transitions[state] = {}
            if symbol not in self.transitions[state]: self.transitions[state][symbol] = frozenset()
            self.transitions[state][symbol] = self.transitions[state][symbol].union(frozenset((frozenset((next_state,)),)))
            temp_states.add(state)
            temp_states.update(next_state)
        self.states = frozenset(temp_states)

    def is_deterministic(self):
        for state in self.transitions:
            if "" in self.transitions[state]: return False
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]: continue
                if len(self.transitions[state][symbol]) > 1: return False
                if "&" in self.transitions[state]: return False
        return True

    def __str__(self) -> str:
        def states_to_string(states: frozenset[frozenset[str]]):
            string = ""
            for state in states:
                for huh in state:
                    string += huh
            return string

        num_states = str(self.num_states)
        initial_state = ''.join(sorted(self.initial_state))
        alphabet = "{" + ','.join(sorted(self.alphabet)) + "};"
        final_states = [str(state)[10:-1] for state in self.final_states]
        final_states = "{" + ",".join(sorted(str(state)[2:-2] for state in final_states)) + "}"
        base = f"{num_states};{initial_state};{final_states};{alphabet}"
        trans = ""
        for state in self.transitions:
            for symbol in self.transitions[state]:
                for next_state in self.transitions[state][symbol]:
                    state = states_to_string(state)
                    next_state = states_to_string(next_state)
                    trans += f"{state},{symbol},{next_state};"

        return base + trans

    def deterministic_equivalent(self) -> 'FDA':
        def epsilon_closure(state: frozenset[str], closure: set=None) -> set[str]:
            if closure is None: closure = set()
            closure.add(state)

            if state not in self.transitions: return closure
            if "" not in self.transitions[state]: return closure

            for reachable_state in self.transitions[state][""]:
                # closure.add(reachable_state)
                if reachable_state not in closure: closure.update(epsilon_closure(reachable_state, closure))
            print(closure)
            return closure

        if self.is_deterministic(): return self.copy()
        deterministic = FDA()
        temp_states = set()
        states_epsilon_closure: dict[str, set[str]] = {}
        for state in self.states.difference({'qm'}): states_epsilon_closure[state] = frozenset(epsilon_closure(state))

        deterministic.initial_state = states_epsilon_closure[self.initial_state]
        deterministic.final_states = {frozenset(state) for state in states_epsilon_closure.values() if state.intersection(self.final_states)}
        temp_states.add(frozenset(deterministic.initial_state))
        temp_states.update(deterministic.final_states)
        
        deterministic.alphabet = self.alphabet.copy()
        deterministic.transitions = {}
        stack = [deterministic.initial_state]

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
                if next_state not in temp_states: stack.append(next_state)
                temp_states.add(next_state)
                deterministic.transitions[current_state][symbol] = next_state

        deterministic.states = frozenset(temp_states)
        deterministic.string = str(deterministic)
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
            
input1 = "4;A;{D};{a,b};A,a,A;A,b,A;B,b,C;C,b,D;"
input2 = "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C;"
input3 = "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C;"
inputs = [input1, input2, input3]

for input in inputs:
    fda = FDA(input)
    print(fda)
    print(fda.deterministic_equivalent())
    print()