def scale_coordinates(x, y, global_manager):
    '''
    Input:
        Two int variables representing unscaled coordinates, global_manager_template object
    Output:
        Returns a tuple of two int variables representing coordinates scaled to the user's resolution
    '''
    x_ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    y_ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_x = round(x * x_ratio)
    scaled_y = round(y * y_ratio)
    return(scaled_x, scaled_y)

def scale_width(width, global_manager):
    '''
    Input:
        int representing unscaled pixel width, global_manager_template object. Also works for x coordinates alone rather than just widths
    Output:
        Returns an int pixel width scaled to the user's resolution
    '''
    ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    scaled_width = round(width * ratio)
    return(scaled_width)

def scale_height(height, global_manager):
    '''
    Input:
        int representing unscaled pixel height, global_manager_template object. Also works for y coordinates alone rather than just heights
    Output:
        Returns an int pixel height scaled to the user's resolution
    '''
    ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_height = round(height * ratio)
    return(scaled_height)

def unscale_width(width, global_manager):
    '''
    Input:
        int representing scaled pixel width, global_manager_template object. Also works for x coordinates alone rather than just widths
    Output:
        Returns an int pixel width restored to the default game resolution
    '''
    ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    unscaled_width = round(width / ratio)
    return(unscaled_width)

def unscale_height(height, global_manager):
    '''
    Input:
        int representing scaled pixel height, global_manager_template object. Also works for y coordinates alone rather than just heights
    Output:
        Returns an int pixel height restored to the default game resolution
    '''
    ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    unscaled_height = round(height / ratio)
    return(unscaled_height)

