from fda import CFG

input_1 = "P = KVC; K = cK; K = &; V = vV; V = F; F = fPiF; F = &; C = bVCe; C = miC; C = &;"
input_2 = "P = KL; P = bKLe; K = cK; K = TV; T = tT; T = &; V = vV; V = &; L = mL; L = &;"

inputs = [input_1, input_2]

for input in inputs:
    cfg = CFG(input.strip())
    print(cfg.first_follow())
    print()