#Contains functionality for actor display images

from ..images import free_image

class actor_display_free_image(free_image):
    '''
    Free image that changes its appearance to match selected mobs or tiles
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            string actor_image_type: Type of actor whose appearance will be copied by this image
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_image_type = actor_image_type
        self.actor = 'none'
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def calibrate(self, new_actor):
        '''
        Description:
            Sets this image to match the inputted object's appearance to show in the actor info display
        Input:
            string/actor new_actor: If this equals 'none', hides this image. Otherwise, causes this image will match this input's appearance
        Output:
            None
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            if self.actor_image_type in ['minister_default', 'country_default']:
                self.set_image(new_actor.image_id)
            elif self.actor_image_type == 'possible_artifact_location':
                if (not self.global_manager.get('current_lore_mission') == 'none') and self.global_manager.get('current_lore_mission').has_revealed_possible_artifact_location(new_actor.x, new_actor.y):
                    self.set_image('misc/possible_artifact_location_icon.png') #only show icon if revealed location in displayed tile
                else:
                    #self.set_image('misc/empty.png')
                    self.set_image(['misc/mob_background.png', 'misc/pmob_outline.png'])
            else:
                image_id_list = []
                default_image_key = 'default'

                if new_actor.actor_type == 'mob':
                    nothing = 0
                elif not new_actor.cell.visible:
                    default_image_key = 'hidden'
                if isinstance(new_actor.images[0].image_id, str): #if id is string image path
                    image_id_list.append(new_actor.image_dict[default_image_key])
                else: #if id is list of strings for image bundle
                    image_id_list += new_actor.get_image_id_list() #images[0].image.to_list()
                if new_actor.actor_type == 'mob':
                    if new_actor.is_pmob:
                        image_id_list.append({'image_id': 'misc/mob_background.png', 'level': -10})
                        image_id_list.append('misc/pmob_outline.png')
                    else:
                        image_id_list.append('misc/npmob_outline.png')
                else:
                    image_id_list.append('misc/tile_outline.png')
                self.set_image(image_id_list)
        else:
            self.set_image(['misc/mob_background.png', 'misc/pmob_outline.png'])#self.set_image('misc/empty.png')

    #def can_show(self):
    #    '''
    #    Description:
    #        Returns whether this image should be drawn
    #    Input:
    #        None
    #    Output:
    #        boolean: False if there is no actor in the info display, otherwise returns same value as superclass
    #    '''
    #    if self.actor == 'none':
    #        return(False)
    #    else:
    #        return(super().can_show())

class actor_display_infrastructure_connection_image(actor_display_free_image):
    '''
    Image appearing on tile info display to show the road/railroad connections of the displayed tile
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, direction, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            string actor_image_type: Type of actor whose appearance will be copied by this image
            string direction: 'up', 'down', 'left', or 'right', side of tile that this image points to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.direction = direction
        super().__init__(coordinates, width, height, modes, actor_image_type, global_manager)

class mob_background_image(free_image):
    '''
    Image appearing behind the displayed actor in the actor info display
    '''
    def __init__(self, image_id, coordinates, width, height, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(image_id, coordinates, width, height, modes, global_manager)
        self.actor = 'none'

    def calibrate(self, new_actor):
        '''
        Description:
            Updates which actor is in front of this image
        Input:
            string/actor new_actor: The displayed actor that goes in front of this image. If this equals 'none', there is no actor in front of it
        Output:
            None
        '''
        self.actor = new_actor
        self.update_image_bundle()

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if there is no actor in the info display, otherwise returns same value as superclass
        '''
        if self.actor == 'none':
            return(False)
        if self.image_id == 'misc/pmob_background.png' and not self.actor.is_pmob:
            return(False)
        if self.image_id == 'misc/npmob_background.png' and not self.actor.is_npmob:
            return(False)
        else:
            return(super().can_show())

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to that of the actor in front of it
        Input:
            None
        Output:
            None
        '''
        if not self.actor == 'none':
            tooltip_text = self.actor.tooltip_text
            self.set_tooltip(tooltip_text)
        else:
            super().update_tooltip()

class minister_background_image(mob_background_image):
    '''
    Image that appears behind a minister and changes to match their current office
    '''
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
        image_id_list = []
        if not self.actor == 'none':
            if self.actor.current_position == 'none':
                image_id_list.append('misc/mob_background.png')
            else:
                image_id_list.append('ministers/icons/' + self.global_manager.get('minister_type_dict')[self.actor.current_position] + '.png')
            if self.actor.just_removed and self.actor.current_position == 'none':
                image_id_list.append({'image_id': 'misc/warning_icon.png', 'x_offset': 0.75})
        return(image_id_list)

    #def calibrate(self, new_minister):
    #    '''
    #    Description:
    #        Updates which minister is in front of this image and changes its appearance to match the minister's current office
    #    Input:
    #        string/minister new_minister: The displayed minister that goes in front of this image. If this equals 'none', there is no minister in front of it
    #    Output:
    #        None
    #    '''
    #    super().calibrate(new_minister)
    #    if not new_minister == 'none':
    #        if new_minister.current_position == 'none':
    #            self.set_image('misc/mob_background.png')
    #        else:
    #            self.set_image('ministers/icons/' + self.global_manager.get('minister_type_dict')[new_minister.current_position] + '.png')
    #    self.update_image_bundle()

class label_image(free_image):
    '''
    Free image that is attached to a label and will only show when the label is showing
    '''
    def __init__(self, coordinates, width, height, modes, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            label attached_label: The label that this image is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_label = attached_label
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if this image's label is not showing, otherwise returns same value as superclass
        '''
        if self.attached_label.can_show():
            return(super().can_show())
        else:
            return(False)
