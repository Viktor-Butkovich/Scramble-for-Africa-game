#Contains functionality for buttons

import pygame
import time
from . import images
from . import text_tools
from . import scaling
from . import main_loop_tools
from . import actor_utility
from . import utility
from . import turn_management_tools
from . import market_tools
from . import notification_tools
from . import game_transitions
from . import minister_utility
from . import trial_utility
from . import interface_elements

class button(interface_elements.interface_element):
    '''
    An object does something when clicked or when the corresponding key is pressed
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.outline_width = 2
        self.outline = pygame.Rect(0, 0, input_dict['width'] + (2 * self.outline_width), input_dict['height'] + (self.outline_width * 2)) 
        #outline is Pygame Rect object that appears around a button when pressed
        super().__init__(input_dict, global_manager)
        self.has_released = True
        self.button_type = input_dict['button_type']
        self.global_manager.get('button_list').append(self)
        if not 'keybind_id' in input_dict:
            input_dict['keybind_id'] = 'none'
        self.keybind_id = input_dict['keybind_id']
        self.has_keybind = self.keybind_id != 'none'
        if self.has_keybind:
            self.set_keybind(self.keybind_id)
        self.image = images.button_image(self, self.width, self.height, input_dict['image_id'], self.global_manager)
        #if not 'color' in input_dict:
        #    input_dict['color'] = 'blue'
        if 'color' in input_dict:
            self.color = self.global_manager.get('color_dict')[input_dict['color']]
        self.showing_outline = False
        self.showing_background = True
        self.button_type = input_dict['button_type']
        self.tooltip_text = []
        self.update_tooltip()
        self.confirming = False
        self.being_pressed = False
        self.in_notification = False #used to prioritize notification buttons in drawing and tooltips

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
        self.outline.y = self.Rect.y - self.outline_width
        self.outline.x = self.Rect.x - self.outline_width

    def set_y(self, attached_label): #called by actor display labels to move to their y position
        '''
        Description:
            Sets this button's y position to be at the same height as the inputted label
        Input:
            actor_display_label attached_label: Label to match this button's y position with
        Output:
            None
        '''
        self.set_origin(self.x, attached_label.y)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        '''
        if self.button_type in ['move up', 'move down', 'move left', 'move right']:
            direction = 'none'
            x_change = 0
            y_change = 0
            if self.button_type == 'move up':
                direction = 'north'
                non_cardinal_direction = 'up'
                y_change = 1
            elif self.button_type == 'move down':
                direction = 'south'
                non_cardinal_direction = 'down'
                y_change = -1
            elif self.button_type == 'move left':
                direction = 'west'
                non_cardinal_direction = 'left'
                x_change = -1
            elif self.button_type == 'move right':
                direction = 'east'
                non_cardinal_direction = 'right'
                x_change = 1
                
            tooltip_text = []
                           
            selected_list = actor_utility.get_selected_list(self.global_manager)
            if len(selected_list) > 0:
                current_mob = selected_list[0]
                message = ''
                movement_cost = current_mob.get_movement_cost(x_change, y_change)
                local_cell = current_mob.images[0].current_cell
                adjacent_cell = local_cell.adjacent_cells[non_cardinal_direction]
                local_infrastructure = local_cell.get_intact_building('infrastructure')
                
                if not adjacent_cell == 'none':
                    passed = False
                    if (current_mob.can_walk and not adjacent_cell.terrain == 'water') or local_cell.has_walking_connection(adjacent_cell): #if walking unit moving onto land or along bridge
                        passed = True
                    elif (current_mob.can_swim and adjacent_cell.terrain == 'water' and ((current_mob.can_swim_river and adjacent_cell.y > 0) or (current_mob.can_swim_ocean and adjacent_cell.y == 0)) or adjacent_cell.has_vehicle('ship')): #if swimming unit going to correct kind of water or embarking ship
                        passed = True
                    elif (current_mob.can_walk and adjacent_cell.terrain == 'water') and adjacent_cell.y > 0: #if land unit entering river for maximum movement points
                        passed = True
                        if current_mob.is_battalion and not adjacent_cell.get_best_combatant('npmob') == 'none': #if battalion attacking unit in water:
                            movement_cost = 1

                    if passed:
                        if adjacent_cell.visible:
                            tooltip_text.append('Press to move to the ' + direction)
                            adjacent_infrastructure = adjacent_cell.get_intact_building('infrastructure')
                            connecting_roads = False
                            if (current_mob.is_battalion and not adjacent_cell.get_best_combatant('npmob') == 'none') or (current_mob.is_safari and not adjacent_cell.get_best_combatant('npmob', 'beast') == 'none'):
                                final_movement_cost = current_mob.get_movement_cost(x_change, y_change, True)
                                message = 'Attacking an enemy unit costs 5 money and requires only 1 movement point, but staying in the enemy\'s tile afterward would require the usual movement'
                                tooltip_text.append(message)
                                message = 'Staying afterward would cost ' + str(final_movement_cost - 1) + ' more movement point' + utility.generate_plural(movement_cost) + ' because the adjacent tile has ' + adjacent_cell.terrain + ' terrain '
                                if local_cell.has_walking_connection(adjacent_cell):
                                    if (not local_infrastructure == 'none') and (not adjacent_infrastructure == 'none'): #if both have infrastructure
                                        connecting_roads = True
                                        message += 'and connecting roads'
                                    elif local_infrastructure == 'none' and not adjacent_infrastructure == 'none': #if local has no infrastructure but adjacent does
                                        message += 'and no connecting roads'
                                    elif not local_infrastructure == 'none': #if local has infrastructure but not adjacent
                                        message += 'and no connecting roads'
                                    else: 
                                        message += 'and no connecting roads'
                        
                            else:
                                if current_mob.is_vehicle and current_mob.vehicle_type == 'train':
                                    if (not adjacent_infrastructure == 'none') and adjacent_infrastructure.is_railroad and (not local_infrastructure == 'none') and local_infrastructure.is_railroad and local_cell.has_walking_connection(adjacent_cell):
                                        message = 'Costs ' + str(movement_cost) + ' movement point' + utility.generate_plural(movement_cost) + ' because the adjacent tile has connecting railroads'
                                    else:
                                        message = 'Not possible because the adjacent tile does not have connecting railroads'
                                    tooltip_text.append(message)
                                    tooltip_text.append('A train can only move along railroads')
                                else:
                                    message = 'Costs ' + str(movement_cost) + ' movement point' + utility.generate_plural(movement_cost) + ' because the adjacent tile has ' + adjacent_cell.terrain + ' terrain '
                                    if local_cell.has_walking_connection(adjacent_cell):
                                        if (not local_infrastructure == 'none') and (not adjacent_infrastructure == 'none'): #if both have infrastructure
                                            connecting_roads = True
                                            message += 'and connecting roads'
                                        elif local_infrastructure == 'none' and not adjacent_infrastructure == 'none': #if local has no infrastructure but adjacent does
                                            message += 'and no connecting roads'
                                        elif not local_infrastructure == 'none': #if local has infrastructure but not adjacent
                                            message += 'and no connecting roads'# + local_infrastructure.infrastructure_type
                                        else: 
                                            message += 'and no connecting roads'

                                    tooltip_text.append(message)
                                    if (current_mob.can_walk and adjacent_cell.terrain == 'water' and (not current_mob.can_swim_river)) and adjacent_cell.y > 0 and not local_cell.has_walking_connection(adjacent_cell):
                                        tooltip_text.append('Moving into a river tile costs an entire turn of movement points for units without canoes')
                                    else:
                                        tooltip_text.append('Moving into a ' + adjacent_cell.terrain + ' tile costs ' + str(self.global_manager.get('terrain_movement_cost_dict')[adjacent_cell.terrain]) + ' movement points')
                            if (not current_mob.is_vehicle) and current_mob.images[0].current_cell.terrain == 'water' and current_mob.images[0].current_cell.has_vehicle('ship'):
                                if (current_mob.images[0].current_cell.y == 0 and not (current_mob.can_swim and current_mob.can_swim_ocean)) or (current_mob.images[0].current_cell.y > 0 and not (current_mob.can_swim and current_mob.can_swim_river)): #if could not naturally move into current tile, must be from vehicle
                                    tooltip_text.append('Moving from a steamship or steamboat in the water after disembarking requires all remaining movement points, at least the usual amount')
                            if connecting_roads:
                                tooltip_text.append('Moving between 2 tiles with roads or railroads costs half as many movement points.')
                        elif current_mob.can_explore:
                            tooltip_text.append('Press to attempt to explore in the ' + direction)
                            tooltip_text.append('Attempting to explore would cost ' + str(self.global_manager.get('action_prices')['exploration']) + ' money and all remaining movement points, at least 1')
                        else:
                            tooltip_text.append('This unit can not currently move to the ' + direction)
                            tooltip_text.append('This unit can not move into unexplored areas')
                    else:
                        tooltip_text.append('This unit can not currently move to the ' + direction)

                else:
                    tooltip_text.append('Moving in this direction would move off of the map')
                if current_mob.can_walk and current_mob.can_swim: #1??
                    if current_mob.can_swim_river and current_mob.can_swim_ocean: #111
                        tooltip_text.append('Can move normally to land and water')
                    elif current_mob.can_swim_river and not current_mob.can_swim_ocean: #110
                        tooltip_text.append('Can move normally to land and rivers but not ocean')
                    else: #101
                        tooltip_text.append('Can move normally to land and ocean but not rivers')
                        
                elif current_mob.can_walk and not current_mob.can_swim: #100
                    tooltip_text.append('Can move normally to land but not water')
                    
                elif current_mob.can_swim and not current_mob.can_walk: #0??
                    if current_mob.can_swim_river and current_mob.can_swim_ocean: #011
                        tooltip_text.append('Can move normally to water but not land')
                    elif current_mob.can_swim_river and not current_mob.can_swim_ocean: #010
                        tooltip_text.append('Can move normally to rivers but not ocean or land')
                    else: #101
                        tooltip_text.append('Can move normally to ocean but not rivers or land')
                #000 is not possible
                    
                if not current_mob.can_swim:
                    if current_mob.is_battalion:
                        tooltip_text.append('However, can embark a ship, attack an enemy in a river, or spend its maximum movement and become disorganized to enter a river')
                    else:
                        tooltip_text.append('However, can embark a ship in the water by moving to it or spend its maximum movement and become disorganized to enter a river')
                    
            self.set_tooltip(tooltip_text)

        elif self.button_type == 'toggle grid lines':
            self.set_tooltip(['Press to show or hide grid lines'])

        elif self.button_type == 'toggle text box':
            self.set_tooltip(['Press to show or hide text box'])

        elif self.button_type == 'expand text box':
            self.set_tooltip(['Press to change the size of the text box'])

        elif self.button_type == 'execute movement routes':
            self.set_tooltip(['Press to move all valid units along their designated movement routes'])

        elif self.button_type == 'instructions':
            self.set_tooltip(['Shows the game\'s instructions',
                              'Press this when instructions are not opened to open them',
                              'Press this when instructions are opened to close them'])

        elif self.button_type == 'merge':
            if (not self.attached_label.actor == 'none') and self.attached_label.actor.is_officer and self.attached_label.actor.officer_type == 'evangelist':
                self.set_tooltip(['Merges this evangelist with church volunteers in the same tile to form a group of missionaries',
                                  'Requires that an evangelist is selected in the same tile as church volunteers'])
            else:
                self.set_tooltip(['Merges this officer with a worker in the same tile to form a group with a type based on that of the officer',
                                  'Requires that an officer is selected in the same tile as a worker'])

        elif self.button_type == 'split':
            self.set_tooltip(['Splits a group into its worker and officer'])

        elif self.button_type == 'crew': #clicked on vehicle side
            self.set_tooltip(['Merges this ' + self.vehicle_type + ' with a worker in the same tile to form a crewed ' + self.vehicle_type,
                              'Requires that an uncrewed ' + self.vehicle_type + ' is selected in the same tile as a worker'])

        elif self.button_type == 'worker to crew': #clicked on worker side
            self.set_tooltip(['Merges this worker with a ' + self.vehicle_type + ' in the same tile to form a crewed ' + self.vehicle_type,
                              'Requires that a worker is selected in the same tile as an uncrewed ' + self.vehicle_type])

        elif self.button_type == 'uncrew':
            self.set_tooltip(['Orders this ' + self.vehicle_type + '\'s crew to abandon the ' + self.vehicle_type + '.'])

        elif self.button_type == 'embark':
            self.set_tooltip(['Orders this unit to embark a ' + self.vehicle_type + ' in the same tile',
                              'Requires that a unit is selected in the same tile as a crewed ' + self.vehicle_type])

        elif self.button_type == 'disembark':
            if self.vehicle_type == 'train':
                self.set_tooltip(['Orders this unit to disembark the ' + self.vehicle_type])
            else:
                self.set_tooltip(['Orders this unit to disembark the ' + self.vehicle_type,
                                  'Disembarking a unit outside of a port renders it disorganized until the next turn, decreasing its combat effectiveness'])

        elif self.button_type == 'embark all':
            self.set_tooltip(['Orders this ' + self.vehicle_type + ' to take all non-vehicle units in this tile as passengers'])

        elif self.button_type == 'disembark all':
            if self.vehicle_type == 'train':
                self.set_tooltip(['Orders this ' + self.vehicle_type + ' to disembark all of its passengers'])
            else:
                self.set_tooltip(['Orders this ' + self.vehicle_type + ' to disembark all of its passengers',
                                  'Disembarking a unit outside of a port renders it disorganized until the next turn, decreasing its combat effectiveness'])

        elif self.button_type == 'pick up commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(['Transfers 1 unit of ' + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + ' to the currently displayed unit in this tile'])
            else:
                self.set_tooltip(['none'])
                
        elif self.button_type == 'pick up all commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(['Transfers all units of ' + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + ' to the currently displayed unit in this tile'])
            else:
                self.set_tooltip(['none'])
                
        elif self.button_type == 'drop commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(['Transfers 1 unit of ' + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + ' into this unit\'s tile'])
            else:
                self.set_tooltip(['none'])
                
        elif self.button_type == 'drop all commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(['Transfers all units of ' + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + ' into this unit\'s tile'])
            else:
                self.set_tooltip(['none'])
                
        elif self.button_type == 'remove worker':
            if not self.attached_label.attached_building == 'none':
                self.set_tooltip(['Detaches this work crew from the ' + self.attached_label.attached_building.name])
            else:
                self.set_tooltip(['none'])
                
        elif self.button_type == 'start end turn': #different from end turn from choice buttons - start end turn brings up a choice notification
            self.set_tooltip(['Ends the current turn'])
            
        elif self.button_type == 'sell commodity' or self.button_type == 'sell all commodity':
            if not self.attached_label.actor == 'none':
                commodity_list = self.attached_label.actor.get_held_commodities()
                commodity = commodity_list[self.attached_label.commodity_index]
                sell_price = self.global_manager.get('commodity_prices')[commodity]
                if self.button_type == 'sell commodity':
                    self.set_tooltip(['Orders your ' + self.global_manager.get('type_minister_dict')['trade'] + ' to sell 1 unit of ' + commodity + ' for about ' + str(sell_price) + ' money at the end of the turn',
                                      'The amount each commodity was sold for is reported at the beginning of your next turn',
                                      'Each unit of ' + commodity + ' sold has a chance of reducing its sale price'])
                else:
                    num_present = self.attached_label.actor.get_inventory(commodity)
                    self.set_tooltip(['Orders your ' + self.global_manager.get('type_minister_dict')['trade'] + ' to sell your entire stockpile of ' + commodity + ' for about ' + str(sell_price) + ' money each at the end of the turn, ' +
                                          'for a total of about ' + str(sell_price * num_present) + ' money',
                                      'The amount each commodity was sold for is reported at the beginning of your next turn',
                                      'Each unit of ' + commodity + ' sold has a chance of reducing its sale price'])
            else:
                self.set_tooltip(['none'])
                
        elif self.button_type == 'switch theatre':
           self.set_tooltip(['Moves this steamship across the ocean to another theatre at the end of the turn',
                             'Once clicked, the mouse pointer can be used to click on the destination',
                             'The destination, once chosen, will having a flashing yellow outline',
                             'Requires that this steamship is able to move'])
           
        elif self.button_type == 'cycle passengers':
            tooltip_text = ['Cycles through this ' + self.vehicle_type + '\'s passengers']
            tooltip_text.append('Passengers: ' )
            if self.can_show():
                for current_passenger in self.attached_label.actor.contained_mobs:
                    tooltip_text.append('    ' + current_passenger.name)
            self.set_tooltip(tooltip_text)
            
        elif self.button_type == 'cycle work crews':
            tooltip_text = ['Cycles through this  building\'s work crews']
            tooltip_text.append('Work crews: ' )
            if self.can_show():
                for current_work_crew in self.attached_label.actor.cell.get_building('resource').contained_work_crews:
                    tooltip_text.append('    ' + current_work_crew.name)
            self.set_tooltip(tooltip_text)
            
        elif self.button_type == 'cycle tile mobs':
            tooltip_text = ['Cycles through this tile\'s units']
            tooltip_text.append('Units: ' )
            if self.can_show():
                for current_mob in self.global_manager.get('displayed_tile').cell.contained_mobs:
                    tooltip_text.append('    ' + current_mob.name)
            self.set_tooltip(tooltip_text)
            
        elif self.button_type == 'build train':
            actor_utility.update_recruitment_descriptions(self.global_manager, 'train')
            cost = actor_utility.get_building_cost(self.global_manager, self.global_manager.get('displayed_mob'), 'train')
            self.set_tooltip(['Orders parts for and attempts to assemble a train in this unit\'s tile for ' + str(cost) + ' money',
                              'Can only be assembled on a train station',
                              'Costs all remaining movement points, at least 1',
                              'Unlike buildings, the cost of vehicle assembly is not impacted by local terrain'])
            
        elif self.button_type == 'build steamboat':
            actor_utility.update_recruitment_descriptions(self.global_manager, 'steamboat')
            cost = actor_utility.get_building_cost(self.global_manager, self.global_manager.get('displayed_mob'), 'train')
            self.set_tooltip(['Orders parts for and attempts to assemble a steamboat in this unit\'s tile for ' + str(cost) + ' money',
                              'Can only be assembled on a port',
                              'Costs all remaining movement points, at least 1',
                              'Unlike buildings, the cost of vehicle assembly is not impacted by local terrain'])
            
        elif self.button_type == 'cycle units':
            tooltip_text = ['Selects the next unit in the turn order']
            turn_queue = self.global_manager.get('player_turn_queue')
            if len(turn_queue) > 0:
                for current_pmob in turn_queue:
                    tooltip_text.append('    ' + utility.capitalize(current_pmob.name))
            self.set_tooltip(tooltip_text)
                   
        elif self.button_type == 'trade':
            self.set_tooltip(['Attempts to trade with natives, paying consumer goods for random commodities',
                              'Can only be done in a village', 'The number of possible trades per turn depends on the village\'s population and aggressiveness',
                              'Each trade spends a unit of consumer goods for a chance of a random commodity',
                              'Regardless of a trade\'s success, the lure of consumer goods has a chance of convincing natives to become available workers',
                              'Has higher success chance and lower risk when a trading post is present',
                              'Costs all remaining movement points, at least 1'])

        elif self.button_type == 'capture slaves':
            self.set_tooltip(['Attempts to capture villagers as slaves for ' + str(self.global_manager.get('action_prices')['slave_capture']) + ' money',
                              'Can only be done in a village',
                              'Regardless the capture\'s success, this may increase the village\'s aggressiveness and/or decrease public opinion',
                              'Has higher success chance and lower risk when aggressiveness is low',
                              'Costs all remaining movement points, at least 1'])

        elif self.button_type == 'suppress slave trade':
            self.set_tooltip(['Attempts to suppress the slave trade for ' + str(self.global_manager.get('action_prices')['suppress_slave_trade']) + ' money',
                              'Can only be done in the slave traders tile',
                              'If successful, will decrease the strength of the slave traders and increase public opinion',
                              'Success chance and risk influenecd by the current strength of the slave traders',
                              'Costs all remaining movement points, at least 1'])

        elif self.button_type == 'religious campaign':
            self.set_tooltip(['Attempts to campaign for church volunteers for ' + str(self.global_manager.get('action_prices')['religious_campaign']) + ' money',
                              'Can only be done in Europe',
                              'If successful, recruits a free unit of church volunteers that can join with an evangelist to form a group of missionaries that can convert native villages',
                              'Costs all remaining movement points, at least 1',
                              'Each religious campaign attempted doubles the cost of other religious campaigns in the same turn'])

        elif self.button_type == 'public relations campaign':
            self.set_tooltip(['Attempts to spread word of your company\'s benevolent goals and righteous deeds in Africa for ' + str(self.global_manager.get('action_prices')['public_relations_campaign']) + ' money',
                              'Can only be done in Europe', 'If successful, increases your company\'s public opinion', 'Costs all remaining movement points, at least 1',
                              'Each public relations campaign attempted doubles the cost of other public relations campaigns in the same turn'])

        elif self.button_type == 'advertising campaign':
            self.set_tooltip(['Attempts to advertise a chosen commodity and increase its price for for ' + str(self.global_manager.get('action_prices')['advertising_campaign']) + ' money',
                              'Can only be done in Europe',
                              'If successful, increases the price of a chosen commodity while randomly decreasing the price of another',
                              'Costs all remaining movement points, at least 1',
                              'Each advertising campaign attempted doubles the cost of other advertising campaigns in the same turn'])

        elif self.button_type == 'take loan':
            self.set_tooltip(['Attempts to find a 100 money loan offer with a favorable interest rate for ' + str(self.global_manager.get('action_prices')['loan_search']) + ' money',
                              'Can only be done in Europe',
                              'While automatically successful, the offered interest rate may vary',
                              'Costs all remaining movement points, at least 1',
                              'Each loan search attempted doubles the cost of other loan searches in the same turn'])

        elif self.button_type == 'track beasts':
            self.set_tooltip(['Attempts to reveal beasts in this tile and adjacent tiles',
                              'If successful, beasts in the area will be visible until the end of the turn, allowing the safari to hunt them',
                              'Can not reveal beasts in unexplored tiles',
                              'Costs 1 movement point'])

        elif self.button_type == 'convert':
            self.set_tooltip(['Attempts to convert some of this village\'s inhabitants to Christianity for ' + str(self.global_manager.get('action_prices')['conversion']) + ' money',
                              'Can only be done in a village',
                              'If successful, reduces the aggressiveness of the village and increases public opinion',
                              'Has higher success chance and lower risk when a mission is present',
                              'Costs all remaining movement points, at least 1'])

        elif self.button_type == 'rumor search':
            if self.global_manager.get('current_lore_mission') == 'none':
                intro = 'Attempts to search this village for rumors of a lore mission artifact\'s location for '
            else:
                intro = 'Attempts to search this village for rumors of the location of the ' + self.global_manager.get('current_lore_mission').name + ' for '
            self.set_tooltip([intro + str(self.global_manager.get('action_prices')['rumor_search']) + ' money',
                              'Can only be done in a village',
                              'If successful, reveals the coordinates of a possible location for the current lore mission\'s artifact',
                              'Has higher success chance and lower risk when a mission is present',
                              'Costs all remaining movement points, at least 1'])

        elif self.button_type == 'artifact search':
            if self.global_manager.get('current_lore_mission') == 'none':
                intro = 'Attempts to search for a lore mission\'s artifact at a location revealed by rumors for '
            else:
                intro = 'Attempts to search for the ' + self.global_manager.get('current_lore_mission').name + ' at a location revealed by rumors for '
            self.set_tooltip([intro + str(self.global_manager.get('action_prices')['rumor_search']) + ' money',
                              'Can only be done on a revealed possible artifact location',
                              'If successful, reveals whether this is the artifact\'s actual location, finding it and completing the lore mission if it is present',
                              'Costs all remaining movement points, at least 1'])

        elif self.button_type == 'new game':
            self.set_tooltip(['Starts a new game'])

        elif self.button_type == 'save game':
            self.set_tooltip(['Saves this game'])

        elif self.button_type == 'load game':
            self.set_tooltip(['Loads a saved game'])

        elif self.button_type == 'cycle available ministers':
            self.set_tooltip(['Cycles through the candidates available to be appointed'])

        elif self.button_type == 'appoint minister':
            self.set_tooltip(['Appoints this candidate as ' + self.appoint_type])

        elif self.button_type == 'remove minister':
            self.set_tooltip(['Removes this minister from their current office'])

        elif self.button_type == 'to trial':
            self.set_tooltip(['Opens the trial planning screen to attempt to imprison this minister for corruption',
                              'A trial has a higher success chance as more evidence of that minister\'s corruption is found',
                              'While entering this screen is free, a trial costs ' + str(self.global_manager.get('action_prices')['trial']) + ' money once started',
                              'Each trial attempted doubles the cost of other trials in the same turn'])

        elif self.button_type == 'launch trial':
            self.set_tooltip(['Tries the defending minister in an attempt to remove him from office and imprison him for corruption',
                              'Costs ' + str(self.global_manager.get('action_prices')['trial']) + ' money',
                              'Each trial attempted doubles the cost of other trials in the same turn'])

        elif self.button_type == 'fabricate evidence':
            if self.global_manager.get('current_game_mode') == 'trial':
                self.set_tooltip(['Creates a unit of fake evidence against this minister to improve the trial\'s success chance for ' + str(self.get_cost()) + ' money',
                                  'Each piece of evidence fabricated in a trial becomes increasingly expensive.',
                                  'Unlike real evidence, fabricated evidence disappears at the end of the turn and is never preserved after a failed trial'])
            else:
                self.set_tooltip(['placeholder'])

        elif self.button_type == 'bribe judge':
            self.set_tooltip(['Bribes the judge of the next trial this turn for ' + str(self.get_cost()) + ' money',
                              'While having unpredictable results, bribing the judge may swing the trial in your favor or blunt the defense\'s efforts to do the same'])

        elif self.button_type == 'free all':
            self.set_tooltip(['Frees all slaves from your company, converting them to workers'])

        elif self.button_type == 'hire village worker':
            actor_utility.update_recruitment_descriptions(self.global_manager, 'village workers')
            self.set_tooltip(['Recruits a unit of African workers for 0 money'] + self.global_manager.get('recruitment_list_descriptions')['village workers'])

        elif self.button_type == 'labor broker':
            actor_utility.update_recruitment_descriptions(self.global_manager, 'village workers')
            self.set_tooltip(['Uses a local labor broker to find and hire a unit of African workers from a nearby village',
                              'The worker\'s initial recruitment cost varies with the chosen village\'s distance and aggressiveness, and even unexplored villages may be chosen',
                              'Automatically finds the cheapest available worker'] +
                              self.global_manager.get('recruitment_list_descriptions')['village workers'] +
                             ['Can only be done at a port',
                              'Requires all movement points, at least 1'])
            
        elif self.button_type == 'hire slums worker':
            actor_utility.update_recruitment_descriptions(self.global_manager, 'slums workers')
            self.set_tooltip(['Recruits a unit of African workers for 0 money'] +
                             self.global_manager.get('recruitment_list_descriptions')['slums workers'])

        elif self.button_type == 'buy slaves':
            actor_utility.update_recruitment_descriptions(self.global_manager, 'slave workers')
            self.set_tooltip(['Recruits a unit of slave workers for ' + str(self.global_manager.get('recruitment_costs')['slave workers']) + ' money'] +
                             self.global_manager.get('recruitment_list_descriptions')['slave workers'])

        elif self.button_type == 'show previous financial report':
            self.set_tooltip(['Displays the previous turn\'s financial report'])

        elif self.button_type in ['enable sentry mode', 'disable sentry mode']:
            if self.button_type == 'enable sentry mode':
                verb = 'enable'
            elif self.button_type == 'disable sentry mode':
                verb = 'disable'
            self.set_tooltip([utility.capitalize(verb) + 's sentry mode for this unit',
                              'A unit in sentry mode is removed from the turn order and will be skipped when cycling through unmoved units'])

        elif self.button_type in ['enable automatic replacement', 'disable automatic replacement']:
            if self.button_type == 'enable automatic replacement':
                verb = 'enable'
                operator = 'not '
            elif self.button_type == 'disable automatic replacement':
                verb = 'disable'
                operator = ''
            if self.target_type == 'unit':
                target = 'unit'
            else:
                target = 'unit\'s ' + self.target_type #worker or officer
            self.set_tooltip([utility.capitalize(verb) + 's automatic replacement for this ' + target,
                              'A unit with automatic replacement will be automatically replaced if it dies from attrition',
                              'This ' + target + ' is currently set to ' + operator + 'be automatically replaced'])

        elif self.button_type == 'wake up all':
            self.set_tooltip(['Disables sentry mode for all units',
                              'A unit in sentry mode is removed from the turn order and will be skipped when cycling through unmoved units'])

        elif self.button_type == 'end unit turn':
            self.set_tooltip(['Ends this unit\'s turn, skipping it when cycling through unmoved units for the rest of the turn'])

        elif self.button_type == 'clear automatic route':
            self.set_tooltip(['Removes this unit\'s currently designated movement route'])
            
        elif self.button_type == 'draw automatic route':
            self.set_tooltip(['Starts customizing a new movement route for this unit',
                              'Add to the route by clicking on valid tiles adjacent to the current destination',
                              'The start is outlined in purple, the destination is outlined in yellow, and the path is outlined in blue',
                              'When moving along its route, a unit will pick up as many commodities as possible at the start and drop them at the destination',
                              'A unit may not be able to move along its route because of enemy units, a lack of movement points, or not having any commodities to pick up at the start'])
            
        elif self.button_type == 'follow automatic route':
            self.set_tooltip(['Moves this unit along its currently designated movement route'])
        
        elif self.button_type == 'generate crash':
            self.set_tooltip(['Generates a crash to reset the crash log'])

        elif self.button_type == 'minimize interface collection':
            if self.parent_collection.minimized:
                verb = 'Opens'
            else:
                verb = 'Minimizes'
            self.set_tooltip([verb + ' the ' + self.parent_collection.description])

        elif self.button_type == 'move interface collection':
            if self.parent_collection.move_with_mouse_config['moving']:
                verb = 'Stops moving'
            else:
                verb = 'Moves'
            self.set_tooltip([verb + ' the ' + self.parent_collection.description])

        elif self.button_type == 'reset interface collection':
            self.set_tooltip(['Resets the ' + self.parent_collection.description + ' to its original location'])

        elif self.button_type == 'tab':
            if hasattr(self.linked_element, 'description'):
                description = self.linked_element.description
            else:
                description = 'attached panel'
            self.set_tooltip(['Displays the ' + description])

        else:
            self.set_tooltip(['placeholder'])
            
    def set_keybind(self, new_keybind):
        '''
        Description:
            Records a string version of the inputted pygame key object, allowing in-game descriptions of keybind to be shown
        Input:
            pygame key object new_keybind: The keybind id that activates this button, like pygame.K_n
        Output:
            None
        '''
        keybind_name_dict = {
            pygame.K_a: 'a',
            pygame.K_b: 'b',
            pygame.K_c: 'c',
            pygame.K_d: 'd',
            pygame.K_e: 'e',
            pygame.K_f: 'f',
            pygame.K_g: 'g',
            pygame.K_h: 'h',
            pygame.K_i: 'i',
            pygame.K_j: 'j',
            pygame.K_k: 'k',
            pygame.K_l: 'l',
            pygame.K_m: 'm',
            pygame.K_n: 'n',
            pygame.K_o: 'o',
            pygame.K_p: 'p',
            pygame.K_q: 'q',
            pygame.K_r: 'r',
            pygame.K_s: 's',
            pygame.K_t: 't',
            pygame.K_u: 'u',
            pygame.K_v: 'v',
            pygame.K_w: 'w',
            pygame.K_x: 'x',
            pygame.K_y: 'y',
            pygame.K_z: 'z',
            pygame.K_DOWN: 'down arrow',
            pygame.K_UP: 'up arrow',
            pygame.K_LEFT: 'left arrow',
            pygame.K_RIGHT: 'right arrow',
            pygame.K_1: '1',
            pygame.K_2: '2',
            pygame.K_3: '3',
            pygame.K_4: '4',
            pygame.K_5: '5',
            pygame.K_6: '6',
            pygame.K_7: '7',
            pygame.K_8: '8',
            pygame.K_9: '9',
            pygame.K_0: '0',
            pygame.K_SPACE: 'space',
            pygame.K_RETURN: 'enter',
            pygame.K_TAB: 'tab',
            pygame.K_ESCAPE: 'escape'
        }
        self.keybind_name = keybind_name_dict[new_keybind]

    def set_tooltip(self, tooltip_text):
        '''
        Description:
            Sets this actor's tooltip to the inputted list, with each inputted list representing a line of the tooltip
        Input:
            string list new_tooltip: Lines for this actor's tooltip
        Output:
            None
        '''
        self.tooltip_text = tooltip_text
        if self.has_keybind:
            self.tooltip_text.append('Press ' + self.keybind_name + ' to use.')
        tooltip_width = 0#50
        font_name = self.global_manager.get('font_name')
        font_size = self.global_manager.get('font_size')
        for text_line in tooltip_text:
            if text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager) > tooltip_width:
                tooltip_width = text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager)
        tooltip_height = (len(self.tooltip_text) * font_size) + scaling.scale_height(5, self.global_manager)
        self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.x - self.tooltip_outline_width, self.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def touching_mouse(self):
        '''
        Description:
            Returns whether this button is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if this button is colliding with the mouse, otherwise returns False
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this button's tooltip can be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        Input:
            None
        Output:
            None
        '''
        if self.touching_mouse() and self.can_show():
            return(True)
        else:
            return(False)
        
    def draw(self):
        '''
        Description:
            Draws this button with a description of its keybind if it has one, along with an outline if its keybind is being pressed
        Input:
            None
        Output:
            None
        '''
        if self.can_show(): #self.global_manager.get('current_game_mode') in self.modes:
            if self.showing_outline and not self in self.global_manager.get('label_list'):
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.outline)
            if self.showing_background and hasattr(self, 'color'):
                pygame.draw.rect(self.global_manager.get('game_display'), self.color, self.Rect)
            self.image.draw()
            if self.has_keybind: #The key to which a button is bound will appear on the button's image
                message = self.keybind_name
                color = 'white'
                textsurface = self.global_manager.get('myfont').render(message, False, self.global_manager.get('color_dict')[color])
                self.global_manager.get('game_display').blit(textsurface, (self.x + scaling.scale_width(10, self.global_manager), (self.global_manager.get('display_height') -
                    (self.y + self.height - scaling.scale_height(5, self.global_manager)))))

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        '''
        Description:
            Draws this button's tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
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

    def on_rmb_click(self):
        '''
        Description:
            Controls this button's behavior when right clicked. By default, the button's right click behavior is the same as its left click behavior.
        Input:
            None
        Output:
            None
        '''
        self.on_click()

    def on_click(self): #sell commodity, sell all commodity
        '''
        Description:
            Controls this button's behavior when left clicked. This behavior depends on the button's button_type
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if self.button_type in ['move left', 'move right', 'move up', 'move down']:
                x_change = 0
                y_change = 0
                if self.button_type == 'move left':
                    x_change = -1
                elif self.button_type == 'move right':
                    x_change = 1
                elif self.button_type == 'move up':
                    y_change = 1
                elif self.button_type == 'move down':
                    y_change = -1
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if main_loop_tools.action_possible(self.global_manager):
                    if minister_utility.positions_filled(self.global_manager):
                        if len(selected_list) == 1:
                            if self.global_manager.get('current_game_mode') == 'strategic':
                                mob = selected_list[0]
                                if mob.can_move(x_change, y_change):
                                    mob.move(x_change, y_change)
                                    self.global_manager.set('show_selection_outlines', True)
                                    self.global_manager.set('last_selection_outline_switch', time.time())
                                    if mob.sentry_mode:
                                        mob.set_sentry_mode(False)
                                    mob.clear_automatic_route()
                            else:
                                text_tools.print_to_screen('You can not move while in the European HQ screen.', self.global_manager)
                        elif len(selected_list) < 1:
                            text_tools.print_to_screen('There are no selected units to move.', self.global_manager)
                        else:
                            text_tools.print_to_screen('You can only move one unit at a time.', self.global_manager)
                    else:
                        text_tools.print_to_screen('You have not yet appointed a minister in each office.', self.global_manager)
                        text_tools.print_to_screen('Press Q to view the minister interface.', self.global_manager)
                else:
                    text_tools.print_to_screen('You are busy and can not move.', self.global_manager)
            elif self.button_type == 'toggle grid lines':
                self.global_manager.get('effect_manager').set_effect('hide_grid_lines', utility.toggle(self.global_manager.get('effect_manager').effect_active('hide_grid_lines')))

            elif self.button_type == 'toggle text box':
                self.global_manager.set('show_text_box', utility.toggle(self.global_manager.get('show_text_box')))

            elif self.button_type == 'expand text box':
                if self.global_manager.get('text_box_height') == self.global_manager.get('default_text_box_height'):
                    self.global_manager.set('text_box_height', scaling.scale_height(self.global_manager.get('default_display_height') - 45, self.global_manager)) #self.height
                else:
                    self.global_manager.set('text_box_height', self.global_manager.get('default_text_box_height'))

            elif self.button_type == 'execute movement routes':
                if main_loop_tools.action_possible(self.global_manager):
                    if minister_utility.positions_filled(self.global_manager):
                        if not self.global_manager.get('current_game_mode') == 'strategic':
                            game_transitions.set_game_mode('strategic', self.global_manager)
                                
                        unit_types = ['porters', 'steamboat', 'steamship', 'train']
                        moved_units = {}
                        attempted_units = {}
                        for current_unit_type in unit_types:
                            moved_units[current_unit_type] = 0
                            attempted_units[current_unit_type] = 0
                        
                        for current_pmob in self.global_manager.get('pmob_list'):
                            if len(current_pmob.base_automatic_route) > 0:
                                if current_pmob.is_vehicle:
                                    if current_pmob.vehicle_type == 'train':
                                        unit_type = 'train'
                                    elif current_pmob.can_swim_ocean:
                                        unit_type = 'steamship'
                                    else:
                                        unit_type = 'steamboat'
                                else:
                                    unit_type = 'porters'
                                attempted_units[unit_type] += 1
                            
                                progressed = current_pmob.follow_automatic_route()
                                if progressed:
                                    moved_units[unit_type] += 1
                                current_pmob.remove_from_turn_queue()
                        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self.global_manager.get('displayed_mob')) #updates mob info display if automatic route changed anything

                        types_moved = 0
                        text = ''
                        for current_unit_type in unit_types:
                            if attempted_units[current_unit_type] > 0:
                            
                                if current_unit_type == 'porters':
                                    singular = 'unit of porters'
                                    plural = 'units of porters'
                                else:
                                    singular = current_unit_type
                                    plural = singular + 's'
                                types_moved += 1
                                num_attempted = attempted_units[current_unit_type]
                                num_progressed = moved_units[current_unit_type]
                                if num_attempted == num_progressed:
                                    if num_attempted == 1:
                                        text += 'The ' + singular + ' made progress on its designated movement route. /n /n'
                                    else:
                                        text += 'All ' + str(num_attempted) + ' of the ' + plural + ' made progress on their designated movement routes. /n /n'
                                else:
                                    if num_progressed == 0:
                                        if num_attempted == 1:
                                            text += 'The ' + singular + ' made no progress on its designated movement route. /n /n' 
                                        else:
                                            text += 'None of the ' + plural + ' made progress on their designated movement routes. /n /n'
                                    else:
                                        text += 'Only ' + str(num_progressed) + ' of the ' + str(num_attempted) + ' ' + plural + ' made progress on their designated movement routes. /n /n'

                        transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
                        if types_moved > 0:
                            transportation_minister.display_message(text)
                        else:
                            transportation_minister.display_message('There were no units with designated movement routes. /n /n')
                    else:
                        text_tools.print_to_screen('You have not yet appointed a minister in each office.', self.global_manager)
                        text_tools.print_to_screen('Press Q to view the minister interface.', self.global_manager)
                else:
                    text_tools.print_to_screen('You are busy and can not move units.', self.global_manager)
                

            elif self.button_type == 'do something':
                text_tools.get_input('do something', 'Placeholder do something message', self.global_manager)
                
            elif self.button_type == 'exploration':
                self.expedition.start_exploration(self.x_change, self.y_change)

            elif self.button_type == 'attack':
                self.battalion.remove_attack_marks()
                self.battalion.move(self.x_change, self.y_change, True)

            elif self.button_type == 'drop commodity' or self.button_type == 'drop all commodity':
                if main_loop_tools.action_possible(self.global_manager):
                    if main_loop_tools.minister_appointed(self.global_manager.get('type_minister_dict')['transportation'], self.global_manager):
                        displayed_mob = self.global_manager.get('displayed_mob')
                        displayed_tile = self.global_manager.get('displayed_tile')
                        commodity = displayed_mob.get_held_commodities()[self.attached_label.commodity_index]
                        num_commodity = 1
                        if self.button_type == 'drop all commodity':
                            num_commodity = displayed_mob.get_inventory(commodity)
                        if (not displayed_mob == 'none') and (not displayed_tile == 'none'):
                            if displayed_mob in displayed_tile.cell.contained_mobs:
                                can_drop_off = True
                                if displayed_mob.is_vehicle and displayed_mob.vehicle_type == 'train' and not displayed_mob.images[0].current_cell.has_intact_building('train_station'):
                                    can_drop_off = False
                                    text_tools.print_to_screen('A train can only drop off cargo at a train station.', self.global_manager)
                                if can_drop_off:
                                    if displayed_mob.sentry_mode:
                                        displayed_mob.set_sentry_mode(False)
                                    displayed_mob.change_inventory(commodity, -1 * num_commodity)
                                    displayed_tile.change_inventory(commodity, num_commodity)
                                    if displayed_tile.get_inventory_remaining() < 0 and not displayed_tile.can_hold_infinite_commodities:
                                        text_tools.print_to_screen('This tile can not hold this many commodities.', self.global_manager)
                                        text_tools.print_to_screen('Any commodities exceeding this tile\'s inventory capacity of ' + str(displayed_tile.inventory_capacity) + ' will disappear at the end of the turn.', self.global_manager)
                            else:
                                text_tools.print_to_screen('This unit is not in this tile.', self.global_manager)
                        else:
                            text_tools.print_to_screen('There is no tile to transfer this commodity to.', self.global_manager)
                else:
                     text_tools.print_to_screen('You are busy and can not transfer commodities.', self.global_manager)
                
            elif self.button_type == 'pick up commodity' or self.button_type == 'pick up all commodity':
                if main_loop_tools.action_possible(self.global_manager):
                    if main_loop_tools.minister_appointed(self.global_manager.get('type_minister_dict')['transportation'], self.global_manager):
                        displayed_mob = self.global_manager.get('displayed_mob')
                        displayed_tile = self.global_manager.get('displayed_tile')
                        commodity = displayed_tile.get_held_commodities()[self.attached_label.commodity_index]
                        num_commodity = 1
                        if self.button_type == 'pick up all commodity':
                            num_commodity = displayed_tile.get_inventory(commodity)
                        if (not displayed_mob == 'none') and (not displayed_tile == 'none'):
                            if displayed_mob in displayed_tile.cell.contained_mobs:
                                if displayed_mob.can_hold_commodities:
                                    can_pick_up = True
                                    if displayed_mob.is_vehicle and displayed_mob.vehicle_type == 'train' and not displayed_mob.images[0].current_cell.has_intact_building('train_station'):
                                        can_pick_up = False
                                        text_tools.print_to_screen('A train can only pick up cargo at a train station.', self.global_manager)
                                    if can_pick_up:
                                        if displayed_mob.get_inventory_remaining(num_commodity) >= 0: #see if adding commodities would exceed inventory capacity
                                            amount_transferred = num_commodity
                                        else:
                                            amount_transferred = displayed_mob.get_inventory_remaining()
                                            text_tools.print_to_screen('This unit can currently only pick up ' + str(amount_transferred) + ' units of ' + commodity + '.', self.global_manager)
                                        if displayed_mob.sentry_mode:
                                            displayed_mob.set_sentry_mode(False)
                                        displayed_mob.change_inventory(commodity, amount_transferred)
                                        displayed_tile.change_inventory(commodity, -1 * amount_transferred)
                                else:
                                    text_tools.print_to_screen('This unit can not hold commodities.', self.global_manager)
                            else:
                                text_tools.print_to_screen('This unit is not in this tile.', self.global_manager)
                        else:
                            text_tools.print_to_screen('There is no unit to transfer this commodity to.', self.global_manager)
                else:
                     text_tools.print_to_screen('You are busy and can not transfer commodities.', self.global_manager)

            elif self.button_type == 'remove worker':
                if not self.attached_label.attached_building == 'none':
                    if not len(self.attached_label.attached_building.contained_workers) == 0:
                        self.attached_label.attached_building.contained_workers[0].leave_building(self.attached_label.attached_building)
                    else:
                        text_tools.print_to_screen('There are no workers to remove from this building.', self.global_manager)

            elif self.button_type == 'start end turn':
                if main_loop_tools.action_possible(self.global_manager):
                    stopping = False
                    for current_position in self.global_manager.get('minister_types'):
                        if self.global_manager.get('current_ministers')[current_position] == 'none':
                            stopping = True
                    if stopping:
                        text_tools.print_to_screen('You have not yet appointed a minister in each office.', self.global_manager)
                        text_tools.print_to_screen('Press Q to view the minister interface.', self.global_manager)
                    else:
                        if not self.global_manager.get('current_game_mode') == 'strategic':
                            game_transitions.set_game_mode('strategic', self.global_manager)
                        for current_minister in self.global_manager.get('minister_list'):
                            if current_minister.just_removed and current_minister.current_position == 'none':
                                text = 'If you do not reappoint ' + current_minister.name + ' by the end of the turn, they will be considered fired, leaving the candidate pool and incurring a large public opinion penalty. /n /n'
                                current_minister.display_message(text)
                        for current_cell in self.global_manager.get('strategic_map_grid').cell_list:
                            if current_cell.visible and current_cell.tile.get_inventory_used() > current_cell.tile.inventory_capacity:
                                text = 'The warehouses at (' + str(current_cell.x) + ', ' + str(current_cell.y) + ') are not sufficient to hold the commodities stored there. /n /n'
                                text += 'Any commodities exceeding the tile\'s storage capacity will be lost at the end of the turn. /n /n'
                                notification_tools.display_zoom_notification(text, current_cell.tile, self.global_manager)
                        choice_info_dict = {'type': 'end turn'}
                        notification_tools.display_choice_notification('Are you sure you want to end your turn? ', ['end turn', 'none'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                else:
                    text_tools.print_to_screen('You are busy and can not end your turn.', self.global_manager)
    
            elif self.button_type == 'end turn':
                turn_management_tools.end_turn(self.global_manager)

            elif self.button_type == 'sell commodity' or self.button_type == 'sell all commodity':
                if main_loop_tools.minister_appointed(self.global_manager.get('type_minister_dict')['trade'], self.global_manager):
                    commodity_list = self.attached_label.actor.get_held_commodities()
                    commodity = commodity_list[self.attached_label.commodity_index]
                    num_present = self.attached_label.actor.get_inventory(commodity)
                    num_sold = 0
                    if self.button_type == 'sell commodity':
                        num_sold = 1
                    else:
                        num_sold = num_present
                    market_tools.sell(self.attached_label.actor, commodity, num_sold, self.global_manager)

            elif self.button_type == 'cycle units':
                if main_loop_tools.action_possible(self.global_manager):
                    game_transitions.cycle_player_turn(self.global_manager)
                else:
                    text_tools.print_to_screen('You are busy and can not cycle through units.', self.global_manager)

            elif self.button_type == 'new game':
                if self.global_manager.get('current_game_mode') == 'new_game_setup':
                    if not self.global_manager.get('displayed_country') == 'none':
                        self.global_manager.get('save_load_manager').new_game(self.global_manager.get('displayed_country'))
                    else:
                        text_tools.print_to_screen('You can not start a game without selecting a country.', self.global_manager)
                else:
                    game_transitions.set_game_mode('new_game_setup', self.global_manager)

            elif self.button_type == 'save game':
                if main_loop_tools.action_possible(self.global_manager):
                    self.global_manager.get('save_load_manager').save_game('save1.pickle')
                    notification_tools.display_notification('Game successfully saved to save1.pickle /n /n', 'default', self.global_manager)
                else:
                    text_tools.print_to_screen('You are busy and can not save the game', self.global_manager)

            elif self.button_type == 'load game':
                self.global_manager.get('save_load_manager').load_game('save1.pickle')

            elif self.button_type == 'fire':
                fired_unit = self.global_manager.get('displayed_mob')
                fired_unit.fire()

            elif self.button_type == 'free':
                displayed_mob = self.global_manager.get('displayed_mob')
                if displayed_mob.is_group:
                    displayed_mob.replace_worker('African')
                elif displayed_mob.is_worker:
                    displayed_mob.free_and_replace()

            elif self.button_type == 'free all':
                actor_utility.deselect_all(self.global_manager)
                pmob_list = utility.copy_list(self.global_manager.get('pmob_list')) #alllows iterating through each unit without any issues from removing from list during iteration
                old_public_opinion = self.global_manager.get('public_opinion')
                num_freed = 0
                for current_pmob in pmob_list:
                    if current_pmob.is_group and current_pmob.worker.worker_type == 'slave':
                        num_freed += 1
                        current_pmob.replace_worker('African')
                    elif current_pmob.is_worker and (not current_pmob.in_group) and current_pmob.worker_type == 'slave':
                        num_freed += 1
                        current_pmob.free_and_replace()
                public_opinion_increase = self.global_manager.get('public_opinion') - old_public_opinion
                if num_freed > 0:
                    message = 'A total of ' + str(num_freed) + ' unit' + utility.generate_plural(num_freed) + ' of slaves ' + utility.conjugate('be', num_freed, 'preterite') + ' freed and converted to workers'
                    message += ', increasing public opinion by a total of ' + str(public_opinion_increase) + '. /n /n'
                    notification_tools.display_notification(message, 'default', self.global_manager)
                else:
                    text_tools.print_to_screen('Your company has no slaves to free.', self.global_manager)

            elif self.button_type == 'stop exploration':
                actor_utility.stop_exploration(self.global_manager)

            elif self.button_type == 'start trading':
                caravan = self.notification.choice_info_dict['caravan']
                caravan.willing_to_trade(self.notification)

            elif self.button_type == 'start religious campaign':
                evangelist = self.notification.choice_info_dict['evangelist']
                evangelist.religious_campaign()

            elif self.button_type == 'start capture slaves':
                battalion = self.notification.choice_info_dict['battalion']
                battalion.capture_slaves()
            
            elif self.button_type == 'start suppress slave trade':
                battalion = self.notification.choice_info_dict['battalion']
                battalion.suppress_slave_trade()

            elif self.button_type == 'start public relations campaign':
                evangelist = self.notification.choice_info_dict['evangelist']
                evangelist.public_relations_campaign()

            elif self.button_type == 'start advertising campaign':
                merchant = self.notification.choice_info_dict['merchant']
                merchant.advertising_campaign()

            elif self.button_type == 'start loan search':
                merchant = self.notification.choice_info_dict['merchant']
                merchant.loan_search()
                for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                    current_minister_image.remove()

            elif self.button_type == 'start converting':
                evangelist = self.notification.choice_info_dict['evangelist']
                evangelist.convert()

            elif self.button_type == 'start rumor search':
                expedition = self.notification.choice_info_dict['expedition']
                expedition.rumor_search()

            elif self.button_type == 'start artifact search':
                expedition = self.notification.choice_info_dict['expedition']
                expedition.artifact_search()

            elif self.button_type == 'start construction':
                constructor = self.notification.choice_info_dict['constructor']
                constructor.construct()

            elif self.button_type == 'start upgrade':
                constructor = self.notification.choice_info_dict['constructor']
                constructor.upgrade()

            elif self.button_type == 'start repair':
                constructor = self.notification.choice_info_dict['constructor']
                constructor.repair()

            elif self.button_type == 'trade':
                caravan = self.notification.choice_info_dict['caravan']
                caravan.trade(self.notification)

            elif self.button_type == 'start trial':
                trial_utility.trial(self.global_manager)

            elif self.button_type in ['stop action', 'stop attack', 'stop trading', 'stop religious campaign', 'stop public relations campaign', 'stop advertising campaign', 
                                      'stop capture slaves', 'stop suppress slave trade', 'stop loan search', 'decline loan offer', 'stop converting', 'stop rumor search', 
                                      'stop artifact search', 'stop construction', 'stop upgrade', 'stop repair', 'stop trial']:
                self.global_manager.set('ongoing_action', False)
                self.global_manager.set('ongoing_action_type', 'none')
                if self.button_type == 'stop attack':
                    self.notification.choice_info_dict['battalion'].remove_attack_marks()
                elif self.button_type in ['stop loan search', 'decline loan offer']:
                    for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                        current_minister_image.remove()

            elif self.button_type == 'accept loan offer':
                input_dict = {}
                input_dict['principal'] = self.notification.choice_info_dict['principal']
                input_dict['interest'] = self.notification.choice_info_dict['interest']
                input_dict['remaining_duration'] = 10
                if self.notification.choice_info_dict['corrupt']:
                    self.global_manager.get('displayed_mob').controlling_minister.steal_money(20, 'loan_interest')
                    
                new_loan = market_tools.loan(False, input_dict, self.global_manager)
                self.global_manager.set('ongoing_action', False)
                self.global_manager.set('ongoing_action_type', 'none')

            elif self.button_type == 'launch trial':
                if main_loop_tools.action_possible(self.global_manager):
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['trial']:
                        if self.global_manager.get('displayed_defense').corruption_evidence > 0:
                            self.showing_outline = True
                            trial_utility.start_trial(self.global_manager)
                        else:
                            text_tools.print_to_screen('No real or fabricated evidence currently exists, so the trial has no chance of success.', self.global_manager)
                    else:
                        text_tools.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['trial']) + ' money needed to start a trial.', self.global_manager)
                else:
                    text_tools.print_to_screen('You are busy and can not start a trial.', self.global_manager)
                    
            elif self.button_type == 'confirm main menu':
                self.global_manager.set('game_over', False)
                game_transitions.to_main_menu(self.global_manager)

            elif self.button_type == 'quit':
                self.global_manager.set('crashed', True)

            elif self.button_type == 'wake up all':
                if main_loop_tools.action_possible(self.global_manager):
                    for current_pmob in self.global_manager.get('pmob_list'):
                        if current_pmob.sentry_mode:
                            current_pmob.set_sentry_mode(False)
                    actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self.global_manager.get('displayed_mob'))
                else:
                    text_tools.print_to_screen('You are busy and can not disable sentry mode.', self.global_manager)

            elif self.button_type == 'confirm remove minister':
                removed_minister = self.global_manager.get('displayed_minister')
                removed_minister.just_removed = True
                removed_minister.appoint('none')
                public_opinion_penalty = removed_minister.status_number
                self.global_manager.get('public_opinion_tracker').change(-1 * public_opinion_penalty)

            elif self.button_type == 'generate crash':
                print(1/0)

            elif self.button_type == 'minimize interface collection':
                self.parent_collection.minimized = utility.toggle(self.parent_collection.minimized)
                if not self.parent_collection.minimized:
                    #If any movement within the collection occurred while minimized, makes sure all newly shown elements are at their correct locations
                    self.parent_collection.set_origin(self.parent_collection.x, self.parent_collection.y)

            elif self.button_type == 'move interface collection':
                if self.parent_collection.move_with_mouse_config['moving']:
                    self.parent_collection.move_with_mouse_config = {'moving': False}
                else:
                    x, y = pygame.mouse.get_pos()
                    y = self.global_manager.get('display_height') - y
                    self.parent_collection.move_with_mouse_config = {
                        'moving': True, 
                        'mouse_x_offset': self.parent_collection.x - x, 
                        'mouse_y_offset': self.parent_collection.y - y
                    }

            elif self.button_type == 'reset interface collection':
                self.parent_collection.set_origin(self.parent_collection.original_coordinates[0], self.parent_collection.original_coordinates[1])
                for member in self.parent_collection.members: #only goes down 1 layer - should modify to recursively iterate through each item below parent in hierarchy
                    if hasattr(member, 'original_coordinates'):
                        member.set_origin(member.original_coordinates[0], member.original_coordinates[1])

            elif self.button_type == 'tab':
                tabbed_collection = self.parent_collection.parent_collection
                tabbed_collection.current_tabbed_member = self.linked_element

    def on_rmb_release(self):
        '''
        Description:
            Controls what this button does when right clicked and released. By default, buttons will stop showing their outlines when released.
        Input:
            None
        Output:
            None
        '''
        self.on_release()
                
    def on_release(self):
        '''
        Description:
            Controls what this button does when left clicked and released. By default, buttons will stop showing their outlines when released.
        Input:
            None
        Output:
            None
        '''
        self.showing_outline = False

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def can_show(self):
        '''
        Description:
            Returns whether this button can be shown. By default, it can be shown during game modes in which this button can appear
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        '''
        if self.button_type == 'move interface collection' and self.parent_collection.move_with_mouse_config['moving']:
            x, y = pygame.mouse.get_pos()
            y = self.global_manager.get('display_height') - y
            destination_x, destination_y = (x + self.parent_collection.move_with_mouse_config['mouse_x_offset'], y + self.parent_collection.move_with_mouse_config['mouse_y_offset'])
            self.parent_collection.set_origin(destination_x, destination_y)

        if super().can_show():
            if self.button_type in ['move left', 'move right', 'move down', 'move up']:
                if self.global_manager.get('displayed_mob') == 'none' or (not self.global_manager.get('displayed_mob').is_pmob):
                    return(False)
            elif self.button_type in ['sell commodity', 'sell all commodity']:
                if self.global_manager.get('europe_grid') in self.attached_label.actor.grids:
                    return(True)
                else:
                    return(False)

            
            return(True)
        return(False)

