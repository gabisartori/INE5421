from fda import CFG

input_1 = "E = TA; A = mTA; A = &; T = FB; B = vFB; B = &; F = i; F = oEc;"
input_2 = "P = KL; P = bKLe; K = cK; K = TV; T = tT; T = &; V = vV; V = &; L = mL; L = &;"
input_3 = "P = KVC; K = cK; K = &; V = vV; V = F; F = fPiF; F = &; C = bVCe; C = miC; C = &;"

inputs = [input_1, input_2, input_3]

for input in inputs:
    cfg = CFG(input)
    print(cfg.table_string(cfg.ll1_parser_table()))
    print()
