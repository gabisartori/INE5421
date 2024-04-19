class FDA:
    def __init__(self, string: str="") -> None:
        self.string: str = string
        self.initial_state: frozenset[str] = None
        self.transitions: dict[frozenset[str], dict[str, frozenset[frozenset[str]]]] = {}
        self.final_states: frozenset[frozenset[str]] = frozenset()
        self.current_state: frozenset[str] = None
        self.states: frozenset[frozenset[str]] = frozenset((frozenset(("qm",)),))
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
        for transition in transitions:
            state, symbol, next_state = transition.split(',')
            if symbol == "": symbol = "&"
            state = frozenset((state,))
            next_state = frozenset((next_state,))
            if state not in self.transitions: self.transitions[state] = {}
            if symbol not in self.transitions[state]: self.transitions[state][symbol] = frozenset()
            self.transitions[state][symbol] = self.transitions[state][symbol].union(frozenset((next_state,)))
            temp_states.add(state)
            temp_states.update(self.transitions[state][symbol])
        self.states = frozenset(temp_states)

    def is_deterministic(self):
        for state in self.transitions:
            if "&" in self.transitions[state]: return False
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]: continue
                if len(self.transitions[state][symbol]) > 1: return False
        return True

    @staticmethod
    def state_to_string(state: frozenset[str]) -> str:
        string = ""
        for state_part in sorted(state):
            string += state_part
        return string

    def __str__(self) -> str:
        num_states = str(self.num_states)
        initial_state = "{" + ''.join(sorted(self.initial_state)) + "}"
        alphabet = "{" + ','.join(sorted(self.alphabet)) + "};"
        final_states = "{"
        for state in sorted(self.final_states_as_tuple()):
            final_states += "{" + self.state_to_string(state) + "},"
        final_states = final_states[:-1] + "}"

        base = f"{num_states};{initial_state};{final_states};{alphabet}"
        trans = ""
        for state, symbol, next_state in self.transitions_as_tuples():
            string_state = "{" + self.state_to_string(state) + "}"
            string_next_state = "{" + self.state_to_string(next_state) + "}"
            trans += f"{string_state},{symbol},{string_next_state};"

        return base + trans

    def deterministic_equivalent(self) -> 'FDA':
        def epsilon_closure(state: frozenset[str], closure: set=None) -> frozenset[str]:
            if closure is None: closure = set(state)
            if state not in self.transitions or "&" not in self.transitions[state]: return frozenset(closure)

            for reachable_state in self.transitions[state]["&"]:
                if reachable_state not in closure:
                    reachable_state_closure: frozenset[str] = epsilon_closure(reachable_state)
                    closure.update(reachable_state_closure)

            return frozenset(closure)

        if self.is_deterministic(): return self.copy()
        deterministic = FDA()
        states_epsilon_closure: dict[frozenset[str], frozenset[str]] = {}
        for state in self.states.difference({'qm'}): states_epsilon_closure[state] = epsilon_closure(state)

        temp_states: set[frozenset[str]] = set()
        deterministic.initial_state = states_epsilon_closure[self.initial_state]
        
        deterministic.alphabet = self.alphabet.copy().difference({"&"})
        deterministic.transitions = {}
        stack = [deterministic.initial_state]

        while stack:
            current_state = stack.pop()
            temp_states.add(current_state)

            if current_state not in deterministic.transitions:
                deterministic.num_states += 1
                deterministic.transitions[current_state] = {}

            for symbol in sorted(deterministic.alphabet.difference({"&"})):
                next_state: set[str] = set()
                for state in sorted(current_state):
                    state = frozenset((state,))
                    if state not in self.transitions or symbol not in self.transitions[state]: continue
                    next_state.update({states_epsilon_closure[huh] for huh in self.transitions[state][symbol]})
                if not next_state: continue
                next_state = frozenset([state_part for x in next_state for state_part in x])
                deterministic.transitions[current_state][symbol] = frozenset([next_state])
                if next_state not in temp_states:
                    stack.append(next_state)


        deterministic.states = frozenset(temp_states)
        for state in deterministic.states:
            for final_state in self.final_states:
                if final_state.intersection(state):
                    deterministic.final_states = deterministic.final_states.union(frozenset((state,)))
                    break

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

    def transitions_as_tuples(self) -> list:
        transitions = []
        for state in self.transitions:
            for symbol in self.transitions[state]:
                for next_state in self.transitions[state][symbol]:
                    transitions.append((self.state_to_string(state), symbol, self.state_to_string(next_state)))
        transitions.sort(key=lambda x: sorted(x[0]))
        return transitions

    def final_states_as_tuple(self) -> tuple:
        final_states = []
        for state in self.final_states:
            final_states.append(tuple(sorted(state)))
        final_states.sort()
        return tuple(final_states)

is_vpl = False

if is_vpl:
    fda = FDA(input())
    print(fda.deterministic_equivalent())
else:
    input1 = "4;A;{D};{a,b};A,a,A;A,a,B;A,b,A;B,b,C;C,b,D"
    input2 = "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C"
    input3 = "4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S"
    inputs = [input1, input2, input3]

    for input in inputs:
        fda = FDA(input)
        print(fda)
        print(fda.deterministic_equivalent())
        print()