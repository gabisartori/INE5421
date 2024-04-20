from fda import FDA

input1 = "8;P;{S,U,V,X};{0,1};P,0,Q;P,1,P;Q,0,T;Q,1,R;R,0,U;R,1,P;S,0,U;S,1,S;T,0,X;T,1,R;U,0,X;U,1,V;V,0,U;V,1,S;X,0,X;X,1,V"
input2 = "17;A;{A,D,F,M,N,P};{a,b,c,d};A,a,B;A,b,E;A,c,K;A,d,G;B,a,C;B,b,H;B,c,L;B,d,Q;C,a,D;C,b,I;C,c,M;C,d,Q;D,a,B;D,b,J;D,c,K;D,d,O;E,a,Q;E,b,F;E,c,H;E,d,N;F,a,Q;F,b,E;F,c,K;F,d,G;G,a,Q;G,b,Q;G,c,Q;G,d,N;H,a,Q;H,b,K;H,c,I;H,d,Q;I,a,Q;I,b,L;I,c,J;I,d,Q;J,a,Q;J,b,M;J,c,H;J,d,P;K,a,Q;K,b,H;K,c,L;K,d,Q;L,a,Q;L,b,I;L,c,M;L,d,Q;M,a,Q;M,b,J;M,c,K;M,d,O;N,a,R;N,b,R;N,c,R;N,d,G;O,a,R;O,b,R;O,c,R;O,d,P;P,a,R;P,b,R;P,c,Q;P,d,O;Q,a,R;Q,b,Q;Q,c,R;Q,d,Q;R,a,Q;R,b,R;R,c,Q;R,d,R"
input3 = "5;A;{E};{0,1};A,0,B;A,1,C;B,0,B;B,1,D;C,0,B;C,1,C;D,0,B;D,1,E;E,0,B;E,1,C"
inputs = [input1, input2, input3]

for input in inputs:
    fda = FDA(input)
    print(fda)
    print(fda.minimal_equivalent())
    print()
