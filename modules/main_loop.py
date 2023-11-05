#Contains game's main loop

import time
import pygame
from .util import main_loop_utility, utility, text_utility, turn_management_utility, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

def main_loop():
    '''
    Description:
        Controls the main loop of the program, handling events such as mouse clicks and button presses, controlling timers, and drawing shapes and images. The program will end once this function stops
    Input:
        None
    Output:
        None
    '''
    while not flags.crashed:
        if status.displayed_notification == None:
            stopping = False
        constants.input_manager.update_input()
        for event in pygame.event.get():
            flags.capital = flags.r_shift or flags.l_shift
            flags.ctrl = flags.r_ctrl or flags.l_ctrl
            match event.type:
                case pygame.QUIT:
                    flags.crashed = True
                case pygame.KEYDOWN:
                    for current_button in status.button_list:
                        if (current_button.showing or (current_button.has_button_press_override and current_button.button_press_override())) and \
                            event.key == current_button.keybind_id and not flags.typing:
                            if current_button.has_released: #if stuck on loading, don't want multiple 'key down' events to repeat on_click - shouldn't on_click again until released
                                current_button.has_released = False
                                current_button.being_pressed = True
                                current_button.on_click()
                                current_button.showing_outline = True
                            break
                        else:
                            current_button.confirming = False
                            current_button.being_pressed = False
                    match event.key:
                        case pygame.K_RSHIFT:
                            flags.r_shift = True
                        case pygame.K_LSHIFT:
                            flags.l_shift = True
                        case pygame.K_RCTRL:
                            flags.r_ctrl = True
                        case pygame.K_LCTRL:
                            flags.l_ctrl = True
                        case pygame.K_ESCAPE:
                            flags.typing = False
                            constants.message = ''
                        case pygame.K_SPACE:
                            if flags.typing:
                                constants.message += ' '
                        case pygame.K_BACKSPACE:
                            if flags.typing:
                                constants.message = constants.message[:-1] #remove last character from message and set message to it
                        case _:
                            if event.key == pygame.K_p and constants.effect_manager.effect_active('debug_print'):
                                main_loop_utility.debug_print()
                    if flags.typing and event.key in constants.key_codes:
                        if flags.capital:
                            constants.message += constants.uppercase_key_values[constants.key_codes.index(event.key)]
                        else:
                            constants.message += constants.lowercase_key_values[constants.key_codes.index(event.key)]

                case pygame.KEYUP:
                    for current_button in status.button_list:
                        if not flags.typing or current_button.keybind_id == pygame.K_TAB or current_button.keybind_id == pygame.K_e:
                            if current_button.has_keybind:
                                if event.key == current_button.keybind_id:
                                    current_button.on_release()
                                    current_button.has_released = True
                                    current_button.being_pressed = False
                    match event.key:
                        case pygame.K_RSHIFT:
                            flags.r_shift = False
                        case pygame.K_LSHIFT:
                            flags.l_shift = False
                        case pygame.K_LCTRL:
                            flags.l_ctrl = False
                        case pygame.K_RCTRL:
                            flags.r_ctrl = False
                        case pygame.K_RETURN:
                            if flags.typing:
                                if constants.input_manager.taking_input:
                                    constants.input_manager.taking_input = False
                                    text_utility.print_to_screen('Response: ' + constants.message)
                                else:
                                    text_utility.print_to_screen(constants.message)
                                flags.typing = False
                                constants.message = ''
                            else:
                                flags.typing = True

                case constants.music_endevent:
                    constants.sound_manager.song_done()

        flags.old_lmb_down, flags.old_rmb_down, flags.old_mmb_down = flags.lmb_down, flags.rmb_down, flags.mmb_down
        flags.lmb_down, flags.mmb_down, flags.rmb_down = pygame.mouse.get_pressed()

        if flags.old_rmb_down != flags.rmb_down: #if rmb changes
            if not flags.rmb_down: #if user just released rmb
                clicked_button = False
                stopping = False
                if status.current_instructions_page == None:
                    for current_button in status.button_list:#here
                        if current_button.touching_mouse() and current_button.showing and (current_button.in_notification) and not stopping: #if notification, click before other buttons
                            current_button.on_rmb_click()
                            current_button.on_rmb_release()
                            clicked_button = True
                            stopping = True
                            break
                else:
                    if status.current_instructions_page.touching_mouse() and status.current_instructions_page.showing:
                        status.current_instructions_page.on_rmb_click()
                        clicked_button = True
                        stopping = True
                if not stopping:
                    for current_button in status.button_list:
                        if current_button.touching_mouse() and current_button.showing:
                            current_button.on_rmb_click()
                            current_button.on_rmb_release()
                            clicked_button = True
                main_loop_utility.manage_rmb_down(clicked_button)

        if flags.old_lmb_down != flags.lmb_down: #if lmb changes
            if not flags.lmb_down: #if user just released lmb
                clicked_button = False #if any button, including a panel, is clicked, do not deselect units
                allow_on_click = True #certain buttons, like panels, allow clicking on another button at the same time
                stopping = False
                if status.current_instructions_page == None:
                    for current_button in status.button_list:#here
                        if current_button.touching_mouse() and current_button.showing and (current_button.in_notification) and not stopping: #if notification, click before other buttons
                            current_button.on_click()
                            current_button.on_release()
                            clicked_button = True
                            allow_on_click = False
                            stopping = True
                            break
                else:
                    if status.current_instructions_page.touching_mouse() and status.current_instructions_page.showing: #if instructions, click before other buttons
                        status.current_instructions_page.on_click()
                        clicked_button = True
                        allow_on_click = False
                        stopping = True
                        break

                if not stopping:
                    for current_button in status.button_list:
                        if current_button.touching_mouse() and current_button.showing and allow_on_click: #only click 1 button at a time
                            if current_button.on_click(): #if on_click has return value, nothing happened - allow other buttons to click but do not deselect units
                                allow_on_click = True
                            else:
                                allow_on_click = False
                            current_button.on_release()
                            clicked_button = True
                            #break
                main_loop_utility.manage_lmb_down(clicked_button) #whether button was clicked or not determines whether characters are deselected

        if (flags.lmb_down or flags.rmb_down):
            for current_button in status.button_list:
                if current_button.touching_mouse() and current_button.showing:
                    current_button.showing_outline = True
                elif not current_button.being_pressed:
                    current_button.showing_outline = False
        else:
            for current_button in status.button_list:
                if current_button.has_released:
                    current_button.showing_outline = False

        if not flags.loading:
            main_loop_utility.update_display()
        else:
            main_loop_utility.draw_loading_screen()
        constants.current_time = time.time()
        if constants.current_time - constants.last_selection_outline_switch > 1:
            flags.show_selection_outlines = not flags.show_selection_outlines
            constants.last_selection_outline_switch = constants.current_time
        constants.event_manager.update(constants.current_time)
        if not flags.player_turn and constants.previous_turn_time + constants.end_turn_wait_time <= constants.current_time: #if enough time has passed based on delay from previous movement
            enemy_turn_done = True
            for enemy in status.npmob_list:
                if not enemy.turn_done:
                    enemy_turn_done = False
                    break
            if enemy_turn_done:
                flags.player_turn = True
                flags.enemy_combat_phase = True
                turn_management_utility.manage_combat()
            else:
                current_enemy = status.enemy_turn_queue[0]
                removed = False
                spawning = False
                did_nothing = False
                moving = False
                if current_enemy.npmob_type == 'native_warriors' and current_enemy.despawning:
                    if current_enemy.selected or not current_enemy.visible():
                        current_enemy.remove_complete()
                        removed = True
                        
                elif current_enemy.npmob_type == 'native_warriors' and current_enemy.creation_turn == constants.turn: #if unit just created
                    spawn_cell = current_enemy.grids[0].find_cell(current_enemy.x, current_enemy.y)
                    if (status.minimap_grid.center_x, status.minimap_grid.center_y) == (current_enemy.x, current_enemy.y) and spawn_cell.visible: #if camera just moved to spawn location to show spawning
                        spawning = True
                        current_enemy.show_images()
                        current_enemy.select()
                        current_enemy.attack_on_spawn()
                        current_enemy.turn_done = True
                    else: #if camera did not move to spawn location
                        spawning = True
                        if spawn_cell.visible: #if spawn location visible but camera hasn't moved there yet, move camera there
                            status.minimap_grid.calibrate(current_enemy.x, current_enemy.y)
                        else: #if spawn location not visible, end turn
                            current_enemy.show_images()
                            current_enemy.turn_done = True 
            
                elif not current_enemy.visible(): #if not just spawned and hidden, do action without displaying
                    if current_enemy.selected:
                        actor_utility.deselect_all()
                    current_enemy.end_turn_move()
                    moving = True
                    
                elif current_enemy.selected: #if enemy is selected and did not just spawn, move it while minimap follows
                    if not current_enemy.creation_turn == constants.turn: #don't do anything on first turn, but still move camera to spawn location if visible
                        current_enemy.end_turn_move() #do_turn()
                        moving = True
                        if current_enemy.visible():
                            if not current_enemy.selected:
                                current_enemy.select()
                                status.minimap_grid.calibrate(current_enemy.x, current_enemy.y)
                            else:
                                status.minimap_grid.calibrate(current_enemy.x, current_enemy.y)
                        else:
                            actor_utility.deselect_all()
                    else:
                        current_enemy.turn_done = True
                    
                if (not (removed or spawning)) and (not current_enemy.creation_turn == constants.turn) and current_enemy.visible(): #if unit visible and not selected, start its turn
                    if current_enemy.npmob_type == 'native_warriors' and current_enemy.find_closest_target() == 'none' and not current_enemy.despawning: #if native warriors have no target, they stand still and no movement is shown
                        did_nothing = True
                        current_enemy.turn_done = True
                    
                    elif current_enemy.npmob_type == 'beast' and current_enemy.find_closest_target == current_enemy.images[0].current_cell and not current_enemy.images[0].current_cell.has_pmob():
                        #if beasts stand still and don't attack anything, no movement is shown
                        did_nothing = True
                        current_enemy.turn_done = True
                    elif current_enemy.visible(): #if unit will do an action, move the camera to it and select it
                        current_enemy.select()
                        status.minimap_grid.calibrate(current_enemy.x, current_enemy.y)
                                                                     
                elif current_enemy.creation_turn == constants.turn and not spawning: #if enemy visible but just spawned, end turn
                    did_nothing = True
                    current_enemy.turn_done = True

                if removed: #show unit despawning if visible
                    current_enemy.turn_done = True
                    if not current_enemy.visible():
                        constants.end_turn_wait_time = 0
                    else:
                        constants.end_turn_wait_time = 1
                    status.enemy_turn_queue.pop(0)
                    
                else: #If unit visible, have short delay depending on action taken to let user see it
                    if (not spawning) and (did_nothing or not current_enemy.visible()): #do not wait if not visible or nothing to show, exception for spawning units, which may not be visible as user watches them spawn
                        constants.end_turn_wait_time = 0
                    elif spawning and not current_enemy.grids[0].find_cell(current_enemy.x, current_enemy.y).visible: #do not wait if spawning unit won't be visible even after it spawns
                        constants.end_turn_wait_time = 0
                    elif moving and not enemy.turn_done:#if will move again after this
                        constants.end_turn_wait_time = 0.25
                    else: #if done with turn
                        constants.end_turn_wait_time = 0.5

                    if current_enemy.turn_done:
                        status.enemy_turn_queue.pop(0)
            if constants.effect_manager.effect_active('fast_turn'):
                constants.end_turn_wait_time = 0
            constants.previous_turn_time = time.time()
    pygame.quit()
