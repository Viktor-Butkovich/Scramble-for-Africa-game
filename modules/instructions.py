from . import label
def display_instructions_page(page_number, global_manager):
    global_manager.set('current_instructions_page_index', page_number)
    global_manager.set('current_instructions_page_text', global_manager.get('instructions_list')[page_number])
    global_manager.set('current_instructions_page', label.instructions_page(global_manager.get('current_instructions_page_text'), global_manager))