class end_turn_button(button):
    '''
    Button that ends the turn when pressed and changes appearance based on the current turn
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'start end turn'
        super().__init__(input_dict, global_manager)
        self.warning_image = images.warning_image(self, global_manager, 'button')
        self.warning_image.set_image('misc/enemy_turn_icon.png')
        self.warning_image.to_front = True
        if self.parent_collection != 'none':
            self.parent_collection.add_member(self.warning_image, {'order_exempt': True, 'order_x_offset': 100})

    def set_origin(self, new_x, new_y):
        '''
        Description:
            Sets this interface element's location and those of its members to the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        '''
        super().set_origin(new_x, new_y)
        if hasattr(self, 'warning_image'):
            self.warning_image.set_origin(new_x + self.warning_image.order_x_offset, new_y + self.warning_image.order_y_offset)

    def can_show_warning(self): #show warning if enemy movements or combat are still occurring
        '''
        Description:
            Whether this button can show its enemy turn version using the 'warning' system, returning True if is the enemy's turn or if it is the enemy combat phase (not technically during enemy turn)
        Input:
            none
        Output:
            boolean: Returns whether this button's enemy turn version should be shown
        '''
        if self.global_manager.get('player_turn') and not self.global_manager.get('enemy_combat_phase'):
            return(False)
        return(True)
        
