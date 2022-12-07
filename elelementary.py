from pyray import *
from math import *
from time import *
from random import *
import re

fail = print

class Element:
    def __init__(self, id):
        self.id = id
        self.children = []
        
    def add_child(self, child):
        self.children.append(child)

    def get_child(self, id, i=0):
        if self.id == id and i != 0: return self
        for child in self.children:
            potential_child = child.get_child(id, i+1)
            if potential_child is not None: return potential_child
        return None

def load_elel(path):
    file = open(path, 'r').read()
    master = Element('')

    file = re.sub('\s+', ' ', file) # remove multiple whites
    element_starts = [i.span() for i in re.finditer('<[^/\s]+>', file)]
    element_ends = [i.span() for i in re.finditer('</[^\s]+>', file)]
    
    if len(element_starts) != len(element_ends):
        fail('unclosed elements')
        return None

    depth = 0
    for e in range(len(element_starts)):
        new_element_id = file[element_starts[e][0]+1:element_starts[e][1]-1]
        new_elemnt = Element(new_element_id)
        print(new_elemnt.id)

        master.add_child(new_elemnt)

    return master

def load_sps(path):
    file = open(path, 'r')
