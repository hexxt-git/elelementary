from math import *
from time import *
from random import *
import re

class Element:
    def __init__(self, id):
        self.id = id
        self.text = ''
        self.children = []
        
    def add_child(self, child):
        self.children.append(child)

    def get_child(self, id):
        for child in self.children:
            if child.id == id:
                return child
        return None

    def get_child_deep(self, id, i=0):
        if self.id == id: return self
        for child in self.children:
            potential_child = child.get_child_deep(id, i+1)
            if potential_child is not None: return potential_child
        return None
    
    def bind(self, file):
        pass
    
    def print(self, i=0):
        print('-'*4*i+'>' + self.id + ':' + self.text)
        [child.print(i+1) for child in self.children]
    
    def open(self):
        pass

def load_elel(path):
    file = open(path, 'r').read()
    file = re.sub('#.*', '', file) # ignore comments

    master = Element('master')
    stack = []
    for line in file.splitlines():
        opening = re.search('<[^/\s]+>', line)
        closing = re.finditer('</>', line)
        read = True
        if opening is not None:
            new_id = line[opening.start()+1:opening.end()-1]
            stack.append(Element(new_id))
        for closed in closing:
            read = False
            if len(stack) > 1:
                stack[-2].add_child(stack[-1])
                stack = stack[:-1]
            else:
                master.add_child(stack[0])
                stack = []
        if read:
            if len(stack) >= 1:
                stack[-1].text += re.sub('\s+', ' ', re.sub('<[^/\s]+>', '', line))
            else:
                master.text += re.sub('\s+', ' ', re.sub('<[^/\s]+>', '', line))
        
    return master

def load_sps(path):
    file = open(path, 'r')
