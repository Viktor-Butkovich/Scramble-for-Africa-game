from . import notification_tools
from . import scaling
from . import game_transitions
from . import minister_utility

def start_trial(global_manager): #called by launch trial button in middle of trial screen
    defense = global_manager.get('displayed_defense')
    prosecution = global_manager.get('displayed_prosecution')
    message = "Are you sure you want to start a trial against " + defense.name + "? You have " + str(defense.corruption_evidence) + " pieces of evidence to use. /n /n"
    message += "Your prosecutor may roll 1 die for each piece of evidence, and the trial is successful if a 6 is rolled on any of the evidence dice. /n /n"
    message += "However, the defense may spend from their personal savings (perhaps stolen from your company) to hire lawyers and negate some of the evidence. /n /n"

    choice_info_dict = {}
    global_manager.set('ongoing_trial', True)
    notification_tools.display_choice_notification(message, ['start trial', 'stop trial'], choice_info_dict, global_manager) #creates choice notification to verify starting trial




def trial(global_manager): #called by choice notification button
    global_manager.get('money_tracker').change(-1 * global_manager.get('action_prices')['trial'], 'trial fees')
    defense = global_manager.get('displayed_defense')
    prosecution = global_manager.get('displayed_prosecution')
    
    effective_evidence = defense.corruption_evidence #can be cancelled out by defense lawyers and such, effective < actual
    
    global_manager.set('trial_rolls', [])
    for i in range(0, effective_evidence):
        current_roll = prosecution.no_corruption_roll(6)
        global_manager.get('trial_rolls').append(current_roll)
        if current_roll == 6:
            break
    print(global_manager.get('trial_rolls'))
    display_evidence_roll(global_manager)

def display_evidence_roll(global_manager):
    text = 'Current evidence roll: /n /n'
    result = global_manager.get('trial_rolls')[0]
    result_outcome_dict = {'min_success': 4, 'min_crit_success': 6, 'max_crit_fail': 0}
    outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
    global_manager.get('actor_creation_manager').display_die(scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 140, 440, global_manager), scaling.scale_width(100, global_manager),
        scaling.scale_height(100, global_manager), ['trial'], 6, result_outcome_dict, outcome_color_dict, result, global_manager)
    notification_tools.display_notification(text + "Click to roll. 6+ required on at least 1 die to succeed.", 'default', global_manager, 1)
    notification_tools.display_notification(text + "Rolling... ", 'roll', global_manager, 1)
    notification_tools.display_notification("You rolled a " + str(result) + ". /n /n", 'trial', global_manager)
    
def complete_trial(final_roll, global_manager):
    defense = global_manager.get('displayed_defense')
    game_transitions.set_game_mode('ministers', global_manager)
    if final_roll == 6:
        notification_tools.display_notification("Success", 'default', global_manager)
        defense.appoint('none')
        minister_utility.calibrate_minister_info_display(global_manager, defense)
    else:
        notification_tools.display_notification("Failure", 'default', global_manager)
    global_manager.set('ongoing_trial', False)
