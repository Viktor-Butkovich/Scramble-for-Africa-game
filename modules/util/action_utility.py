#Contains miscellaneous functions relating to action functionality

def cancel_ongoing_actions(global_manager):
    '''
    Description:
        Cancels any ongoing actions and frees the player to take other actions
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('ongoing_action', False)
    global_manager.set('ongoing_action_type', 'none')