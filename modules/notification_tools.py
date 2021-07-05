from . import notification
from . import scaling

def display_notification(message, global_manager):
    global_manager.get('notification_queue').append(message)
    if len(global_manager.get('notification_queue')) == 1:
        notification_to_front(message, global_manager)

def notification_to_front(message, global_manager):
    '''#displays a notification from the queue, which is a list of string messages that this formats into notifications'''
    new_notification = notification.notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)#coordinates, ideal_width, minimum_height, showing, modes, image, message

def show_tutorial_notifications(global_manager):
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message, global_manager)
