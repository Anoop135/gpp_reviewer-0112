import os,sys
def CalculateTotal( items ):
    Total=0
    for i in items:
        Total = Total+i
    return Total

class shopping_cart:
    def __init__(self,name):
        self.name=name
        self.x = []
    def add( self,item ):
        self.x.append(item)

c = shopping_cart("Anoop")
c.add(10)
c.add(20)
print( CalculateTotal(c.x) )