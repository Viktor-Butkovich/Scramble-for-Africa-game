from . import notification
from . import scaling

def display_notification(message, notification_type, global_manager): #default, exploration, or roll
    global_manager.get('notification_queue').append(message)
    global_manager.get('notification_type_queue').append(notification_type)
    if len(global_manager.get('notification_queue')) == 1:
        notification.notification_to_front(message, global_manager)

def show_tutorial_notifications(global_manager):
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message, 'default', global_manager)
