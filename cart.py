def get_cart(session):
    return session.setdefault("cart",{})

def add(session,item):
    c=get_cart(session)
    c[item]=c.get(item,0)+1
    session["cart"]=c

def remove(session,item):
    c=get_cart(session)
    if item in c:
        c[item]-=1
        if c[item]<=0: del c[item]
    session["cart"]=c
