#Contains functionality for interface elements and collections

import pygame

class interface_element():
    '''
    Abstract base interface element class
    Object that can be contained in an interface collection and has a location, rect, and image bundle with particular conditions for displaying, along with an optional tooltip when displayed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.width = input_dict['width']
        self.height = input_dict['height']
        self.Rect = pygame.Rect(0, self.global_manager.get('display_height') - (self.height), self.width, self.height)
        if not 'parent_collection' in input_dict:
            input_dict['parent_collection'] = 'none'
        self.parent_collection = input_dict['parent_collection']
        self.has_parent_collection = self.parent_collection != 'none'
        if self.has_parent_collection:
            self.parent_collection.add_member(self, input_dict['coordinates'][0], input_dict['coordinates'][1])
        else:
            self.set_origin(input_dict['coordinates'][0], input_dict['coordinates'][1])
        self.set_modes(input_dict['modes'])

    def can_show(self):
        '''
        Description:
            Returns whether this button can be shown. By default, elements can be shown during game modes in which they can appear, iff their parent collection (if any) is also showing
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        '''
        if (not self.has_parent_collection) or self.parent_collection.can_show():
            if self.global_manager.get('current_game_mode') in self.modes:
                return(True)
        return(False)

    def set_origin(self, new_x, new_y):
        '''
        Description:
            Sets this interface element's location at the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        '''
        self.x = new_x
        self.Rect.x = self.x
        self.y = new_y
        self.Rect.y = self.global_manager.get('display_height') - (self.y + self.height)
        if self.has_parent_collection:
            self.x_offset = self.x - self.parent_collection.x
            self.y_offset = self.y - self.parent_collection.y

    def set_modes(self, new_modes):
        '''
        Description:
            Sets this interface element's active modes to the inputted list
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        '''
        self.modes = new_modes

class interface_collection(interface_element):
    '''
    Object managing an image bundle and collection of interactive interface elements, including buttons, free images, and other interface collections
    An entire collection can be displayed or hidden as a unit, along with individual components having their own conditions for being visible when the window is displayed
    A collection could have different modes that display different sub-windows under different conditions while keeping other elements constant
    A particular type of collection could have special ordered functionality, like a series of buttons that can be scrolled through, or a images displayed in horizontal rows w/ maximum widths
    Older, informal collections such as the available minister scrollbar, the movement buttons, and the mob, tile, minister, prosecution, and defense displays should be able to be 
        implemented as interface collections. Additionally, the "mode" system could possibly be changed to use overarching interface collections for each mode
    Like an image bundle, members of an interface collection should have independent types and characteristics but be controlled as a unit and created in a list with a dictionary or simple 
        string. Unlike an image bundle, a collection does not necessarily have to be saved, and 
    '''
    def __init__(self, input_dict, global_manager):    
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''    
        super().__init__(input_dict, global_manager)
        self.members = []
    
    def add_member(self, new_member, x_offset, y_offset):
        '''
        Description:
            Adds an existing interface element as a member of this collection and sets its origin coordinates relative to this collection's origin coordinates
        Input:
            interface_element new_member: New element to add as a member
            int x_offset: Number of pixels to the right the new member's origin should be from the collection's origin
            int x_offset: Number of pixels upward the new member's origin should be from the collection's origin
        Output:
            None
        '''
        new_member.parent_collection = self
        new_member.has_parent_collection = True
        self.members.append(new_member)
        new_member.set_origin(self.x + x_offset, self.y + y_offset)

    def set_origin(self, new_x, new_y):
        '''
        Description:
            Sets this interface element's location at the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        '''
        super().set_origin(new_x, new_y)
        for member in self.members: #members will retain their relative positions with the collection while shifting to be centered around the new collection origin
            member.set_origin(new_x + member.x_offset, new_y + member.y_offset)

    def set_modes(self, new_modes):
        '''
        Description:
            Sets this interface element's active modes and those of its members to the inputted list
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        '''
        super().set_modes(new_modes)
        for member in self.members:
            member.set_modes(new_modes)
