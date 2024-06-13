from fda import FDA

inputs = [
    "(&|b)(ab)*(&|a)",
    "aa*(bb*aa*b)*",
    "a(a|b)*a",
    "a(a*(bb*a)*)*|b(b*(aa*b)*)*"
]

for input in inputs:
    print(FDA(regex=input))
