#Contains functionality for images

import pygame
from . import utility
from . import drawing_tools
from . import text_tools
from . import scaling

class image():
    '''
    Abstract base image class
    '''
    def __init__(self, width, height, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int width: Pixel width of this image
            int height: Pixel height of this image
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.contains_bundle = False
        self.width = width
        self.height = height
        self.Rect = 'none'
        if self.image_type != 'bundle':
            self.global_manager.get('image_list').append(self)
    
    def complete_draw(self):
        '''
        Description:
            Draws this image after the necessary pre-call checks are done
        Input:
            None
        Output:
            None
        '''
        if self.contains_bundle:
            self.image.complete_draw()
        else:
            drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)

    def touching_mouse(self):
        '''
        Description:
            Returns whether this image is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if this image is colliding with the mouse, otherwise returns False
        '''
        if self.Rect != 'none' and self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)
        
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self))

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown
        Input:
            None
        Output:
            boolean: Returns True
        '''
        return(True)

    def draw(self):
        '''
        Description:
            Draws this image if it should currently be visible
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.complete_draw()

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

    def get_image_id_list(self, override_values={}):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        if type(self.image_id) == str:
            image_id_list = [self.image_id]
        else:
            image_id_list = self.image_id
        return(image_id_list)


class image_bundle(image):
    '''
    Group of 'anonymous' bundle images that act as a single image object and are always drawn together in a particular order
    An image can be set to an image bundle rather than a string image path
    '''
    def __init__(self, parent_image, image_id_list, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            image parent_image: Image that this bundle is attached to
            list image_id_list: List of string image file paths and/or offset image dictionaries
                offset image dictionary: String keys corresponding to extra information for offset images
                    'image'_id': string value - File path to image used for this offset image
                    'size': float value - Scale of offset image, with 1 being the same size as the bundle
                    'x_offset': float value - x-axis offset of image, with 1 being shifted a full width to the right
                    'y_offset': float value - y-axis offset of image, with 1 being shifted a full height upward
                    'level': int value - Layer for image to appear on, with 0 being the default layer, positive levels being above it, and negative levels being below it
            global_manager_template global_manager: Object that accesses shared variables
            boolean to_front = False: If True, allows this image to appear in front of most other objects instead of being behind them
        Output:
            None
        '''
        self.image_type = 'bundle'
        super().__init__(parent_image.width, parent_image.height, global_manager)
        self.parent_image = parent_image
        self.members = []
        for current_image_id in image_id_list:
            self.add_member(current_image_id)
        self.scale()
                
    def scale(self):
        '''
        Description:
            Sets this bundle to be the size of its attached images and scales each of its member images relative to the bundle size
        Input:
            None
        Output:
            None
        '''
        self.width = self.parent_image.width
        self.height = self.parent_image.height
        for member in self.members:
            member.scale()

    def add_member(self, image_id, member_type = 'default'):
        '''
        Description:
            Adds a new member image to this bundle
        Input:
            string/dictionary image_id: String image file path or offset image dictionary that defines the member added
            string member_type = 'default': Optional string to designate this member's type, allowing it to be specifically removed or found based on type later
        '''
        if isinstance(image_id, str):
            new_member = bundle_image(self, image_id, member_type)
        else: #if image id is dictionary with extra information
            new_member = bundle_image(self, image_id, member_type, is_offset = True)
        index = 0
        while index < len(self.members) and self.members[index].level <= new_member.level: #inserts at back of same level
            index += 1
        self.members.insert(index, new_member)

    def complete_draw(self):
        '''
        Description:
            Draws each of this bundle's member images in the correct order with each one's respective size and offsets
        Input:
            None
        Output:
            None
        '''
        for member in self.members:
            if not member.is_offset:
                drawing_tools.display_image(member.image, self.parent_image.x, self.parent_image.y - self.height, self.global_manager)
            else:
                drawing_tools.display_image(member.image, 
                                            self.parent_image.x + (self.width * member.x_offset) - (member.width / 2) + (self.width / 2), 
                                            (self.parent_image.y - (self.height * member.y_offset) - (member.height / 2) + (self.height / 2)) - self.height, 
                                            self.global_manager)
    def remove_member(self, member_type):
        '''
        Description:
            Removes all members of the inputted member type
        Input:
            string member_type: Type of member image to remove
        Output:
            None
        '''
        new_member_list = []
        for current_member in self.members:
            if current_member.member_type != member_type:
                new_member_list.append(current_member)
        self.members = new_member_list

    def has_member(self, member_type):
        '''
        Description:
            Returns whether this bundle contains any member images of the inputted type
        Input:
            string member_type: Type of member image to search for
        Output:
            None
        '''
        for current_member in self.members:
            if current_member.member_type == member_type:
                return(True)
        return(False)

    def clear(self):
        '''
        Description:
            Removes all of this bundle's member images
        Input:
            None
        Output:
            None
        '''
        self.members = []

    def to_list(self):
        '''
        Description:
            Generates and returns a list of string image file paths and/or offset image dictionaries that could be passed to a new image bundle to create an identical copy
        Input:
            None
        Output:
            list: Returns list of string image file paths and/or offset image dictionaries
        '''
        return_list = []
        for current_member in self.members:
            if not current_member.is_offset:
                return_list.append(current_member.image_id)
            else:
                return_list.append(current_member.image_id_dict)
        return(return_list)

class bundle_image():
    '''
    Not a true image, just a width, height, and id for an image in a bundle
    '''
    def __init__(self, bundle, image_id, member_type, is_offset = False):
        '''
        Description:
            Initializes this object
        Input:
            image_bundle bundle: Image bundle that this bundle image is a member of
            string/dictionary image_id: String image file path or offset image dictionary to define this image's appearance
                offset image dictionary: String keys corresponding to extra information for offset images
                    'image'_id': string value - File path to image used for this offset image
                    'size' = 1: float value - Scale of offset image, with 1 being the same size as the bundle
                    'x_offset' = 0: float value - x-axis offset of image, with 1 being shifted a full width to the right
                    'y_offset' = 0: float value - y-axis offset of image, with 1 being shifted a full height upward
                    'level' = 0: int value - Layer for image to appear on, with 0 being the default layer, positive levels being above it, and negative levels being below it
                    'green_screen': string list value - List of colors to use to replace particular preset colors in this image - if given ['red'] or 'red', replace each instance of the 1st 
                        preset green screen color of (62, 82, 82) with color_dict['red']
            string member_type: String to designate this member's type, allowing it to be specifically removed or found based on type later, 'default' by default
            boolean is_offset = False: Whether this is an offset image that takes a dictionary image id or a normal image that takes a string image id
        Output:
            None
        '''
        self.bundle = bundle
        self.image = 'none'
        self.member_type = member_type
        self.is_offset = is_offset

        if not is_offset:
            self.image_id = image_id
            self.level = 0
        else:
            self.image_id_dict = image_id
            self.image_id = image_id['image_id']
            if 'size' in image_id:
                self.size = image_id['size']
            else:
                self.size = 1
            if 'x_offset' in image_id:
                self.x_offset = image_id['x_offset']
            else:
                self.x_offset = 0
            if 'y_offset' in image_id:
                self.y_offset = image_id['y_offset']
            else:
                self.y_offset = 0
            if 'level' in image_id:
                self.level = image_id['level']
            else:
                self.level = 0
            if 'green_screen' in image_id:
                self.has_green_screen = True
                self.green_screen_colors = []
                if type(image_id['green_screen']) == list:
                    for index in range(0, len(image_id['green_screen'])):
                        self.green_screen_colors.append(image_id['green_screen'][index])
                else:
                    self.green_screen_colors.append(image_id['green_screen'])

            else:
                self.has_green_screen = False
        if type(self.image_id) == pygame.Surface: #if given pygame Surface, avoid having to render it again
            self.image = self.image_id
        else:
            self.load()
        self.scale()

    def scale(self):
        '''
        Description:
            Sets this image's size to one relative to its bundle's size based on its size multiplier
        Input:
            None
        Output:
            None
        '''
        if self.is_offset:
            self.width = self.bundle.width * self.size
            self.height = self.bundle.height * self.size
        else:
            self.width = self.bundle.width
            self.height = self.bundle.height
        if self.image != 'none':
            self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def load(self):
        '''
        Description:
            Loads in this image's image file on initialization
        Input:
            None
        Output:
            None
        '''
        full_image_id = 'graphics/' + self.image_id
        key = full_image_id
        if self.is_offset and self.has_green_screen:
            for current_green_screen_color in self.green_screen_colors:
                key += str(current_green_screen_color)
        if key in self.bundle.global_manager.get('rendered_images'): #if image already loaded, use it
            self.image = self.bundle.global_manager.get('rendered_images')[key]
        else: #if image not loaded, load it and add it to the loaded images
            try: #use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                self.image = pygame.image.load(full_image_id)
            except:
                print(full_image_id)
                self.image = pygame.image.load(full_image_id)
            if self.is_offset and self.has_green_screen:
                width, height = self.image.get_size()
                index = 0
                for current_green_screen_color in self.bundle.global_manager.get('green_screen_colors'):
                    if index < len(self.green_screen_colors):
                        if type(self.green_screen_colors[index]) == str: #like 'red'
                            replace_with = self.bundle.global_manager.get('color_dict')[self.green_screen_colors[index]]
                        else: #like (255, 0, 0)
                            replace_with = self.green_screen_colors[index]
                        for x in range(width):
                            for y in range(height):
                                current_color = self.image.get_at((x, y))
                                if current_color[0] == current_green_screen_color[0] and current_color[1] == current_green_screen_color[1] and current_color[2] == current_green_screen_color[2]:
                                    self.image.set_at((x, y), (replace_with[0], replace_with[1], replace_with[2], current_color[3])) #preserves alpha value
                    index += 1
            self.bundle.global_manager.get('rendered_images')[key] = self.image
            #print('loading new image' + str(time.time()))

class free_image(image):
    '''
    Image unrelated to any actors or grids that appears at certain pixel coordinates
    '''
    def __init__(self, image_id, coordinates, width, height, modes, global_manager, to_front = False):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this button can appear
            global_manager_template global_manager: Object that accesses shared variables
            boolean to_front = False: If True, allows this image to appear in front of most other objects instead of being behind them
        Output:
            None
        '''
        self.image_type = 'free'
        self.has_parent_collection = False
        super().__init__(width, height, global_manager)
        self.modes = modes
        self.set_image(image_id)
        self.set_origin(coordinates[0], coordinates[1])
        self.to_front = to_front
        self.global_manager.get('free_image_list').append(self)

    def calibrate(self, new_actor):
        return

    def set_origin(self, new_x, new_y):
        '''
        Description:
            Sets this interface element's location at the inputted coordinates. Along with set_modes, allows a free image to behave as an interface element and join interface collections
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        '''
        self.x = new_x
        self.y = self.global_manager.get('display_height') - new_y
        if hasattr(self, 'Rect') and self.Rect != 'none':
            self.Rect.x = self.x
            self.Rect.y = self.global_manager.get('display_height') - (new_y + self.height)
        if self.has_parent_collection:
            self.x_offset = new_x - self.parent_collection.x
            self.y_offset = new_y - self.parent_collection.y

    def set_modes(self, new_modes):
        '''
        Description:
            Sets this interface element's active modes to the inputted list. Along with set_origin, allows a free image to behave as an interface element and join interface collections
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        '''
        self.modes = new_modes

    def set_y(self, attached_label): #called by actor display labels
        '''
        Description:
            Sets this image's y position to be at the same height as the inputted label
        Input:
            actor_display_label attached_label: Label to match this image's y position with
        Output:
            None
        '''
        self.y = self.global_manager.get('display_height') - attached_label.y + attached_label.image_y_displacement
        if not self.Rect == 'none':
            self.Rect.y = self.y - self.height + attached_label.image_y_displacement

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. By default, it can be shown during game modes in which this image can appear
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        '''
        if (self.has_parent_collection and self.parent_collection.can_show()) or not self.has_parent_collection:
            if self.global_manager.get('current_game_mode') in self.modes:
                return(True)
        return(False)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('free_image_list', utility.remove_from_list(self.global_manager.get('free_image_list'), self))

    def set_image(self, new_image):
        '''
        Description:
            Changes this image to reflect the inputted image file path
        Input:
            string new_image: Image file path to change this image to
        Output:
            None
        '''
        self.image_id = new_image
        if isinstance(self.image_id, str): #if set to string image path
            self.contains_bundle = False
            full_image_id = 'graphics/' + self.image_id
            if full_image_id in self.global_manager.get('rendered_images'):
                self.image = self.global_manager.get('rendered_images')[full_image_id]
            else:
                try: #use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                    self.image = pygame.image.load(full_image_id)
                except:
                    print(full_image_id)
                    self.image = pygame.image.load(full_image_id)
                self.global_manager.get('rendered_images')[full_image_id] = self.image
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else: #if set to image path list
            self.contains_bundle = True
            self.image = image_bundle(self, self.image_id, self.global_manager) #self.image_id
        
    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this image's tooltip can currently be shown. By default, free images do not have tooltips and this always returns False
        Input:
            None
        Output:
            Returns whether this image's tooltip can currently be shown
        '''
        return(False)

class tooltip_free_image(free_image):
    '''
    Free image that has a tooltip when moused over
    '''
    def __init__(self, image_id, coordinates, width, height, modes, global_manager, to_front = False):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this button can appear
            global_manager_template global_manager: Object that accesses shared variables
            boolean to_front = False: If True, allows this image to appear in front of most other objects instead of being behind them
        Output:
            None
        '''
        super().__init__(image_id, coordinates, width, height, modes, global_manager, to_front)
        self.Rect = pygame.Rect(self.x, self.global_manager.get('display_height') - (self.y + self.height), self.width, self.height)
        self.Rect.y = self.y - self.height
        self.tooltip_text = []
        self.update_tooltip()

    def set_tooltip(self, tooltip_text):
        '''
        Description:
            Sets this image's tooltip to the inputted list, with each inputted list representing a line of the tooltip
        Input:
            string list new_tooltip: Lines for this image's tooltip
        Output:
            None
        '''
        self.tooltip_text = tooltip_text
        tooltip_width = 0
        font_name = self.global_manager.get('font_name')
        font_size = self.global_manager.get('font_size')
        for text_line in tooltip_text:
            if text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager) > tooltip_width:
                tooltip_width = text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager)
        tooltip_height = (len(self.tooltip_text) * font_size) + scaling.scale_height(5, self.global_manager)
        self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.x - self.tooltip_outline_width, self.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its subclass. By default, tooltip free images do not have any tooltip text
        Input:
            None
        Output:
            None
        '''
        self.tooltip_text = []

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this image's tooltip can currently be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        Input:
            None
        Output:
            Returns whether this image's tooltip can currently be shown
        '''
        if self.touching_mouse() and self.can_show():
            return(True)
        else:
            return(False)

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        '''
        Description:
            Draws this image's tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
        Input:
            boolean below_screen: Whether any of the currently showing tooltips would be below the bottom edge of the screen. If True, moves all tooltips up to prevent any from being below the screen
            boolean beyond_screen: Whether any of the currently showing tooltips would be beyond the right edge of the screen. If True, moves all tooltips to the left to prevent any from being beyond the screen
            int height: Combined pixel height of all tooltips
            int width: Pixel width of the widest tooltip
            int y_displacement: How many pixels below the mouse this tooltip should be, depending on the order of the tooltips
        Output:
            None
        '''
        if self.can_show():
            self.update_tooltip()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if below_screen:
                mouse_y = self.global_manager.get('display_height') + 10 - height
            if beyond_screen:
                mouse_x = self.global_manager.get('display_width') - width
            mouse_y += y_displacement
            self.tooltip_box.x = mouse_x
            self.tooltip_box.y = mouse_y
            self.tooltip_outline.x = self.tooltip_box.x - self.tooltip_outline_width
            self.tooltip_outline.y = self.tooltip_box.y - self.tooltip_outline_width
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.tooltip_outline)
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.tooltip_box)
            for text_line_index in range(len(self.tooltip_text)):
                text_line = self.tooltip_text[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (self.tooltip_box.x + scaling.scale_width(10, self.global_manager), self.tooltip_box.y +
                    (text_line_index * self.global_manager.get('font_size'))))

class indicator_image(tooltip_free_image):
    '''
    Image that appears under certain conditions based on its type
    '''
    def __init__(self, image_id, coordinates, width, height, modes, indicator_type, global_manager, to_front = False):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this button can appear
            string indicator_type: Type of variable that this indicator is attached to, like 'prosecution_bribed_judge'
            global_manager_template global_manager: Object that accesses shared variables
            boolean to_front = False: If True, allows this image to appear in front of most other objects instead of being behind them
        Output:
            None
        '''
        self.indicator_type = indicator_type
        super().__init__(image_id, coordinates, width, height, modes, global_manager, to_front)

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. Indicator images are shown when their attached variables are at certain values
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        '''
        if super().can_show():
            if self.indicator_type == 'prosecution_bribed_judge':
                if self.global_manager.get('prosecution_bribed_judge'):
                    return(True)
            elif self.indicator_type == 'not prosecution_bribed_judge':
                if not self.global_manager.get('prosecution_bribed_judge'):
                    return(True)
            else:
                return(True)
        return(False)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its attached variable
        Input:
            None
        Output:
            None
        '''
        if self.indicator_type == 'prosecution_bribed_judge':
            text = []
            text.append('The judge has been bribed, giving you an advantage in the next trial this turn')
            text.append('This bonus will fade at the end of the turn if not used')
            self.set_tooltip(text)
        elif self.indicator_type == 'not prosecution_bribed_judge':
            text = []
            text.append('The judge has not yet been bribed')
            text.append('Bribing the judge may give you an advantage in the next trial this turn or blunt the impact of any bribes made by the defense.')
            self.set_tooltip(text)
        else:
            self.set_tooltip([])
                
class dice_roll_minister_image(tooltip_free_image):
    '''
    Part of a pair of images that shows the controlling minister's position and portrait next to notifications during dice rolls
    '''
    def __init__(self, coordinates, width, height, modes, attached_minister, minister_image_type, global_manager, minister_message_image = False):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this button can appear
            minister attached_minister: Minister attached to this image
            string minister_image_type: Type of minister information shown by this image, like 'portrait' or 'position'
            global_manager_template global_manager: Object that accesses shared variables
            boolean minister_message_image = False: Whether this image is attached to a minister message or an action notification dice roll
        Output:
            None
        '''
        self.attached_minister = attached_minister #minister object
        self.minister_image_type = minister_image_type #position or portrait
        if minister_image_type == 'portrait':
            image_id = attached_minister.image_id
        elif minister_image_type == 'position':
            if not self.attached_minister.current_position == 'none':
                image_id = 'ministers/icons/' + global_manager.get('minister_type_dict')[self.attached_minister.current_position] + '.png'
            else:
                image_id = 'misc/mob_background.png'
        self.minister_message_image = minister_message_image #whether this is an image attached to a minister message notification or an action notification - action notification by default, acts differently
        super().__init__(image_id, coordinates, width, height, modes, global_manager)
        global_manager.get('dice_roll_minister_images').append(self)
        self.to_front = True

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its subclass. A dice roll minister image's tooltip copies the tooltip of the minister, which describes their name and position. Only the portrait image has a
                tooltip, preventing a double tooltip from the position image
        Input:
            None
        Output:
            None
        '''
        if self.minister_image_type == 'portrait':
            self.set_tooltip(self.attached_minister.tooltip_text)
        else:
            self.set_tooltip([])

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. Normal dice roll minister images return the same as superclass, while minister message images are only shown when their minister's message is currently displayed
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        '''
        if super().can_show():
            if self.minister_message_image:
                current_notification = self.global_manager.get('notification_list')[0]
                if current_notification.notification_type == 'minister' and current_notification.attached_minister == self.attached_minister:
                    return(True)
            else:
                return(True)
        return(False)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('dice_roll_minister_images', utility.remove_from_list(self.global_manager.get('dice_roll_minister_images'), self))

class minister_type_image(tooltip_free_image):
    '''
    Image that displays the icon corresponding to a certain minister office. Can be set to always show the icon for the same office or to show the icon of a certain unit's minister
    '''
    def __init__(self, coordinates, width, height, modes, minister_type, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this button can appear
            string minister_type: Minister office whose icon is always represented by this image, or 'none' if the icon can change
            actor_display_label/string attached_label: Actor display label that this image appears next to, or 'none' if not attached to a label
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.current_minister = 'none'
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)
        self.attached_label = attached_label
        self.minister_type = minister_type #position, like General
        if not self.minister_type == 'none':
            self.calibrate(global_manager.get('current_ministers')[self.minister_type]) #calibrate to current minister or none if no current minister
        self.global_manager.get('minister_image_list').append(self)
        self.to_front = True

    def calibrate(self, new_minister):
        '''
        Description:
            Attaches this image to the inputted minister and updates this image's appearance to the minister's office icon
        Input:
            string/minister new_minister: The displayed minister whose information is matched by this label. If this equals 'none', the label is detached from any minister and is hidden
        Output:
            None
        '''
        if new_minister != 'none':
            if new_minister.actor_type != 'minister':
                if hasattr(new_minister, 'controlling_minister'):
                    new_minister = new_minister.controlling_minister
                else:
                    new_minister = 'none'
        else:
            new_minister = 'none'

        #if new_minister != 'none' and new_minister.actor_type == 'minister':
        #    continue
        #if new_minister != 'none' and hasattr(new_minister, 'controlling_minister'): #if calibrating to a mob, calibrate to its minister instead
        #    new_minister = new_minister.controlling_minister
        #else:
        #    new_minister = 'none'
        self.current_minister = new_minister
        if not new_minister == 'none':
            self.minister_type = new_minister.current_position #new_minister.current_position
        current_minister_type = self.minister_type
        if (not self.attached_label == 'none') and (not self.attached_label.actor == 'none') and self.attached_label.actor.is_pmob:
            current_minister_type = self.attached_label.actor.controlling_minister_type
        if not current_minister_type == 'none':
            keyword = self.global_manager.get('minister_type_dict')[current_minister_type] #type, like military
            self.tooltip_text = []
            if keyword == 'prosecution':
                self.tooltip_text.append('Rather than controlling units, a prosecutor controls the process of investigating and removing ministers suspected to be corrupt.')
            else:
                self.tooltip_text.append('Whenever you command a ' + keyword + '-oriented unit to do an action, the ' + current_minister_type + ' is responsible for executing the action.')#new_minister.tooltip_text
                if keyword == 'military':
                    self.tooltip_text.append('Military-oriented units include military officers and European battalions.')
                elif keyword == 'religion':
                    self.tooltip_text.append('Religion-oriented units include evangelists, church volunteers, and missionaries.')
                elif keyword == 'trade':
                    self.tooltip_text.append('Trade-oriented units include merchants and caravans.')
                    self.tooltip_text.append('The ' + current_minister_type + ' also controls the purchase and sale of goods in Europe.')
                elif keyword == 'exploration':
                    self.tooltip_text.append('Exploration-oriented units include explorers, expeditions, hunters, and safaris.')
                elif keyword == 'construction':
                    self.tooltip_text.append('Construction-oriented units include engineers and construction gangs.')
                elif keyword == 'production':
                    self.tooltip_text.append('Production-oriented units include work crews, foremen, and workers not attached to other units.')
                elif keyword == 'transportation':
                    self.tooltip_text.append('Transportation-oriented units include ships, trains, drivers, and porters.')
                    self.tooltip_text.append('The ' + current_minister_type + ' also ensures that goods are not lost in transport or storage.')
            if new_minister == 'none':
                self.tooltip_text.append('There is currently no ' + current_minister_type + ' appointed, so ' + keyword + '-oriented actions are not possible.')
            self.set_image('ministers/icons/' + keyword + '.png')
        self.update_image_bundle()
            
    def get_image_id_list(self, override_values={}):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        image_id_list = super().get_image_id_list(override_values)
        if self.current_minister == 'none':
            image_id_list.append('misc/warning_icon.png')
        return(image_id_list)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its subclass. A minister type image's tooltip describes what the office of its office icon does
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(self.tooltip_text)

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. If not attached to label, returns same as superclass. Otherwise, returns True if the attached label is showing or False if it is not showing
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        '''
        if not self.attached_label == 'none':
            return(self.attached_label.can_show())
        else:
            return(super().can_show())

class warning_image(free_image):
    '''
    Image that appears over the image it is attached to under certain conditions to draw attention from the player
    '''
    def __init__(self, attached_image, global_manager, attachment_type = 'image'):
        '''
        Description:
            Initializes this object
        Input:
            image attached_image: Image that this warning appears over under certain conditions
            global_manager_template global_manager: Object that accesses shared variables
            string attachment_type = 'image': Type of object this image is attached to, like 'image' or 'button'
        Output:
            None
        '''
        self.attached_image = attached_image
        if attachment_type == 'image':
            x_position = self.attached_image.x
            y_position = global_manager.get('display_height') - self.attached_image.y
        else:
            x_position = self.attached_image.x - 100
            y_position = self.attached_image.y
            
        super().__init__('misc/warning_icon.png', (x_position, y_position), self.attached_image.width, self.attached_image.height, self.attached_image.modes,
            global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. A warning image is shown when the image it is attached to says to show a warning
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        '''
        return(self.attached_image.can_show_warning())

class loading_image_template(free_image):
    '''
    Image that occupies the entire screen, covering all other objects while the game is loading 
    '''
    def __init__(self, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(image_id, (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), [], global_manager)
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self)) #different from other images, should only be drawn when directly requested

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. Unlike other images, a loading screen image will always be visible when draw() is called
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        '''
        return(True)

class actor_image(image):
    '''
    Image that is attached to an actor and a grid, representing the actor on a certain grid. An actor will have a different actor_image for each grid on which it appears
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            actor actor: actor to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            grid grid: actor's grid on which this image appears. Each of an actor's images appears on a different grid
            string image_description: Key in this image's actor's image_dict corresponding to the appearance that this image has. For example, a 'default' actor_image will show the actor's default appearance
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.image_type = 'actor'
        super().__init__(width, height, global_manager)
        self.global_manager = global_manager
        self.actor = actor
        self.modes = actor.modes
        self.Rect = pygame.Rect(self.actor.x, self.actor.y - self.height, self.width, self.height) #(left, top, width, height), bottom left on coordinates
        self.set_image(image_description)
        self.image_description == image_description
        self.grid = grid
        self.outline_width = self.grid.grid_line_width + 1
        self.outline = pygame.Rect(self.actor.x, self.global_manager.get('display_height') - (self.actor.y + self.height), self.width, self.height)
        self.x, self.y = self.grid.convert_coordinates((self.actor.x, self.actor.y))
        if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            grid_x, grid_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
        else:
            grid_x = self.actor.x
            grid_y = self.actor.y
        self.go_to_cell((grid_x, grid_y))
        self.set_tooltip('')
        self.change_with_other_images = True #determines whether set_image function of actor affects this image

    def get_center_coordinates(self):
        '''
        Description:
            Returns the pixel coordinates of the center of this image's cell
        Input:
            None
        Output:
            int tuple: Two values representing x and y pixel coordinates of the center of this image's cell
        '''
        cell_width = self.grid.get_cell_width()
        cell_height = self.grid.get_cell_height()
        return((self.x + round(cell_width / 2), self.global_manager.get('display_height') -(self.y + round(cell_height / 2))))
        
    def set_image(self, new_image_description):
        '''
        Description:
            Changes this image to reflect this image's actor's image_dict file path value for the inputted key
        Input:
            string new_image_description: Key in this image's actor's image_dict corresponding to this image's new appearance. For example, 'default' will change this actor_image to show the actor's default appearance
            or string list new_image_description: List of image file paths corresponding to this image's new appearance
        Output:
            None
        '''
        if isinstance(new_image_description, str) and new_image_description in self.actor.image_dict:
            self.image_description = new_image_description
            self.image_id = self.actor.image_dict[new_image_description]
        else:
            self.image_description = 'default'
            self.image_id = new_image_description
        
        if isinstance(self.image_id, str): #if set to string image path
            self.contains_bundle = False
            full_image_id = 'graphics/' + self.image_id
            if full_image_id in self.global_manager.get('rendered_images'):
                self.image = self.global_manager.get('rendered_images')[full_image_id]
            else:
                try: #use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                    self.image = pygame.image.load(full_image_id)
                except:
                    print(full_image_id)
                    self.image = pygame.image.load(full_image_id)
                self.global_manager.get('rendered_images')[full_image_id] = self.image
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else: #if set to image path list
            self.contains_bundle = True
            self.image = image_bundle(self, self.image_id, self.global_manager) #self.image_id
        
    def draw(self):
        '''
        Description:
            Draws this image if it should currently be visible. Unlike free images, actor images appear at their actor's grid coordinates
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
                if(self.grid.is_on_mini_grid(self.actor.x, self.actor.y)):
                    grid_x, grid_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
                    self.go_to_cell((grid_x, grid_y))
                    self.complete_draw()
            else:
                self.go_to_cell((self.actor.x, self.actor.y))
                self.complete_draw()
        
    def go_to_cell(self, coordinates):
        '''
        Description:
            Moves this image to the pixel coordinates corresponding to the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y coordinates on this image's grid
        Output:
            None
        '''
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x
        self.outline.y = self.y - self.height
        if self.contains_bundle:
            self.image.x = self.x
            self.image.y = self.y
                
    def set_tooltip(self, tooltip_text):
        '''
        Description:
            Sets this image's tooltip to the inputted list, with each item representing a line of the tooltip
        Input:
            string list tooltip_text: Lines for this actor's tooltip
        Output:
            None
        '''
        self.tooltip_text = tooltip_text
        tooltip_width = 10 #minimum tooltip width
        font_size = self.global_manager.get('font_size')
        font_name = self.global_manager.get('font_name')
        for text_line in tooltip_text:
            if text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager) > tooltip_width:
                tooltip_width = text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager)
        tooltip_height = (font_size * len(tooltip_text)) + scaling.scale_height(5, self.global_manager)
        self.tooltip_box = pygame.Rect(self.actor.x, self.actor.y, tooltip_width, tooltip_height)
        self.actor.tooltip_box = self.tooltip_box
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.actor.x - self.tooltip_outline_width, self.actor.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. By default, it can be shown during game modes in which this image can appear
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)
            
