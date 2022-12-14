#Contains functionality for different player countries

class country:
    '''
    Country with associated flavor text, art, images, and abilities that can be selected to play as
    '''
    def __init__(self, name, adjective, allow_particles, allow_double_last_names, image_id, background_set, country_effect, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string name: Name for this country, like 'France'
            string adjective: Descriptor for this country used in descriptions and associated art and flavor text files, like 'french'
            boolean allow_particles: Whether ministers of this country are allowed to have name particles, like de Rouvier
            boolean allow_double_last_names: Whether ministers of this country are allowed to have hyphenated last names, like Dupont-Rouvier
            string image_id: File path to the image used by this country
            string list background_set: Weighted list of backgrounds available to ministers of this country, like ['lowborn', 'lowborn', 'aristocrat']
            effect country_effect: Effect that is applied when this country is selected and vice versa
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_type = 'country'
        self.global_manager = global_manager
        self.global_manager.get('country_list').append(self)
        self.tooltip_text = []
        self.name = name
        self.adjective = adjective
        self.allow_particles = allow_particles
        self.allow_double_last_names = allow_double_last_names
        self.image_id = image_id
        self.background_set = background_set
        self.country_effect = country_effect

    def select(self):
        '''
        Description:
            Selects this country and modifies various game elements to match it, like setting the first name flavor text to this country's first name list
        Input:
            None
        Output:
            None
        '''
        if not self.global_manager.get('current_country') == 'none':
            self.global_manager.get('current_country').country_effect.remove()
        self.global_manager.set('current_country', self)
        self.global_manager.set('current_country_name', self.name)
        self.global_manager.get('flavor_text_manager').set_flavor_text('minister_first_names', 'text/flavor_minister_' + self.adjective + '_first_names.csv')
        self.global_manager.get('flavor_text_manager').allow_particles = self.allow_particles
        if self.allow_particles:
            self.global_manager.get('flavor_text_manager').set_flavor_text('minister_particles', 'text/flavor_minister_' + self.adjective + '_particles.csv')
        self.global_manager.get('flavor_text_manager').allow_double_last_names = self.allow_double_last_names
        self.global_manager.get('flavor_text_manager').set_flavor_text('minister_last_names', 'text/flavor_minister_' + self.adjective + '_last_names.csv')
        self.global_manager.set('weighted_backgrounds', self.background_set)
        for current_recruitment_button in self.global_manager.get('recruitment_button_list'):
            if current_recruitment_button.recruitment_type in self.global_manager.get('country_specific_units'):
                current_recruitment_button.calibrate(self)
        self.country_effect.apply()

    def update_tooltip(self):
        '''
        Description:
            Sets this country's tooltip to what it should be whenever the player looks at the tooltip
        Input:
            None
        Output:
            None
        '''
        self.tooltip_text = []
        self.tooltip_text.append('Name: ' + self.name)