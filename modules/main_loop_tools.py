import pygame
import time
from . import scaling
from . import text_tools
from . import actor_utility

def update_display(global_manager): #to do: transfer if current game mode in modes to draw functions, do not manage it here
    '''
    Input:
        global_manager_template object
    Output:
        Draws all images and shapes and calls the drawing of the text box and tooltips
    '''
    if global_manager.get('loading'):
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 1) #makes it faster if the program starts repeating this part
        draw_loading_screen(global_manager)
    else:
        global_manager.get('game_display').fill((125, 125, 125))
        possible_tooltip_drawers = []

        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                current_grid.draw()

        for current_image in global_manager.get('image_list'):
            current_image.has_drawn = False

        for current_background_image in global_manager.get('background_image_list'):
            current_background_image.draw()
            current_background_image.has_drawn = True
            
        for current_tile in global_manager.get('tile_list'):
            if global_manager.get('current_game_mode') in current_tile.image.modes and not current_tile in global_manager.get('overlay_tile_list'):
                current_tile.image.draw()
                current_tile.image.has_drawn = True
        
        for current_image in global_manager.get('image_list'):
            if not current_image.has_drawn:
                if global_manager.get('current_game_mode') in current_image.modes:
                    current_image.draw()
                    current_image.has_drawn = True
        for current_bar in global_manager.get('bar_list'):
            if global_manager.get('current_game_mode') in current_bar.modes:
                current_bar.draw()
                
        for current_overlay_tile in global_manager.get('overlay_tile_list'):
            if global_manager.get('current_game_mode') in current_overlay_tile.image.modes:
                current_overlay_tile.image.draw()
                current_overlay_tile.image.has_drawn = True
                
        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                current_grid.draw_grid_lines()

        for current_mob in global_manager.get('mob_list'):
            for current_image in current_mob.images:
                if current_mob.selected and global_manager.get('current_game_mode') in current_image.modes:
                    current_mob.draw_outline()
            if current_mob.can_show_tooltip():
                for same_tile_mob in current_mob.images[0].current_cell.contained_mobs:
                    if same_tile_mob.can_show_tooltip() and not same_tile_mob in possible_tooltip_drawers: #if multiple mobs are in the same tile, draw their tooltips in order
                        possible_tooltip_drawers.append(same_tile_mob)
            
        for current_actor in global_manager.get('actor_list'):
            if current_actor.can_show_tooltip() and not current_actor in possible_tooltip_drawers:
                possible_tooltip_drawers.append(current_actor) #only one of these will be drawn to prevent overlapping tooltips

        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                for current_cell in current_grid.cell_list:
                    current_cell.show_num_mobs()

        for current_button in global_manager.get('button_list'):
            if not (current_button in global_manager.get('button_list') and current_button.in_notification): #notifications are drawn later
                current_button.draw()
                if current_button.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                    possible_tooltip_drawers = [current_button]
                
        for current_label in global_manager.get('label_list'):
            if not (current_label in global_manager.get('button_list') and current_label.in_notification):
                current_label.draw()
                
        for current_button in global_manager.get('button_list'): #draws notifications and buttons attached to notifications
            if current_button.in_notification and not current_button == global_manager.get('current_instructions_page'):
                current_button.draw()
                if current_button.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                    possible_tooltip_drawers = [current_button]#notifications have priority over buttons and will be shown first
                
        if global_manager.get('show_text_box'):
            draw_text_box(global_manager)

        if global_manager.get('making_mouse_box'):
            mouse_destination_x, mouse_destination_y = pygame.mouse.get_pos()
            global_manager.set('mouse_destination_x', mouse_destination_x + 4)
            global_manager.set('mouse_destination_y', mouse_destination_y + 4)
            if abs(mouse_destination_x - global_manager.get('mouse_origin_x')) > 3 or (mouse_destination_y - global_manager.get('mouse_origin_y')) > 3:
                mouse_box_color = 'white'
                pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')[mouse_box_color], (min(global_manager.get('mouse_destination_x'), global_manager.get('mouse_origin_x')), min(global_manager.get('mouse_destination_y'), global_manager.get('mouse_origin_y')), abs(global_manager.get('mouse_destination_x') - global_manager.get('mouse_origin_x')), abs(global_manager.get('mouse_destination_y') - global_manager.get('mouse_origin_y'))), 3)
            
        if not global_manager.get('current_instructions_page') == 'none':
            instructions_page = global_manager.get('current_instructions_page')
            instructions_page.draw()
            if instructions_page.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                possible_tooltip_drawers = [instructions_page]#instructions have priority over everything
        if not (global_manager.get('old_mouse_x'), global_manager.get('old_mouse_y')) == pygame.mouse.get_pos():
            global_manager.set('mouse_moved_time', time.time())
            old_mouse_x, old_mouse_y = pygame.mouse.get_pos()
            global_manager.set('old_mouse_x', old_mouse_x)
            global_manager.set('old_mouse_y', old_mouse_y)
        if time.time() > global_manager.get('mouse_moved_time') + 0.15:#show tooltip when mouse is still
            manage_tooltip_drawing(possible_tooltip_drawers, global_manager)
        pygame.display.update()
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 3)

