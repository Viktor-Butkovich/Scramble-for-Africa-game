from .mobs import mob
from .tiles import veteran_icon
from . import workers
from . import actor_utility
from . import utility
from . import notification_tools
from . import text_tools
from . import dice_utility
from . import dice
from . import scaling


class officer(mob):
    '''
    Mob that is considered an officer and can join groups and become a veteran
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, officer_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this mob's images can appear
            string image_id: File path to the image used by this object
            string name: This mob's name
            string list modes: Game modes during which this mob's images can appear
            string officer_type: Type of officer that this is, like 'explorer' or 'engineer'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('officer_list').append(self)
        self.veteran = False
        self.veteran_icons = []
        self.is_officer = True
        self.officer_type = officer_type
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_officer changing

    def promote(self):
        self.veteran = True
        self.set_name("Veteran " + self.name.lower()) # Expedition to Veteran expedition
        for current_grid in self.grids:
            if current_grid == self.global_manager.get('minimap_grid'):
                veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
            elif current_grid == self.global_manager.get('europe_grid'):
                veteran_icon_x, veteran_icon_y = (0, 0)
            else:
                veteran_icon_x, veteran_icon_y = (self.x, self.y)
            self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic', 'europe'], False, self, self.global_manager))
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates actor info display with veteran icon

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Description:
            Links this officer to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when an officer that was previously attached to another actor becomes independent and
                visible, like when an explorer leaves an expedition. Also moves veteran icons to follow this officer
        Input:
            grid new_grid: grid that this officer is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        '''
        if self.veteran and not self.in_group: #if (not (self.in_group or self.in_vehicle)) and self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
        self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if self.veteran and not self.in_group: #if (not (self.in_group or self.in_vehicle)) and self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                elif current_grid == self.global_manager.get('europe_grid'):
                    veteran_icon_x, veteran_icon_y = (0, 0)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self, self.global_manager))

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this officer's tooltip can be shown. Along with the superclass' requirements, officer tooltips can not be shown when attached to another actor, such as when part of a group
        Input:
            None
        Output:
            None
        '''
        if not (self.in_group or self.in_vehicle):
            return(super().can_show_tooltip())
        else:
            return(False)

    def join_group(self):
        '''
        Description:
            Hides this officer when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            None
        Output:
            None
        '''
        self.in_group = True
        self.selected = False
        self.hide_images()

    def leave_group(self, group):
        '''
        Description:
            Reveals this officer when its group is disbanded, allowing it to be directly interacted with. Also selects this officer, meaning that the officer will be selected rather than the worker when a group is disbanded
        Input:
            group group: group from which this officer is leaving
        Output:
            None
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()
        self.select()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #calibrate info display to officer's tile upon disbanding

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
        self.global_manager.set('officer_list', utility.remove_from_list(self.global_manager.get('officer_list'), self))
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.remove()

    def die(self):
        self.remove()

class head_missionary(officer):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, 'head missionary', global_manager)
        self.current_campaign_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1

    def start_religious_campaign(self): #called when player presses head missionary's start religious campaign button in Europe
        self.current_campaign_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        #determine modifier here
        self.current_min_success -= self.current_campaign_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_campaign_modifier
        choice_info_dict = {'head missionary': self,'type': 'start religious campaign'}
        self.global_manager.set('ongoing_religious_campaign', True)
        message = "Are you sure you want to start a religious campaign? /n /n"
        notification_tools.display_choice_notification(message, ['start religious campaign', 'stop religious campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager+

    def religious_campaign(self): #called when start religious campaign clicked in choice notification
        text_tools.print_to_screen('placeholder religious campaign', self.global_manager)
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        text = ""
        text += "The head missionary tries to convince church volunteers to join your cause. /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'religious_campaign', self.global_manager)
        else:
            text += ("The veteran head missionary can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'religious_campaign', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            first_roll_list = dice_utility.roll_to_list(6, "Religous campaign roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_religious_campaign_die((die_x, 500), first_roll_list[0])
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_religious_campaign_die((die_x, 380), second_roll_list[0])
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i == 6:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Religious campaign roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_religious_campaign_die((die_x, 440), roll_list[0])
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'religious_campaign', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "You get a unit of church volunteers placeholder message /n"
        else:
            text += "You did not get a unit of church volunteers placeholder message /n"
        if roll_result <= self.current_max_crit_fail:
            text += "/nThe head missionary gives up placeholder message. /n" #actual 'death' occurs when religious campaign completes

        if (not self.veteran) and roll_result == 6:
            self.just_promoted = True
            text += "The head missionary did well enough to become a veteran message /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_religious_campaign', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('religious_campaign_result', [self, roll_result])

    def complete_religious_campaign(self):
        roll_result = self.global_manager.get('religious_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            new_church_volunteers = workers.church_volunteers((0, 0), [self.global_manager.get('europe_grid')], 'mobs/church volunteers/default.png', 'Church volunteers', ['strategic', 'europe'], self.global_manager)
            if roll_result == 6 and not self.veteran:
                self.promote()
            self.select()
            for current_image in self.images: #move mob to front of each stack it is in - also used in button.same_tile_icon.on_click(), make this a function of all mobs to move to front of tile
                if not current_image.current_cell == 'none':
                    while not self == current_image.current_cell.contained_mobs[0]:
                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        elif roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_religious_campaign', False)

    def display_religious_campaign_die(self, coordinates, result):
        '''
        Description:
            Creates a die object with preset colors and possible roll outcomes and the inputted location and predetermined roll result to use for exploration rolls
        Input:
            int tuple coordinates: Two values representing x and y pixel coordinates for the bottom left corner of the die
            int result: Predetermined result that the die will end on after rolling
        Output:
            None
        '''
        result_outcome_dict = {'min_success': self.current_min_success, 'min_crit_success': 6, 'max_crit_fail': self.current_max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)
