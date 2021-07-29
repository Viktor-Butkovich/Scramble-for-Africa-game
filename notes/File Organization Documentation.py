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
        imports pygame, time, random, math, scaling, main_loop, text_tools, utility, notification_tools
        imports images, buttons, game_transitions, grids, data_managers, actor_utility, groups, mobs

    modules folder
        actor_utility.py
            imports random
            def create_image_dict
            def can_merge
            def can_split
            def get_selected_list
            def get_start_coordinates

        actors.py
            imports pygame, text_tools, utility
            class actor

        bars.py
            imports pygame
            class bar
                class actor_bar

        buttons.py
            imports pygame, time, images, text_tools, instructions, main_loop, actor_utility
            class button
                class selected_icon

        cells.py
            imports pygame
            class cell

        csv_tools.py
            imports csv
            def read_csv

        data_managers.py
            imports random, csv_tools
            class global_manager_template
            class input_manager_template
            class flavor_text_manager_template

        dice.py
            imports pygame, time, random, buttons, utility
            class die

        dice_utility.py
            imports random, text_tools
            def roll
            def roll_to_list

        drawing_tools.py
            imports pygame
            def rect_to_surface
            def display_image
            def display_image_angle

        game_transitions.py
            imports time, main_loop, text_tools, tiles
            def set_game_mode
            def create_strategic_map
            def start_loading

        grids.py
            class grid
                class mini_grid

        groups.py
            imports time, mobs, tiles, buttons, actor_utility, text_tools, dice_utility, utility
            imports notification_tools, dice, scaling, main_loop
            class group(mob)
                class expedition
            class merge_button(button)
            class split_button(button)
            def create_group

        images.py
            imports pygame, time, utility, drawing_tools, text_tools
            class free_image
                class loading_image_template
            class actor_image
                class mob_image
                class button_image
                class tile_image
                    class veteran_icon_image

        instructions.py
            imports labels
            def display_instructions

        labels.py
            imports pygame, button, scaling, text_tools, utility
            class label(button)
                class instructions_page

        main_loop.py
            imports pygame, time, scaling, text_tools, actor_utility
            def update_display
            def action_possible
            def draw_loading_screen
            def manage_tooltip_drawing
            def draw_text_box
            def manage_rmb_down
            def manage_lmb_down

        mobs.py
            imports pygame, time, images, text_tools, utility, actors
            class mob(actor)
                class worker
                class officer
                    class explorer

        notification_tools.py
            imports notifications
            def display_notification
            def show_tutorial_notifications

        notifications.py
            imports labels, text_tools, utility, scaling
            class notification(label)
                class dice_rolling_notification
                class exploration_notification
            def notification_to_front
            
        scaling.py
            def scale_coordinates
            def scale_width
            def scale_height

        utility.py
            def find_object_distance
            def find_coordinate_distance
            def remove_from_list
            def toggle
            def generate_article
            def add_to_message

        text_tools.py
            imports pygame
            def message_width
            def get_input
            def text
            def manage_text_list
            def print_to_screen
            def print_to_previous_message
            def clear_message

        tiles.py
            imports pygame, images, utility, actors
            class tile
            class veteran_icon
            class overlay_tile
'''
