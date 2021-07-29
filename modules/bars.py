import pygame

class bar():
    '''
    Rectangle that will be filled certain amounts by different colors based on how close its value is to being at its maximum
    '''
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, global_manager):
        '''
        Inputs:
            coordinates: tuple of two int variables representing pixel coordinates where the bar will appear
            minimum: int representing the minimum value that the bar can hold
            maximum: int representing the maximum value that the bar can hold
            current: int representing the value that the bar currently holds
            width: int representing the width of the bar in pixels
            height: int representing the height of the bar in pixels
            full_color: tuple of three int variables representing the RGB value of the bar's filled portion
            empty_color: tuple of three int variables representing the RGB value of the bar's unfilled portion
            global_manager: global_manager_template object
        '''
        self.global_manager = global_manager
        self.global_manager.get('bar_list').append(self)
        self.x, self.y = coordinates
        self.y = self.global_manager.get('display_height') - self.y
        self.minimum = minimum
        self.maximum = maximum
        self.current = current
        self.width = width
        self.height = height
        self.full_color = full_color
        self.empty_color = empty_color
        self.full_Rect = pygame.Rect(10, 10, 10, 10) #left top width height
        self.empty_Rect = pygame.Rect(10, 10, 10, 10)
        self.Rect = pygame.Rect(10, 10, 10, 10)

    def calculate_full_width(self):
        '''
        Inputs:
            none
        Outputs:
            Returns the width that the filled portion of the bar will be
        '''
        return(int((self.current/ self.maximum) * self.width))

    def calculate_empty_width(self, full_width):
        '''
        Inputs:
            none
        Outputs:
            Returns the width that the unfilled portion of the bar will be
        '''
        return(self.width - full_width)

    def update_bar(self):
        '''
        Inputs:
            none
        Outputs:
            Updates the bar's appearance to match its current value
        '''
        if self.current < self.minimum:
            self.current = self.minimum
        elif self.current > self.maximum:
            self.current = self.maximum
        self.full_Rect.x = self.x
        self.full_Rect.y = self.y
        self.full_Rect.width = self.calculate_full_width()
        self.full_Rect.height = self.height
        self.empty_Rect.height = self.height
        self.empty_Rect.width = self.calculate_empty_width(self.full_Rect.width)
        self.empty_Rect.x = self.x + self.full_Rect.width
        self.empty_Rect.y = self.y
        self.Rect.width = self.full_Rect.width + self.empty_Rect.width
        self.Rect.height = self.height
        self.Rect.x = self.full_Rect.x
        self.Rect.y = self.full_Rect.y

    def draw(self):
        '''
        Inputs:
            none
        Outputs:
            Draws this bar with an appearance based on its current value
        '''
        self.update_bar()
        if self.full_Rect.width > 0:
            pygame.draw.rect(game_display, self.full_color, self.full_Rect)
        if self.empty_Rect.width > 0:
            pygame.draw.rect(game_display, self.empty_color, self.empty_Rect)

    def touching_mouse(self):
        '''
        Inputs:
            none
        Outputs:
            Returns whether the bar is colliding with the mouse
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

class actor_bar(bar):
        '''
        Bar that is attached to an actor and appears over its image
        '''
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, actor, y_multiplier, global_manager):
        '''
        Inputs:
            coordinates: tuple of two int variables representing pixel coordinates where the bar will appear
            minimum: int representing the minimum value that the bar can hold
            maximum: int representing the maximum value that the bar can hold
            current: int representing the value that the bar currently holds
            width: int representing the width of the bar in pixels
            height: int representing the height of the bar in pixels
            full_color: tuple of three int variables representing the RGB value of the bar's filled portion
            empty_color: tuple of three int variables representing the RGB value of the bar's unfilled portion
            actor: actor object that this bar is attached to and will appear over
            y_multiplier: float value determining which part of the attached actor the bar will appear over: 1 will appear in the lowest 10th of the actor, 2 appears in the second-lowest 10th of the actor
            global_manager: global_manager_template object
        '''
        super().__init__(coordinates, minimum, maximum, current, width, height, full_color, empty_color, global_manager)
        self.actor = actor
        self.modes = self.actor.modes
        self.y_multiplier = y_multiplier
        
    def update_status(self):
        '''
        Inputs:
            none
        Outputs:
            Changes the bar's location depending on its actors location
        '''
        self.x = int(self.actor.image.x + (self.actor.image.width * 0.1))
        self.y = int(self.actor.image.y - (self.actor.image.height * (0.1 * self.y_multiplier)))
        self.width = int(self.actor.image.width * 0.8)
        self.height = int(self.actor.image.height * 0.075)
        
    def draw(self):
        '''
        Inputs:
            none
        Outputs:
            Draws the bar on top of its actor
        '''
        self.update_status()
        bar.draw(self)
        
    def draw_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            none, superclass is supposed to show current value as tooltip
        '''
        self.update_status()
