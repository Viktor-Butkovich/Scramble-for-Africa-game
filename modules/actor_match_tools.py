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
            elif self.actor_image_type == 'resource building':
                if not new_actor.cell.contained_buildings['resource'] == 'none':
                    self.set_image(new_actor.cell.contained_buildings['resource'].image_dict['default']) #matches resource building
                else:
                    self.set_image('misc/empty.png')
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
            if not ((self.button_type == 'sell commodity' or self.button_type == 'sell all commodity') and self.attached_label.current_commodity == 'consumer goods'):
                return(super().can_show())
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
        elif self.actor_label_type == 'movement':
            self.message_start = 'Movement points: '
        elif self.actor_label_type == 'building worker':
            self.message_start = ''
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
                if new_actor.grid.is_abstract_grid:
                    self.set_label(self.message_start + 'n/a')
                elif self.actor.cell.visible:
                    self.set_label(self.message_start + str(new_actor.cell.terrain))
                else:
                    self.set_label(self.message_start + 'unknown')
            elif self.actor_label_type == 'resource':
                if new_actor.grid.is_abstract_grid:
                    self.set_label(self.message_start + 'n/a')
                elif new_actor.cell.visible:
                    if new_actor.cell.contained_buildings[self.actor_label_type] == 'none': #if no building built, show resource: name
                        self.message_start = 'Resource: '
                        self.set_label(self.message_start + new_actor.cell.resource)
                    else:
                        self.message_start = 'Resource building: '
                        self.set_label(self.message_start + new_actor.cell.contained_buildings[self.actor_label_type].name)
                else:
                    self.set_label(self.message_start + 'unknown')
            elif self.actor_label_type == 'movement':
                self.set_label(self.message_start + str(new_actor.movement_points) + '/' + str(new_actor.max_movement_points))
            elif self.actor_label_type == 'building worker':
                if self.list_type == 'resource building':
                    if not new_actor.cell.contained_buildings['resource'] == 'none':
                        self.attached_list = new_actor.cell.contained_buildings['resource'].contained_workers
                        if len(self.attached_list) > self.list_index:
                            self.set_label(self.message_start + self.attached_list[self.list_index].name)
                    else:
                        self.attached_list = []
        else:
            self.set_label(self.message_start + 'n/a')

class list_item_label(actor_match_label): #attached to a certain list based on list type, has index of list that it shows
    def __init__(self, coordinates, minimum_width, height, modes, image_id, actor_label_type, list_index, list_type, global_manager):
        self.list_index = list_index
        self.list_type = list_type
        self.attached_list = []
        super().__init__(coordinates, minimum_width, height, modes, image_id, actor_label_type, global_manager)

    def calibrate(self, new_actor):
        self.attached_list = []
        super().calibrate(new_actor)

    def can_show(self):
        if len(self.attached_list) > self.list_index:
            return(super().can_show())
        return(False)

class building_workers_label(actor_match_label):
    def __init__(self, coordinates, minimum_width, height, modes, image_id, building_type, global_manager):
        self.remove_worker_button = 'none'
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'building workers', global_manager)
        self.building_type = building_type
        self.attached_building = 'none'
        self.remove_worker_button = label_button((self.x, self.y), self.height, self.height, 'remove worker', self.modes, 'misc/remove_worker_button.png', self, global_manager)
        self.showing = False

    def calibrate(self, new_actor):
        self.actor = new_actor
        self.showing = False
        if not new_actor == 'none':
            self.attached_building = new_actor.cell.contained_buildings[self.building_type]
            if not self.attached_building == 'none':
                self.set_label("Workers: " + str(len(self.attached_building.contained_workers)) + '/' + str(self.attached_building.worker_capacity))
                self.showing = True

    def set_label(self, new_message):
        super().set_label(new_message)
        if not self.remove_worker_button == 'none':
            self.remove_worker_button.x = self.x + self.width + 5 #to do: make a function to move all elements of a button
            self.remove_worker_button.Rect.x = self.remove_worker_button.x
            self.remove_worker_button.outline.x = self.remove_worker_button.x - self.remove_worker_button.outline_width

    def can_show(self):
        if self.showing:
            return(super().can_show())
        else:
            return(False)

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
        self.actor = 'none'
        self.current_commodity = 'none'
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'commodity', global_manager)
        self.showing_commodity = False
        self.commodity_index = commodity_index
        self.commodity_image = label_image((self.x - self.height, self.y), self.height, self.height, self.modes, self, self.global_manager) #self, coordinates, width, height, modes, attached_label, global_manager
        self.attached_buttons = []
        if matched_actor_type == 'mob':
            self.attached_buttons.append(label_button((self.x, self.y), self.height, self.height, 'drop commodity', self.modes, 'misc/drop_commodity_button.png', self, global_manager))
        elif matched_actor_type == 'tile':
            self.attached_buttons.append(label_button((self.x, self.y), self.height, self.height, 'pick up commodity', self.modes, 'misc/pick_up_commodity_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + (self.height + 5), self.y), self.height, self.height, 'sell commodity', ['europe'], 'misc/commodity_sell_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + ((self.height + 5) * 2), self.y), self.height, self.height, 'sell all commodity', ['europe'], 'misc/commodity_sell_all_button.png', self, global_manager))

    def set_label(self, new_message):
        super().set_label(new_message)
        if not self.actor == 'none': #self.setup_complete: #if not new_message == 'n/a':
            commodity_list = self.actor.get_held_commodities()
            if len(commodity_list) > self.commodity_index:
                commodity = commodity_list[self.commodity_index]
                for i in range(len(self.attached_buttons)):
                    current_button = self.attached_buttons[i]
                    current_button.x = self.x + self.width + 5 + ((self.height + 5) * i) #to do: make a function to move all elements of a button
                    current_button.Rect.x = current_button.x
                    current_button.outline.x = current_button.x - current_button.outline_width
                self.commodity_image.set_image('scenery/resources/' + commodity + '.png')
            

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
                self.current_commodity = commodity
                self.set_label(commodity + ': ' + str(new_actor.get_inventory(commodity))) #format - commodity_name: how_many
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
