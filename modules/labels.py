#Contains functionality for labels

import pygame
from .buttons import button
from . import scaling
from . import text_tools
from . import utility
from . import market_tools

class label(button):
    '''
    A button that shares most of a button's behaviors but displays a message and does nothing when clicked
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'message': string value - Default text for this label
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.get('label_list').append(self)
        self.font_size = scaling.scale_width(25, global_manager)
        self.font_name = self.global_manager.get('font_name')
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.current_character = 'none'
        self.message = input_dict['message']
        self.minimum_width = input_dict['minimum_width']
        input_dict['width'] = self.minimum_width
        input_dict['button_type'] = 'label'
        super().__init__(input_dict, global_manager)
        self.set_label(self.message)

    def set_label(self, new_message):
        '''
        Description:
            Sets this label's text to the inputted string, adjusting width as needed
        Input:
            string new_message: New text for this label
        Output:
            None
        '''
        self.message = new_message
        if text_tools.message_width(self.message, self.font_size, self.font_name) + scaling.scale_width(10, self.global_manager) > self.minimum_width:
            self.width = text_tools.message_width(self.message, self.font_size, self.font_name) + scaling.scale_width(10, self.global_manager)
        else:
            self.width = self.minimum_width
        self.image.width = self.width
        self.Rect.width = self.width
        self.image.set_image(self.image.image_id)
        self.image.Rect = self.Rect

    def update_tooltip(self):
        '''
        Description:
            Sets this label's tooltip to what it should be. By default, labels have tooltips matching their text
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip([self.message])
            
    def on_click(self):
        '''
        Description:
            Controls this label's behavior when clicked. By default, labels do nothing when clicked, though label subclasses like notifications may still need on_click functionality
        Input:
            None
        Output:
            None
        '''
        return

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
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))

    def draw(self):
        '''
        Description:
            Draws this label and draws its text on top of it
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            super().draw()
            self.global_manager.get('game_display').blit(text_tools.text(self.message, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                (self.y + self.height)))

class value_label(label):
    '''
    Label that tracks the value of a certain variable and is attached to a value_tracker object. Whenever the value of the value_tracker changes, this label is automatically changed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'value_name': string value - Type of value tracked by this label, like 'turn' for turn number label
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.value_name = input_dict['value_name']
        input_dict['message'] = 'none'
        super().__init__(input_dict, global_manager)
        self.display_name = text_tools.remove_underscores(self.value_name) #public_opinion to public opinion
        self.tracker = self.global_manager.get(self.value_name + '_tracker')
        self.tracker.value_label = self
        self.update_label(self.tracker.get())

    def update_label(self, new_value):
        '''
        Description:
            Updates the value shown by this label when to match the value of its value_tracker
        Input:
            int new_value: New value of this label's value_tracker
        Output:
            None
        '''
        self.set_label(utility.capitalize(self.display_name + ': ' + str(new_value)))

    def update_tooltip(self):
        '''
        Description:
            Sets this label's tooltip to what it should be. A value label's tooltip label's tooltip shows its text followed by a message related to the type of value represented
        Input:
            None
        Output:
            None
        '''
        tooltip_text = [self.message]
        if self.value_name == 'public_opinion':
            tooltip_text.append('Public opinion represents your company\'s reputation and expectations for its success and is used to calculate government subsidies')
            tooltip_text.append('Public opinion tends to approach the netural value of 50 over time')
        if self.value_name == 'turn':
            tooltip_text.append('Current lore mission: ')
            if self.global_manager.get('current_lore_mission') == 'none':
                text = '    None'
            else:
                text = '    Find the ' + self.global_manager.get('current_lore_mission').name + ' (' + self.global_manager.get('current_lore_mission').lore_type + ')'
            tooltip_text.append(text)
        self.set_tooltip(tooltip_text)

