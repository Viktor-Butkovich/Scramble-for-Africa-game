import random
from . import text_tools

def roll(num_sides, roll_type, requirement, global_manager):
    #text_tools.print_to_screen("", global_manager)
    result = random.randrange(1, num_sides + 1)
    global_manager.get('roll_label').set_label("Roll: " + str(result))
    text_tools.print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        text_tools.print_to_screen("You rolled a " + str(result) + ": success!", global_manager)
        #return(True)
    else:
        text_tools.print_to_screen("You rolled a " + str(result) + ": failure", global_manager)
        #return(False)
    return(result) #returns int rather than boolean