class cycle_same_tile_button(button):
    '''
    Button that appears near the displayed tile and cycles the order of mobs displayed in a tile
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'cycle tile mobs'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button cycles the order of mobs displayed in a tile, moving the first one shown to the bototm and moving others up
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                cycled_tile = self.global_manager.get('displayed_tile')
                moved_mob = cycled_tile.cell.contained_mobs.pop(0)
                cycled_tile.cell.contained_mobs.append(moved_mob)
                cycled_tile.cell.contained_mobs[0].select()
                if cycled_tile.cell.contained_mobs[0].is_pmob:
                    cycled_tile.cell.contained_mobs[0].selection_sound()
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), cycled_tile) #updates mob info display list to show changed passenger order
            else:
                text_tools.print_to_screen('You are busy and can not cycle units.', self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the currently displayed tile contains 3 or less mobs. Otherwise, returns same as superclass
        '''
        result = super().can_show()
        if result:
            displayed_tile = self.global_manager.get('displayed_tile')
            if not displayed_tile == 'none':
                if len(displayed_tile.cell.contained_mobs) >= 4:
                    return(True)
        return(False)

class same_tile_icon(button):
    '''
    Button that appears near the displayed tile and selects mobs that are not currently at the top of the tile
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'index': int value - Index to determine which item of the displayed tile's cell's list of contained mobs is selected by this button
                'is_last': boolean value - Whether this is the last of the displayed tile's selection icons. If it is last, it will show all mobs are not being shown rather than being 
                        attached to a specific mob
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_mob = 'none'
        input_dict['button_type'] = 'same tile'
        super().__init__(input_dict, global_manager)
        self.old_contained_mobs = []
        self.default_image_id = input_dict['image_id']
        self.index = input_dict['index']
        self.is_last = input_dict['is_last']
        if self.is_last:
            self.name_list = []
        self.global_manager.get('same_tile_icon_list').append(self)

    def reset(self):
        '''
        Description:
            Resets this icon when a new tile is selected, forcing it to re-calibrate with any new units
        Input:
            None
        Output:
            None
        '''
        self.resetting = True

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button selects the mob that it is currently attached to when clicked
        Input:
            None
        Output:
            None
        '''
        if self.can_show() and (not self.is_last) and (not self.attached_mob == 'none'):
            if main_loop_tools.action_possible(self.global_manager): #when clicked, calibrate minimap to attached mob and move it to the front of each stack
                self.showing_outline = True
                self.attached_mob.select()
                if self.attached_mob.is_pmob:
                    self.attached_mob.selection_sound()
                for current_image in self.attached_mob.images: #move mob to front of each stack it is in
                    if not current_image.current_cell == 'none':
                        while not self.attached_mob == current_image.current_cell.contained_mobs[0]:
                            current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
            else:
                text_tools.print_to_screen('You are busy and can not select a different unit', self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is no tile selected or if the selected tile has not been explored, otherwise returns same as superclass
        '''
        if (not self.global_manager.get('displayed_tile') == 'none') and self.global_manager.get('displayed_tile').cell.visible:
            return(super().can_show())
        else:
            return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this button's tooltip can be shown. A same tile icon has the the normal requirements for a tooltip to be shown, along with requiring that it is attached to a unit
        Input:
            None
        Output:
            None
        '''
        if super().can_show_tooltip():
            if not self.attached_mob == 'none':
                return(True)
        return(False)
                         
    def draw(self):
        '''
        Description:
            Draws this button and draws a copy of the this button's attached mob's image on top of it
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if not self.global_manager.get('displayed_tile') == 'none':
                new_contained_mobs = self.global_manager.get('displayed_tile').cell.contained_mobs #actor_utility.get_selected_list(self.global_manager)
                if (not new_contained_mobs == self.old_contained_mobs) or self.resetting:
                    self.resetting = False
                    self.old_contained_mobs = []
                    for current_item in new_contained_mobs:
                        self.old_contained_mobs.append(current_item)
                    if self.is_last and len(new_contained_mobs) > self.index:
                        self.attached_mob = 'last'
                        self.image.set_image('buttons/extra_selected_button.png')
                        name_list = []
                        for current_mob_index in range(len(self.old_contained_mobs)):
                            if current_mob_index > self.index - 1:
                                name_list.append(self.old_contained_mobs[current_mob_index].name)
                        self.name_list = name_list
                        
                    elif len(self.old_contained_mobs) > self.index:
                        self.attached_mob = self.old_contained_mobs[self.index]
                        self.image.set_image(self.attached_mob.images[0].image_id)
            else:
                self.image.set_image('misc/empty.png')
                self.attached_mob = 'none'
                
            if len(self.old_contained_mobs) > self.index:
                displayed_tile = self.global_manager.get('displayed_tile')
                if self.index == 0 and self.can_show() and not displayed_tile == 'none':
                    if displayed_tile.cell.contained_mobs[0].selected: #self.global_manager.get('displayed_tile').cell.contained_mobs[0].selected:
                        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['bright green'], self.outline)
                    else:
                        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.outline)
                super().draw()

            else:
                self.image.set_image('misc/empty.png')
                self.attached_mob = 'none'

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button copies the tooltip of its attached mob
        Input:
            None
        Output:
            None
        '''
        if not self.can_show():
            self.set_tooltip([])
        else:
            if self.is_last:
                self.set_tooltip(['More: '] + self.name_list)
            else:
                self.attached_mob.update_tooltip()
                self.set_tooltip(self.attached_mob.tooltip_text + ['Click to select this unit'])

class fire_unit_button(button):
    '''
    Button that fires the selected unit, removing it from the game as if it died
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_mob = 'none'
        input_dict['button_type'] = 'fire unit'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button fires the selected unit
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager): #when clicked, calibrate minimap to attached mob and move it to the front of each stack
                if not(self.attached_mob.is_vehicle and self.attached_mob.vehicle_type == 'ship' and not self.attached_mob.can_leave()):
                    self.showing_outline = True
                    message = 'Are you sure you want to fire this unit? Firing this unit would remove it, any units attached to it, and any associated upkeep from the game. /n /n '
                    if self.attached_mob.is_worker:
                        if self.attached_mob.worker_type in ['European', 'religious']:
                            if self.attached_mob.worker_type == 'European':
                                message += 'Unlike African workers, fired European workers will never settle in slums and will instead return to Europe. /n /n'
                                message += 'Firing European workers reflects poorly on your company and will incur a public opinion penalty of 1. /n /n'
                            else:
                                message += 'Unlike African workers, fired church volunteers will never settle in slums and will instead return to Europe. /n /n'
                                message += 'Firing church volunteers reflects poorly on your company and will incur a public opinion penalty of 1. /n /n'
                        elif self.attached_mob.worker_type == 'African':
                            message += 'Fired workers will enter the labor pool and wander, eventually settling in slums where they may be hired again.'
                        elif self.attached_mob.worker_type == 'slave':
                            message += 'Firing slaves frees them, increasing public opinion and entering them into the labor pool. Freed slaves will wander and eventually settle in slums, where they may be hired as workers.'
                    notification_tools.display_choice_notification(message, ['fire', 'cancel'], {}, self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not fire a unit', self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if there is a selected unit, otherwise returns False
        '''
        if super().can_show():
            if not self.attached_mob == self.global_manager.get('displayed_mob'):
                self.attached_mob = self.global_manager.get('displayed_mob')
            if not self.attached_mob == 'none':
                if self.attached_mob.controllable:
                    return(True)
        return(False)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes how firing units works
        Input:
            None
        Output:
            None
        '''
        if not self.can_show():
            self.set_tooltip([])
        else:
            tooltip_text = ['Click to fire this unit']
            if self.attached_mob.is_group or self.attached_mob.is_worker:
                tooltip_text.append('Once fired, this unit will cost no longer cost upkeep')
            elif self.attached_mob.is_vehicle:
                tooltip_text.append('Firing this unit will also fire all of its passengers.')
            self.set_tooltip(tooltip_text)

class free_unit_slaves_button(button):
    '''
    Button that frees any slaves in the selected unit and immediately recruits them as African workers
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_mob = 'none'
        input_dict['button_type'] = 'free unit slaves'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button fires the selected unit
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                if not(self.attached_mob.is_vehicle and self.attached_mob.vehicle_type == 'ship' and not self.attached_mob.can_leave()):
                    self.showing_outline = True
                    message = 'Are you sure you want to free the slaves in this unit? This would convert them to free African workers with any associated upkeep. /n /n '
                    notification_tools.display_choice_notification(message, ['free', 'cancel'], {}, self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not free slaves', self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if there is a selected unit, otherwise returns False
        '''
        if super().can_show():
            if not self.attached_mob == self.global_manager.get('displayed_mob'):
                self.attached_mob = self.global_manager.get('displayed_mob')
            if not self.attached_mob == 'none':
                if self.attached_mob.controllable:
                    if (self.attached_mob.is_group and self.attached_mob.worker.worker_type == 'slave') or (self.attached_mob.is_worker and self.attached_mob.worker_type == 'slave'):
                        return(True)
        return(False)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes how firing units works
        Input:
            None
        Output:
            None
        '''
        if not self.can_show():
            self.set_tooltip([])
        else:
            tooltip_text = ['Click to free this unit']
            if self.attached_mob.is_group or self.attached_mob.is_worker:
                tooltip_text.append('Once freed, this unit\'s slaves will be converted to free African workers with any associated upkeep')
            self.set_tooltip(tooltip_text)

class switch_game_mode_button(button):
    '''
    Button that switches between game modes, like from the strategic map to the minister conference room
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'to_mode': string value - Game mode that this button switches to. If this equals 'previous', it switches to the previous game mode rather than a preset one
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.to_mode = input_dict['to_mode']
        self.to_mode_tooltip_dict = {}
        self.to_mode_tooltip_dict['main_menu'] = ['Exits to the main menu', 'Does not automatically save the game']
        self.to_mode_tooltip_dict['strategic'] = ['Enters the strategic map screen']
        self.to_mode_tooltip_dict['europe'] = ['Enters the European headquarters screen']
        self.to_mode_tooltip_dict['ministers'] = ['Enters the minister conference room screen']
        input_dict['button_type'] = 'switch game mode'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button transtions from the current game mode to either the previous game mode or one specified on button initialization
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.to_mode in ['ministers', 'main_menu', 'new_game_setup'] or (self.global_manager.get('minister_appointment_tutorial_completed') and minister_utility.positions_filled(self.global_manager)):
                    if self.to_mode == 'ministers' and 'trial' in self.modes:
                        defense = self.global_manager.get('displayed_defense')
                        if defense.fabricated_evidence > 0:
                            text = 'WARNING: Your ' + str(defense.fabricated_evidence) + ' piece' + utility.generate_plural(defense.fabricated_evidence) + ' of fabricated evidence against ' + defense.current_position + ' '
                            text += defense.name + ' will disappear at the end of the turn if left unused. /n /n'
                            notification_tools.display_notification(text, 'default', self.global_manager)
                        if self.global_manager.get('prosecution_bribed_judge'):
                            text = 'WARNING: The effect of bribing the judge will disappear at the end of the turn if left unused. /n /n'
                            notification_tools.display_notification(text, 'default', self.global_manager)
                    
                    if self.to_mode == 'main_menu':
                        notification_tools.display_choice_notification('Are you sure you want to exit to the main menu without saving? /n /n', ['confirm main menu', 'none'], {}, self.global_manager) #message, choices, choice_info_dict, global_manager
                    elif not self.to_mode == 'previous':
                        game_transitions.set_game_mode(self.to_mode, self.global_manager)
                    else:
                        self.global_manager.set('exit_minister_screen_tutorial_completed', True)
                        game_transitions.set_game_mode(self.global_manager.get('previous_game_mode'), self.global_manager)
                else:
                    text_tools.print_to_screen('You have not yet appointed a minister in each office.', self.global_manager)
                    text_tools.print_to_screen('Press Q to view the minister interface.', self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not switch screens.', self.global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes which game mode it switches to
        Input:
            None
        Output:
            None
        '''
        if self.to_mode == 'previous':
            self.set_tooltip(utility.copy_list(self.to_mode_tooltip_dict[self.global_manager.get('previous_game_mode')]))
        else:
            self.set_tooltip(utility.copy_list(self.to_mode_tooltip_dict[self.to_mode]))

class minister_portrait_image(button):
    '''
    Button that can be calibrated to a minister to show that minister's portrait and selects the minister when clicked
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'minister_type': string value - Minister office that this button is linked to, causing this button to always be connected to the minister in that office. If equals 'none', 
                    can be calibrated to an available minister candidate
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.default_image_id = 'ministers/empty_portrait.png'
        self.current_minister = 'none'
        input_dict['image_id'] = self.default_image_id
        input_dict['button_type'] = 'minister portrait'
        super().__init__(input_dict, global_manager)
        self.minister_type = input_dict['minister_type'] #position, like General
        if self.minister_type == 'none': #if available minister portrait
            if 'ministers' in self.modes:
                self.global_manager.get('available_minister_portrait_list').append(self)
        else:
            self.type_keyword = self.global_manager.get('minister_type_dict')[self.minister_type]
        self.global_manager.get('minister_image_list').append(self)
        self.warning_image = images.warning_image(self, global_manager, 'button')
        self.calibrate('none')

    def can_show_warning(self):
        '''
        Description:
            Returns whether this image should display its warning image. It should be shown when this image is visible and its attached minister is about to be fired at the end of the turn
        Input:
            None
        Output:
            Returns whether this image should display its warning image
        '''
        if not self.current_minister == 'none':
            if self.current_minister.just_removed and self.current_minister.current_position == 'none':
                return(True)
        return(False)

    def draw(self):
        '''
        Description:
            Draws this button's image along with a white background and, if its minister is currently selected, a flashing green outline
        Input:
            None
        Output:
            None
        '''
        if self.can_show(): #draw outline around portrait if minister selected
            if not self.current_minister == 'none':
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.Rect) #draw white background
                if self.global_manager.get('displayed_minister') == self.current_minister and self.global_manager.get('show_selection_outlines'): 
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['bright green'], self.outline)
        super().draw()

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button selects its attached minister when clicked
        Input:
            None
        Output:
            None
        '''
        if main_loop_tools.action_possible(self.global_manager):
            if self.global_manager.get('current_game_mode') == 'ministers' and not self.current_minister == 'none':
                if self in self.global_manager.get('available_minister_portrait_list'): #if available minister portrait
                    own_index = self.global_manager.get('available_minister_list').index(self.current_minister)
                    self.global_manager.set('available_minister_left_index', own_index - 2)
                    minister_utility.update_available_minister_display(self.global_manager)
                else: #if cabinet portrait
                    minister_utility.calibrate_minister_info_display(self.global_manager, self.current_minister)
                if not self.current_minister == 'none':
                    self.current_minister.selection_sound()
        else:
            text_tools.print_to_screen('You are busy and can not select other ministers.', self.global_manager)

    def calibrate(self, new_minister):
        '''
        Description:
            Attaches this button to the inputted minister and updates this button's image to that of the minister
        Input:
            string/minister new_minister: The minister whose information is matched by this button. If this equals 'none', this button is detached from any ministers
        Output:
            None
        '''
        if not new_minister == 'none':
            new_minister.update_tooltip()
            self.tooltip_text = new_minister.tooltip_text #[self.minister_type + ' ' + new_minister.name]
            self.image.set_image(new_minister.image_id)
        else:
            if self.minister_type == 'none': #if available minister portrait
                self.tooltip_text = ['There is no available candidate in this slot.']
            else: #if appointed minister portrait
                self.tooltip_text = ['No ' + self.minister_type + ' is currently appointed.', 'Without a ' + self.minister_type + ', ' + self.type_keyword + '-oriented actions are not possible']
            self.image.set_image(self.default_image_id)
        self.current_minister = new_minister

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button copies the tooltip text of its attached minister, or says there is no attached minister if there is none attached
        Input:
            None
        Output:
            None
        '''
        if not self.current_minister == 'none':
            self.current_minister.update_tooltip()
            self.tooltip_text = self.current_minister.tooltip_text
        self.set_tooltip(self.tooltip_text)

class country_selection_image(button):
    '''
    Button that can be calibrated to a country to show that country and selects the country when clicked
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'country': country value - Country to start this button calibrated to, or 'none' if not initially calibrated to any country
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.default_image_id = 'misc/empty.png'
        self.current_country = 'none'
        input_dict['button_type'] = 'country images'
        input_dict['image_id'] = self.default_image_id
        super().__init__(input_dict, global_manager)
        self.global_manager.get('country_selection_image_list').append(self)
        self.current_country = input_dict['country']
        self.calibrate(self.current_country)

    def draw(self):
        '''
        Description:
            Draws this button's image along with a white background and, if its country is currently selected, a flashing green outline
        Input:
            None
        Output:
            None
        '''
        if self.can_show(): #draw outline around portrait if country selected
            if not self.current_country == 'none':
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.Rect) #draw white background
                if self.global_manager.get('displayed_country') == self.current_country and self.global_manager.get('show_selection_outlines'): 
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['bright green'], self.outline)
        super().draw()

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button selects its attached country when clicked
        Input:
            None
        Output:
            None
        '''
        if main_loop_tools.action_possible(self.global_manager):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('country_info_display'), self.current_country)
        else:
            text_tools.print_to_screen('You are busy and can not select another country.', self.global_manager)

    def calibrate(self, new_country):
        '''
        Description:
            Attaches this button to the inputted country and updates this button's image to that of the country
        Input:
            string/country new_country: The country whose information is matched by this button. If this equals 'none', this button is detached from any country
        Output:
            None
        '''
        if not new_country == 'none':
            new_country.update_tooltip()
            self.tooltip_text = new_country.tooltip_text 
            self.image.set_image(new_country.flag_image_id)
        else:
            self.image.set_image(self.default_image_id)
        self.current_country = new_country

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button copies the tooltip text of its attached country, or says there is no attached country if there is none attached
        Input:
            None
        Output:
            None
        '''
        if not self.current_country == 'none':
            self.current_country.update_tooltip()
            self.tooltip_text = self.current_country.tooltip_text
        self.set_tooltip(self.tooltip_text)

