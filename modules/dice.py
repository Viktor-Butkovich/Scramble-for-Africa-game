import pygame
import time
import random
from .buttons import button
from . import utility

class die(button):
    '''
    A die with a predetermined result that will appear, show random rolling, and end with the predetermined result and an outline with a color based on the result
    '''
    def __init__(self, coordinates, width, height, modes, num_sides, result_outcome_dict, outcome_color_dict, final_result, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables that represents the pixel location of the bottom left of this die
            width: int representing the width in pixels of this die
            height: int representing the height in pixels of this die
            modes: list of string representing the game modes in which this die can appear
            num_sides: int representing the number of sides of the simulated die
            result_outcome_dict: dictionary of string keys and int values that records the die results required for certain outcomes
            outcome_color_dict: dictionary of string keys and int values that records the colors associated with certain die results
            final_result: int representing the predetermined final result of this die roll
            global_manager: global_manager_template object
        '''
        self.result_outcome_dict = result_outcome_dict #min_success: 4, min_crit_success: 6, max_crit_fail: 1
        self.outcome_color_dict = outcome_color_dict #'success': 'green', 'crit_success': 'bright green', 'fail': 'red', crit_fail: 'black', 'default': 'gray'
        self.rolls_completed = 0
        self.num_sides = num_sides
        self.num_rolls = random.randrange(-3, 4) + 7 #4-10
        self.roll_interval = 0.3
        self.rolling = False
        self.last_roll = 0
        self.highlighted = False
        super().__init__(coordinates, width, height, 'green', 'label', 'none', modes, 'misc/dice/' + str(self.result_outcome_dict['min_success']) + '.png', global_manager)
        global_manager.get('dice_list').append(self)
        self.final_result = final_result
        self.Rect = pygame.Rect(self.x, self.global_manager.get('display_height') - (self.y + height), width, height)#create pygame rect with width and height, set color depending on roll result, maybe make a default gray appearance
        self.highlight_Rect = pygame.Rect(self.x - 3, self.global_manager.get('display_height') - (self.y + height + 3), width + 6, height + 6)
        self.color = 'white'#self.outcome_color_dict['default']
        self.outline_color = self.outcome_color_dict['default']

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this die's tooltip to describe it. If the die is not rolling yet, the tooltip will describe the results required for different outcomes.
            If the die is currently rolling, its current value will be displayed.
            If the die is finished rolling, its final value will be displayed and a description that it has finished rolling and whether its outcome was chosen for the roll's purpose will be described.
        '''
        tooltip_list = []
        if self.rolls_completed == 0:
            tooltip_list.append(str(self.result_outcome_dict['min_success']) + '+ required for success')
            if not self.result_outcome_dict['min_crit_success'] > self.num_sides: #do not mention critical success if impossible 
                if self.result_outcome_dict['min_crit_success'] == self.num_sides:
                    tooltip_list.append(str(self.result_outcome_dict['min_crit_success']) + ' required for critical success')
                else:
                    tooltip_list.append(str(self.result_outcome_dict['min_crit_success']) + '+ required for critical success')
            if not self.result_outcome_dict['max_crit_fail'] <= 0: #do not mention critical failure if impossible 
                if self.result_outcome_dict['max_crit_fail'] == self.num_sides:
                    tooltip_list.append(str(self.result_outcome_dict['max_crit_fail']) + ' required for critical failure')
                else:
                    tooltip_list.append(str(self.result_outcome_dict['max_crit_fail']) + ' or lower required for critical failure')
        else:
            tooltip_list.append(str(self.roll_result))
            if not self.rolling: #if rolls completed
                tooltip_list.append('Finished rolling')
                if self.highlighted and len(self.global_manager.get('dice_list')) > 1: #if other dice present and this die chosen
                    tooltip_list.append('This result was chosen')
        self.set_tooltip(tooltip_list)

    def start_rolling(self):
        '''
        Input:
            none
        Output:
            Causes the die to start rolling, after which it will roll to a different side every roll_interval seconds
        '''
        self.last_roll = time.time()
        self.rolling = True
        
    def roll(self):
        '''
        Input:
            none
        Output:
            Rolls the die to a random face, or to the predetermined result if it is the last roll. When all dice finish rolling, dice rolling notifications will be removed.
        '''
        self.last_roll = time.time()
        if self.rolls_completed == self.num_rolls: #if last roll just happened, stop rolling - allows slight pause after last roll during which you don't know if it is the final one
            self.rolling = False
            dice_rolling = False
            for current_die in self.global_manager.get('dice_list'):
                if current_die.rolling:
                    dice_rolling = True
            if (not self.global_manager.get('current_dice_rolling_notification') == 'none') and not dice_rolling: #if notification present and dice finished rolling, remove notification
                self.global_manager.get('current_dice_rolling_notification').remove()
        else:
            self.roll_result = 0
            if self.rolls_completed == self.num_rolls - 1: #if last roll
                self.roll_result = self.final_result
            else:
                self.roll_result = random.randrange(1, self.num_sides + 1) #1 - num_sides, inclusive
            if self.roll_result >= self.result_outcome_dict['min_success']: #if success
                if self.roll_result >= self.result_outcome_dict['min_crit_success']: #if crit success
                    self.outline_color = self.outcome_color_dict['crit_success']
                else: #if normal success
                    self.outline_color = self.outcome_color_dict['success']
            else: #if failure
                if self.roll_result <= self.result_outcome_dict['max_crit_fail']: #if crit fail
                    self.outline_color = self.outcome_color_dict['crit_fail']
                else: #if normal fail
                    self.outline_color = self.outcome_color_dict['fail']
            self.image.set_image('misc/dice/' + str(self.roll_result) + '.png')#self.set_label(str(self.roll_result))
            self.rolls_completed += 1

    def draw(self):
        '''
        Input:
            none
        Output:
            If enough time has passed since the last roll and the die is still rolling, this will roll the die. Additionally, this draws the die, displaying its current value.
            If it is finished rolling and it was chosen as the result to use for the roll's purpose, an outline with a color depending on the roll's outcome will be displayed.
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            if self.rolling and time.time() >= self.last_roll + self.roll_interval: #if roll_interval time has passed since last_roll
                self.roll()
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.color], self.Rect)
            if self.highlighted:
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.outline_color], self.Rect, 6)
            else:
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.Rect, 6)
            self.image.draw()        

    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('dice_list', utility.remove_from_list(self.global_manager.get('dice_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))


