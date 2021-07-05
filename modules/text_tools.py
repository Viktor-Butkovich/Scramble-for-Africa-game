import pygame

def message_width(message, fontsize, font_name):
    current_font = pygame.font.SysFont(font_name, fontsize)
    text_width, text_height = current_font.size(message)
    return(text_width)


def get_input(solicitant, message, global_manager):
    global_manager.get('input_manager').start_receiving_input(solicitant, message)


def text(message, font, global_manager):
    return(font.render(message, False, global_manager.get('color_dict')['black']))

def manage_text_list(text_list, max_length):
    if len(text_list) > max_length:
        while not len(text_list) == max_length:
            text_list.pop(0)
    return(text_list)


def print_to_screen(input_message, global_manager):
    global_manager.get('text_list').append(input_message)

    
def print_to_previous_message(message, global_manager):
    global_manager.get('text_list')[-1] = global_manager.get('text_list')[-1] + message

    
def clear_message(global_manager):
    global_manager.set('message', '')
