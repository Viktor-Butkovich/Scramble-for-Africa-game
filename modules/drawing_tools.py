import pygame

def rect_to_surface(rect):
    return pygame.Surface((rect.width, rect.height))

def display_image(image, x, y, global_manager):
    global_manager.get('game_display').blit(image, (x, y))

def display_image_angle(image, x, y, angle, global_manager):
    topleft = (x, y)
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    global_manager.get('game_display').blit(rotated_image, new_rect.topleft)