class money_label(value_label):
    '''
    Special type of value label that tracks money
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['value_name'] = 'money'
        super().__init__(input_dict, global_manager)

    def update_label(self, new_value):
        '''
        Description:
            Updates the value shown by this label when to match the value of its value tracker. Money labels additionally show the projected income for the next turn
        Input:
            int new_value: New value of this label's value_tracker
        Output:
            None
        '''
        end_turn_money_change = market_tools.calculate_end_turn_money_change(self.global_manager)
        if end_turn_money_change >= 0:
            sign = '+'
        else:
            sign = ''
        self.set_label(utility.capitalize(self.display_name + ': ' + str(new_value) + ' (' + sign + str(end_turn_money_change) + ')'))

    def check_for_updates(self):
        '''
        Description:
            Updates the projected income shown by this label when the income would change for any reason, such as when a worker is hired
        Input:
            None
        Output:
            None
        '''
        self.update_label(self.global_manager.get(self.tracker.value_key))
    
    def update_tooltip(self):
        '''
        Description:
            Sets this label's tooltip to what it should be. A money label's tooltip shows its text followed by the upkeep of the player's units each turn
        Input:
            None
        Output:
            None
        '''
        tooltip_text = [self.message]

        num_african_workers = self.global_manager.get('num_african_workers')
        african_worker_upkeep = self.global_manager.get('african_worker_upkeep')
        total_african_worker_upkeep = round(num_african_workers * african_worker_upkeep, 2)

        num_european_workers = self.global_manager.get('num_european_workers')
        european_worker_upkeep = self.global_manager.get('european_worker_upkeep')
        total_european_worker_upkeep = round(num_european_workers * european_worker_upkeep, 2)

        num_slave_workers = self.global_manager.get('num_slave_workers')
        slave_worker_upkeep = self.global_manager.get('slave_worker_upkeep')
        total_slave_worker_upkeep = round(num_slave_workers * slave_worker_upkeep, 2)
        
        num_church_volunteers = self.global_manager.get('num_church_volunteers')

        num_workers = num_african_workers + num_european_workers + num_slave_workers + num_church_volunteers
        total_upkeep = round(total_african_worker_upkeep + total_european_worker_upkeep + total_slave_worker_upkeep, 2)

        tooltip_text.append('')
        tooltip_text.append('At the end of the turn, you will pay a total of ' + str(total_upkeep) + ' money to your ' + str(num_workers) + ' workers.')
        if num_african_workers > 0:
            tooltip_text.append('    Your ' + str(num_african_workers) + ' free African worker' + utility.generate_plural(num_african_workers) + ' will be paid ' + str(african_worker_upkeep) + ' money, totaling to ' + str(total_african_worker_upkeep) + ' money.')
        else:
            tooltip_text.append('    Any free African workers would each be paid ' + str(african_worker_upkeep) + ' money.')
        if num_european_workers > 0:
            tooltip_text.append('    Your ' + str(num_european_workers) + ' European worker' + utility.generate_plural(num_european_workers) + ' will be paid ' + str(european_worker_upkeep) + ' money, totaling to ' + str(total_european_worker_upkeep) + ' money.')
        else:
            tooltip_text.append('    Any European workers would each be paid ' + str(european_worker_upkeep) + ' money.')
        if num_slave_workers > 0:
            tooltip_text.append('    Your ' + str(num_slave_workers) + ' slave worker' + utility.generate_plural(num_slave_workers) + ' will cost ' + str(slave_worker_upkeep) + ' in upkeep, totaling to ' + str(total_slave_worker_upkeep) + ' money.')
        else:
            tooltip_text.append('    Any slave workers would each cost ' + str(slave_worker_upkeep) + ' money in upkeep.')
        if num_church_volunteers > 0:
            tooltip_text.append('    Your ' + str(num_church_volunteers) + ' church volunteer' + utility.generate_plural(num_church_volunteers) + ' will not need to be paid.')
        else:
            tooltip_text.append('    Any church volunteers would not need to be paid.')

        tooltip_text.append('')
        num_available_workers = market_tools.count_available_workers(self.global_manager)
        tooltip_text.append('Between workers in slums and villages and recently fired wandering workers, the free labor pool consists of ' + str(num_available_workers) + ' African worker' + utility.generate_plural(num_available_workers) + '.')
        
        if len(self.global_manager.get('loan_list')) > 0:
            tooltip_text.append('')
            tooltip_text.append('Loans: ')
            for current_loan in self.global_manager.get('loan_list'):
                tooltip_text.append('    ' + current_loan.get_description())

        tooltip_text.append('')
        tooltip_text.append('While public opinion and government subsidies are not entirely predictable, your company is estimated to receive ' + str(market_tools.calculate_subsidies(self.global_manager, True)) + ' money in subsidies this turn')

        total_sale_revenue = market_tools.calculate_total_sale_revenue(self.global_manager)
        if total_sale_revenue > 0:
            tooltip_text.append('')
            tooltip_text.append('Your ' + self.global_manager.get('type_minister_dict')['trade'] + ' has been ordered to sell commodities at the end of the turn for an estimated total of ' + str(total_sale_revenue) + ' money')

        tooltip_text.append('')
        estimated_money_change = market_tools.calculate_end_turn_money_change(self.global_manager)
        if estimated_money_change > 0:
            tooltip_text.append('Between these revenues and expenses, your company is expected to gain about ' + str(estimated_money_change) + ' money at the end of the turn.')
        elif estimated_money_change < 0:
            tooltip_text.append('Between these revenues and expenses, your company is expected to lose about ' + str(-1 * estimated_money_change) + ' money at the end of the turn.')
        else:
            tooltip_text.append('Between these revenues and expenses, your company is expected to neither gain nor lose money at the end of the turn.')
        
        self.set_tooltip(tooltip_text)

class commodity_prices_label(label):
    '''
    Label that shows the price of each commodity. Unlike most labels, its message is a list of strings rather than a string, allowing it to have a line for each commodity
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.ideal_width = input_dict['minimum_width']
        self.minimum_height = input_dict['height']
        input_dict['message'] = 'none'
        super().__init__(input_dict, global_manager)
        self.font_size = self.global_manager.get('font_size') * 2
        self.font_name = self.global_manager.get('font_name')
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.update_label()

    def update_label(self):
        '''
        Description:
            Updates the values shown by this label when commodity prices change
        Input:
            None
        Output:
            None
        '''
        message = ['Prices: ']
        widest_commodity_width = 0
        for current_commodity in self.global_manager.get('commodity_types'):
            current_message_width = text_tools.message_width(current_commodity, self.font_size, self.font_name)
            if current_message_width > widest_commodity_width:
                widest_commodity_width = current_message_width
        for current_commodity in self.global_manager.get('commodity_types'):
            current_line = ''
            while text_tools.message_width(current_line + current_commodity, self.font_size, self.font_name) < widest_commodity_width:
                current_line += ' '
            current_line += current_commodity + ': ' +  str(self.global_manager.get('commodity_prices')[current_commodity])
            message.append(current_line)
        self.set_label(message)
            
    def set_label(self, new_message):
        '''
        Description:
            Sets each line of this label's text to the corresponding item in the inputted list, adjusting width as needed
        Input:
            string list new_message: New text for this label, with each item corresponding to a line of text
        Output:
            None
        '''
        self.message = new_message
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) > self.ideal_width - scaling.scale_width(10, self.global_manager) and text_tools.message_width(text_line, self.font_size, self.font_name) + scaling.scale_width(10, self.global_manager) > self.width:
                self.width = scaling.scale_width(text_tools.message_width(text_line, self.font_size, self.font_name), self.global_manager) + scaling.scale_width(20, self.global_manager)# + 20
                self.image.width = self.width
                self.Rect.width = self.width
                self.image.set_image(self.image.image_id) #update width scaling
                self.image.Rect = self.Rect

    def draw(self):
        '''
        Description:
            Draws this label and draws its text on top of it
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                    (self.y + self.height - (text_line_index * self.font_size))))

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this label's tooltip to be the same as the text it displays
        '''
        self.set_tooltip(self.message)

