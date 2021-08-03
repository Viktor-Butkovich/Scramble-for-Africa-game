from . import labels
def display_instructions_page(page_number, global_manager):
    '''
    Input:
        int representing the page number to display, global_manager_template object
    Output:
        Displays a new instructions page corresponding to the inputted page number
    '''
    global_manager.set('current_instructions_page_index', page_number)
    global_manager.set('current_instructions_page_text', global_manager.get('instructions_list')[page_number])
    global_manager.set('current_instructions_page', labels.instructions_page(global_manager.get('current_instructions_page_text'), global_manager))

