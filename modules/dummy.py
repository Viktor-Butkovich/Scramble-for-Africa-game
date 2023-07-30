#Contains functionality for dummies, which replicate other objects or act as models of hypothetical objects with fake attribute values and tooltips 

import pygame
from . import text_tools
from . import scaling
from . import mobs

class dummy(mobs.mob):
    def __init__(self, input_dict, global_manager):
        '''
        input dict always includes dummy_type, which is generally equal to the init type of the unit being replicated?
        '''
        for key in input_dict:
            setattr(self, key, input_dict[key])
        self.global_manager = global_manager

    def set_tooltip(self, tooltip_text):
        self.tooltip_text = tooltip_text
        #tooltip_width = 0
        #font_name = self.global_manager.get('font_name')
        #font_size = self.global_manager.get('font_size')
        #for text_line in tooltip_text:
        #    if text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager) > tooltip_width:
        #        tooltip_width = text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager)
        #tooltip_height = (len(self.tooltip_text) * font_size) + scaling.scale_height(5, self.global_manager)
        #self.x, self.y = (0, 0)
        #self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)   
        #self.tooltip_outline_width = 1
        #self.tooltip_outline = pygame.Rect(self.x - self.tooltip_outline_width, self.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def get_image_id_list(self):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        return(self.image_id_list)

    def update_image_bundle(self):
        '''
        Description:
            Updates this actor's images with its current image id list
        Input:
            None
        Output:
            None
        '''
        self.set_image(self.get_image_id_list())