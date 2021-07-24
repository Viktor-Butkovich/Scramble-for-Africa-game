from . import notification
from . import scaling

def display_notification(message, global_manager):
    global_manager.get('notification_queue').append(message)
    global_manager.get('notification_type_queue').append('default')
    if len(global_manager.get('notification_queue')) == 1:
        notification.notification_to_front(message, global_manager)

def display_exploration_notification(message, global_manager):
    global_manager.get('notification_queue').append(message)
    global_manager.get('notification_type_queue').append('exploration')
    if len(global_manager.get('notification_queue')) == 1:
        notification.notification_to_front(message, global_manager)

def display_dice_rolling_notification(message, global_manager):
    #message = "roll"
    global_manager.get('notification_queue').append(message)
    global_manager.get('notification_type_queue').append('roll')
    if len(global_manager.get('notification_queue')) == 1:
        notification.notification_to_front(message, global_manager)
        
#def explorer_notification_to_front(message, global_manager):
#    new_notification = notification.notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)

def show_tutorial_notifications(global_manager):
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message, global_manager)
