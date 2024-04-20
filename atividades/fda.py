from typing import Dict, FrozenSet, Set

class FDA:
    def __init__(self, string: str="") -> None:
        self.string: str = string
        self.initial_state: FrozenSet[str] = None
        self.transitions: Dict[FrozenSet[str], Dict[str, FrozenSet[FrozenSet[str]]]] = {}
        self.final_states: FrozenSet[FrozenSet[str]] = frozenset()
        self.current_state: FrozenSet[str] = None
        self.states: FrozenSet[FrozenSet[str]] = frozenset((frozenset(("qm",)),))
        self.num_states: int = 0
        self.alphabet: Set[chr] = set()
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
        '''Busca por transições por ε ou por um estado que tenha mais de um destino para um mesmo símbolo.'''
        for state in self.transitions:
            if "&" in self.transitions[state]: return False
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]: continue
                if len(self.transitions[state][symbol]) > 1: return False
        return True

    @staticmethod
    def state_to_string(state: FrozenSet[str]) -> str:
        '''Une as partes de um estado em uma string.'''
        '''Exemplo: um estado {"A", "B"} vira "AB"'''
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
        def epsilon_closure(state: FrozenSet[str], closure: set=None) -> FrozenSet[str]:
            '''Retorna o ε* de um estado, realizando uma busca em profundidade.'''
            if closure is None: closure = set(state)
            if state not in self.transitions or "&" not in self.transitions[state]: return frozenset(closure)

            for reachable_state in self.transitions[state]["&"]:
                if reachable_state not in closure:
                    reachable_state_closure: FrozenSet[str] = epsilon_closure(reachable_state)
                    closure.update(reachable_state_closure)

            return frozenset(closure)

        # Se o autômato já é determinístico, retorna uma cópia dele mesmo
        if self.is_deterministic(): return self.copy()

        deterministic = FDA()
        # Trata todo autômato não determinístico como se tivesse transições por ε
        # Caso não tenha, ε* de cada estado é ele mesmo, não influenciando no resultado
        states_epsilon_closure: Dict[FrozenSet[str], FrozenSet[str]] = {}
        for state in self.states.difference({'qm'}): states_epsilon_closure[state] = epsilon_closure(state)

        # Construir o autômato determinístico equivalente

        # Conjunto temporário para armaenar os estados a serem incluídos no autômato determinístico
        temp_states: set[FrozenSet[str]] = set()

        # O estado inicial do autômato determinístico é o ε* do estado inicial do autômato não determinístico
        deterministic.initial_state = states_epsilon_closure[self.initial_state]
        
        # O alfabeto do autômato determinístico é o mesmo do autômato não determinístico, sem o símbolo ε
        deterministic.alphabet = self.alphabet.copy().difference({"&"})
        
        # Começa a construir as transições do autômato determinístico, partindo do estado inicial
        deterministic.transitions = {}
        stack = [deterministic.initial_state]
        while stack:
            # Adiciona o estado visitado ao conjunto de estados do autômato determinístico
            current_state = stack.pop()
            temp_states.add(current_state)

            # Prepara a tabela de transições para receber o novo estado
            if current_state not in deterministic.transitions:
                deterministic.num_states += 1
                deterministic.transitions[current_state] = {}

            # Para cada símbolo do alfabeto, visita os estados alcançáveis a partir do estado atual
            for symbol in sorted(deterministic.alphabet.difference({"&"})):
                next_state: Set[str] = set()
                for state in sorted(current_state):
                    state = frozenset((state,))
                    if state not in self.transitions or symbol not in self.transitions[state]: continue
                    next_state.update({states_epsilon_closure[huh] for huh in self.transitions[state][symbol]})
                if not next_state: continue
                next_state = frozenset([state_part for x in next_state for state_part in x])
                deterministic.transitions[current_state][symbol] = frozenset([next_state])
                if next_state not in temp_states:
                    stack.append(next_state)

        # Agora que todos os estados foram calculados, o conjunto temporário pode ser transformado em um conjunto imutável
        deterministic.states = frozenset(temp_states)
        # Adiciona ao conjunto de estados finais do autômato determinístico os estados que contém algum estado final do autômato não determinístico
        for state in deterministic.states:
            for final_state in self.final_states:
                if final_state.intersection(state):
                    deterministic.final_states = deterministic.final_states.union(frozenset((state,)))
                    break

        deterministic.string = str(deterministic)
        return deterministic

    def minimal_equivalent(self) -> 'FDA':
        pass

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
        '''Retorna as transições do autômato como uma lista de tuplas (estado, símbolo, próximo estado) para facilitar a ordenação da saída do programa.'''
        transitions = []
        for state in self.transitions:
            for symbol in self.transitions[state]:
                for next_state in self.transitions[state][symbol]:
                    transitions.append((self.state_to_string(state), symbol, self.state_to_string(next_state)))
        transitions.sort(key=lambda x: sorted(x[0]))
        return transitions

    def final_states_as_tuple(self) -> tuple:
        '''Mesma ideia da função transitions_as_tuples, mas para os estados finais.'''
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