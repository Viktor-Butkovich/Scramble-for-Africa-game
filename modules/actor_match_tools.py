from .images import free_image
from .labels import label
from .buttons import button
from . import scaling

class actor_match_free_image(free_image):
    '''
    Free image that changes its appearance to match selected mobs or tiles
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel location of this image
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            modes: list of strings representing the game modes in which this image can appear
            actor_image_type: string representing the type of actor whose appearance will be copied by this image
            global_manager: global_manager_template object
        '''
        self.actor_image_type = actor_image_type
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def calibrate(self, new_actor):
        '''
        Input:
            new_actor: actor object or string representing the actor whose appearance will be copied by this image. If resetting to an empty image, new_actor will equal 'none'.
        Output:
            Sets this image to match the inputted actor or string. If the input is 'none', it will be reset to an empty image. Otherwise, it will use the default appearance of the inputted actor.
        '''
        if not new_actor == 'none':
            if self.actor_image_type == 'resource':
                if new_actor.cell.visible:
                    if not new_actor.resource_icon == 'none':
                        self.set_image(new_actor.resource_icon.image_dict['default'])
                    else: #show nothing if no resource
                        self.set_image('misc/empty.png')
                else: #show nothing if cell not visible
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'terrain' and not new_actor.cell.visible:
                self.set_image(new_actor.image_dict['hidden'])
            else:
                self.set_image(new_actor.image_dict['default'])
        else:
            self.set_image('misc/empty.png')

class label_image(free_image):
    '''
    Free image that is attached to a label and will only show when the label is showing
    '''
    def __init__(self, coordinates, width, height, modes, attached_label, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel location of this image
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            modes: list of strings representing the game modes in which this image can appear
            attached_label: label object representing the label to which this image is attached.
            global_manager: global_manager_template object
        '''
        self.attached_label = attached_label
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def can_show(self):
        '''
        Input:
            none
        Output:
            Controls whether this image should be shown. This image is shown only when its attached label is shown. 
        '''
        if self.attached_label.can_show():
            return(super().can_show())
        else:
            return(False)

class label_button(button):
    '''
    Button that is attached to a label, has have behavior related to the label, will only show when the label is showing
    '''
    def __init__(self, coordinates, width, height, button_type, modes, image_id, attached_label, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            width: int representing the width in pixels of the button
            height: int representing the height in pixels of the button
            button_type: string representing a subtype of button, such as a 'move up' button, determining its tooltip and behavior
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            attached_label: label object representing the label to which this button is attached.
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.attached_label = attached_label
        super().__init__(coordinates, width, height, 'blue', button_type, 'none', modes, image_id, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def can_show(self):
        '''
        Input:
            none
        Output:
            Controls whether this button should be shown. This button is shown only when its attached label is shown. 
        '''
        if self.attached_label.can_show():
            return(super().can_show())
        else:
            return(False)

class actor_match_label(label):
    '''
    Label that changes its text to match the information of selected mobs or tiles
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, actor_label_type, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            minimum_width: int representing the minimum width in pixels of the button. As the length of its message increases, the label's width will increase to accomodate it. 
            height: int representing the height in pixels of the button
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            actor_image_type: string representing the type of information of a selected mob or tile that will be shown
            global_manager: global_manager_template object
        '''
        message = 'default'
        super().__init__(coordinates, minimum_width, height, modes, image_id, message, global_manager)
        self.actor_label_type = actor_label_type
        if self.actor_label_type == 'name':
            self.message_start = 'Name: '
        elif self.actor_label_type == 'resource':
            self.message_start = 'Resource: '
        elif self.actor_label_type == 'terrain':
            self.message_start = 'Terrain: '
        else:
            self.message_start = 'none'
        self.actor = 'none'
        self.calibrate('none')

    def calibrate(self, new_actor):
        '''
        Input:
            new_actor: actor object or string representing the actor whose information will be shown by this label. If resetting to a default message, new_actor will equal 'none'.
        Output:
            Sets this label's text to match the information of the inputted actor or string. If the input is 'none', it will be reset to a default message. Otherwise, it will show the information of the inputted actor.
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            if self.actor_label_type == 'name':
                self.set_label(self.message_start + str(new_actor.name))
            elif self.actor_label_type == 'terrain':
                if self.actor.cell.visible:
                    self.set_label(self.message_start + str(new_actor.cell.terrain))
                else:
                    self.set_label(self.message_start + 'unknown')
            elif self.actor_label_type == 'resource':
                if self.actor.cell.visible:
                    self.set_label(self.message_start + str(new_actor.cell.resource))
                else:
                    self.set_label(self.message_start + 'unknown')
        else:
            self.set_label(self.message_start + 'n/a')

class commodity_match_label(actor_match_label):
    '''
    Label that changes its text and attached image and button to match the commodity in a certain part of a currently selected actor's inventory    
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, commodity_index, matched_actor_type, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            minimum_width: int representing the minimum width in pixels of the button. As the length of its message increases, the label's width will increase to accomodate it. 
            height: int representing the height in pixels of the button
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            commodity_index: int representing the part of an actor's inventory shown by this label. A commodity index of 0 would cause this label to match the first item in a selected actor's inventory.
            matched_actor_type: string representing whether this label should match selected mobs or tiles
            global_manager: global_manager_template object
        '''
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'commodity', global_manager)
        self.showing_commodity = False
        self.commodity_index = commodity_index
        self.commodity_image = label_image((self.x - self.height, self.y), self.height, self.height, self.modes, self, self.global_manager) #self, coordinates, width, height, modes, attached_label, global_manager   
        if matched_actor_type == 'mob':
            self.commodity_button = label_button((self.x  + scaling.scale_width(175, self.global_manager), self.y), self.height, self.height, 'drop commodity', self.modes, 'misc/drop_commodity_button.png', self, global_manager)
        elif matched_actor_type == 'tile':
            self.commodity_button = label_button((self.x + scaling.scale_width(175, self.global_manager), self.y), self.height, self.height, 'pick up commodity', self.modes, 'misc/pick_up_commodity_button.png', self, global_manager)

    def calibrate(self, new_actor):
        '''
        Input:
            new_actor: actor object or string representing the actor whose inventory will be shown by this label.
        Output:
            Sets this label's text, image, and button to match a certain index of new_actor's inventory. If new_actor is 'none', the label and its attached image and button will not be shown.
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            commodity_list = new_actor.get_held_commodities()
            if len(commodity_list) - 1 >= self.commodity_index: #if index in commodity list
                self.showing_commodity = True
                commodity = commodity_list[self.commodity_index]
                self.set_label(commodity + ': ' + str(new_actor.get_inventory(commodity))) #format - commodity_name: how_many
                self.commodity_image.set_image('scenery/resources/' + commodity + '.png')
            else:
                self.showing_commodity = False
                self.set_label('n/a')
        else:
            self.showing_commodity = False
            self.set_label('n/a')

    def can_show(self):
        '''
        Input:
            none
        Output:
            Controls whether this label should be shown. This button is shown only when it is calibrated to an actor with an inventory size that includes this label's commodity index.
        '''
        if not self.showing_commodity:
            return(False)
        else:
            return(super().can_show())