class multi_line_label(label):
    '''
    Label that has multiple lines and moves to the next line when a line of text exceeds its width
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.ideal_width = input_dict['ideal_width']
        self.minimum_height = input_dict['minimum_height']
        self.original_y = input_dict['coordinates'][1]
        input_dict['minimum_width'] = input_dict['ideal_width']
        input_dict['height'] = self.minimum_height
        super().__init__(input_dict, global_manager)

    def draw(self):
        '''
        Description:
            Draws this label and draws each line of its text on top of it
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                    (self.y + self.height - (text_line_index * self.font_size))))

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this label's tooltip to be the same as the text it displays
        '''
        self.set_tooltip(self.message)

    def format_message(self):
        '''
        Description:
            Converts this label's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text
        Input:
            None
        Output:
            None
        '''
        new_message = []
        next_line = ''
        next_word = ''
        for index in range(len(self.message)):
            if not ((not (index + 2) > len(self.message) and self.message[index] + self.message[index + 1]) == '/n'): #don't add if /n
                if not (index > 0 and self.message[index - 1] + self.message[index] == '/n'): #if on n after /, skip
                    next_word += self.message[index]
            if self.message[index] == ' ':
                if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ''
                next_line += next_word
                next_word = ''
            elif (not (index + 2) > len(self.message) and self.message[index] + self.message[index + 1]) == '/n': #don't check for /n if at last index
                new_message.append(next_line)
                next_line = ''
                next_line += next_word
                next_word = ''
        if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
            new_message.append(next_line)
            next_line = ''
        next_line += next_word
        new_message.append(next_line)
        self.message = new_message
        new_height = len(new_message) * self.global_manager.get('font_size')
        if new_height > self.minimum_height:
            self.height = new_height

    def set_label(self, new_message):
        '''
        Description:
            Sets each line of this label's text to the corresponding item in the inputted list, adjusting width and height as needed
        Input:
            string list new_message: New text for this label, with each item corresponding to a line of text
        Output:
            None
        '''
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) > self.ideal_width:
                self.width = text_tools.message_width(text_line, self.font_size, self.font_name)
        self.image.update_state(self.x, self.y, self.width, self.height)
