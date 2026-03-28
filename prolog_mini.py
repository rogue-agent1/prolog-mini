#!/usr/bin/env python3
"""Minimal Prolog-like inference engine."""
import sys,re
def parse_term(s):
    s=s.strip()
    m=re.match(r'(\w+)\((.+)\)$',s)
    if m: return (m[1],[x.strip() for x in m[2].split(',')])
    return s
def is_var(x): return isinstance(x,str) and x[0].isupper()
def unify(x,y,bindings):
    if bindings is None: return None
    x=resolve(x,bindings); y=resolve(y,bindings)
    if x==y: return bindings
    if is_var(x): return {**bindings,x:y}
    if is_var(y): return {**bindings,y:x}
    if isinstance(x,tuple) and isinstance(y,tuple):
        if x[0]!=y[0] or len(x[1])!=len(y[1]): return None
        for a,b in zip(x[1],y[1]):
            bindings=unify(a,b,bindings)
            if bindings is None: return None
        return bindings
    return None
def resolve(x,b):
    while is_var(x) and x in b: x=b[x]
    if isinstance(x,tuple): return (x[0],[resolve(a,b) for a in x[1]])
    return x
class DB:
    def __init__(self):self.facts=[];self.rules=[]
    def add_fact(self,f):self.facts.append(parse_term(f))
    def add_rule(self,head,body):self.rules.append((parse_term(head),[parse_term(b) for b in body]))
    def query(self,goals,bindings=None,depth=0):
        if bindings is None: bindings={}
        if not goals: yield bindings; return
        if depth>50: return
        goal=goals[0]; rest=goals[1:]
        n=depth
        for fact in self.facts:
            f=self._rename(fact,n)
            b=unify(goal,f,dict(bindings))
            if b is not None: yield from self.query(rest,b,depth+1)
        for head,body in self.rules:
            h=self._rename(head,n); bd=[self._rename(b,n) for b in body]
            b=unify(goal,h,dict(bindings))
            if b is not None: yield from self.query(bd+rest,b,depth+1)
    def _rename(self,term,n):
        if is_var(term): return f"{term}_{n}"
        if isinstance(term,tuple): return (term[0],[self._rename(a,n) for a in term[1]])
        return term
def main():
    db=DB()
    db.add_fact("parent(tom,bob)"); db.add_fact("parent(tom,liz)")
    db.add_fact("parent(bob,ann)"); db.add_fact("parent(bob,pat)")
    db.add_rule("grandparent(X,Z)",["parent(X,Y)","parent(Y,Z)"])
    db.add_rule("ancestor(X,Y)",["parent(X,Y)"])
    db.add_rule("ancestor(X,Y)",["parent(X,Z)","ancestor(Z,Y)"])
    print("Facts: parent(tom,bob), parent(tom,liz), parent(bob,ann), parent(bob,pat)")
    print("\nQuery: grandparent(tom,Who)?")
    for b in db.query([parse_term("grandparent(tom,Who)")]):
        print(f"  Who = {resolve('Who',b)}")
    print("\nQuery: ancestor(tom,Who)?")
    for b in db.query([parse_term("ancestor(tom,Who)")]):
        print(f"  Who = {resolve('Who',b)}")
if __name__=="__main__": main()
