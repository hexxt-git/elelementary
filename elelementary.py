from pyray import * # should probably replace this
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

def decide_text_height(text, text_size):
    return (len(re.findall('[|]', text)) + 1) * text_size

def decide_text_width(text, text_size):
    return max(len(l) for l in text.split('|')) * text_size

class Element:
    def __init__(self, id):
        self.id = id
        self.text = ''
        self.children = []
        self.properties = copy.deepcopy(default_properties)
        self.events = [] # events are yet to be implemented.
        
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
            if self.properties['align_children'] == 'vertically':
                text_size = decide_text_width(self.text, int(self.properties['text_size']))
                biggest_child = max([child.get_width() for child in self.children]+[0])
                padding = int(self.properties['padding_left']) + int(self.properties['padding_right']) 
                return max(text_size, biggest_child) + padding
            if self.properties['align_children'] == 'horizontally':
                text_size = decide_text_width(self.text, int(self.properties['text_size']))
                children_size = sum([child.get_width() for child in self.children])
                gaps = int(self.properties['children_horizontal_gap']) * (len(self.children)) 
                padding = int(self.properties['padding_left']) + int(self.properties['padding_right']) 
                return text_size + children_size + gaps + padding

        if self.properties['width'] == 'fullscreen':
            return get_screen_width()
        return int(self.properties['width'])

    def get_height(self):
        if self.properties['height'] == 'auto':
            if self.properties['align_children'] == 'vertically':
                text_size = decide_text_height(self.text, int(self.properties['text_size']))
                children_size = sum([child.get_height() for child in self.children]+[0])
                gaps = int(self.properties['children_vertical_gap']) * (len(self.children))
                padding = int(self.properties['padding_top']) + int(self.properties['padding_bottom'])
                return text_size + children_size + gaps + padding
            if self.properties['align_children'] == 'horizontally':
                text_size = decide_text_height(self.text, int(self.properties['text_size']))
                biggest_child = max([child.get_height() for child in self.children]+[0])
                padding = int(self.properties['padding_top']) + int(self.properties['padding_bottom'])
                return max(text_size, biggest_child) + padding
        if self.properties['height'] == 'fullscreen':
            return get_screen_height()
        return int(self.properties['height'])
    
    def render(self, x, y):
        x += int(self.properties['x_offset'])
        y += int(self.properties['y_offset'])
        render_rectangle(x, y, self.get_width(), self.get_height(), color(self.properties['background_color']), color(self.properties['border']))
        x += int(self.properties['padding_left'])
        y += int(self.properties['padding_top'])
        if self.properties['align_children'] == 'vertically':
            for line in self.text.split('|'):
                render_text(line, x, y, int(self.properties['text_size']), color(self.properties['text_color']))
                y += int(self.properties['text_size'])
        if self.properties['align_children'] == 'horizontally':
            Y = y
            for line in self.text.split('|'):
                render_text(line, x, Y, int(self.properties['text_size']), color(self.properties['text_color']))
            Y += int(self.properties['text_size'])
            x += decide_text_width(self.text, int(self.properties['text_size']))

        if self.text == '':
            y -= int(self.properties['text_size'])

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
    if string == '':
        return color('lime')
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
    'text_size': '20',
    'text_color': 'black',
    'background_color': 'white',
    'border': 'transparent',
    'cursor': 'default',
}

def load_elel(path):
    file = open(path, 'r').read()
    file = re.sub('//.*', '', file)

    element = Element(path)
    stack = []
    for word in re.split('\s', file):
        opened = re.search('<[^/\s]+>', word)
        closed = sum([1 for _ in re.finditer('</>', word)])
        if opened:
            new_id = word[opened.start()+1: opened.end()-1]
            stack.append(Element(new_id))
        
        for _ in range(closed):
            if len(stack) >= 2:
                stack[-2].add_child(stack[-1])
                stack = stack[:-1]
            else:
                element.add_child(stack[-1])
                stack = []
        if len(stack) >= 1:
            stack[-1].text += re.sub('<.*>', '', word)
        else:
            element.text += re.sub('<.*>', '', word)
        
    element.properties['width'] = '800'
    element.properties['height'] = '600'

    return element

def load_sps(path):
    file = open(path, 'r').read()
    file = re.sub('//.*', '', file)

    special = Special()
    tmp_selector = None
    tmp_event = None
    tmp_property = None
    for word in re.split('\s', file):
        if word == ' ': 
            print('a')
        opened = re.search('<[^/\s]+>', word)
        closed = sum([1 for _ in re.finditer('</>', word)])
        opened_event = re.search('{[^/\s]+}', word)
        closed_event = sum([1 for _ in re.finditer('{/}', word)])

        if opened is not None:
            if tmp_selector is None:
                new_selector = word[opened.start()+1: opened.end()-1]
                tmp_selector = Selector(new_selector)
            else:
                new_property = word[opened.start()+1: opened.end()-1]
                tmp_property = {new_property: ''}

        if opened_event is not None:
            if tmp_event is None:
                tmp_event = Event(word[opened_event.start()+1: opened_event.end()-1])
            else:
                tmp_event.add_function(Function(word[opened_event.start()+1: opened_event.end()-1]))
        
        if tmp_property is not None:
            tmp_property[list(tmp_property)[0]] += re.sub('([<{].*[}>])|\s+', '', word) + ' '
        
        for _ in range(closed):
            if tmp_property is None:
                special.add_selector(tmp_selector)
                tmp_selector = None
            else:
                tmp_property[list(tmp_property)[0]] = re.sub('\s', '',tmp_property[list(tmp_property)[0]])
                if tmp_event is None:
                    tmp_selector.add_property(list(tmp_property)[0], tmp_property[list(tmp_property)[0]])
                    tmp_property = None
                else:
                    tmp_event.add_property(list(tmp_property)[0], tmp_property[list(tmp_property)[0]])
                    tmp_property = None
        
        for _ in range(closed_event):
            tmp_selector.add_event(tmp_event)
            tmp_event = None
    
    return special