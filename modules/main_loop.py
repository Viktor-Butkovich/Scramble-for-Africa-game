import pygame
import time
from . import scaling
from . import text_tools

def update_display(global_manager): #to do: transfer if current game mode in modes to draw functions, do not manage it here
    if global_manager.get('loading'):
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 1) #makes it faster if the program starts repeating this part
        draw_loading_screen(global_manager)
    else:
        global_manager.get('game_display').fill((125, 125, 125))
        possible_tooltip_drawers = []

        for grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in grid.modes:
                grid.draw()

        for image in global_manager.get('image_list'):
            image.has_drawn = False

        global_manager.get('background_image').draw()
        global_manager.get('background_image').has_drawn = True
            
        for tile in global_manager.get('tile_list'):
            if global_manager.get('current_game_mode') in tile.image.modes and not tile in global_manager.get('overlay_tile_list'):
                tile.image.draw()
                tile.image.has_drawn = True
        
        for image in global_manager.get('image_list'):
            if not image.has_drawn:
                if global_manager.get('current_game_mode') in image.modes:
                    image.draw()
                    image.has_drawn = True
        for bar in global_manager.get('bar_list'):
            if global_manager.get('current_game_mode') in bar.modes:
                bar.draw()
        for overlay_tile in global_manager.get('overlay_tile_list'):
            if global_manager.get('current_game_mode') in overlay_tile.image.modes:
                overlay_tile.image.draw()
                overlay_tile.image.has_drawn = True
                
        for grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in grid.modes:
                grid.draw_grid_lines()

        for mob in global_manager.get('mob_list'):
            for current_image in mob.images:
                if mob.selected and global_manager.get('current_game_mode') in current_image.modes:
                    mob.draw_outline()
            
        for actor in global_manager.get('actor_list'):
            #if show_selected and current_game_mode in actor.image.modes:
            #    if actor.selected:
            #        pygame.draw.rect(game_display, color_dict['light gray'], (actor.image.outline), actor.image.outline_width)
            #    elif actor.targeted:
            #        pygame.draw.rect(game_display, color_dict['red'], (actor.image.outline), actor.image.outline_width)
            if actor.can_show_tooltip():
                possible_tooltip_drawers.append(actor) #only one of these will be drawn to prevent overlapping tooltips

        for button in global_manager.get('button_list'):
            if not button in global_manager.get('notification_list'): #notifications are drawn later
                button.draw()
            if button.can_show_tooltip():
                possible_tooltip_drawers.append(button) #only one of these will be drawn to prevent overlapping tooltips
        for label in global_manager.get('label_list'):
            if not label in global_manager.get('notification_list'):
                label.draw()
        for notification in global_manager.get('notification_list'):
            if not notification == global_manager.get('current_instructions_page'):
                notification.draw()
        if global_manager.get('show_text_box'):
            draw_text_box(global_manager)

        if global_manager.get('making_mouse_box'):
            mouse_destination_x, mouse_destination_y = pygame.mouse.get_pos()
            global_manager.set('mouse_destination_x', mouse_destination_x + 4)
            global_manager.set('mouse_destination_y', mouse_destination_y + 4)
            #mouse_destination_y += 4
            if abs(mouse_destination_x - global_manager.get('mouse_origin_x')) > 3 or (mouse_destination_y - global_manager.get('mouse_origin_y')) > 3:
                mouse_box_color = 'dark gray'
                pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')[mouse_box_color], (min(global_manager.get('mouse_destination_x'), global_manager.get('mouse_origin_x')), min(global_manager.get('mouse_destination_y'), global_manager.get('mouse_origin_y')), abs(global_manager.get('mouse_destination_x') - global_manager.get('mouse_origin_x')), abs(global_manager.get('mouse_destination_y') - global_manager.get('mouse_origin_y'))), 3)
            
        if not global_manager.get('current_instructions_page') == 'none':
            global_manager.get('current_instructions_page').draw()
        if not (global_manager.get('old_mouse_x'), global_manager.get('old_mouse_y')) == pygame.mouse.get_pos():
            global_manager.set('mouse_moved_time', time.time())
            old_mouse_x, old_mouse_y = pygame.mouse.get_pos()
            global_manager.set('old_mouse_x', old_mouse_x)
            global_manager.set('old_mouse_y', old_mouse_y)
        if time.time() > global_manager.get('mouse_moved_time') + 0.15:#show tooltip when mouse is still
            manage_tooltip_drawing(possible_tooltip_drawers, global_manager)
        pygame.display.update()
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 3)

def draw_loading_screen(global_manager):
    global_manager.get('game_display').fill((125, 125, 125))
    global_manager.get('loading_image').draw()
    pygame.display.update()    
    if global_manager.get('loading_start_time') + 2 < time.time():#max of 1 second, subtracts 1 in update_display to lower loading screen showing time
        global_manager.set('loading', False)

