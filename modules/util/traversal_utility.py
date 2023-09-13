#Contains functions to manage interface collection traversal, doing particular actions for each element with simple decision-making
def draw_interface_elements(interface_elements, global_manager):
    '''
    Description:
        Recursively traverses through each of the inputted interface elements and their member trees, updating each element's showing attribute to its current can_show()
            value and, if it showing, drawing it - if an element is not showing, elements below it can not show either
    Input:
        interface_element list interface_elements: List of interface elements to traverse through - no element in the list should be a member of any other element in the
            list, either directly or indirectly. This will preferably be the list of all 'root' elements
        global_manager_template global_manager: Object that accesses shared variables
    '''
    for current_interface_element in interface_elements:
        collection_traversal(current_interface_element, set_showing, set_not_showing, 
                check_showing, global_manager, posttraversal_action=update_collection)
    for current_interface_element in global_manager.get('draw_list'):
        current_interface_element.draw()
    global_manager.set('draw_list', [])
        
def collection_traversal(current_element, pretraversal_action, alternative_action, condition, global_manager, posttraversal_action=None):
    '''
    Description:
        Recursively traverses through an interface element/collection, any of its members, any of their members, and so on, doing a particular action for each member based
            on whether the condition is true for that member
    Input:
        interface_element current_element: Element being traversed through
        function pretraversal_action(interface_element): Called before traversing through a particular element's members
        function alternative_action(interface_element): Given as pretraversal action for lower recursive calls if condition was false for a collection
        function condition(interface_element): Checked before traversing through a particular element's members - determines whether that element will continue having a
            choice between 2 actions or automatically choose the alternative action each time
        global_manager_template global_manager: Object that accesses shared variables
        function posttraversal_action(interface_element)=None: Called after traversing through a particular element's members, if present
    Output:
        None
    '''
    if hasattr(current_element, 'members'):
        for member_element in current_element.members:
            pretraversal_action(member_element, global_manager)
            if pretraversal_action != alternative_action:
                if condition(member_element):
                    collection_traversal(member_element, pretraversal_action, alternative_action, condition, global_manager, posttraversal_action=posttraversal_action)
                else: #if condition false, do alternative action for every element below without checking condition
                    collection_traversal(member_element, alternative_action, alternative_action, condition, global_manager)
            else: #if condition was false previously, continue doing alternative action for every element below without checking condition
                collection_traversal(member_element, alternative_action, alternative_action, condition, global_manager)
            if posttraversal_action:
                posttraversal_action(member_element, global_manager)
    if (not hasattr(current_element, 'has_parent_collection')) or not current_element.has_parent_collection: #if independent element
        pretraversal_action(current_element, global_manager)
        if posttraversal_action:
            posttraversal_action(current_element, global_manager)

def set_showing(current_element, global_manager):
    '''
    Description:
        Updates the inputted elements showing attribute
    Input:
        interface_element current_element: Element being traversed through
    Output:
        None
    '''
    current_element.showing = current_element.can_show()

def update_collection(current_element, global_manager):
    '''
    Description:
        Updates the inputted element's collection and tells it to draw, if it is showing
    Input:
        interface_element current_element: Element being traversed through
    Output:
        None
    '''
    if current_element.showing:
        if hasattr(current_element, 'members'):
            current_element.update_collection()
        if current_element.can_draw():
            global_manager.get('draw_list').append(current_element)

def set_not_showing(current_element, global_manager):
    '''
    Description:
        Sets the inputted elements showing attribute to False
    Input:
        interface_element current_element: Element being traversed through
    Output:
        None
    '''
    current_element.showing = False

def check_showing(current_element):
    '''
    Description:
        Returns whether the inputted element is showing
    Input:
        interface_element current_element: Element being traversed through
    Output:
        boolean: Returns whether the inputted element is showing
    '''
    return(current_element.showing)
