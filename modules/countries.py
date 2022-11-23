#Contains functionality for different player countries

class country:
    '''
    Country with associated flavor text, art, and images that can be selected to play as
    '''
    def __init__(self, name, adjective, global_manager):
        global_manager.get('country_list').append(self)
        self.name = name
        self.adjective = adjective
        self.global_manager = global_manager

    def select(self):
        '''
        Description:
            Selects this country and modifies various game elements to match it, like setting the first name flavor text to this country's first name list
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('current_country', self)
        self.global_manager.get('flavor_text_manager').set_flavor_text('minister_first_names', 'text/flavor_minister_' + self.adjective + '_first_names.csv')
        self.global_manager.get('flavor_text_manager').set_flavor_text('minister_last_names', 'text/flavor_minister_' + self.adjective + '_last_names.csv')