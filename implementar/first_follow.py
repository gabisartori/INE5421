from fda import CFG

input_1 = "P = KVC; K = cK; K = &; V = vV; V = F; F = fPiF; F = &; C = bVCe; C = miC; C = &;"
input_2 = "P = KL; P = bKLe; K = cK; K = TV; T = tT; T = &; V = vV; V = &; L = mL; L = &;"
input_3 = "S = SoA; S = A; A = AaB; A = B; B = nB; B = (S); B = t; B = f;"

# S -> S or A | A
# A -> A and B | B
# B -> not B | (S) | true | false

inputs = [input_1, input_2, input_3]

for input in inputs:
    cfg = CFG(input.strip())
    print(cfg.first_follow_string())
    print()
