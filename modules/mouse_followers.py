import pygame

from .images import free_image

class mouse_follower(free_image):
    def __init__(self, global_manager):
        x, y = pygame.mouse.get_pos()
        super().__init__('misc/targeting_mouse.png', (x, y), 50, 50, ['strategic', 'europe'], global_manager)
        
    def update(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.x -= self.width // 2
        self.y += self.height // 2
        global targeting_ability

    def draw(self):
        global targeting_ability
        global current_turn
        #if targeting_ability and current_turn == 'controlled':
        if self.global_manager.get('choosing_destination'):
            self.update()
            super().draw()