class cycle_available_ministers_button(button):
    '''
    Button that cycles through the ministers available to be appointed
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'direction': string value - If equals 'right', this button cycles forward in the list of available ministers. If equals 'left', this button cycles backwards in the list of 
                    available ministers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.direction = input_dict['direction']
        input_dict['button_type'] = 'cycle available ministers'
        super().__init__(input_dict, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if clicking this button would move more than 1 past the edge of the list of available ministers, otherwise returns same as superclass
        '''
        if self.direction == 'left':
            if self.global_manager.get('available_minister_left_index') > -2:
                return(super().can_show())
            else:
                return(False)
        elif self.direction == 'right': #left index = 0, left index + 4 = 4 which is greater than the length of a 3-minister list, so can't move right farther
            if not self.global_manager.get('available_minister_left_index') + 4 > len(self.global_manager.get('available_minister_list')):
                return(super().can_show())
            else:
                return(False)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button changes the range of available ministers that are displayed depending on its direction
        Input:
            None
        Output:
            None
        '''
        if main_loop_tools.action_possible(self.global_manager):
            if self.direction == 'left':
                self.global_manager.set('available_minister_left_index', self.global_manager.get('available_minister_left_index') - 1)
            if self.direction == 'right':
                self.global_manager.set('available_minister_left_index', self.global_manager.get('available_minister_left_index') + 1)
            minister_utility.update_available_minister_display(self.global_manager)
            self.global_manager.get('available_minister_portrait_list')[2].on_click() #select new middle portrait
        else:
            text_tools.print_to_screen('You are busy and can not select other ministers.', self.global_manager)

class commodity_button(button):
    '''
    Button appearing near commodity prices label that can be clicked as a target for advertising campaigns
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'commodity': string value - Commodity that this button corresponds to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.commodity = input_dict['commodity']
        input_dict['button_type'] = 'commodity selection'
        super().__init__(input_dict, global_manager)
        self.showing_background = False
        self.outline.width = 0
        self.outline.height = 0
        self.outline.x = 0
        self.outline.y = 0

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. When the player is choosing a target for an advertising campaign, clicking on this button starts an advertising campaign for this button's commodity
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('choosing_advertised_commodity'):
            if self.commodity == 'consumer goods':
                text_tools.print_to_screen('You can not advertise consumer goods.', self.global_manager)
            else:
                can_advertise = False
                for current_commodity in self.global_manager.get('collectable_resources'):
                    if (not current_commodity == self.commodity) and self.global_manager.get('commodity_prices')[current_commodity] > 1:
                        can_advertise = True
                        break
                if can_advertise:
                    self.global_manager.get('displayed_mob').start_advertising_campaign(self.commodity)
                    self.global_manager.set('choosing_advertised_commodity', False)
                else:
                    text_tools.print_to_screen('You can not advertise ' + self.commodity + ' because all other commodities are already at the minimum price.', self.global_manager)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this button's tooltip can be shown. A commodity button never shows a tooltip
        Input:
            None
        Output:
            None
        '''
        return(False)

class show_previous_financial_report_button(button):
    '''
    Button appearing near money label that can be clicked to display the previous turn's financial report again
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
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'show previous financial report'
        super().__init__(input_dict, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False during the first turn when there is no previous financial report to show, otherwise returns same as superclass
        '''
        if super().can_show():
            if not self.global_manager.get('previous_financial_report') == 'none':
                return(True)
        return(False)
    
    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button displays the previous turn's financial report again
        Input:
            None
        Output:
            None
        '''
        self.showing_outline = True
        if main_loop_tools.action_possible(self.global_manager):
            notification_tools.display_notification(self.global_manager.get('previous_financial_report'), 'default', self.global_manager)
        else:
            text_tools.print_to_screen('You are busy and can not view the last turn\'s financial report', self.global_manager)

class tab_button(button):
    def __init__(self, input_dict, global_manager):
        input_dict['button_type'] = 'tab'
        self.linked_element = input_dict['linked_element']
        super().__init__(input_dict, global_manager)

    def can_show(self):
        if self.linked_element == self.parent_collection.parent_collection.current_tabbed_member:
            self.showing_outline = True
        else:
            self.showing_outline = False
        return(super().can_show())
