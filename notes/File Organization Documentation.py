'''
SFA folder

    Instructions.docx

    graphics folder
        locations
        misc
        mobs
        scenery
        textures

    text folder
        flavor_explorer.csv

    Scramble_for_Africa.py
        imports pygame, time, scaling, main_loop, notification_tools, images, buttons, game_transitions, grids
        imports data_managers, actor_utility, groups, europe_transactions, labels, actor_match_tools
        
    modules folder

        utility.py
            def find_object_distance
            def find_coordinate_distance
            def remove_from_list
            def toggle
            def generate_article
            def add_to_message

        tiles.py
            imports pygame, images, utility, actor_utility, actors
            class tile(actor)
                class abstract_tile
                class veteran_icon
                class overlay_tile

        text_tools.py
            imports pygame
            def message_width
            def get_input
            def text
            def manage_text_list
            def print_to_screen
            def print_to_previous_message
            def clear_message

        scaling.py
            def scale_coordinates
            def scale_width
            def scale_height

        notifications.py
            imports labels, images, text_tools, utility, scaling, actor_utility
            class notification(label)
                class dice_rolling_notification
                class exploration_notification

        notification_tools.py
            imports notifications
            def display_notification
            def show_tutorial_notifications

        mobs.py
            imports pygame, time, images, text_tools, utility, actor_utility, actors, tiles
            class mob(actor)
                class worker
                class officer
                    class explorer

        main_loop_tools.py
            imports pygame, time, scaling, text_tools, actor_utility
            def update_display
            def action_possible
            def draw_loading_screen
            def manage_tooltip_drawing
            def draw_text_box
            def manage_rmb_down
            def manage_lmb_down

        main_loop.py
            imports time, pygame, main_loop_tools, utility, text_tools
            def main_loop

        labels.py
            imports pygame, buttons, scaling, text_tools, utility
            class label(button)
                class instructions_page

        instructions.py
            imports labels
            def display_instructions_page

        images.py
            imports pygame, time, utility, drawing_tools, text_tools
            class free_image
                class loading_image_template
            class actor_iamge
                class mob_image
                class button_image
                class tile_image
                    class veteran_icon_image

        groups.py
            imports time, mobs, tiles, buttons, actor_utility, text_tools, dice_utility, utility, notification_tools
            imports dice, scaling, main_loop_tools
            class group(mob)
                class expedition
            class merge_button(button)
            class split_button(button)
            def create_group

        grids.py
            imports random, pygame, cells, actor_utility
            class grid
                class mini_grid
                class abstract_grid

        game_transitions.py
            imports time, main_loop_tools, text_tools, tiles, actor_utility
            def set_game_mode
            def create_strategic_map
            def start_loading

        europe_transactions.py
            imports buttons, game_transitions, mobs
            class european_hq_button(button)
            class recruitment_button(button)

        drawing_tools.py
            imports pygame
            def rect_to_surface
            def display_image
            def display_image_angle

        dice_utility.py
            imports random, text_tools
            def roll
            def roll_to_list

        dice.py
            imports pygame, time, random, buttons, utility
            class die

        data_managers.py
            imports random, csv_tools
            class global_manager_template
            class input_manager_template
            class flavor_text_manager_template

        csv_tools.py
            imports csv
            def read_csv

        cells.py
            imports pygame
            class cell

        buttons.py
            imports pygame, time, images, text_tools, instructions, main_loop_tools, actor_utility
            class button
                class selected_icon(button)
                class switch_grid_button(button)

        bars.py
            imports pygame
            class bar
                class actor_bar

        actors.py
            imports pygame, text_tools, utility, actor_utility
            class actor

        actor_utility.py
            imports random
            def create_image_dict
            def can_merge
            def can_split
            def get_selected_list
            def get_start_coordinates
            def calibrate_actor_info_display

        actor_match_tools.py
            imports images, labels, buttons, scaling
            class actor_match_free_image(free_image)
            class label_image(free_image)
            class label_button(button)
            class actor_match_label(label)
                class commodity_match_label
        
'''
