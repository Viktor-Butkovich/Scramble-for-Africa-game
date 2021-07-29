from . import notifications

def display_notification(message, notification_type, global_manager): #default, exploration, or roll
    '''
    Inputs:
        string representing the text of the notification created, string representing the type of notification created, global_manager_template object
    Outputs:
        Creates a notification of inputted type with inputted text
    '''
    global_manager.get('notification_queue').append(message)
    global_manager.get('notification_type_queue').append(notification_type)
    if len(global_manager.get('notification_queue')) == 1:
        notifications.notification_to_front(message, global_manager)

def show_tutorial_notifications(global_manager):
    '''
    Inputs:
        global_manager_template object
    Outputs:
        Displays a tutorial message notification when the program is started
    '''
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message, 'default', global_manager)
