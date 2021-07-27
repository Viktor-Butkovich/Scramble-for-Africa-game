import random

def create_image_dict(stem):
    '''if stem is a certain value, add extra ones, such as special combat animations: only works for images in graphics/mobs'''
    stem = 'mobs/' + stem
    stem += '/'#goes to that folder
    image_dict = {}
    image_dict['default'] = stem + 'default.png'
    image_dict['right'] = stem + 'right.png'  
    image_dict['left'] = stem + 'left.png'
    return(image_dict)

def can_merge(global_manager):
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 2:
        return(True)
    return(False)
    
def get_selected_list(global_manager):
    selected_list = []
    for current_mob in global_manager.get('mob_list'):
        if current_mob.selected:
            selected_list.append(current_mob)
    return(selected_list)

def get_start_coordinates(global_manager):
    mob_list = global_manager.get('mob_list')
    mob_coordinate_list = []
    start_x, start_y = (0, 0)
    for current_mob in mob_list:
        mob_coordinate_list.append((current_mob.x, current_mob.y))
    while True: #to do: prevent 2nd row from the bottom of the map grid from ever being completely covered with water due to unusual river RNG, causing infinite loop here, or start increasing y until land is found
        start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
        start_y = 1
        if (start_x, start_y) in mob_coordinate_list: #do not spawn there if another mob starts there
            continue
        if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
            break
    return(start_x, start_y)
            