def action_possible(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Returns whether the player is allowed to do anything, preventing actions from being done before other actions are done
    '''
    if global_manager.get('ongoing_exploration'):
        return(False)
    elif global_manager.get('making_choice'):
        return(False)
    elif not global_manager.get('player_turn'):
        return(False)
    return(True)

def draw_loading_screen(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Draws loading screen while the game is still loading
    '''
    global_manager.get('game_display').fill((125, 125, 125))
    global_manager.get('loading_image').draw()
    pygame.display.update()    
    if global_manager.get('loading_start_time') + 2 < time.time():#max of 1 second, subtracts 1 in update_display to lower loading screen showing time
        global_manager.set('loading', False)

def manage_tooltip_drawing(possible_tooltip_drawers, global_manager): #to do: if near bottom of screen, make first tooltip appear higher and have last tooltip on bottom of screen
    '''
    Input:
        list of objects that can draw tooltips based on the mouse position and their status, global_manager_template object
    Output:
        Draws tooltips of objecst that can draw tooltips, with tooltips beyond the first appearing at progressively lower locations
    '''
    possible_tooltip_drawers_length = len(possible_tooltip_drawers)
    font_size = global_manager.get('font_size')
    y_displacement = font_size * 2
    if possible_tooltip_drawers_length == 0:
        return()
    elif possible_tooltip_drawers_length == 1:
        possible_tooltip_drawers[0].draw_tooltip(y_displacement)
    else:
        stopping = False
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == global_manager.get('current_instructions_page'):
                possible_tooltip_drawer.draw_tooltip(scaling.scale_height(y_displacement, global_manager))
                y_displacement += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += font_size
                stopping = True
            if (possible_tooltip_drawer in global_manager.get('button_list') and possible_tooltip_drawer.in_notification) and not stopping:
                possible_tooltip_drawer.draw_tooltip(scaling.scale_height(y_displacement, global_manager))
                y_displacement += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += font_size
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                possible_tooltip_drawer.draw_tooltip(scaling.scale_height(y_displacement, global_manager))
                y_displacement += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += font_size

def draw_text_box(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Draws the text box and any text it contains
    '''
    greatest_width = 300
    greatest_width = scaling.scale_width(greatest_width, global_manager)
    max_screen_lines = (global_manager.get('default_display_height') // global_manager.get('font_size')) - 1
    max_text_box_lines = (global_manager.get('text_box_height') // global_manager.get('font_size')) - 1
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
    '''
    Input:
        boolean representing whether a button was just clicked (not pressed), global_manager_template object
    Output:
        Does nothing if the user was clicking a button, cycles through the mobs in a clicked location if user was not clicking a button, changing which mob is shown
    '''
    if (not clicked_button) and action_possible(global_manager):
        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                for current_cell in current_grid.cell_list:
                    if current_cell.touching_mouse():
                        if len(current_cell.contained_mobs) > 1:
                            moved_mob = current_cell.contained_mobs[1]
                            for current_image in moved_mob.images:
                                if not current_image.current_cell == 'none':
                                    while not moved_mob == current_image.current_cell.contained_mobs[0]:
                                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
                            global_manager.set('show_selection_outlines', True)
                            global_manager.set('last_selection_outline_switch', time.time())
                            global_manager.get('minimap_grid').calibrate(moved_mob.x, moved_mob.y)
                            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_cell.tile)
            
    
def manage_lmb_down(clicked_button, global_manager): #to do: seems to be called when lmb/rmb is released rather than pressed, clarify name
    '''
    Input:
        boolean representing whether a button was just clicked (not pressed), global_manager_template object
    Output:
        Will do nothing if the user was clicking a button.
        If the user was not clicking a button and a mouse box was being drawn, the mouse box will stop being drawn and all mobs within it will be selected.
        If the user was not clicking a button, was not drawing a mouse box, and clicked on a cell, the top mob (the displayed one) in that cell will be selected.
        If the user was not clicking a button, any mobs not just selected will be unselected. However, if shift is being held down, no mobs will be unselected.
    '''
    if (not clicked_button) and action_possible(global_manager):#do not do selecting operations if user was trying to click a button
        mouse_x, mouse_y = pygame.mouse.get_pos()
        selected_new_mob = False
        #for current_mob in global_manager.get('mob_list'): #regardless of whether a box is made or not, deselect mobs if not holding shift
        #    if (not global_manager.get('capital')) and global_manager.get('current_game_mode') in current_mob.modes: #if holding shift, do not deselect
        #        current_mob.selected = False
        if (not global_manager.get('capital')):
            actor_utility.deselect_all(global_manager)
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), 'none')
                    
        if abs(global_manager.get('mouse_origin_x') - mouse_x) < 5 and abs(global_manager.get('mouse_origin_y') - mouse_y) < 5: #if clicked rather than mouse box drawn, only select top mob of cell
            for current_grid in global_manager.get('grid_list'):
                if global_manager.get('current_game_mode') in current_grid.modes:
                    for current_cell in current_grid.cell_list:
                        if current_cell.touching_mouse():
                            if len(current_cell.contained_mobs) > 0:
                                selected_new_mob = True
                                current_cell.contained_mobs[0].select()
                                if current_grid == global_manager.get('minimap_grid'):
                                    main_x, main_y = global_manager.get('minimap_grid').get_main_grid_coordinates(current_cell.x, current_cell.y) #main_x, main_y = global_manager.get('strategic_map_grid').get_main_grid_coordinates(current_cell.x, current_cell.y)
                                    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('strategic_map_grid').find_cell(main_x, main_y).tile)
                                else: #elif current_grid == global_manager.get('strategic_map_grid'):
                                    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_cell.tile)

        else:
            for clicked_mob in global_manager.get('mob_list'):
                for current_image in clicked_mob.images: #if mouse box drawn, select all mobs within mouse box
                    if current_image.can_show() and current_image.Rect.colliderect((min(global_manager.get('mouse_destination_x'), global_manager.get('mouse_origin_x')), min(global_manager.get('mouse_destination_y'), global_manager.get('mouse_origin_y')), abs(global_manager.get('mouse_destination_x') - global_manager.get('mouse_origin_x')), abs(global_manager.get('mouse_destination_y') - global_manager.get('mouse_origin_y')))):
                        selected_new_mob = True
                        for current_mob in current_image.current_cell.contained_mobs: #mobs that can't show but are in same tile are selected
                            #if (not ((current_mob in global_manager.get('officer_list') or current_mob in global_manager.get('worker_list')) and current_mob.in_group)): #do not select workers or officers in group, should be unnecessary because they are removed from cell when in group
                            current_mob.select()#if mob can show
                            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_mob.images[0].current_cell.tile)
        if selected_new_mob:
            selected_list = actor_utility.get_selected_list(global_manager)
            if len(selected_list) == 1 and selected_list[0].grids[0] == global_manager.get('minimap_grid').attached_grid: #do not calibrate minimap if selecting someone outside of attached grid
                global_manager.get('minimap_grid').calibrate(selected_list[0].x, selected_list[0].y)
                
        else:
            if abs(global_manager.get('mouse_origin_x') - mouse_x) < 5 and abs(global_manager.get('mouse_origin_y') - mouse_y) < 5: #only move minimap if clicking, not when making box
                breaking = False
                for current_grid in global_manager.get('grid_list'): #if grid clicked, move minimap to location clicked
                    if current_grid.can_show():
                        for current_cell in current_grid.cell_list:
                            if current_cell.touching_mouse():
                                if current_grid == global_manager.get('minimap_grid'): #if minimap clicked, calibrate to corresponding place on main map
                                    if not current_cell.terrain == 'none': #if off map, do not move minimap there
                                        main_x, main_y = current_grid.get_main_grid_coordinates(current_cell.x, current_cell.y)
                                        global_manager.get('minimap_grid').calibrate(main_x, main_y)
                                elif current_grid == global_manager.get('strategic_map_grid'):
                                    global_manager.get('minimap_grid').calibrate(current_cell.x, current_cell.y)
                                else: #if abstract grid, show the inventory of the tile clicked without calibrating minimap
                                    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_grid.cell_list[0].tile)
                                breaking = True
                                break
                            if breaking:
                                break
                        if breaking:
                            break
    global_manager.set('making_mouse_box', False) #however, stop making mouse box regardless of if a button was pressed

