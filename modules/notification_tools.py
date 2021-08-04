#from . import notifications

def display_notification(message, notification_type, global_manager): #default, exploration, or roll
    '''
    Input:
        string representing the text of the notification created, string representing the type of notification created, global_manager_template object
    Output:
        Creates a notification of inputted type with inputted text
    '''
    global_manager.get('notification_manager').notification_queue.append(message)#global_manager.get('notification_queue').append(message)
    global_manager.get('notification_manager').notification_type_queue.append(notification_type)#global_manager.get('notification_type_queue').append(notification_type)
    if len(global_manager.get('notification_manager').notification_queue) == 1: #_type_queue
        global_manager.get('notification_manager').notification_to_front(message)#notifications.notification_to_front(message, global_manager)

def display_choice_notification(message, choices, choice_info_dict, global_manager): #default, exploration, or roll
    global_manager.get('notification_manager').notification_queue.append(message)#global_manager.get('notification_queue').append(message)
    global_manager.get('notification_manager').notification_type_queue.append('choice')#global_manager.get('notification_type_queue').append(notification_type)
    global_manager.get('notification_manager').choice_notification_choices_queue.append(choices)
    global_manager.get('notification_manager').choice_notification_info_dict_queue.append(choice_info_dict)
    if len(global_manager.get('notification_manager').notification_queue) == 1: #_type_queue
        global_manager.get('notification_manager').notification_to_front(message)#notifications.notification_to_front(message, global_manager)



def show_tutorial_notifications(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Displays a tutorial message notification when the program is started
    '''
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message, 'default', global_manager)
