from fda import FDA

input1 = "4;A;{D};{a,b};A,a,A;A,a,B;A,b,A;B,b,C;C,b,D"
input2 = "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C"
input3 = "4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S"
inputs = [input1, input2, input3]

for input in inputs:
    fda = FDA(input)
    print(fda)
    print(fda.deterministic_equivalent())
    print()