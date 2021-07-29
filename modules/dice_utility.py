import random
from . import text_tools

def roll(num_sides, roll_type, requirement, min_crit_success, max_crit_fail, global_manager):
    '''
    Input:
        num_sides: int representing the number of sides of the simulated die
        roll_type: string representing the purpose of the roll, changing the roll's description
        requirement: int representing the minimum value required to succeed at the roll
        min_crit_success: int representing the minimum value required to critically suceed at the roll
        max_crit_fail: int representing the maximum value required to critically fail at the roll
        global_manager: global_manager_template object
    Output:
        Conducts a dice roll and prints a description of the outcome to the text box
    '''
    result = random.randrange(1, num_sides + 1)
    text_tools.print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        if result >= min_crit_success:
            text_tools.print_to_screen("You rolled a " + str(result) + ": critical success!", global_manager)
        else:
            text_tools.print_to_screen("You rolled a " + str(result) + ": success!", global_manager)
    else:
        if result <= max_crit_fail:
            text_tools.print_to_screen("You rolled a " + str(result) + ": critical failure", global_manager)
        else:
            text_tools.print_to_screen("You rolled a " + str(result) + ": failure", global_manager)
    return(result)

def roll_to_list(num_sides, roll_type, requirement, min_crit_success, max_crit_fail, global_manager):
    '''
    Input:
        num_sides: int representing the number of sides of the simulated die
        roll_type: string representing the purpose of the roll, changing the roll's description
        requirement: int representing the minimum value required to succeed at the roll
        min_crit_success: int representing the minimum value required to critically suceed at the roll
        max_crit_fail: int representing the maximum value required to critically fail at the roll
        global_manager: global_manager_template object
    Output:
        Conducts a dice roll and prints a description of the outcome to a list.
        The list's first item is an int, representing the result of the roll, and the list's second item is a string, representing the description of the roll with lines separated by /n.
    '''
    result = random.randrange(1, num_sides + 1)
    text = ""
    text += (roll_type + ": " + str(requirement) + "+ required to succeed /n")
    if result >= requirement:
        if result >= min_crit_success:
            text += "You rolled a " + str(result) + ": critical success! /n"
        else:
            text += "You rolled a " + str(result) + ": success! /n"
    else:
        if result <= max_crit_fail:
            text += ("You rolled a " + str(result) + ": critical failure /n")
        else:
            text += ("You rolled a " + str(result) + ": failure /n")
    return([result, text])
