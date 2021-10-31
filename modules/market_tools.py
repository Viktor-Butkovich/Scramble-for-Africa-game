import random
from . import text_tools
from . import utility

def adjust_prices(global_manager):
    '''
    Description:
        Increases the prices of 2 normal commodities by 1 and decreases the price of 1 normal commodity by 1. Also has a 1/3 chance to decrease the cost of consumer goods by 1 and a 1/6 chance to increase the cost of consumer goods by 1
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    num_increased = 2
    num_decreased = 1
    for i in range(2):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        change_price(changed_commodity, 1, global_manager)
    for i in range(1):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        while changed_commodity == 'consumer goods':
            changed_commodity = random.choice(global_manager.get('commodity_types'))
        change_price(changed_commodity, -1, global_manager)
    consumer_goods_roll = random.randrange(1, 7)
    if consumer_goods_roll == 1:
        change_price('consumer goods', 1, global_manager)
    elif consumer_goods_roll >= 5:
        change_price('consumer goods', -1, global_manager)

def change_price(changed_commodity, num_change, global_manager):
    '''
    Description:
        Changes the price of the inputted commodity by the inputted amount
    Input:
        string changed_commodity: Type of commodity whose price changes, like 'exotic wood'
        int num_change: Amount the price of the inputted commodity increases
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('commodity_prices')[changed_commodity] += num_change
    if global_manager.get('commodity_prices')[changed_commodity] < 1:
        global_manager.get('commodity_prices')[changed_commodity] = 1
    global_manager.get('commodity_prices_label').update_label()

def sell(seller, sold_commodity, num_sold, global_manager):
    '''
    Description:
        Sells the inputted amount of the inputted commodity from the inputted actor's inventory, removing it from the inventory and giving an amount of money corresponding to the commodity's price. Each unit sold also has a 1/6 chance
            to decrease the price of the commodity by 1
    Input:
        actor seller: actor whose inventory the sold commodity is removed from
        string sold_commodity: Type of commodity that is sold, like 'exotic wood'
        int num_sold: Number of units of the commodity sold
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    sell_price = global_manager.get('commodity_prices')[sold_commodity]
    for i in range(num_sold):
        global_manager.get('money_tracker').change(sell_price)
        seller.change_inventory(sold_commodity, -1)
        if random.randrange(1, 7) == 1: #1/6 chance
            change_price(sold_commodity, -1, global_manager)
    text_tools.print_to_screen("You have gained " + str(sell_price * num_sold) + " money from selling " + str(num_sold) + " unit" + utility.generate_plural(num_sold) + " of " + sold_commodity + ".", global_manager)
    new_price = global_manager.get('commodity_prices')[sold_commodity]
    if new_price < sell_price:
        text_tools.print_to_screen("The price of " + sold_commodity + " has decreased from " + str(sell_price) + " to " + str(new_price) + ".", global_manager)
