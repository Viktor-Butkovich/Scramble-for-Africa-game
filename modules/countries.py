#Contains functionality for different player countries

class country:
    '''
    Country with associated flavor text, art, images, and abilities that can be selected to play as
    '''
    def __init__(self, name, adjective, allow_particles, aristocratic_particles, allow_double_last_names, background_set, country_effect, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string name: Name for this country, like 'France'
            string adjective: Descriptor for this country used in descriptions and associated art and flavor text files, like 'french'
            boolean allow_particles: Whether ministers of this country are allowed to have name particles, like de Rouvier
            boolean aristocratic_particles: Whether name particles for this country are reserved for aristocratic ministers
            boolean allow_double_last_names: Whether ministers of this country are allowed to have hyphenated last names, like Dupont-Rouvier
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
        self.aristocratic_particles = aristocratic_particles
        self.allow_double_last_names = allow_double_last_names
        self.image_id = 'locations/europe/' + self.name + '.png'
        self.flag_image_id = 'locations/flags/' + self.adjective + '.png'
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
        
        self.global_manager.get('flavor_text_manager').set_flavor_text('minister_first_names', 'text/names/' + self.adjective + '_first_names.csv')
        self.global_manager.get('flavor_text_manager').allow_particles = self.allow_particles
        if self.allow_particles:
            self.global_manager.get('flavor_text_manager').set_flavor_text('minister_particles', 'text/names/' + self.adjective + '_particles.csv')
        self.global_manager.get('flavor_text_manager').aristocratic_particles = self.aristocratic_particles
        self.global_manager.get('flavor_text_manager').allow_double_last_names = self.allow_double_last_names
        self.global_manager.get('flavor_text_manager').set_flavor_text('minister_last_names', 'text/names/' + self.adjective + '_last_names.csv')
        self.global_manager.set('weighted_backgrounds', self.background_set)
        for current_recruitment_button in self.global_manager.get('recruitment_button_list'):
            if current_recruitment_button.recruitment_type in self.global_manager.get('country_specific_units'):
                current_recruitment_button.calibrate(self)
        for current_flag_icon in self.global_manager.get('flag_icon_list'):
            current_flag_icon.image.set_image(self.flag_image_id)
        self.country_effect.apply()

    def get_effect_descriptor(self):
        if self.country_effect.effect_type == 'advertising_campaign_plus_modifier':
            return('Bonus when advertising')
        elif self.country_effect.effect_type == 'conversion_plus_modifier':
            return('Bonus when converting natives')
        elif self.country_effect.effect_type == 'attack_plus_modifier':
            return('Bonus when attacking natives')
        elif self.country_effect.effect_type == 'slave_capture_plus_modifier':
            return('Bonus when capturing slaves')
        elif self.country_effect.effect_type == 'no_slave_trade_penalty':
            return('No slave trade penalty')
        elif self.country_effect.effect_type == 'attack_minus_modifier':
            return('Penalty when attacking natives')


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

class hybrid_country(country):
    '''
    Country that uses combination of multiple namesets, like Belgium
    '''
    def __init__(self, name, adjective, background_set, country_effect, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string name: Name for this country, like 'France'
            string adjective: Descriptor for this country used in descriptions and associated art and flavor text files, like 'french'
            string image_id: File path to the Europe image used by this country
            string list background_set: Weighted list of backgrounds available to ministers of this country, like ['lowborn', 'lowborn', 'aristocrat']
            effect country_effect: Effect that is applied when this country is selected and vice versa
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(name, adjective, False, False, False, background_set, country_effect, global_manager)

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
        
        #specific text files are managed in flavor_text_manager for the time being, don't try to set to nonexistent belgium nameset
        #self.global_manager.get('flavor_text_manager').set_flavor_text('minister_first_names', 'text/flavor_minister_' + self.adjective + '_first_names.csv')
        self.global_manager.get('flavor_text_manager').allow_particles = self.allow_particles
        #if self.allow_particles:
        #    self.global_manager.get('flavor_text_manager').set_flavor_text('minister_particles', 'text/flavor_minister_' + self.adjective + '_particles.csv')
        self.global_manager.get('flavor_text_manager').aristocratic_particles = self.aristocratic_particles
        self.global_manager.get('flavor_text_manager').allow_double_last_names = self.allow_double_last_names
        #self.global_manager.get('flavor_text_manager').set_flavor_text('minister_last_names', 'text/flavor_minister_' + self.adjective + '_last_names.csv')
        self.global_manager.set('weighted_backgrounds', self.background_set)
        for current_recruitment_button in self.global_manager.get('recruitment_button_list'):
            if current_recruitment_button.recruitment_type in self.global_manager.get('country_specific_units'):
                current_recruitment_button.calibrate(self)
        for current_flag_icon in self.global_manager.get('flag_icon_list'):
            current_flag_icon.image.set_image(self.flag_image_id)
        self.country_effect.apply()
