#Contains functions that manage market prices and sale of commodities

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
    for i in range(4):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        change_price(changed_commodity, 1, global_manager)
    for i in range(2):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        while changed_commodity == 'consumer goods':
            changed_commodity = random.choice(global_manager.get('commodity_types'))
        change_price(changed_commodity, -1, global_manager)
    consumer_goods_roll = random.randrange(1, 7)
    if consumer_goods_roll == 1:
        change_price('consumer goods', 2, global_manager)
    elif consumer_goods_roll >= 5:
        change_price('consumer goods', -2, global_manager)

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

def set_price(changed_commodity, new_value, global_manager):
    '''
    Description:
        Sets the price of the inputted commodity to the inputted amount
    Input:
        string changed_commodity: Type of commodity whose price changes, like 'exotic wood'
        int new_value: New price of the inputted commodity
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('commodity_prices')[changed_commodity] = new_value
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
        global_manager.get('money_tracker').change(sell_price, 'commodities sold')
        seller.change_inventory(sold_commodity, -1)
        if random.randrange(1, 7) <= 2: #1/3 chance
            change_price(sold_commodity, -1, global_manager)
    text_tools.print_to_screen("You have gained " + str(sell_price * num_sold) + " money from selling " + str(num_sold) + " unit" + utility.generate_plural(num_sold) + " of " + sold_commodity + ".", global_manager)
    new_price = global_manager.get('commodity_prices')[sold_commodity]
    if new_price < sell_price:
        text_tools.print_to_screen("The price of " + sold_commodity + " has decreased from " + str(sell_price) + " to " + str(new_price) + ".", global_manager)

def attempt_worker_upkeep_change(change_type, worker_type, global_manager):
    '''
    Description:
        Controls the chance to increase worker upkeep when a worker leaves the labor pool or decrease worker upkeep when a worker joins the labor pool
    Input:
        string change_type: 'increase' or 'decrease' depending on whether a worker is being added to or removed from the labor pool, decides whether worker price increases or decreases
        string worker_type: 'European' or 'African', decides which type of worker has a price change
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if random.randrange(1, 7) >= 4: #half chance of change
        current_price = global_manager.get(worker_type.lower() + '_worker_upkeep')
        if change_type == 'increase':
            changed_price = round(current_price + global_manager.get('worker_upkeep_fluctuation_amount'), 1)
            global_manager.set(worker_type.lower() + '_worker_upkeep', changed_price)
            text_tools.print_to_screen("Hiring " + utility.generate_article(worker_type) + " " + worker_type + " worker increased " + worker_type + " worker upkeep from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
        elif change_type == 'decrease':
            changed_price = round(current_price - global_manager.get('worker_upkeep_fluctuation_amount'), 1)
            if changed_price >= global_manager.get('min_' + worker_type.lower() + '_worker_upkeep'):
                global_manager.set(worker_type.lower() + '_worker_upkeep', changed_price)
                text_tools.print_to_screen("Adding " + utility.generate_article(worker_type) + " " + worker_type + " worker to the labor pool decreased " + worker_type + " worker upkeep from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)

def attempt_slave_recruitment_cost_change(change_type, global_manager):
    '''
    Description:
        Controls the chance to increase slave recruitment cost when a slave worker is bought or decrease the recruitment cost over time
    Input:
        string change_type: 'increase' or 'decrease' depending on whether a worker is being added to or removed from the labor pool, decides whether worker price increases or decreases
        string worker_type: 'European' or 'African', decides which type of worker has a price change
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if random.randrange(1, 7) >= 4:
        current_price = global_manager.get('recruitment_costs')['slave worker']
        if change_type == 'increase':
            changed_price = round(current_price + global_manager.get('slave_recruitment_cost_fluctuation_amount'), 1)
            global_manager.get('recruitment_costs')['slave worker'] = changed_price
            text_tools.print_to_screen("Buying a slave worker increased the recruitment cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
        elif change_type == 'decrease':
            changed_price = round(current_price - global_manager.get('slave_recruitment_cost_fluctuation_amount'), 1)
            if changed_price >= global_manager.get('min_slave_worker_recruitment_cost'):
                global_manager.get('recruitment_costs')['slave worker'] = changed_price
                text_tools.print_to_screen("Adding slaves to the slave recruitment pool decreased the recruitment cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)

class loan():
    def __init__(self, from_save, input_dict, global_manager):
        self.global_manager = global_manager
        self.principal = input_dict['principal']
        self.interest = input_dict['interest']
        self.remaining_duration = input_dict['remaining_duration']
        self.total_to_pay = self.interest * self.remaining_duration
        self.global_manager.get('loan_list').append(self)
        if not from_save:
            self.global_manager.get('money_tracker').change(self.principal, 'loans')
            text_tools.print_to_screen("You have accepted a " + str(self.principal) + " money loan with interest payments of " + str(self.interest) + "/turn for " + str(self.remaining_duration) + " turns.", self.global_manager)

    def to_save_dict(self):
        save_dict = {}
        save_dict['init_type'] = 'loan'
        save_dict['principal'] = self.principal
        save_dict['interest'] = self.interest
        save_dict['remaining_duration'] = self.remaining_duration
        return(save_dict)

    def make_payment(self):
        self.global_manager.get('money_tracker').change(-1 * self.interest, 'loan interest')
        self.remaining_duration -= 1
        self.total_to_pay -= self.interest
        if self.total_to_pay <= 0:
            self.remove()

    def remove(self):
        total_paid = self.interest * 10
        text_tools.print_to_screen("You have finished paying off the " + str(total_paid) + " money required for your " + str(self.principal) + " money loan", self.global_manager)
        self.global_manager.set('loan_list', utility.remove_from_list(self.global_manager.get('loan_list'), self))

    def get_description(self):
        message = ""
        message += str(self.principal) + " money loan with interest payments of " + str(self.interest) + " each turn. " + str(self.remaining_duration) + " turns/" + str(self.total_to_pay) + "money remaining"
        return(message)
