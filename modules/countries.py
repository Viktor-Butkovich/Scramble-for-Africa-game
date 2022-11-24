#Contains functionality for different player countries

class country:
    '''
    Country with associated flavor text, art, images, and abilities that can be selected to play as
    '''
    def __init__(self, name, adjective, allow_particles, allow_double_last_names, background_set, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string name: Name for this country, like 'France'
            string adjective: Descriptor for this country used in descriptions and associated art and flavor text files, like 'french'
            boolean allow_particles: Whether ministers of this country are allowed to have name particles, like de Rouvier
            boolean allow_double_last_names: Whether ministers of this country are allowed to have hyphenated last names, like Dupont-Rouvier
            string list background_set: Weighted list of backgrounds available to ministers of this country, like ['lowborn', 'lowborn', 'aristocrat']
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        global_manager.get('country_list').append(self)
        self.name = name
        self.adjective = adjective
        self.allow_particles = allow_particles
        self.allow_double_last_names = allow_double_last_names
        self.global_manager = global_manager
        self.background_set = background_set

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
        self.global_manager.get('flavor_text_manager').allow_particles = self.allow_particles
        if self.allow_particles:
            self.global_manager.get('flavor_text_manager').set_flavor_text('minister_particles', 'text/flavor_minister_' + self.adjective + '_particles.csv')
        self.global_manager.get('flavor_text_manager').allow_double_last_names = self.allow_double_last_names
        self.global_manager.get('flavor_text_manager').set_flavor_text('minister_last_names', 'text/flavor_minister_' + self.adjective + '_last_names.csv')
        self.global_manager.set('weighted_backgrounds', self.background_set)