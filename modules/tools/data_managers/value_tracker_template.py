import modules.constants.constants as constants

class value_tracker():
    '''
    Object that controls the value of a certain variable
    '''
    def __init__(self, value_key, initial_value, min_value, max_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string value_key: Key used to access this tracker's variable in the global manager
            any type initial_value: Value that this tracker's variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.set(value_key, initial_value)
        self.value_label = 'none'
        self.value_key = value_key
        self.min_value = min_value
        self.max_value = max_value

    def get(self):
        '''
        Description:
            Returns the value of this tracker's variable
        Input:
            None
        Output:
            any type: Value of this tracker's variable
        '''
        return(self.global_manager.get(self.value_key))

    def change(self, value_change):
        '''
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        '''
        self.set(self.get() + value_change)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())
    
    def set(self, new_value):
        '''
        Description:
            Sets the value of this tracker's variable to the inputted amount
        Input:
            any type value_change: Value that this tracker's variable is set to
        Output:
            None
        '''
        self.global_manager.set(self.value_key, new_value)
        if not self.min_value == 'none':
            if self.get() < self.min_value:
                self.global_manager.set(self.value_key, self.min_value)
        if not self.max_value == 'none':
            if self.get() > self.max_value:
                self.global_manager.set(self.value_key, self.max_value)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())

class public_opinion_tracker(value_tracker):
    '''
    Value tracker that tracks public opinion
    '''
    def change(self, value_change):
        '''
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        '''
        super().change(value_change)
        self.global_manager.get('money_label').check_for_updates()

class money_tracker(value_tracker):
    '''
    Value tracker that tracks money and causes the game to be lost when money runs out
    '''
    def __init__(self, initial_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            any type initial_value: Value that the money variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.transaction_history = {}
        self.reset_transaction_history()
        super().__init__('money', initial_value, 'none', 'none', global_manager)

    def reset_transaction_history(self):
        '''
        Description:
            Resets the stored transactions from the last turn, allowing new transactions to be recorded for the current turn's financial report
        Input:
            None
        Output:
            None
        '''
        self.transaction_history = {}
        for current_transaction_type in constants.transaction_types:
            self.transaction_history[current_transaction_type] = 0

    def change(self, value_change, change_type = 'misc.'):
        '''
        Description:
            Changes the money variable by the inputted amount
        Input:
            int value_change: Amount that the money variable is changed
        Output:
            None
        '''
        if change_type == 'misc.':
            if value_change > 0:
                change_type = 'misc_revenue'
            else:
                change_type = 'misc_expenses'
        self.transaction_history[change_type] += value_change
        if not value_change == 0:
            if abs(value_change) < 15:
                self.global_manager.get('sound_manager').play_sound('coins_1')
            else:
                self.global_manager.get('sound_manager').play_sound('coins_2')
        super().change(value_change)

    def set(self, new_value):
        '''
        Description:
            Sets the money variable to the inputted amount
        Input:
            int value_change: Value that the money variable is set to
        Output:
            None
        '''
        super().set(round(new_value, 2))

    def prepare_financial_report(self):
        '''
        Description:
            Creates and formats the text for a financial report based on the last turn's transactions
        Input:
            None
        Output:
            string: Formatted financial report text with /n being a new line
        '''
        notification_text = 'Financial report: /n /n'
        notification_text += 'Revenue: /n'
        total_revenue = 0
        for transaction_type in constants.transaction_types:
            if self.transaction_history[transaction_type] > 0:
                notification_text += '  ' + constants.transaction_descriptions[transaction_type].capitalize() + ': ' + str(self.transaction_history[transaction_type]) + ' /n'
                total_revenue += self.transaction_history[transaction_type]
        if total_revenue == 0:
            notification_text += '  None /n'
        
        notification_text += '/nExpenses: /n'
        total_expenses = 0
        for transaction_type in constants.transaction_types:
            if self.transaction_history[transaction_type] < 0:
                #if transaction_type == 'misc. expenses':
                #    notification_text += '  Misc: ' + str(self.transaction_history[transaction_type]) + ' /n'
                #else:
                notification_text += '  ' + constants.transaction_descriptions[transaction_type].capitalize() + ': ' + str(self.transaction_history[transaction_type]) + ' /n'
                total_expenses += self.transaction_history[transaction_type]
        if total_expenses == 0:
            notification_text += '  None /n'
        notification_text += ' /n'
        notification_text += 'Total revenue: ' + str(round(total_revenue, 2)) + ' /n'
        notification_text += 'Total expenses: ' + str(round(total_expenses, 2)) + ' /n'
        notification_text += 'Total profit: ' + str(round(total_revenue + total_expenses, 2)) + ' /n'
        return(notification_text)