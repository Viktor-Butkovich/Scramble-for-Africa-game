#Contains functionality for interface elements and collections

class interface_collection():
    '''
    Object managing an image bundle and collection of interactive interface elements, including buttons, free images, and other interface windows
    An entire collection can be displayed or hidden as a unit, along with individual components having their own conditions for being visible when the window is displayed
    A collection could have different modes that display different sub-windows under different conditions while keeping other elements constant
    A particular type of collection could have special ordered functionality, like a series of buttons that can be scrolled through, or a images displayed in horizontal rows w/ maximum widths
    Older, informal collections such as the available minister scrollbar, the movement buttons, and the mob, tile, minister, prosecution, and defense displays should be able to be 
        implemented as interface collections. Additionally, the "mode" system could possibly be changed to use overarching interface collections for each mode
    Like an image bundle, members of an interface collection should have independent types and characteristics but be controlled as a unit and created in a list with a dictionary or simple 
        string. Unlike an image bundle, a collection does not necessarily have to be saved, and 
    '''
    def __init__(self, modes, global_manager):
        self.global_manager = global_manager
        self.modes = modes
        return
