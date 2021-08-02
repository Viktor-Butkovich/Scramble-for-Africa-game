from .images import free_image
from .labels import label
from .buttons import button
from . import scaling

class actor_match_free_image(free_image): #free image that matches any selected mobs
    def __init__(self, coordinates, width, height, modes, actor_image_type, global_manager):
        self.actor_image_type = actor_image_type
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)
        #self.global_manager.get('mob_info_display_list').append(self) #include mob labels and mob free images

    def calibrate(self, new_actor):
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
    def __init__(self, coordinates, width, height, modes, attached_label, global_manager):
        self.attached_label = attached_label
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def can_show(self):
        if self.attached_label.can_show():
            return(super().can_show())
        else:
            return(False)

class label_button(button):
    def __init__(self, coordinates, width, height, button_type, modes, image_id, attached_label, global_manager):
        self.attached_label = attached_label
        super().__init__(coordinates, width, height, 'blue', button_type, 'none', modes, image_id, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def can_show(self):
        if self.attached_label.can_show():
            return(super().can_show())
        else:
            return(False)

class actor_match_label(label):
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image_id, actor_label_type, global_manager):
        message = 'default'
        super().__init__(coordinates, ideal_width, minimum_height, modes, image_id, message, global_manager)
        #self.global_manager.get('mob_info_display_list').append(self) #include mob labels and mob free images
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
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image_id, commodity_index, matched_actor_type, global_manager):
        super().__init__(coordinates, ideal_width, minimum_height, modes, image_id, 'commodity', global_manager)
        self.showing_commodity = False
        self.commodity_index = commodity_index
        #self.matched_actor_type = matched_actor_type
        self.commodity_image = label_image((self.x - self.height, self.y), self.height, self.height, self.modes, self, self.global_manager) #self, coordinates, width, height, modes, attached_label, global_manager   
        if matched_actor_type == 'mob':
            self.commodity_button = label_button((self.x  + scaling.scale_width(175, self.global_manager), self.y), self.height, self.height, 'drop commodity', self.modes, 'misc/drop_commodity_button.png', self, global_manager)
        elif matched_actor_type == 'tile':
            self.commodity_button = label_button((self.x + scaling.scale_width(175, self.global_manager), self.y), self.height, self.height, 'pick up commodity', self.modes, 'misc/pick_up_commodity_button.png', self, global_manager)

    def calibrate(self, new_actor):
        self.actor = new_actor
        if not new_actor == 'none':
            commodity_list = new_actor.get_held_commodities()
            if len(commodity_list) - 1 >= self.commodity_index: #if index in commodity list
                self.showing_commodity = True
                commodity = commodity_list[self.commodity_index]
                self.set_label(commodity + ': ' + str(new_actor.get_inventory(commodity))) #commodity_name: how_many
                self.commodity_image.set_image('scenery/resources/' + commodity + '.png')
            else:
                self.showing_commodity = False
                self.set_label('n/a')
        else:
            self.showing_commodity = False
            self.set_label('n/a')

    def can_show(self):
        if not self.showing_commodity:
            return(False)
        else:
            return(super().can_show())
