from .mobs import mob
from .tiles import veteran_icon
from . import actor_utility
from . import utility
from . import notification_tools
from . import text_tools


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

class head_missionary(officer):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, 'head missionary', global_manager)

    def start_religious_campaign(self): #called when player presses head missionary's start religious campaign button in Europe
        choice_info_dict = {'head missionary': self,'type': 'start religious campaign'}
        self.global_manager.set('ongoing_religious_campaign', True)
        message = "Are you sure you want to start a religious campaign? /n /n"
        notification_tools.display_choice_notification(message, ['start religious campaign', 'stop religious campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager+

    def religious_campaign(self): #called when start religious campaign clicked in choice notification
        text_tools.print_to_screen('placeholder religious campaign', self.global_manager)
        self.global_manager.set('ongoing_religious_campaign', False)
