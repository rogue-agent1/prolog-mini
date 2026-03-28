#!/usr/bin/env python3
"""prolog_mini - Minimal Prolog-like logic engine."""
import sys,re
def unify(x,y,subst=None):
    if subst is None:subst={}
    if subst is False:return False
    if x==y:return subst
    if isinstance(x,str) and x[0].isupper():
        if x in subst:return unify(subst[x],y,subst)
        subst[x]=y;return subst
    if isinstance(y,str) and y[0].isupper():return unify(y,x,subst)
    if isinstance(x,tuple) and isinstance(y,tuple) and len(x)==len(y):
        for a,b in zip(x,y):subst=unify(a,b,subst)
        return subst
    return False
def apply_subst(x,subst):
    if isinstance(x,str) and x[0].isupper():
        if x in subst:return apply_subst(subst[x],subst)
        return x
    if isinstance(x,tuple):return tuple(apply_subst(a,subst) for a in x)
    return x
class KB:
    def __init__(s):s.facts=[];s.rules=[]
    def fact(s,*args):s.facts.append(args)
    def rule(s,head,*body):s.rules.append((head,body))
    def query(s,goal,subst=None):
        if subst is None:subst={}
        for fact in s.facts:
            s2=unify(goal,fact,dict(subst))
            if s2 is not False:yield s2
        for head,body in s.rules:
            fresh=s._fresh(head,body)
            fhead,fbody=fresh
            s2=unify(goal,fhead,dict(subst))
            if s2 is not False:yield from s._solve(list(fbody),s2)
    def _solve(s,goals,subst):
        if not goals:yield subst;return
        goal=apply_subst(goals[0],subst)
        for s2 in s.query(goal,subst):yield from s._solve(goals[1:],s2)
    _counter=0
    def _fresh(s,head,body):
        KB._counter+=1;n=KB._counter;mapping={}
        def rename(x):
            if isinstance(x,str) and x[0].isupper():
                if x not in mapping:mapping[x]=f"{x}_{n}"
                return mapping[x]
            if isinstance(x,tuple):return tuple(rename(a) for a in x)
            return x
        return rename(head),tuple(rename(b) for b in body)
if __name__=="__main__":
    kb=KB()
    kb.fact("parent","tom","bob");kb.fact("parent","tom","liz");kb.fact("parent","bob","ann");kb.fact("parent","bob","pat")
    kb.rule(("grandparent","X","Z"),("parent","X","Y"),("parent","Y","Z"))
    print("Parents of bob:");
    for s in kb.query(("parent","X","bob")):print(f"  {apply_subst('X',s)}")
    print("Grandchildren of tom:");
    for s in kb.query(("grandparent","tom","X")):print(f"  {apply_subst('X',s)}")
