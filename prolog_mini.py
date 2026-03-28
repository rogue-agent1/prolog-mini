#!/usr/bin/env python3
"""Minimal Prolog interpreter (unification + backtracking)."""
import re,sys
def parse_term(s):
    s=s.strip()
    m=re.match(r"(\w+)\((.+)\)",s)
    if m: return (m.group(1),[parse_term(a) for a in split_args(m.group(2))])
    if s[0].isupper() or s=="_": return ("var",s)
    return ("atom",s)
def split_args(s):
    depth=0; parts=[]; cur=""
    for c in s:
        if c=="(": depth+=1
        elif c==")": depth-=1
        if c=="," and depth==0: parts.append(cur); cur=""
        else: cur+=c
    if cur: parts.append(cur)
    return parts
def unify(t1,t2,subst):
    t1=deref(t1,subst); t2=deref(t2,subst)
    if t1==t2: return subst
    if t1[0]=="var": return {**subst,t1[1]:t2}
    if t2[0]=="var": return {**subst,t2[1]:t1}
    if t1[0]==t2[0] and isinstance(t1[1],list) and isinstance(t2[1],list) and len(t1[1])==len(t2[1]):
        for a,b in zip(t1[1],t2[1]):
            subst=unify(a,b,subst)
            if subst is None: return None
        return subst
    return None
def deref(t,subst):
    while t[0]=="var" and t[1] in subst: t=subst[t[1]]
    if isinstance(t[1],list): return (t[0],[deref(a,subst) for a in t[1]])
    return t
def query(db,goals,subst={}):
    if not goals: yield subst; return
    goal=goals[0]; rest=goals[1:]
    for head,body in db:
        s=unify(goal,rename(head,{}),dict(subst))
        if s is not None:
            new_goals=[rename(b,{}) for b in body]+rest
            yield from query(db,new_goals,s)
_cnt=[0]
def rename(t,mapping):
    if t[0]=="var":
        if t[1] not in mapping: _cnt[0]+=1; mapping[t[1]]=("var",f"_{_cnt[0]}")
        return mapping[t[1]]
    if isinstance(t[1],list): return (t[0],[rename(a,mapping) for a in t[1]])
    return t
if __name__=="__main__":
    db=[(parse_term("parent(tom,bob)"),[]),(parse_term("parent(tom,liz)"),[]),(parse_term("parent(bob,ann)"),[]),(parse_term("parent(bob,pat)"),[]),(parse_term("grandparent(X,Z)"),[parse_term("parent(X,Y)"),parse_term("parent(Y,Z)")])]
    g=[parse_term("grandparent(tom,W)")]
    results=[]
    for s in query(db,g):
        w=deref(("var","W"),s); results.append(w)
    print(f"Grandchildren of tom: {[r[1] for r in results]}")
    assert len(results)==2; print("Prolog mini OK")
