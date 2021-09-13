import pygame

def rect_to_surface(rect):
    '''
    Input:
        a pygame Rect object
    Output:
        Converts the inputted Rect to a pygame Surface and returns it, allowing an image or text to be drawn on it
    '''
    return pygame.Surface((rect.width, rect.height))

def display_image(image, x, y, global_manager):
    '''
    Input:
        a pygame image object, the pixel x coordinate at which to display the image, the pixel y coordinate at which to display the image, global_manager_template object
    Output:
        Draws the inputted image at the inputted coordinates
    '''
    global_manager.get('game_display').blit(image, (x, y))

def display_image_angle(image, x, y, angle, global_manager):
    '''
    Input:
        a pygame image object, the pixel x coordinate at which to display the image, the pixel y coordinate at which to display the image, the angle at which to draw the image global_manager_template object
    Output:
        Draws inputted image at the inputted coordinates, turned at the inputted angle
    '''
    topleft = (x, y)
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    global_manager.get('game_display').blit(rotated_image, new_rect.topleft)
