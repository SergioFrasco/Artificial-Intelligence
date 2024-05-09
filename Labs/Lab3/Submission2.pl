
members([],_).
members([H|T],L) :- member(H,L), members(T,L).

rule1(C1,C2,C3,C4,C5) :- member([red,ntokozo,_,_,_,_], [C1,C2,C3,C4,C5]).

rule2(C1,C2,C3,C4,C5) :- member([_,saul,_,_,dog,_], [C1,C2,C3,C4,C5]).


rule3(C1,C2,C3,C4,C5) :- member([green,_,coffee,_,_,_], [C1,C2,C3,C4,C5]).

rule4(C1,C2,C3,C4,C5) :- member([_,kgosi,tea,_,_,_], [C1,C2,C3,C4,C5]).


rule5(C1,C2,C3,C4,C5) :-
    member([white,_,_,_,_,P1], [C1,C2,C3,C4,C5]),
    member([green,_,_,_,_,P2], [C1,C2,C3,C4,C5]),
    P2 is P1 + 1.


rule6(C1,C2,C3,C4,C5) :- member([_,_,_,superman,snails,_], [C1,C2,C3,C4,C5]).

rule7(C1,C2,C3,C4,C5) :- member([yellow,_,_,hulk,_,_], [C1,C2,C3,C4,C5]).

rule8(C1,C2,C3,C4,C5) :- member([_,_,milk,_,_,3], [C1,C2,C3,C4,C5]).

rule9(C1,C2,C3,C4,C5) :- member([_,jay,_,_,_,1], [C1,C2,C3,C4,C5]).


rule10(C1,C2,C3,C4,C5) :-
    member([_,_,_,ironman,_,P1], [C1,C2,C3,C4,C5]),
    member([_,_,_,_,parrot,P2], [C1,C2,C3,C4,C5]),
    abs(P1 - P2) =:= 1.


rule11(C1,C2,C3,C4,C5) :-
    member([_,_,_,hulk,_,P1], [C1,C2,C3,C4,C5]),
    member([_,_,_,_,horse,P2], [C1,C2,C3,C4,C5]),
    abs(P1 - P2) =:= 1.


rule12(C1,C2,C3,C4,C5) :- member([_,_,orange,spiderman,_,_], [C1,C2,C3,C4,C5]).

rule13(C1,C2,C3,C4,C5) :- member([_,john,_,batman,_,_], [C1,C2,C3,C4,C5]).

rule14(C1,C2,C3,C4,C5) :-
    member([_,jay,_,_,_,P1], [C1,C2,C3,C4,C5]),
    member([blue,_,_,_,_,P2], [C1,C2,C3,C4,C5]),
    abs(P1 - P2) =:= 1.



solve(C1,C2,C3,C4,C5) :-
    C1 = [C1_col,C1_name,C1_drink,C1_superhero,C1_pet,1],
    C2 = [C2_col,C2_name,C2_drink,C2_superhero,C2_pet,2],
    C3 = [C3_col,C3_name,C3_drink,C3_superhero,C3_pet,3],
    C4 = [C4_col,C4_name,C4_drink,C4_superhero,C4_pet,4],
    C5 = [C5_col,C5_name,C5_drink,C5_superhero,C5_pet,5],
    rule1(C1,C2,C3,C4,C5),
    rule2(C1,C2,C3,C4,C5),
    rule3(C1,C2,C3,C4,C5),
    rule4(C1,C2,C3,C4,C5),
    rule5(C1,C2,C3,C4,C5),
    rule6(C1,C2,C3,C4,C5),
    rule7(C1,C2,C3,C4,C5),
    rule8(C1,C2,C3,C4,C5),
    rule9(C1,C2,C3,C4,C5),
    rule10(C1,C2,C3,C4,C5),
    rule11(C1,C2,C3,C4,C5),
    rule12(C1,C2,C3,C4,C5),
    rule13(C1,C2,C3,C4,C5),
    rule14(C1,C2,C3,C4,C5),
    members([white,green,red,blue,yellow], [C1_col,C2_col,C3_col,C4_col,C5_col]),
    members([saul,john,ntokozo,kgosi,jay], [C1_name,C2_name,C3_name,C4_name,C5_name]),
    members([orange,coffee,milk,tea,water], [C1_drink,C2_drink,C3_drink,C4_drink,C5_drink]),
    members([spiderman,batman,superman,ironman,hulk], [C1_superhero,C2_superhero,C3_superhero,C4_superhero,C5_superhero]),
    members([dog,cat,snails,horse,parrot], [C1_pet,C2_pet,C3_pet,C4_pet,C5_pet]).