from . import utility
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

def manage_defense(corruption_evidence, global_manager):
    defense = global_manager.get('displayed_defense')
    max_defense_fund = 0.6 * defense.stolen_money #pay up to 60% of savings
    building_defense = True
    num_lawyers = 0
    defense_cost = 0
    while building_defense:
        lawyer_cost = get_lawyer_cost(num_lawyers)
        if (defense_cost + lawyer_cost <= max_defense_fund) and (num_lawyers + 1 < corruption_evidence): #pay no more than 60% of savings and allow some chance of success for prosecution
            defense_cost += lawyer_cost
            num_lawyers += 1
        else:
            building_defense = False
    defense.stolen_money -= defense_cost
    defense_info_dict = {}
    defense_info_dict['num_lawyers'] = num_lawyers
    defense_info_dict['corruption_evidence'] = corruption_evidence
    defense_info_dict['effective_evidence'] = corruption_evidence - num_lawyers
    return(defense_info_dict)
            
        
def get_lawyer_cost(num_lawyers):
    base_cost = 5
    multiplier = 2 ** num_lawyers #1, 2, 4, 8
    return(base_cost * multiplier)

def trial(global_manager): #called by choice notification button
    global_manager.get('money_tracker').change(-1 * global_manager.get('action_prices')['trial'], 'trial fees')
    defense = global_manager.get('displayed_defense')
    prosecution = global_manager.get('displayed_prosecution')

    defense_info_dict = manage_defense(defense.corruption_evidence, global_manager)

    if defense_info_dict['num_lawyers'] == 0:
        text = 'As the defense decided not to hire any additional lawyers, each piece of evidence remains usable, allowing ' + str(defense_info_dict['effective_evidence']) + ' evidence rolls to attempt to win the trial. /n /n'
    else:
        text = 'The defense hired ' + str(defense_info_dict['num_lawyers']) + ' additional lawyers, who each cancel out a piece of evidence. This leaves ' + str(defense_info_dict['effective_evidence'])
        text += ' evidence rolls to attempt to win the trial. /n /n'
    
    
    text += str(defense_info_dict['corruption_evidence']) + ' initial evidence - '
    text += str(defense_info_dict['num_lawyers']) + ' defense lawyers = '
    text += str(defense_info_dict['effective_evidence']) + ' evidence rolls /n /n'
    notification_tools.display_notification(text, 'default', global_manager)
    #effective_evidence = defense.corruption_evidence - defense_info_dict['num_lawyers'] #can be cancelled out by defense lawyers and such, effective < actual
    
    global_manager.set('trial_rolls', [])
    for i in range(0, defense_info_dict['effective_evidence']):
        current_roll = prosecution.no_corruption_roll(6)
        global_manager.get('trial_rolls').append(current_roll)

    display_evidence_roll(global_manager)

def display_evidence_roll(global_manager):
    text = ''
    text += ''
    text = 'Evidence rolls remaining: ' + str(len(global_manager.get('trial_rolls'))) + ' /n /n'
    result = global_manager.get('trial_rolls')[0]
    result_outcome_dict = {'min_success': 6, 'min_crit_success': 6, 'max_crit_fail': 0}
    outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
    global_manager.get('actor_creation_manager').display_die(scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 140, 440, global_manager), scaling.scale_width(100, global_manager),
        scaling.scale_height(100, global_manager), ['trial'], 6, result_outcome_dict, outcome_color_dict, result, global_manager)
    notification_tools.display_notification(text + "Click to roll. 6+ required on at least 1 die to succeed.", 'default', global_manager, 1)
    notification_tools.display_notification(text + "Rolling... ", 'roll', global_manager, 1)
    notification_tools.display_notification("You rolled a " + str(result) + ". /n /n", 'trial', global_manager)
    
def complete_trial(final_roll, global_manager):
    prosecution = global_manager.get('displayed_prosecution')
    defense = global_manager.get('displayed_defense')
    game_transitions.set_game_mode('ministers', global_manager)
    if final_roll == 6:
        confiscated_money = defense.stolen_money / 2.0
        text = "You have won the trial, removing " + defense.name + " as " + defense.current_position + " and putting them in prison. /n /n"
        if confiscated_money > 0:
            text += "While most of " + defense.name + "'s money was spent on the trial or unaccounted for, authorities managed to confiscate " + str(confiscated_money) + " money, which has been given to your company as compensation. "
            text += " /n /n"
            global_manager.get('money_tracker').change(confiscated_money, 'trial compensation')
        else:
            text += "Authorities searched " + defense.name + "'s properties but were not able to find any stolen money with which to compensate your company. Perhaps it remains hidden, had already been spent, or had never been stolen. "
            text += " /n /n"
        notification_tools.display_notification(text, 'default', global_manager)
        
        defense.appoint('none')
        defense.remove()
        #minister_utility.calibrate_minister_info_display(global_manager, defense)
    else:
        text = "You have lost the trial and " + defense.name + " goes unpunished, remaining your " + defense.current_position + ". /n /n"
        fabricated_evidence = defense.fabricated_evidence
        real_evidence = defense.corruption_evidence - defense.fabricated_evidence

        remaining_evidence = 0
        lost_evidence = 0
        for i in range(0, real_evidence):
            if prosecution.no_corruption_roll(6) >= 4:
                remaining_evidence += 1
            else:
                lost_evidence += 1
                
        if fabricated_evidence > 0:
            text += "Fabricated evidence is temporary, so the " + str(fabricated_evidence) + " piece" + utility.generate_plural(fabricated_evidence) + " of fabricated evidence used in this trial "
            text += utility.conjugate('be', fabricated_evidence) + " now irrelevant to future trials. /n /n"

        if real_evidence > 0:
            if lost_evidence == 0:
                text += "All of the real evidence used in this trial remains potent enough to be used in future trials against "
                text += defense.name + ". /n /n"
            elif lost_evidence < real_evidence:
                text += "Of the " + str(real_evidence) + " piece" + utility.generate_plural(real_evidence) + " of real evidence used in this trial, " + str(remaining_evidence)
                text += " " + utility.conjugate('remain', remaining_evidence) + " potent enough to be relevant to future trials against " + defense.name + ", while " + str(lost_evidence) + " " + utility.conjugate('be', lost_evidence)
                text += " now irrelevant. /n /n"
            else: #if all evidence lost
                text += "Of the " + str(real_evidence) + " piece" + utility.generate_plural(real_evidence) + " of real evidence used in this trial, none remain potent enough to be relevant to future trials against " + defense.name + ". /n /n"

        defense.fabricated_evidence = 0
        defense.corruption_evidence = remaining_evidence
        notification_tools.display_notification(text, 'default', global_manager)
        minister_utility.calibrate_minister_info_display(global_manager, defense)
        
    global_manager.set('ongoing_trial', False)
