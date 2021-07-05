import pygame

class bar():
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, global_manager):
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
        return(int((self.current/ self.maximum) * self.width))

    def calculate_empty_width(self, full_width):
        return(self.width - full_width)

    def update_bar(self):
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
        self.update_bar()
        if self.full_Rect.width > 0:
            pygame.draw.rect(game_display, self.full_color, self.full_Rect)
        if self.empty_Rect.width > 0:
            pygame.draw.rect(game_display, self.empty_color, self.empty_Rect)

    def touching_mouse(self):
        if self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

class actor_bar(bar):
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, actor, y_multiplier, global_manager):
        super().__init__(coordinates, minimum, maximum, current, width, height, full_color, empty_color, global_manager)
        self.actor = actor
        self.modes = self.actor.modes
        self.y_multiplier = y_multiplier
        
    def update_status(self):
        self.x = int(self.actor.image.x + (self.actor.image.width * 0.1))
        self.y = int(self.actor.image.y - (self.actor.image.height * (0.1 * self.y_multiplier)))
        self.width = int(self.actor.image.width * 0.8)
        self.height = int(self.actor.image.height * 0.075)
        
    def draw(self):
        self.update_status()
        bar.draw(self)
        
    def draw_tooltip(self):
        self.update_status()
