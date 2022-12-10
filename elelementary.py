from pyray import *
from random import *
import re
import copy

def render_rectangle(x, y, width, height, color, border):
    draw_rectangle(x, y, width, height, color)
    draw_rectangle_lines(x, y, width, height, border)
    return None

def render_text(text, x, y, size, color):
    draw_text(text, x, y, size, color)
    return None

class Element:
    def __init__(self, id):
        self.id = id
        self.text = ''
        self.children = []
        self.properties = copy.deepcopy(default_properties)
        self.events = []
        
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

    def set_property(self, key, value):
        self.properties[key] = value
            
    def add_event(self, event):
        self.events.append(event)

    def bind(self, special):
        for selector in special.selectors:
            element = self.get_child_deep(selector.id)
            if element is None:
                continue
            for p in selector.properties:
                element.set_property(p, selector.properties[p])
            for e in selector.events:
                element.add_event(e)

    def print(self, i=0):
        print(' '*4*i + self.id +'('+str(self.get_width())+', '+str(self.get_height())+'): ' + self.text)
        [child.print(i+1) for child in self.children]
        
    def get_width(self):
        if self.properties['width'] == 'auto':
            if self.properties['align_children'] == 'vertically': # TDOD: include the text
                return max(max([child.get_width() for child in self.children]+[0]) \
                    +int(self.properties['padding_left'])\
                    +int(self.properties['padding_right'])\
                    , 50)
            if self.properties['align_children'] == 'horizontally':
                return max(sum([child.get_width()+int(self.properties['children_horizontal_gap']) for child in self.children])\
                    +(int(self.properties['children_horizontal_gap']) * len(self.children)\
                    +int(self.properties['padding_left']) + int(self.properties['padding_right']))\
                    -int(self.properties['children_horizontal_gap'])\
                    , 50)
        if self.properties['width'] == 'fullscreen':
            return get_screen_width()
        return int(self.properties['width'])

    def get_height(self):
        if self.properties['height'] == 'auto':
            if self.properties['align_children'] == 'vertically':
                return max(sum([child.get_height() + int(self.properties['children_vertical_gap']) for child in self.children]+[0])\
                    +int(self.properties['padding_top'])\
                    +int(self.properties['padding_bottom'])\
                    -int(self.properties['children_horizontal_gap'])\
                    , 50)
            if self.properties['align_children'] == 'horizontally':
                return max(max([child.get_height() for child in self.children])\
                +(int(self.properties['children_horizontal_gap']) * len(self.children)\
                +int(self.properties['padding_top'])\
                +int(self.properties['padding_bottom']))\
                , 50)
        if self.properties['height'] == 'fullscreen':
            return get_screen_height()
        return int(self.properties['height'])
    
    def render(self, x, y):
        render_rectangle(x, y, self.get_width(), self.get_height(), color(self.properties['background_color']), color(self.properties['border']))
        render_text(self.text, x, y, int(self.properties['text_size']), color(self.properties['text_color']))
        x += int(self.properties['padding_left'])
        y += int(self.properties['padding_top'])
        for child in self.children:
            child.render(x, y)
            if self.properties['align_children'] == 'vertically':
                y += child.get_height()
                y += int(self.properties['children_vertical_gap'])
            if self.properties['align_children'] == 'horizontally':
                x += child.get_width()
                x += int(self.properties['children_horizontal_gap'])

    def open(self):
        #set_config_flags(FLAG_WINDOW_RESIZABLE)
        init_window(self.get_width(), self.get_height(), self.id)

        set_target_fps(50)
        while not window_should_close():
            begin_drawing()
            clear_background(color('dark_grey'))
            self.render(0, 0)

            end_drawing()
        close_window()
    
    def close(self):
        close_window()

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
        self.properties = {}
        self.events = []

    def print(self, i=0):
        print(' '*4*i + self.id + ': ')
        [print_property(p, self.properties[p], i+1) for p in self.properties]
        [e.print(i+1) for e in self.events]
    
    def add_property(self, key, value):
        self.properties[key] = value
    
    def add_event(self, event):
        self.events.append(event)