def manage_tooltip_drawing(possible_tooltip_drawers, global_manager): #to do: if near bottom of screen, make first tooltip appear higher and have last tooltip on bottom of screen
    possible_tooltip_drawers_length = len(possible_tooltip_drawers)
    if possible_tooltip_drawers_length == 0:
        return()
    elif possible_tooltip_drawers_length == 1:
        possible_tooltip_drawers[0].draw_tooltip(60)
    else:
        tooltip_index = 1
        stopping = False
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == global_manager.get('current_instructions_page'):
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                stopping = True
            if (possible_tooltip_drawer in global_manager.get('notification_list')) and not stopping:
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                tooltip_index += 1

def draw_text_box(global_manager):
    #if global_manager.get('current_game_mode') == 'strategic': #obsolete, text box width could be different on different game modes
    #    greatest_width = 300
    #else:
    greatest_width = 300
    greatest_width = scaling.scale_width(greatest_width, global_manager)
    max_screen_lines = (global_manager.get('default_display_height') // global_manager.get('font_size')) - 1
    max_text_box_lines = (global_manager.get('text_box_height') // global_manager.get('font_size')) - 1
    text_index = 0 #probably obsolete, to do: verify that this is obsolete
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            if text_tools.message_width(global_manager.get('text_list')[-text_index - 1], global_manager.get('font_size'), 'Times New Roman') > greatest_width:
                greatest_width = text_tools.message_width(global_manager.get('text_list')[-text_index - 1], global_manager.get('font_size'), 'Times New Roman') #manages the width of already printed text lines
    if global_manager.get('input_manager').taking_input:
        if text_tools.message_width("Response: " + global_manager.get('message'), font_size, 'Times New Roman') > greatest_width: #manages width of user input
            greatest_width = text_tools.message_width("Response: " + global_manager.get('message'), global_manager.get('font_size'), 'Times New Roman')
    else:
        if text_tools.message_width(global_manager.get('message'), global_manager.get('font_size'), 'Times New Roman') > greatest_width: #manages width of user input
            greatest_width = text_tools.message_width(global_manager.get('message'), global_manager.get('font_size'), 'Times New Roman')
    text_box_width = greatest_width + 10
    x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
    pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['white'], (x, y, text_box_width, global_manager.get('text_box_height'))) #draws white rect to prevent overlapping
    if global_manager.get('typing'):
        x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
        pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['red'], (x, y, text_box_width, global_manager.get('text_box_height')), 3)
        pygame.draw.line(global_manager.get('game_display'), global_manager.get('color_dict')['red'], (0, global_manager.get('display_height') - (global_manager.get('font_size') + 5)), (text_box_width, global_manager.get('display_height') - (global_manager.get('font_size') + 5)))
    else:
        x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
        pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['black'], (x, y, text_box_width, global_manager.get('text_box_height')), 3)
        #x, y = (0, default_display_height - (font_size))
        pygame.draw.line(global_manager.get('game_display'), global_manager.get('color_dict')['black'], (0, global_manager.get('display_height') - (global_manager.get('font_size') + 5)), (text_box_width, global_manager.get('display_height') - (global_manager.get('font_size') + 5)))

    global_manager.set('text_list', text_tools.manage_text_list(global_manager.get('text_list'), max_screen_lines)) #number of lines
    
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            textsurface = global_manager.get('myfont').render(global_manager.get('text_list')[(-1 * text_index) - 1], False, (0, 0, 0))
            global_manager.get('game_display').blit(textsurface,(10, (-1 * global_manager.get('font_size') * text_index) + global_manager.get('display_height') - ((2 * global_manager.get('font_size')) + 5)))
    if global_manager.get('input_manager').taking_input:
        textsurface = global_manager.get('myfont').render('Response: ' + global_manager.get('message'), False, (0, 0, 0))
    else:
        textsurface = global_manager.get('myfont').render(global_manager.get('message'), False, (0, 0, 0))
    global_manager.get('game_display').blit(textsurface,(10, global_manager.get('display_height') - (global_manager.get('font_size') + 5)))

def manage_rmb_down(clicked_button, global_manager):
    manage_lmb_down(clicked_button, global_manager)
    
def manage_lmb_down(clicked_button, global_manager): #to do: seems to be called when lmb/rmb is released rather than pressed, clarify name
    if global_manager.get('making_mouse_box'): 
        if not clicked_button:#do not do selecting operations if user was trying to click a button
            for mob in global_manager.get('mob_list'):
                mob.selected = False
                for current_image in mob.images:
                    if current_image.Rect.colliderect((min(global_manager.get('mouse_destination_x'), global_manager.get('mouse_origin_x')), min(global_manager.get('mouse_destination_y'), global_manager.get('mouse_origin_y')), abs(global_manager.get('mouse_destination_x') - global_manager.get('mouse_origin_x')), abs(global_manager.get('mouse_destination_y') - global_manager.get('mouse_origin_y')))):
                        mob.selected = True
        global_manager.set('making_mouse_box', False) #however, stop making mouse box regardless of if a button was pressed
