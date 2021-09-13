import random
from . import text_tools
from . import utility

def adjust_prices(global_manager):
    num_increased = 2
    num_decreased = 1
    
    for i in range(2):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        #while changed_commodity == 'consumer goods':
        #    changed_commodity = random.choice(global_manager.get('commodity_types'))
        #global_manager.get('commodity_prices')[changed_commodity] += 1
        change_price(changed_commodity, 1, global_manager)
        
    for i in range(1):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        while changed_commodity == 'consumer goods':
            changed_commodity = random.choice(global_manager.get('commodity_types'))
        change_price(changed_commodity, -1, global_manager)
        #if global_manager.get('commodity_prices')[changed_commodity] > 1:
        #    global_manager.get('commodity_prices')[changed_commodity] -= 1

    consumer_goods_roll = random.randrange(1, 7)
    if consumer_goods_roll == 1:
        change_price('consumer goods', 1, global_manager)
    #    global_manager.get('commodity_prices')['consumer goods'] += 1
    elif consumer_goods_roll >= 5:
        change_price('consumer goods', -1, global_manager)
    #    if global_manager.get('commodity_prices')['consumer goods'] > 1:
    #        global_manager.get('commodity_prices')['consumer goods'] -= 1

    #global_manager.get('commodity_prices_label').update_label()

def change_price(changed_commodity, num_change, global_manager):
    global_manager.get('commodity_prices')[changed_commodity] += num_change
    if global_manager.get('commodity_prices')[changed_commodity] < 1:
        global_manager.get('commodity_prices')[changed_commodity] = 1
    global_manager.get('commodity_prices_label').update_label()

def sell(seller, sold_commodity, num_sold, global_manager):
    sell_price = global_manager.get('commodity_prices')[sold_commodity]
    for i in range(num_sold):
        global_manager.get('money_tracker').change(sell_price)
        seller.change_inventory(sold_commodity, -1)
        if random.randrange(1, 7) == 1: #1/6 chance
            #global_manager.get('commodity_prices')[sold_commodity] -= 1
            change_price(sold_commodity, -1, global_manager)
    text_tools.print_to_screen("You have gained " + str(sell_price * num_sold) + " money from selling " + str(num_sold) + " unit" + utility.generate_plural(num_sold) + " of " + sold_commodity + ".", global_manager)
    new_price = global_manager.get('commodity_prices')[sold_commodity]
    if new_price < sell_price:
        text_tools.print_to_screen("The price of " + sold_commodity + " has decreased from " + str(sell_price) + " to " + str(new_price) + ".", global_manager)
