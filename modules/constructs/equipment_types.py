# Contains functionality for worker type templates, such as European, African, Asian, slave workers

from typing import Dict, List
import modules.constants.constants as constants
import modules.constants.status as status

class equipment_type():
    '''
    Equipment template that tracks the effects, descriptions, and requirements of a particular equipment type
    '''
    def __init__(self, input_dict: Dict) -> None:
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'equipment_type': string value - Name of this equipment type
                'description': string list value - Description tooltip for this equipment type
                'price': float value - Purchase price of this equipment type
                'requirement': str value - Name of boolean attribute that must be True for units to equip this
        Output:
            None
        '''
        self.equipment_type: str = input_dict['equipment_type']
        self.description: List[str] = input_dict.get('description', [])
        status.equipment_types[self.equipment_type] = self
        self.price: float = input_dict.get('price', 5.0)
        self.requirement: str = input_dict.get('requirement', None)

    def check_requirement(self, unit):
        '''
        Description:
            Returns whether the inputted unit fulfills the requirements to equip this item - must have the requirement boolean attribute and it must be True
        Input:
            pmob unit: Unit to check requirement for
        Output:
            bool: Returns whether the inputted unit fulfills the requirements to equip this item
        '''
        return(self.requirement and hasattr(unit, self.requirement) and getattr(unit, self.requirement))
