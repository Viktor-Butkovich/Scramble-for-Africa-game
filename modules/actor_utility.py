import random

def create_image_dict(stem):
    '''
    Inputs:
        string representing the path to a folder of an actor's images
    Outputs:
        Returns a dictionary of key strings of descriptions of images and corresponding values of the images' file paths
    '''
    '''if stem is a certain value, add extra ones, such as special combat animations: only works for images in graphics/mobs'''
    stem = 'mobs/' + stem
    stem += '/'#goes to that folder
    image_dict = {}
    image_dict['default'] = stem + 'default.png'
    image_dict['right'] = stem + 'right.png'  
    image_dict['left'] = stem + 'left.png'
    return(image_dict)

def can_merge(global_manager):
    '''
    Inputs:
        global_manager_template object
    Outputs:
        Returns whether the player is able to merge a worker and an officer. A single worker and a single officer must be the only mobs selected to merge them into a group.
        If the correct mobs are selected but they are in different locations, this will return True and the merge button will show, but pressing it will prompt the user to move them to the same location.
    '''
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 1:
        #worker_present = False
        officer_present = False
        for current_selected in selected_list:
            #if current_selected in global_manager.get('worker_list'):
            #    worker_present = True
            if current_selected in global_manager.get('officer_list'):
                officer_present = True
        if officer_present:
            return(True)
        else:
            return(False)
    return(False)

def can_split(global_manager):
    '''
    Inputs:
        global_manager_template object
    Outputs:
        Returns whether the player is able to split a group. A single group and no other mobs must be selected to split the group.
    '''
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 1 and selected_list[0] in global_manager.get('group_list'):
        return(True)
    return(False)
    
def get_selected_list(global_manager):
    '''
    Inputs:
        global_manager_template object
    Outputs:
        Returns a list of all selected mobs
    '''
    selected_list = []
    for current_mob in global_manager.get('mob_list'):
        if current_mob.selected:
            selected_list.append(current_mob)
    return(selected_list)

def get_start_coordinates(global_manager):
    '''
    Inputs:
        global_manager_template object
    Outputs:
        Returns a random tuple of two ints representing the grid coordinates at which to start the game, which must be on the 2nd lowest row of the map on a land tile
    '''
    mob_list = global_manager.get('mob_list')
    mob_coordinate_list = []
    start_x, start_y = (0, 0)
    #for current_mob in mob_list:
    #    mob_coordinate_list.append((current_mob.x, current_mob.y))
    while True: #to do: prevent 2nd row from the bottom of the map grid from ever being completely covered with water due to unusual river RNG, causing infinite loop here, or start increasing y until land is found
        start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
        start_y = 1
        #if (start_x, start_y) in mob_coordinate_list: #do not spawn there if another mob starts there
        #    continue
        if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
            break
    return(start_x, start_y)
            
