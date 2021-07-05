def scale_coordinates(x, y, global_manager):
    x_ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    y_ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_x = round(x * x_ratio)
    scaled_y = round(y * y_ratio)
    return(scaled_x, scaled_y)

def scale_width(width, global_manager):
    ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    scaled_width = round(width * ratio)
    return(scaled_width)

def scale_height(height, global_manager):
    ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_height = round(height * ratio)
    return(scaled_height)
