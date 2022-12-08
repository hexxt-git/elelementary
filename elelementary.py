from math import *
from time import *
from random import *
import re

class Element:
    def __init__(self, id):
        self.id = id
        self.children = []
        
    def add_child(self, child):
        self.children.append(child)

    def get_child(self, id):
        for child in self.children:
            if child.id == id:
                return child
        return None

    def get_child_deep(self, id, i=0):
        if self.id == id and i != 0: return self
        for child in self.children:
            potential_child = child.get_child(id, i+1)
            if potential_child is not None: return potential_child
        return None
    
    def bind(self, file):
        pass
    
    def open(self):
        pass

def load_elel(path):
    file = open(path, 'r').read()
    master = Element('master')

    file = re.sub('#.*', '', file) # ignore comments
    file = re.sub('\s+', ' ', file) # ignore multiple whites
    element_starts = [i.span() for i in re.finditer('<[^/\s]+>', file)] # find where elements start and their ids position
    element_ends = [i.start() for i in re.finditer('</>', file)] # find where elements end

    if len(element_starts) > len(element_ends): # assure all elements are closed
        print(file)
        raise Exception('unclosed elements')

    current_position = 0
    for e in range(len(element_starts)): # loop through each new element declaration
        new_element_id = file[element_starts[e][0]+1:element_starts[e][1]-1] # read the elements id
        new_elemnt = Element(new_element_id) # create the element
        current_position += 1 # we just went one deeper so we increment the position

        closed = len([end for end in element_ends if end > element_starts[e-1][1] and end < element_starts[e][1]]) # all closed since last element
        current_position -= closed
        print('-'*current_position + '>' + new_element_id )

        master.add_child(new_elemnt)

    return master

def load_sps(path):
    file = open(path, 'r')
