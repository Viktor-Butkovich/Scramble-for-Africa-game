#Contains functions that control the display of new notifications

def display_notification(message, notification_type, global_manager): #default, exploration, or roll
    '''
    Description:
        Adds a future notification to the notification queue with the inputted text and type. If other notifications are already in the notification queue, adds this notification to the back, causing it to appear last. When a
            notification is closed, the next notification in the queue is shown
    Input:
        string message: Text for future notification
        string notification_type: Type of notification created, like 'roll, 'choice', or 'exploration'
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('notification_manager').notification_queue.append(message)#global_manager.get('notification_queue').append(message)
    global_manager.get('notification_manager').notification_type_queue.append(notification_type)#global_manager.get('notification_type_queue').append(notification_type)
    if len(global_manager.get('notification_manager').notification_queue) == 1: #_type_queue
        global_manager.get('notification_manager').notification_to_front(message)#notifications.notification_to_front(message, global_manager)

def display_choice_notification(message, choices, choice_info_dict, global_manager): #default, exploration, or roll
    '''
    Description:
        Adds a future notification to the notification queue with the inputted text and type. If other notifications are already in the notification queue, adds this notification to the back, causing it to appear last. When a
            notification is closed, the next notification in the queue is shown
    Input:
        string message: Text for future notification
        string list choices: Types of buttons for the choices on the choice notification, like 'end turn' or 'none'
        dictionary choice_info_dict: dictionary containing various information needed for the choice notifications and its buttons correctly, such as by recording which caravan is trading during a trade notification to allow the
            bought commodities to go to the correct mob. Contains different information based on the situation and the choices list
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('notification_manager').notification_queue.append(message)#global_manager.get('notification_queue').append(message)
    global_manager.get('notification_manager').notification_type_queue.append('choice')#global_manager.get('notification_type_queue').append(notification_type)
    global_manager.get('notification_manager').choice_notification_choices_queue.append(choices)
    global_manager.get('notification_manager').choice_notification_info_dict_queue.append(choice_info_dict)
    if len(global_manager.get('notification_manager').notification_queue) == 1: #_type_queue
        global_manager.get('notification_manager').notification_to_front(message)#notifications.notification_to_front(message, global_manager)



def show_tutorial_notifications(global_manager):
    '''
    Description:
        Displays a tutorial message notification when the program is started     
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message, 'default', global_manager)