class mob_image(actor_image):
    '''
    actor image attached to a mob rather than an actor, gaining the ability to manage the cells corresponding to this image's mob's coordinates
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            actor actor: actor to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            grid grid: actor's grid on which this image appears. Each of an actor's images appears on a different grid
            string image_description: Key in this image's actor's image_dict corresponding to the appearance that this image has. For example, a 'default' actor_image will show the actor's default appearance
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.current_cell = 'none'
        self.image_type = 'mob'
        self.add_to_cell()
        
    def remove_from_cell(self):
        '''
        Description:
            Removes this image and its mob from this image's cell
        Input:
            None
        Output:
            None
        '''
        if not self.current_cell == 'none':
            self.current_cell.contained_mobs = utility.remove_from_list(self.current_cell.contained_mobs, self.actor)
        self.current_cell = 'none'

    def add_to_cell(self):
        '''
        Description:
            Moves this image to the cell corresponding to its grid coordinates, causing this image's actor to be considered to be in the cell. Removes this image from its previous cell. Unlike go_to_cell, which handles pixel location,
                this handles grid location
        Input:
            None
        Output:
            None
        '''
        if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            mini_x, mini_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
            if(self.grid.is_on_mini_grid(self.actor.x, self.actor.y)):
                old_cell = self.current_cell
                self.current_cell = self.grid.find_cell(mini_x, mini_y)
                if not old_cell == self.current_cell and not self.actor in self.current_cell.contained_mobs and not (self.actor.in_group or self.actor.in_vehicle or self.actor.in_building):
                    self.current_cell.contained_mobs.insert(0, self.actor)
            else:
                self.remove_from_cell()
            self.go_to_cell((mini_x, mini_y))
        else:
            self.remove_from_cell()
            self.current_cell = self.grid.find_cell(self.actor.x, self.actor.y)
            if not self.actor in self.current_cell.contained_mobs and not (self.actor.in_group or self.actor.in_vehicle or self.actor.in_building):
                self.current_cell.contained_mobs.insert(0, self.actor)
            self.go_to_cell((self.current_cell.x, self.current_cell.y))
            
    def can_show(self):
        '''
        Description:
            Returns whether this image can be shown. By default, it can be shown when its mob should be visible
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode and if its mob is not attached to another actor or behind another mob, otherwise returns False
        '''
        return(self.actor.can_show())

class button_image(actor_image):
    '''
    actor image attached to a button rather than an actor, causing it to be located at a pixel coordinate location where its button should be rather than within a grid cell
    '''
    def __init__(self, button, width, height, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            button button: button to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.image_type = 'button'
        self.button = button
        self.width = width
        self.height = height
        self.x = self.button.x
        self.y = self.global_manager.get('display_height') - (self.button.y + self.height) - self.height
        self.modes = button.modes
        self.image_id = image_id
        self.set_image(image_id)
        self.global_manager.get('image_list').append(self)
        self.Rect = self.button.Rect
        self.outline_width = 2
        self.outline = pygame.Rect(self.x - self.outline_width, self.global_manager.get('display_height') - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))

    def update_state(self, new_x, new_y, new_width, new_height):
        '''
        Description:
            Changes this image's size and location to match its button when its button's size or location changes
        Input:
            new_x: New pixel x coordinate for this image
            new_y: New pixel y coordinate for this image
            new_width: new pixel width for this image
            new_height: new pixel height for this image
        Output:
            None
        '''
        self.Rect = self.button.Rect
        self.width = new_width
        self.height = new_height
        self.outline.x = new_x - self.outline_width
        self.outline.y = self.global_manager.get('display_height') - (new_y + new_height + self.outline_width)
        self.outline.width = new_width + (2 * self.outline_width)
        self.outline.height = new_height + (self.outline_width * 2)
        self.set_image(self.image_id)
        
    def set_image(self, new_image_id):
        '''
        Description:
            Changes the image file reflected by this object
        Input:
            string new_image_id: File path to the new image used by this object
        Output:
            None
        '''
        self.image_id = new_image_id
        if isinstance(self.image_id, str): #if set to string image path
            self.contains_bundle = False
            full_image_id = 'graphics/' + self.image_id
            if full_image_id in self.global_manager.get('rendered_images'):
                self.image = self.global_manager.get('rendered_images')[full_image_id]
            else:
                try: #use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                    self.image = pygame.image.load(full_image_id)
                except:
                    print(full_image_id)
                    self.image = pygame.image.load(full_image_id)
                self.global_manager.get('rendered_images')[full_image_id] = self.image
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else: #if set to image path list
            self.contains_bundle = True
            self.image = image_bundle(self, self.image_id, self.global_manager) #self.image_id
        
    def draw(self):
        '''
        Description:
            Draws this image if it should currently be visible at the coordinates of its button
        Input:
            None
        Output:
            None
        '''
        if self.button.can_show():
            self.x = self.button.x
            self.y = self.global_manager.get('display_height') - (self.button.y + self.height) + self.height
            self.complete_draw()
        
    def draw_tooltip(self):
        '''
        Description:
            Usually draws a tooltip when moused over. However, since buttons, unlike actors, manage their own tooltips, button images do not need any tooltip functionality
        Input:
            None
        Output:
            None
        '''
        return()
        
    def set_tooltip(self, tooltip_text):
        '''
        Description:
            Usually sets an image's tooltip to the inputted list, with each item representing a line of the tooltip. However, since buttons, unlike actors, manage their own tooltips, button images do not need any tooltip functionality
        Input:
            string list tooltip_text: Lines for this image's tooltip
        Output:
            None
        '''
        return()

class collection_image(button_image):
    def draw(self):
        if self.button.can_show():
            self.x = self.button.x
            self.y = self.global_manager.get('display_height') + self.height - self.button.y# + self.height
            #self.y = self.global_manager.get('display_height') + self.button.y - (self.height * 3)
            self.complete_draw()

class tile_image(actor_image):
    '''
    actor_image attached to a tile rather than an actor, causing it to use file paths directly rather than an dictionary of image keys and file path values
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            actor actor: actor to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            grid grid: actor's grid on which this image appears. Each of an actor's images appears on a different grid
            string image_description: Key in this image's actor's image_dict corresponding to the appearance that this image has. For example, a 'default' actor_image will show the actor's default appearance
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.go_to_cell((self.actor.x, self.actor.y))

    def go_to_cell(self, coordinates):
        '''
        Description:
            Moves this image to the pixel coordinates corresponding to the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y coordinates on this image's grid
        Output:
            None
        '''
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)
        
    def draw(self):
        '''
        Description:
            Draws this image if it should currently be visible
        Input:
            None
        Output:
            None
        '''
        if self.actor.name == 'resource icon' and not self.actor.cell.visible:
            return() #do not show if resource icon in undiscovered tile
        self.go_to_cell((self.actor.x, self.actor.y))
        self.complete_draw()
