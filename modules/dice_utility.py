import random
from . import text_tools

def roll(num_sides, roll_type, requirement, min_crit_success, max_crit_fail, global_manager):
    '''
    Description:
        Conducts a dice roll and prints a description of the outcome to the text box. Does not actually create a die object, instead providing information that can be used to show the result through a die object
    Input:
        int num_sides: Number of sides of the simulated die
        string roll_type: Represents the purpose of the roll, affecting the roll's description
        int requirement: Minimum value required for the roll to succeed
        int min_crit_success: Minimum value required for the roll to critically succed
        max_crit_fail: Maximum value required for the roll to critically fail
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        int: Returns the random value rolled
    '''
    result = random.randrange(1, num_sides + 1)
    text_tools.print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        if result >= min_crit_success:
            text_tools.print_to_screen("You rolled a " + str(result) + ": CRITICAL SUCCESS!", global_manager)
        else:
            text_tools.print_to_screen("You rolled a " + str(result) + ": SUCCESS!", global_manager)
    else:
        if result <= max_crit_fail:
            text_tools.print_to_screen("You rolled a " + str(result) + ": CRITICAL FAILURE", global_manager)
        else:
            text_tools.print_to_screen("You rolled a " + str(result) + ": FAILURE", global_manager)
    return(result)

def roll_to_list(num_sides, roll_type, requirement, min_crit_success, max_crit_fail, global_manager):
    '''
    Description:
        Conducts a dice roll and returns a list that contains the roll's result and a description of the roll. Does not actually create a die object, instead providing information that can be used to show the result through a die object
    Input:
        int num_sides: Number of sides of the simulated die
        string roll_type: Represents the purpose of the roll, affecting the roll's description
        int requirement: Minimum value required for the roll to succeed
        int min_crit_success: Minimum value required for the roll to critically succed
        max_crit_fail: Maximum value required for the roll to critically fail
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        int/string list: List representing the roll's outcome, with the first item being the roll's int result and the second item being a string description of the roll
    '''
    result = random.randrange(1, num_sides + 1)
    text = ""
    if not roll_type == 'second': #do not show again for 2nd die rolled by veteran
        text += (roll_type + ": " + str(requirement) + "+ required to succeed /n")
    if result >= requirement:
        if result >= min_crit_success:
            text += "You rolled a " + str(result) + ": CRITICAL SUCCESS! /n"
        else:
            text += "You rolled a " + str(result) + ": SUCCESS! /n"
    else:
        if result <= max_crit_fail:
            text += ("You rolled a " + str(result) + ": CRITICAL FAILURE /n")
        else:
            text += ("You rolled a " + str(result) + ": FAILURE /n")
    return([result, text])