class Event:
    def __init__(self, activation):
        self.activation = activation
        self.properties = {}
        self.functions = []
    
    def print(self, i=0):
        print(' '*4*i + self.activation + ': ')
        [print_property(p, self.properties[p], i+1) for p in self.properties]
        [f.print(i+1) for f in self.functions]
        
    def add_property(self, key, value):
        self.properties[key] = value
    
    def add_function(self, function):
        self.functions.append(function)

class Function:
    def __init__(self, execute):
        self.execute = execute
    def print(self, i=0):
        print(' '*4*i + self.execute + '')

def print_property(key, value, i=0):
    print(' '*4*i + key + ': ' + value)

colors = {
    'transparent': Color(255, 255, 255, 0),
    'white': Color(255, 255, 255, 255),
    'black': Color(0, 0, 0, 255),
    'light_grey': Color(170, 170, 170, 255),
    'light_gray': Color(170, 170, 170, 255),
    'grey': Color(90, 90, 90, 255),
    'gray': Color(90, 90, 90, 255),
    'dark_grey': Color(30, 30, 30, 255),
    'dark_gray': Color(30, 30, 30, 255),
    'red': Color(215, 15, 15, 255),
    'green': Color(15, 215, 15, 255),
    'blue': Color(15, 15, 215, 255),
    'yellow': Color(200, 200, 25, 255),
    'magenta': Color(200, 25, 200, 255),
    'cyan': Color(25, 200, 200, 255),
    'orange': Color(215, 115, 15, 255),
    'pink': Color(215, 15, 115, 255),
    'light_green': Color(115, 215, 15, 255),
    'purple': Color(115, 15, 215, 255),
    'light_blue': Color(15, 115, 215, 255),
    'turquoise': Color(15, 215, 115, 255),
    'lime': Color(0, 255, 0, 255)
}

def hex_to_rgb(value): # couldnt be bothered to write my own so copied https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def color(string):
    if string == 'random':
        return Color(randint(50, 200), randint(50, 200), randint(50, 200), 255)
    if string in colors:
        return colors[string]
    if string[0] == '#':
        return Color(*hex_to_rgb(string), 255)
    return color('lime')

default_properties = {
    'width': 'auto',
    'height': 'auto',
    'x_offset': '0',
    'y_offset': '0',
    'align_children': 'vertically',
    'children_vertical_align': 'start',
    'children_horizontal_align': 'start',
    'children_vertical_gap': '5',
    'children_horizontal_gap': '5',
    'padding_left': '5',
    'padding_right': '5',
    'padding_top': '5',
    'padding_bottom': '5',
    'text_size': '15',
    'text_color': 'black',
    'background_color': 'white',
    'border': 'transparent',
    'cursor': 'default',
}

def load_elel(path):
    file = open(path, 'r').read()
    file = re.sub('#.*', '', file)

    main = Element(path)
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
    
    main.properties['width'] = '800'
    main.properties['height'] = '600'
    
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
                current_property = {line[opened.start()+1:opened.end()-1]: ''}
        elif opened_event is not None:
            if current_event is None:
                current_event = Event(line[opened_event.start()+1:opened_event.end()-1])
            else:
                current_event.add_function(Function(line[opened_event.start()+1:opened_event.end()-1]))

        if closed is not None:
            if current_property is not None:
                if current_event is None:
                    current_selector.add_property(list(current_property)[0], current_property[list(current_property)[0]])
                    current_property = None
                else:
                    current_event.add_property(list(current_property)[0], current_property[list(current_property)[0]])
                    current_property = None
            else:
                special.add_selector(current_selector)
                current_selector = None
        
        if closed_event is not None:
            current_selector.add_event(current_event)
            current_event = None

        if opened is None and opened_event is None and closed is None and closed_event is None and current_property is not None:
            current_property[list(current_property)[0]] += re.sub('\s+', '', line) 

    return special