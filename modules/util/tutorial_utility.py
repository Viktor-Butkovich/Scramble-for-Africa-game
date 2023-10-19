#Contains functions that control the display of new notifications

import modules.constants.constants as constants

def show_tutorial_notifications(global_manager):
    '''
    Description:
        Displays tutorial messages at various points in the program. The exact message depends on how far the player has advanced through the tutorial   
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if not global_manager.get('minister_appointment_tutorial_completed'):
        message = 'Welcome to Scramble for Africa! /n /n'
        message += 'Your goal as colonial governor is to bring glory to your country\'s name by conquering and enlightening this hostile continent, hopefully becoming fabulously rich in the process. /n /n'
        global_manager.get('notification_manager').display_notification({
            'message': message,
        })

        message = 'Welcome to Scramble for Africa! /n /n'
        message += 'You must start the game by appointing ministers to control each part of your company\'s operations. Choose wisely, as skilled, loyal ministers will prove to be capable and reliable in their exploits while the '
        message += 'corrupt will lie and steal and the incompetent will repeatedly try and fail, losing money and lives in the process. /n /n'
        global_manager.get('notification_manager').display_notification({
            'message': message,
        })

        message = 'Welcome to Scramble for Africa! /n /n'
        message += 'To appoint a minister, scroll through the available ministers in the lower right and click on one to select it. Then, see the selected minister in the upper left and select an office to appoint them to. /n /n'
        message += 'Repeat this until all offices are filled. /n /n'
        global_manager.get('notification_manager').display_notification({
            'message': message,
        })

    elif not global_manager.get('exit_minister_screen_tutorial_completed'):
        message = 'Now a minister has been appointed for each part of your company. Throughout the game, you will order these ministers to complete various actions and they will report their success or failure through dice rolls. '
        message += 'These dice rolls are not purely random - a skilled minister may have higher results while a corrupt one may report a failure and steal the money given for the action without even '
        message += 'attempting it. /n /nIs an unsuccessful minister incompetent, corrupt, or merely unlucky? Perhaps all three? /n /n'
        global_manager.get('notification_manager').display_notification({
            'message': message,
        })

        message = 'Now, exit the minister screen through the button in the top left corner. You may use the same button to return here in the future to modify minister appointments and examine potential recruits. /n /n'
        global_manager.get('notification_manager').display_notification({
            'message': message,
        })
