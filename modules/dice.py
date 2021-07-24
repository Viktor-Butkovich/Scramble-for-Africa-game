import random
from . import text_tools

def roll(num_sides, roll_type, requirement, global_manager):
    #text_tools.print_to_screen("", global_manager)
    result = random.randrange(1, num_sides + 1)
    #global_manager.get('roll_label').set_label("Roll: " + str(result))
    text_tools.print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        text_tools.print_to_screen("You rolled a " + str(result) + ": success!", global_manager)
        #return(True)
    else:
        text_tools.print_to_screen("You rolled a " + str(result) + ": failure", global_manager)
        #return(False)
    return(result) #returns int roll result

def roll_to_list(num_sides, roll_type, requirement, global_manager):
    #text_tools.print_to_screen("", global_manager)
    result = random.randrange(1, num_sides + 1)
    #global_manager.get('roll_label').set_label("Roll: " + str(result))
    text = ""
    text += (roll_type + ": " + str(requirement) + "+ required to succeed /n")
    #text_tools.print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        #text_tools.print_to_screen("You rolled a " + str(result) + ": success!", global_manager)
        text += "You rolled a " + str(result) + ": success! /n"
        #return(True)
    else:
        #text_tools.print_to_screen("You rolled a " + str(result) + ": failure", global_manager)
        text += ("You rolled a " + str(result) + ": failure /n")
        #return(False)
    return([result, text]) #returns int roll result and string with lines separated with \n

