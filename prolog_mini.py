#!/usr/bin/env python3
"""prolog_mini - Minimal Prolog interpreter with unification."""
import sys, copy
class Atom:
    def __init__(self, name): self.name=name
    def __repr__(self): return self.name
    def __eq__(self, o): return isinstance(o,Atom) and self.name==o.name
    def __hash__(self): return hash(self.name)
class Var:
    def __init__(self, name): self.name=name
    def __repr__(self): return self.name
class Compound:
    def __init__(self, functor, args): self.functor=functor; self.args=args
    def __repr__(self): return f"{self.functor}({','.join(map(str,self.args))})"
class Clause:
    def __init__(self, head, body=None): self.head=head; self.body=body or []
def unify(x, y, subst):
    if subst is None: return None
    x=walk(x,subst); y=walk(y,subst)
    if isinstance(x,Var): subst[x.name]=y; return subst
    if isinstance(y,Var): subst[y.name]=x; return subst
    if isinstance(x,Atom) and isinstance(y,Atom): return subst if x==y else None
    if isinstance(x,Compound) and isinstance(y,Compound):
        if x.functor!=y.functor or len(x.args)!=len(y.args): return None
        for a,b in zip(x.args,y.args):
            subst=unify(a,b,subst)
            if subst is None: return None
        return subst
    return None
def walk(x, subst):
    while isinstance(x,Var) and x.name in subst: x=subst[x.name]
    return x
def solve(goals, clauses, subst, depth=0):
    if depth>50: return
    if not goals: yield dict(subst); return
    goal=goals[0]; rest=goals[1:]
    for clause in clauses:
        c=rename_vars(clause, depth)
        s=unify(goal, c.head, dict(subst))
        if s is not None:
            new_goals=c.body+rest
            yield from solve(new_goals, clauses, s, depth+1)
_counter=[0]
def rename_vars(clause, depth):
    mapping={}
    def rename(term):
        if isinstance(term,Var):
            if term.name not in mapping: mapping[term.name]=Var(f"{term.name}_{depth}")
            return mapping[term.name]
        if isinstance(term,Compound): return Compound(term.functor,[rename(a) for a in term.args])
        return term
    return Clause(rename(clause.head),[rename(g) for g in clause.body])
if __name__=="__main__":
    # parent(tom, bob). parent(bob, ann).
    clauses=[
        Clause(Compound("parent",[Atom("tom"),Atom("bob")])),
        Clause(Compound("parent",[Atom("bob"),Atom("ann")])),
        Clause(Compound("parent",[Atom("bob"),Atom("pat")])),
        Clause(Compound("grandparent",[Var("X"),Var("Z")]),
               [Compound("parent",[Var("X"),Var("Y")]),Compound("parent",[Var("Y"),Var("Z")])]),
    ]
    goal=[Compound("grandparent",[Atom("tom"),Var("W")])]
    print("Query: grandparent(tom, W)?")
    for s in solve(goal, clauses, {}):
        w=walk(Var("W"),s)
        print(f"  W = {w}")
