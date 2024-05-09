male(greg).
male(adam).
male(trent).
male(martin).
male(marcus).
male(gabriel).
male(dave).
male(michael).

female(lucy).
female(amy).
female(kgomotso).
female(naledi).
female(karen).
female(michelle).

parent(trent, greg).
parent(naledi, greg).
parent(trent, adam).
parent(trent, kgomotso).
parent(karen, adam).
parent(karen, kgomotso).
parent(gabriel, marcus).
parent(gabriel, michelle).
parent(gabriel, naledi).
parent(amy, marcus).
parent(amy, michelle).
parent(amy, naledi).
parent(dave, trent).
parent(dave, martin).
parent(lucy, trent).
parent(lucy, martin).
parent(martin, michael).

married(amy, gabriel).
married(lucy, dave).
married(naledi, trent).

spouse(A, B) :-
    married(A, B).

mother(A, B) :-
    female(A),
    parent(A, B).

father(A, B) :-
    male(A),
    parent(A, B).


sibling(A, B) :-
    parent(M, A),
    parent(F, A),
    parent(M, B),
    parent(F, B),
    A \= B,
    M \= F.

brother(A, B) :-
    sibling(A, B),
    male(A).

sister(A, B) :-
    sibling(A, B),
    female(A).

half_sibling(A, B) :-
    parent(Z, A),
    parent(Z, B),
    parent(W, A),
    parent(V, B),
    Z \= W,
    Z \= V,
    A \= B.


half_brother(A, B) :-
    half_sibling(A, B),
    male(A).

half_sister(A, B) :-
    half_sibling(A, B),
    female(A).

uncle(A, B) :-
    parent(Z, B),
    brother(A, Z).

aunt(A, B) :-
    parent(Z, B),
    sister(A, Z).

grandparent(A, B) :-
    parent(A, Z),
    parent(Z, B).

grandmother(A, B) :-
    grandparent(A, B),
    female(A).


grandfather(A, B) :-
    grandparent(A, B),
    male(A).

nephew(A, B) :-
    parent(Z, B),
    (brother(Z, A); sister(Z, A)),
    male(A).

niece(A, B) :-
    parent(Z, B),
    (brother(Z, A); sister(Z, A)),
    female(A).

cousin(A, B) :-
    parent(Z, A),
    parent(W, B),
    (sibling(Z, W); half_sibling(Z, W)).

in_law(A, B) :-
    spouse(A, Z),
    (parent(Z, B); sibling(Z, B)).

brother_in_law(A, B) :-
    in_law(A, B),
    male(B).

sister_in_law(A, B) :-
    in_law(A, B),
    female(B).
