import random
from . import text_tools

def roll(num_sides, roll_type, requirement, min_crit_success, max_crit_fail, global_manager):
    #text_tools.print_to_screen("", global_manager)
    result = random.randrange(1, num_sides + 1)
    #global_manager.get('roll_label').set_label("Roll: " + str(result))
    text_tools.print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        if result >= min_crit_success:
            text_tools.print_to_screen("You rolled a " + str(result) + ": critical success!", global_manager)
        else:
            text_tools.print_to_screen("You rolled a " + str(result) + ": success!", global_manager)
        #return(True)
    else:
        if result <= max_crit_fail:
            text_tools.print_to_screen("You rolled a " + str(result) + ": critical failure", global_manager)
        else:
            text_tools.print_to_screen("You rolled a " + str(result) + ": failure", global_manager)
        #return(False)
    return(result) #returns int roll result

def roll_to_list(num_sides, roll_type, requirement, min_crit_success, max_crit_fail, global_manager):
    #text_tools.print_to_screen("", global_manager)
    result = random.randrange(1, num_sides + 1)
    #global_manager.get('roll_label').set_label("Roll: " + str(result))
    text = ""
    text += (roll_type + ": " + str(requirement) + "+ required to succeed /n")
    #text_tools.print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        #text_tools.print_to_screen("You rolled a " + str(result) + ": success!", global_manager)
        if result >= min_crit_success:
            text += "You rolled a " + str(result) + ": critical success! /n"
        else:
            text += "You rolled a " + str(result) + ": success! /n"
        #return(True)
    else:
        #text_tools.print_to_screen("You rolled a " + str(result) + ": failure", global_manager)
        if result <= max_crit_fail:
            text += ("You rolled a " + str(result) + ": critical failure /n")
        else:
            text += ("You rolled a " + str(result) + ": failure /n")
        #return(False)
    #if die_display_info_dict['show_die']:
    #    result_outcome_dict = {'min_success': requirement, 'min_crit_success': min_crit_success, 'max_crit_fail': max_crit_fail}
    #    outcome_color_dict = {'success': 'green', 'fail': 'red', 'crit_success': 'bright green', 'crit_fail': 'black'}
        #new_die = label.die(300, 300, 100, 100, ['strategic'], 6, result_outcome_dict, outcome_color_dict, 7, result, global_manager)#coordinates, width, height, modes, num_sides, result_outcome_dict, outcome_color_dict, num_rolls, final_result, global_manager
    return([result, text]) #returns int roll result and string with lines separated with \n
