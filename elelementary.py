from pyray import *
from random import *
import re

colors = {
    'white': Color(255, 255, 255, 255),
    'black': Color(0, 0, 0, 255),
    'lightgrey': Color(170, 170, 170, 255),
    'lightgray': Color(170, 170, 170, 255),
    'grey': Color(90, 90, 90, 255),
    'gray': Color(90, 90, 90, 255),
    'darkgrey': Color(30, 30, 30, 255),
    'darkgray': Color(30, 30, 30, 255),
    'red': Color(215, 15, 15, 255),
    'green': Color(15, 215, 15, 255),
    'blue': Color(15, 15, 215, 255),
    'yellow': Color(200, 200, 25, 255),
    'magenta': Color(200, 25, 200, 255),
    'cyan': Color(25, 200, 200, 255),
    'orange': Color(215, 115, 15, 255),
    'pink': Color(215, 15, 115, 255),
    'lightgreen': Color(115, 215, 15, 255),
    'purple': Color(115, 15, 215, 255),
    'lightblue': Color(15, 115, 215, 255),
    'turquoise': Color(15, 215, 115, 255),
    'lime': Color(0, 255, 0, 255)
}

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
        print(' '*4*i + self.id + ':' + self.text)
        [child.print(i+1) for child in self.children]
    
    def open(self):
        pass

# selector
#     property
#     event
#         property

class Special:
    def __init__(self):
        self.selectors = []

    def add_selector(self, selector):
        self.selectors.append(selector)

    def print(self, i=0):
        print(' '*4*i + 'special: ')
        [s.print(i+1) for s in self.selectors]

class Selector:
    def __init__(self, id):
        self.id = id
        self.properties = []
        self.events = []

    def print(self, i=0):
        print(' '*4*i + self.id + ': ')
        [p.print(i+1) for p in self.properties]
        [e.print(i+1) for e in self.events]
    
    def add_property(self, property):
        self.properties.append(property)
    
    def add_event(self, event):
        self.events.append(event)

class Event:
    def __init__(self, activation):
        self.activation = activation
        self.properties = []
    
    def print(self, i=0):
        print(' '*4*i + self.activation + ': ')
        [p.print(i+1) for p in self.properties]
        
    def add_property(self, property):
        self.properties.append(property)

class Property:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def print(self, i=0):
        print(' '*4*i + self.key + ': ' + self.value)

def load_elel(path):
    file = open(path, 'r').read()
    file = re.sub('#.*', '', file)

    main = Element('main')
    stack = []
    for line in file.splitlines():
        opened = re.search('<[^/\s]+>', line)
        closed = sum([1 for _ in re.finditer('</>', line)])
        if opened is not None:
            new_id = line[opened.start()+1:opened.end()-1]
            stack.append(Element(new_id))
        for c in range(closed):
            if len(stack) > 1:
                stack[-2].add_child(stack[-1])
                stack = stack[:-1]
            else:
                main.add_child(stack[0])
                stack = []
        if closed == 0:
            if len(stack) >= 1:
                stack[-1].text += re.sub('\s+', ' ', re.sub('<[^/\s]+>', '', line))
            else:
                main.text += re.sub('\s+', ' ', re.sub('<[^/\s]+>', '', line))
        
    return main

def load_sps(path):
    file = open(path, 'r').read()
    file = re.sub('#.*', '', file)
    special = Special()

    current_selector = None
    current_event = None
    current_property = None
    for line in file.splitlines():
        opened = re.search('<[^/\s]+>', line)
        closed = re.search('</>', line)
        opened_event = re.search('{[^/\s]+}', line)
        closed_event = re.search('{/}', line)
        
        if opened is not None: 
            if current_selector is None:
                current_selector = Selector(line[opened.start()+1:opened.end()-1])
            else:
                current_property = Property(line[opened.start()+1:opened.end()-1], '')
        elif opened_event is not None:
            current_event = Event(line[opened_event.start()+1:opened_event.end()-1])

        if closed is not None:
            if current_property is not None:
                if current_event is None:
                    current_selector.add_property(current_property)
                    current_property = None
                else:
                    current_event.add_property(current_property)
                    current_property = None
            else:
                special.add_selector(current_selector)
                current_selector = None
        
        if closed_event is not None:
            current_selector.add_event(current_event)
            current_event = None

        if opened is None and opened_event is None and closed is None and closed_event is None and current_property is not None:
            current_property.value += re.sub('\s+', '', line) 

    return special