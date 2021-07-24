import pygame
import time
import random
from .button import button_class
from . import scaling
from . import text_tools
from . import utility

class die(button_class):
    def __init__(self, coordinates, width, height, modes, num_sides, result_outcome_dict, outcome_color_dict, final_result, global_manager):
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
        #self.roll()
        self.last_roll = time.time()
        self.rolling = True
        
    def roll(self):
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
        if self.global_manager.get('current_game_mode') in self.modes:
            if self.rolling and time.time() >= self.last_roll + self.roll_interval: #if roll_interval time has passed since last_roll
                self.roll()
            #self.image.draw()
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.color], self.Rect)
            #pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.Rect, 6)
            if self.highlighted:
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.outline_color], self.Rect, 6)
            else:
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.Rect, 6)
                #pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.highlight_Rect, 3)
            self.image.draw()
            #for text_line_index in range(len(self.message)):
            #    text_line = self.message[text_line_index]
            #    self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height - (text_line_index * self.font_size))))
        

    def remove(self):
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('dice_list', utility.remove_from_list(self.global_manager.get('dice_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))


