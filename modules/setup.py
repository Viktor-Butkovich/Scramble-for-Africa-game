# Manages initial game setup in a semi-modular order

import pygame
import os
import logging
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags
import modules.util.scaling as scaling
import modules.util.actor_utility as actor_utility
import modules.util.game_transitions as game_transitions
import modules.constructs.fonts as fonts
import modules.constructs.countries as countries
import modules.constructs.worker_types as worker_types
import modules.constructs.equipment_types as equipment_types
import modules.constructs.terrain_feature_types as terrain_feature_types
from modules.tools.data_managers import (
    notification_manager_template,
    value_tracker_template,
    achievement_manager_template,
)
from modules.action_types import (
    public_relations_campaign,
    religious_campaign,
    suppress_slave_trade,
    advertising_campaign,
    conversion,
    combat,
    exploration,
    construction,
    upgrade,
    repair,
    loan_search,
    rumor_search,
    artifact_search,
    trade,
    willing_to_trade,
    slave_capture,
    active_investigation,
    track_beasts,
    trial,
    canoe_purchase,
    canoe_construction,
    attack_village,
)


def setup(*args):
    """
    Description:
        Runs the inputted setup functions in order
    Input:
        function list args: List of setup functions to run
    Output:
        None
    """
    flags.startup_complete = False
    for setup_function in args:
        setup_function()
    flags.startup_complete = True
    flags.creating_new_game = False


def info_displays():
    """
    Description:
        Initializes info displays collection (must be run after new game setup is created for correct layering)
    Input:
        None
    Output:
        None
    """
    status.info_displays_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    5, constants.default_display_height - 205 + 125 - 5
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(10),
                "modes": ["strategic", "europe", "ministers", "new_game_setup"],
                "init_type": "ordered collection",
                "description": "general information panel",
                "resize_with_contents": True,
            }
        )
    )


def misc():
    """
    Description:
        Initializes object lists, current object variables, current status booleans, and other misc. values
    Input:
        None
    Output:
        None
    """
    constants.font_size = scaling.scale_height(constants.default_font_size)
    constants.notification_font_size = scaling.scale_height(
        constants.default_notification_font_size
    )

    constants.myfont = fonts.font(
        {
            "descriptor": "default",
            "name": constants.font_name,
            "size": constants.font_size,
            "color": "black",
        }
    )
    fonts.font(
        {
            "descriptor": "white",
            "name": constants.font_name,
            "size": constants.font_size,
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "default_notification",
            "name": constants.font_name,
            "size": constants.notification_font_size,
            "color": "black",
        }
    )
    fonts.font(
        {
            "descriptor": "white_notification",
            "name": constants.font_name,
            "size": constants.notification_font_size,
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "large_notification",
            "name": constants.font_name,
            "size": scaling.scale_height(30),
            "color": "black",
        }
    )
    fonts.font(
        {
            "descriptor": "large_white_notification",
            "name": constants.font_name,
            "size": scaling.scale_height(30),
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "max_detail_white",
            "name": "helvetica",
            "size": scaling.scale_height(100),
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "max_detail_black",
            "name": "helvetica",
            "size": scaling.scale_height(100),
            "color": "black",
        }
    )

    # page 1
    instructions_message = "Placeholder instructions, use += to add"
    status.instructions_list.append(instructions_message)

    status.loading_image = constants.actor_creation_manager.create_interface_element(
        {
            "image_id": ["misc/title.png", "misc/loading.png"],
            "init_type": "loading image template image",
        }
    )

    strategic_background_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "modes": [
                    "strategic",
                    "europe",
                    "trial",
                    "new_game_setup",
                ],
                "image_id": "misc/background.png",
                "init_type": "background image",
            }
        )
    )

    ministers_background_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "modes": [
                    "ministers",
                ],
                "image_id": "misc/ministers_background.png",
                "init_type": "background image",
            }
        )
    )

    title_background_image = constants.actor_creation_manager.create_interface_element(
        {
            "modes": [
                "main_menu",
            ],
            "image_id": "misc/title.png",
            "init_type": "background image",
        }
    )

    status.safe_click_area = constants.actor_creation_manager.create_interface_element(
        {
            "width": constants.display_width / 2 - scaling.scale_width(35),
            "height": constants.display_height,
            "modes": ["strategic", "europe", "ministers", "new_game_setup"],
            "image_id": "misc/empty.png",  # make a good image for this
            "init_type": "safe click panel",
        }
    )
    # safe click area has empty image but is managed with panel to create correct behavior - its intended image is in the background image's bundle to blit more efficiently

    game_transitions.set_game_mode("main_menu")

    constants.mouse_follower = (
        constants.actor_creation_manager.create_interface_element(
            {"init_type": "mouse follower image"}
        )
    )

    constants.notification_manager = (
        notification_manager_template.notification_manager_template()
    )

    constants.achievement_manager = (
        achievement_manager_template.achievement_manager_template()
    )

    status.grids_collection = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.grids_collection_x, constants.grids_collection_y
            ),
            "width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "europe"],
            "init_type": "interface collection",
        }
    )

    # anchor = constants.actor_creation_manager.create_interface_element(
    #    {'width': 1, 'height': 1, 'init_type': 'interface element', 'parent_collection': status.info_displays_collection}
    # ) #rect at original location prevents collection from moving unintentionally when resizing


def worker_types_config():
    """
    Description:
        Defines worker type templates
    Input:
        None
    Output:
        None
    """
    worker_types.worker_type(
        False,
        {
            "adjective": "European",
            "upkeep": 6.0,
            "can_crew": ["steamship", "steamboat", "train"],
            "upkeep_variance": True,
            "fired_description": "Unlike African workers, fired European workers will return home rather than settle in slums. /n /n"
            + "Firing European workers reflects poorly on your company and will incur a public opinion penalty of 1. /n /n",
        },
    )
    worker_types.worker_type(
        False,
        {
            "adjective": "African",
            "upkeep": 4.0,
            "can_crew": ["steamboat", "train"],
            "fired_description": "Fired workers will enter the labor pool and wander, eventually settling in slums where they may be hired again. /n /n",
        },
    )
    worker_types.worker_type(
        False,
        {
            "adjective": "Asian",
            "upkeep": 4.0,
            "can_crew": ["steamboat", "train"],
            "upkeep_variance": True,
            "fired_description": "Like European workers, fired Asian workers will return home rather than settle in slums, but can be fired with no effect on your reputation. /n /n",
        },
    )
    worker_types.worker_type(
        False,
        {
            "init_type": "slaves",
            "adjective": "slave",
            "recruitment_cost": 5.0,
            "upkeep": 2.0,
            "fired_description": "Firing slaves frees them, increasing public opinion. Freed slaves join the labor pool and are automatically hired as workers. /n /n",
        },
    )
    worker_types.worker_type(
        False,
        {
            "adjective": "religious",
            "name": "church volunteers",
            "upkeep": 0.0,
            "fired_description": "Unlike African workers, fired church volunteers will never settle in slums and will instead return to Europe. /n /n"
            + "Firing church volunteers reflects poorly on your company and will incur a public opinion penalty of 1. /n /n",
        },
    )


def equipment_types_config():
    """
    Description:
        Defines equipment type templates
    Input:
        None
    Output:
        None
    """
    equipment_types.equipment_type(
        {
            "equipment_type": "Maxim gun",
            "requirement": "is_battalion",
            "effects": {
                "positive_modifiers": [
                    "combat",
                    "attack_village",
                    "suppress_slave_trade",
                ],
                "max_movement_points": -1,
            },
            "description": [
                "A Maxim gun provides a positive modifier (half chance of +1) to all combat rolls, but decreases movement points by 1",
                "Can only be equipped by battalions",
            ],
        }
    )
    equipment_types.equipment_type(
        {
            "equipment_type": "canoes",
            "requirement": ["is_safari", "can_explore"],
            "description": [
                "Canoes allow units to travel through river water for 1 movement point, except for cataracts",
                "Can only be equipped by expeditions and safaris",
            ],
        }
    )


def terrain_feature_types_config():
    """
    Description:
        Defines terrain feature type templates
    Input:
        None
    Output:
        None
    """
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "cataract",
            "requirements": {"terrain": "water", "min_y": 1},
            "frequency": (1, 12),
            "description": [
                "A cataract, or waterfall, slows most movement through this section of the river",
                "Canoes can not traverse cataracts, but canoe units can spend their whole turn moving into a cataract in the same way that non-canoe units can enter rivers",
                "Steamboats can not traverse cataracts, but can circumvent them through a series of adjacent ports",
                "Other units treat cataracts as usual river water",
            ],
        }
    )
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "cannibals",
            "requirements": {"resource": "natives"},
            "frequency": (1, 3),
            "level": 1,  # Appears above village icon
            "description": [
                "Locals rumor that this village traditionally practices cannibalism",
                "Warriors from this village will be more formidable in combat",
                "Any successful religious conversion at yellow or lower aggressiveness will convince the villagers to abandon cannibalism",
            ],
        }
    )

    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "river mouth",
            "image_id": "misc/empty.png",
            "description": [
                "This river will lead inland for some distance, eventually stopping at its source",
                "Rivers are much easier to explore - an expedition on a river automatically explores all adjacent tiles",
                "Discovering the source of a river is much sought after, and will result in rewards from your country's Geographical Society",
            ],
        }
    )

    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "river source",
            "image_id": "misc/empty.png",
            "description": [
                "This is a river's point of origin, which has been sought after by explorers for hundreds of years",
                "Your country's Geographical Sociey will grant rewards for any river sources discovered",
            ],
        }
    )


def terrains():
    """
    Description:
        Defines terrains and beasts
    Input:
        None
    Output:
        None
    """
    for current_terrain in constants.terrain_list + ["ocean_water", "river_water"]:
        current_index = 0
        while os.path.exists(
            "graphics/terrains/" + current_terrain + "_" + str(current_index) + ".png"
        ):
            current_index += 1
        current_index -= 1  # back up from index that didn't work
        constants.terrain_variant_dict[current_terrain] = (
            current_index + 1
        )  # number of variants, variants in format 'mountain_0', 'mountain_1', etc.


def actions():
    """
    Description:
        Configures any actions in the action_types folder, preparing them to be automatically implemented
    Input:
        None
    Output:
        none
    """
    for building_type in constants.building_types + ["train", "steamboat"]:
        if not building_type in [
            "warehouses",
            "slums",
        ]:  # only include buildings that can be built manually
            construction.construction(building_type=building_type)
            if not building_type in ["train", "steamboat", "infrastructure"]:
                repair.repair(building_type=building_type)
    for upgrade_type in constants.upgrade_types:
        upgrade.upgrade(building_type=upgrade_type)
    public_relations_campaign.public_relations_campaign()
    religious_campaign.religious_campaign()
    suppress_slave_trade.suppress_slave_trade()
    advertising_campaign.advertising_campaign()
    conversion.conversion()
    combat.combat()
    exploration.exploration()
    loan_search.loan_search()
    rumor_search.rumor_search()
    artifact_search.artifact_search()
    willing_to_trade.willing_to_trade()
    trade.trade()
    slave_capture.slave_capture()
    attack_village.attack_village()
    active_investigation.active_investigation()
    track_beasts.track_beasts()
    trial.trial()
    canoe_purchase.canoe_purchase()
    canoe_construction.canoe_consruction()

    for action_type in status.actions:
        if status.actions[action_type].placement_type == "free":
            button_input_dict = status.actions[action_type].button_setup({})
            if button_input_dict:
                constants.actor_creation_manager.create_interface_element(
                    button_input_dict
                )
    # action imports hardcoded here, alternative to needing to keep module files in .exe version


def commodities():
    """
    Description:
        Defines commodities with associated buildings and icons, along with buildings
    Input:
        None
    Output:
        None
    """
    for current_commodity in constants.commodity_types:
        constants.item_prices[current_commodity] = 0
        constants.sold_commodities[current_commodity] = 0

    for current_commodity in constants.collectable_resources:
        constants.commodities_produced[current_commodity] = 0

    for current_equipment in status.equipment_types:
        constants.item_prices[current_equipment] = status.equipment_types[
            current_equipment
        ].price


def def_ministers():
    """
    Description:
        Defines minister positions, backgrounds, and associated units
    Input:
        None
    Output:
        None
    """
    for current_minister_type in constants.minister_types:
        status.current_ministers[current_minister_type] = None


def def_countries():
    """
    Description:
        Defines countries with associated passive effects and background, name, and unit sets
    Input:
        None
    Output:
        None
    """
    # 25 backgrounds by default
    default_weighted_backgrounds = [
        "lowborn",
        "lowborn",
        "lowborn",
        "lowborn",
        "lowborn",
        "lowborn",
        "lowborn",
        "lowborn",
        "lowborn",
        "lowborn",
        "banker",
        "merchant",
        "lawyer",
        "industrialist",
        "industrialist",
        "industrialist",
        "industrialist",
        "industrialist",
        "industrialist",
        "natural scientist",
        "doctor",
        "politician",
        "politician",
        "army officer",
        "naval officer",
    ]

    # each country adds 18 backgrounds for what is more common in that country - half middle, half upper class
    british_weighted_backgrounds = default_weighted_backgrounds + [
        "merchant",
        "lawyer",
        "natural scientist",
        "doctor",
        "naval officer",
        "naval officer",
        "naval officer",
        "preacher",
        "preacher",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "royal heir",
    ]

    status.Britain = countries.country(
        {
            "name": "Britain",
            "adjective": "british",
            "government_type_adjective": "royal",
            "religion": "protestant",
            "allow_particles": False,
            "aristocratic_particles": False,
            "allow_double_last_names": False,
            "background_set": british_weighted_backgrounds,
            "country_effect": constants.effect_manager.create_effect(
                "british_country_modifier", "construction_plus_modifier"
            ),
        }
    )

    french_weighted_backgrounds = default_weighted_backgrounds + [
        "merchant",
        "lawyer",
        "natural scientist",
        "doctor",
        "doctor",
        "naval officer",
        "army officer",
        "priest",
        "priest",
        "politician",
        "politician",
        "politician",
        "politician",
        "politician",
        "politician",
        "industrialist",
        "industrialist",
        "business magnate",
    ]

    status.France = countries.country(
        {
            "name": "France",
            "adjective": "french",
            "government_type_adjective": "national",
            "religion": "catholic",
            "allow_particles": True,
            "aristocratic_particles": False,
            "allow_double_last_names": True,
            "background_set": french_weighted_backgrounds,
            "country_effect": constants.effect_manager.create_effect(
                "french_country_modifier", "conversion_plus_modifier"
            ),
            "has_aristocracy": False,
        }
    )

    german_weighted_backgrounds = default_weighted_backgrounds + [
        "merchant",
        "lawyer",
        "natural scientist",
        "doctor",
        "army officer",
        "army officer",
        "army officer",
        "preacher",
        "preacher",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "royal heir",
    ]

    status.Germany = countries.country(
        {
            "name": "Germany",
            "adjective": "german",
            "government_type_adjective": "imperial",
            "religion": "protestant",
            "allow_particles": True,
            "aristocratic_particles": True,
            "allow_double_last_names": False,
            "background_set": german_weighted_backgrounds,
            "country_effect": constants.effect_manager.create_effect(
                "german_country_modifier", "combat_plus_modifier"
            ),
        }
    )

    belgian_weighted_backgrounds = default_weighted_backgrounds + [
        "merchant",
        "lawyer",
        "natural scientist",
        "doctor",
        "army officer",
        "army officer",
        "naval officer",
        "priest",
        "priest",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "royal heir",
    ]

    status.Belgium = countries.hybrid_country(
        {
            "name": "Belgium",
            "adjective": "belgian",
            "government_type_adjective": "royal",
            "religion": "catholic",
            "background_set": belgian_weighted_backgrounds,
            "country_effect": constants.effect_manager.create_effect(
                "belgian_country_modifier", "slave_capture_plus_modifier"
            ),
        }
    )

    portuguese_weighted_backgrounds = default_weighted_backgrounds + [
        "merchant",
        "lawyer",
        "natural scientist",
        "natural scientist",
        "doctor",
        "naval officer",
        "naval officer",
        "priest",
        "priest",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "royal heir",
    ]

    status.Portugal = countries.country(
        {
            "name": "Portugal",
            "adjective": "portuguese",
            "government_type_adjective": "royal",
            "religion": "catholic",
            "allow_particles": True,
            "aristocratic_particles": False,
            "allow_double_last_names": False,
            "background_set": portuguese_weighted_backgrounds,
            "country_effect": constants.effect_manager.create_effect(
                "portuguese_country_modifier", "no_slave_trade_penalty"
            ),
        }
    )

    italian_weighted_backgrounds = default_weighted_backgrounds + [
        "merchant",
        "lawyer",
        "lawyer",
        "natural scientist",
        "doctor",
        "army officer",
        "naval officer",
        "priest",
        "priest",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "aristocrat",
        "royal heir",
    ]

    status.Italy = countries.country(
        {
            "name": "Italy",
            "adjective": "italian",
            "government_type_adjective": "royal",
            "religion": "catholic",
            "allow_particles": True,
            "aristocratic_particles": True,
            "allow_double_last_names": False,
            "background_set": italian_weighted_backgrounds,
            "country_effect": constants.effect_manager.create_effect(
                "italian_country_modifier", "combat_minus_modifier"
            ),
        }
    )


def transactions():
    """
    Description:
        Defines recruitment, upkeep, building, and action costs, along with action and financial transaction types
    Input:
        None
    Output:
        None
    """
    for current_officer in constants.officer_types:
        constants.recruitment_costs[current_officer] = constants.recruitment_costs[
            "officer"
        ]
    actor_utility.update_descriptions()
    actor_utility.reset_action_prices()
    actor_utility.set_slave_traders_strength(0)


def lore():
    """
    Description:
        Defines the types of lore missions, artifacts within each one, and the current lore mission
    Input:
        None
    Output:
        None
    """
    status.lore_types_effects_dict["zoology"] = constants.effect_manager.create_effect(
        "zoology_completion_effect", "hunting_plus_modifier"
    )
    status.lore_types_effects_dict["botany"] = constants.effect_manager.create_effect(
        "botany_completion_effect", "health_attrition_plus_modifier"
    )
    status.lore_types_effects_dict[
        "archaeology"
    ] = constants.effect_manager.create_effect(
        "archaeology_completion_effect", "combat_plus_modifier"
    )
    status.lore_types_effects_dict[
        "anthropology"
    ] = constants.effect_manager.create_effect(
        "anthropology_completion_effect", "conversion_plus_modifier"
    )
    status.lore_types_effects_dict[
        "paleontology"
    ] = constants.effect_manager.create_effect(
        "paleontology_completion_effect", "public_relations_campaign_modifier"
    )
    status.lore_types_effects_dict["theology"] = constants.effect_manager.create_effect(
        "theology_completion_effect", "religious_campaign_plus_modifier"
    )


def value_trackers():
    """
    Description:
        Defines important global values and initializes associated tracker labels
    Input:
        None
    Output:
        None
    """
    value_trackers_ordered_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    250, constants.default_display_height - 5
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "modes": [
                    "strategic",
                    "europe",
                    "ministers",
                    "trial",
                    "main_menu",
                    "new_game_setup",
                ],
                "init_type": "ordered collection",
            }
        )
    )

    constants.turn_tracker = value_tracker_template.value_tracker_template(
        "turn", 0, "none", "none"
    )
    constants.actor_creation_manager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "europe", "ministers"],
            "image_id": "misc/default_label.png",
            "value_name": "turn",
            "init_type": "value label",
            "parent_collection": value_trackers_ordered_collection,
            "member_config": {
                "order_x_offset": scaling.scale_width(315),
                "order_overlap": True,
            },
        }
    )

    constants.money_tracker = value_tracker_template.money_tracker_template(100)
    constants.money_label = constants.actor_creation_manager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "europe", "ministers", "trial"],
            "image_id": "misc/default_label.png",
            "init_type": "money label",
            "parent_collection": value_trackers_ordered_collection,
            "member_config": {
                "index": 1
            },  # should appear before public opinion in collection but relies on public opinion existing
        }
    )

    constants.public_opinion_tracker = (
        value_tracker_template.public_opinion_tracker_template(
            "public_opinion", 0, 0, 100
        )
    )
    constants.actor_creation_manager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "europe", "ministers", "trial"],
            "image_id": "misc/default_label.png",
            "value_name": "public_opinion",
            "init_type": "value label",
            "parent_collection": value_trackers_ordered_collection,
        }
    )

    if constants.effect_manager.effect_active("track_fps"):
        constants.fps_tracker = value_tracker_template.value_tracker_template(
            "fps", 0, 0, "none"
        )
        constants.actor_creation_manager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "modes": [
                    "strategic",
                    "europe",
                    "ministers",
                    "trial",
                    "main_menu",
                    "new_game_setup",
                ],
                "image_id": "misc/default_label.png",
                "value_name": "fps",
                "init_type": "value label",
                "parent_collection": value_trackers_ordered_collection,
            }
        )

    constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                225, constants.default_display_height - 35
            ),
            "width": scaling.scale_width(30),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "europe", "ministers", "trial"],
            "image_id": "buttons/instructions.png",
            "init_type": "show previous reports button",
        }
    )
    constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                225, constants.default_display_height - 70
            ),
            "width": scaling.scale_width(30),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "europe", "ministers", "trial"],
            "image_id": "buttons/execute_single_movement_route_button.png",
            "init_type": "show lore missions button",
        }
    )

    constants.evil_tracker = value_tracker_template.value_tracker_template(
        "evil", 0, 0, 100
    )

    constants.fear_tracker = value_tracker_template.value_tracker_template(
        "fear", 1, 1, 6
    )


def buttons():
    """
    Description:
        Initializes static buttons
    Input:
        None
    Output:
        None
    """
    # Could implement switch game mode buttons based on state machine logic for different modes
    input_dict = {
        "coordinates": scaling.scale_coordinates(0, 10),
        "width": scaling.scale_width(150),
        "height": scaling.scale_height(100),
        "image_id": "buttons/european_hq_button.png",
        "modes": ["strategic", "europe"],
        "to_mode": "europe",
        "init_type": "free image",
        "parent_collection": status.grids_collection,
    }
    strategic_flag_icon = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    status.flag_icon_list.append(
        strategic_flag_icon
    )  # sets button image to update to flag icon when country changes

    input_dict["modes"] = ["ministers"]
    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width / 2 - 75, constants.default_display_height - 160
    )
    input_dict["parent_collection"] = "none"
    ministers_flag_icon = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    status.flag_icon_list.append(ministers_flag_icon)

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            1065, constants.default_display_height - 55
        ),
        "height": scaling.scale_height(50),
        "width": scaling.scale_width(50),
        "keybind_id": pygame.K_1,
        "image_id": "locations/africa_button.png",
        "modes": ["ministers", "strategic", "europe", "trial"],
        "to_mode": "strategic",
        "init_type": "switch game mode button",
    }
    to_strategic_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict.update(
        {
            "coordinates": scaling.scale_coordinates(
                1125, constants.default_display_height - 55
            ),
            "image_id": "locations/europe_button.png",
            "to_mode": "europe",
            "keybind_id": pygame.K_2,
        }
    )
    to_europe_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict.update(
        {
            "coordinates": scaling.scale_coordinates(
                1185, constants.default_display_height - 55
            ),
            "width": scaling.scale_width(50),
            "to_mode": "ministers",
            "image_id": "buttons/european_hq_button.png",
            "keybind_id": pygame.K_3,
        }
    )
    to_ministers_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    rhs_menu_collection = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.default_display_width - 55,
                constants.default_display_height - 5,
            ),
            "width": 10,
            "height": 10,
            "modes": ["strategic", "europe", "ministers", "trial", "new_game_setup"],
            "init_type": "ordered collection",
            "member_config": {"order_exempt": True},
            "separation": 5,
        }
    )

    lhs_menu_collection = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                5, constants.default_display_height - 55
            ),
            "width": 10,
            "height": 10,
            "modes": ["strategic", "europe", "ministers", "new_game_setup"],
            "init_type": "ordered collection",
            "member_config": {"order_exempt": True},
            "separation": 5,
            "direction": "horizontal",
        }
    )

    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width - 50, constants.default_display_height - 50
    )
    input_dict["image_id"] = "buttons/exit_european_hq_button.png"
    input_dict["init_type"] = "switch game mode button"
    input_dict["width"] = scaling.scale_width(50)
    input_dict["height"] = scaling.scale_height(50)
    input_dict["modes"] = ["strategic", "europe", "ministers", "trial"]
    input_dict["keybind_id"] = pygame.K_ESCAPE
    input_dict["to_mode"] = "main_menu"
    to_main_menu_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(to_main_menu_button)

    input_dict["coordinates"] = scaling.scale_coordinates(
        0, constants.default_display_height - 50
    )
    input_dict["modes"] = ["new_game_setup"]
    input_dict["keybind_id"] = pygame.K_ESCAPE
    new_game_setup_to_main_menu_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )
    lhs_menu_collection.add_member(new_game_setup_to_main_menu_button)

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            round(constants.default_display_width * 0.4),
            constants.default_display_height - 55,
        ),
        "width": scaling.scale_width(round(constants.default_display_width * 0.2)),
        "height": scaling.scale_height(50),
        "modes": ["strategic", "europe", "ministers", "trial"],
        "keybind_id": pygame.K_SPACE,
        "image_id": "buttons/end_turn_button.png",
        "init_type": "end turn button",
    }
    end_turn_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height / 2 - 150),
    )
    input_dict["modes"] = ["main_menu"]
    input_dict["keybind_id"] = pygame.K_n
    input_dict["image_id"] = "buttons/new_game_button.png"
    input_dict["init_type"] = "new game button"
    main_menu_new_game_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height / 2 - 400),
    )
    input_dict["modes"] = ["new_game_setup"]
    input_dict["keybind_id"] = pygame.K_n
    setup_new_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height / 2 - 225),
    )
    input_dict["modes"] = ["main_menu"]
    input_dict["keybind_id"] = pygame.K_l
    input_dict["image_id"] = "buttons/load_game_button.png"
    input_dict["init_type"] = "load game button"
    load_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            constants.default_display_width - 50, constants.default_display_height - 125
        ),
        "width": scaling.scale_width(50),
        "height": scaling.scale_height(50),
        "modes": ["strategic", "europe", "ministers", "trial"],
        "image_id": "buttons/save_game_button.png",
        "init_type": "save game button",
    }
    save_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(save_game_button)

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height - 200),
    )
    input_dict["modes"] = ["strategic"]
    input_dict["image_id"] = "buttons/grid_line_button.png"
    input_dict["init_type"] = "toggle grid lines button"
    toggle_grid_lines_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )
    rhs_menu_collection.add_member(toggle_grid_lines_button)

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height - 275),
    )
    input_dict["modes"] = ["strategic", "europe", "ministers", "trial"]
    input_dict["keybind_id"] = pygame.K_j
    input_dict["image_id"] = "buttons/text_box_size_button.png"
    input_dict["init_type"] = "expand text box button"
    expand_text_box_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(expand_text_box_button)

    input_dict["coordinates"] = scaling.scale_coordinates(
        110, constants.default_display_height - 50
    )
    input_dict["modes"] = ["strategic", "europe", "ministers"]
    input_dict["keybind_id"] = pygame.K_TAB
    input_dict["image_id"] = "buttons/cycle_units_button.png"
    input_dict["init_type"] = "cycle units button"
    cycle_units_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    lhs_menu_collection.add_member(cycle_units_button)

    input_dict["coordinates"] = (scaling.scale_width(55), input_dict["coordinates"][1])
    input_dict["modes"] = ["strategic"]
    del input_dict["keybind_id"]
    input_dict["image_id"] = "buttons/free_slaves_button.png"
    input_dict["init_type"] = "confirm free all button"
    free_all_slaves_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    lhs_menu_collection.add_member(free_all_slaves_button)

    input_dict["coordinates"] = (scaling.scale_width(165), input_dict["coordinates"][1])
    input_dict["modes"] = ["strategic", "europe"]
    input_dict["image_id"] = "buttons/disable_sentry_mode_button.png"
    input_dict["init_type"] = "wake up all button"
    wake_up_all_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    lhs_menu_collection.add_member(wake_up_all_button)

    input_dict["coordinates"] = (scaling.scale_width(220), input_dict["coordinates"][1])
    input_dict["image_id"] = "buttons/execute_movement_routes_button.png"
    input_dict["init_type"] = "execute movement routes button"
    execute_movement_routes_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )
    lhs_menu_collection.add_member(execute_movement_routes_button)

    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width - 55, constants.default_display_height - 55
    )
    input_dict["modes"] = ["main_menu"]
    input_dict["image_id"] = ["buttons/exit_european_hq_button.png"]
    input_dict["init_type"] = "generate crash button"
    generate_crash_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )


def europe_screen():
    """
    Description:
        Initializes static interface of Europe screen - purchase buttons for units and items, 8 per column
    Input:
        None
    Output:
        None
    """
    europe_purchase_buttons = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(1500, 20),
            "width": 10,
            "height": 10,
            "modes": ["europe"],
            "init_type": "ordered collection",
            "separation": scaling.scale_height(20),
            "reversed": True,
            "second_dimension_increment": scaling.scale_width(125),
            "direction": "vertical",
        }
    )

    for recruitment_index, recruitment_type in enumerate(
        constants.recruitment_types
    ):  # Creates recruitment button for each officer type, workers, and steamship
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(100),
                "init_type": "recruitment button",
                "parent_collection": europe_purchase_buttons,
                "recruitment_type": recruitment_type,
                "member_config": {
                    "second_dimension_coordinate": -1 * (recruitment_index // 8)
                },
            }
        )

    for item_type in [
        "consumer goods",
        "Maxim gun",
    ]:  # Creates purchase button for items from Europe
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(100),
                "init_type": "buy item button",
                "parent_collection": europe_purchase_buttons,
                "item_type": item_type,
                "member_config": {
                    "second_dimension_coordinate": -1 * (recruitment_index // 8)
                },  # Re-uses recruitment index from previous loop
            }
        )
        recruitment_index += 1


def ministers_screen():
    """
    Description:
        Initializes static interface of ministers screen
    Input:
        None
    Output:
        None
    """
    # minister table setup
    table_width = 400
    table_height = 750
    constants.actor_creation_manager.create_interface_element(
        {
            "image_id": "misc/minister_table.png",
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2) - (table_width / 2), 55
            ),
            "width": scaling.scale_width(table_width),
            "height": scaling.scale_height(table_height),
            "modes": ["ministers"],
            "init_type": "free image",
        }
    )
    status.table_map_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2) - 100, 400
            ),
            "init_type": "free image",
            "modes": ["ministers"],
            "width": scaling.scale_width(200),
            "height": scaling.scale_height(200),
            "image_id": "misc/empty.png",
        }
    )
    position_icon_width = 75
    portrait_icon_width = 125
    input_dict = {
        "width": scaling.scale_width(portrait_icon_width),
        "height": scaling.scale_height(portrait_icon_width),
        "modes": ["ministers"],
        "color": "gray",
        "init_type": "minister portrait image",
    }
    for current_index in range(
        0, 8
    ):  # creates an office icon and a portrait at a section of the table for each minister
        input_dict["minister_type"] = constants.minister_types[current_index]
        if current_index <= 3:  # left side
            constants.actor_creation_manager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(
                        (constants.default_display_width / 2) - (table_width / 2) + 10,
                        current_index * 180
                        + 95
                        + (portrait_icon_width / 2 - position_icon_width / 2),
                    ),
                    "width": scaling.scale_width(position_icon_width),
                    "height": scaling.scale_height(position_icon_width),
                    "modes": ["ministers"],
                    "minister_type": constants.minister_types[current_index],
                    "attached_label": "none",
                    "init_type": "minister type image",
                }
            )

            input_dict["coordinates"] = scaling.scale_coordinates(
                (constants.default_display_width / 2)
                - (table_width / 2)
                - portrait_icon_width
                - 10,
                current_index * 180 + 95,
            )
            constants.actor_creation_manager.create_interface_element(input_dict)

        else:
            constants.actor_creation_manager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(
                        (constants.default_display_width / 2)
                        + (table_width / 2)
                        - position_icon_width
                        - 10,
                        (current_index - 4) * 180
                        + 95
                        + (portrait_icon_width / 2 - position_icon_width / 2),
                    ),
                    "width": scaling.scale_width(position_icon_width),
                    "height": scaling.scale_height(position_icon_width),
                    "modes": ["ministers"],
                    "minister_type": constants.minister_types[current_index],
                    "attached_label": "none",
                    "init_type": "minister type image",
                }
            )

            input_dict["coordinates"] = scaling.scale_coordinates(
                (constants.default_display_width / 2) + (table_width / 2) + 10,
                (current_index - 4) * 180 + 95,
            )
            constants.actor_creation_manager.create_interface_element(input_dict)

    available_minister_display_x = constants.default_display_width - 205
    available_minister_display_y = 770
    cycle_input_dict = {
        "coordinates": scaling.scale_coordinates(
            available_minister_display_x - (position_icon_width / 2) - 50,
            available_minister_display_y,
        ),
        "width": scaling.scale_width(50),
        "height": scaling.scale_height(50),
        "keybind_id": pygame.K_w,
        "modes": ["ministers"],
        "image_id": "buttons/cycle_ministers_up_button.png",
        "init_type": "cycle available ministers button",
        "direction": "left",
    }
    cycle_left_button = constants.actor_creation_manager.create_interface_element(
        cycle_input_dict
    )

    for i in range(0, 5):
        available_minister_display_y -= portrait_icon_width + 10
        current_portrait = constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    available_minister_display_x - portrait_icon_width,
                    available_minister_display_y,
                ),
                "width": scaling.scale_width(portrait_icon_width),
                "height": scaling.scale_height(portrait_icon_width),
                "modes": ["ministers"],
                "init_type": "minister portrait image",
                "color": "gray",
                "minister_type": "none",
            }
        )

    available_minister_display_y -= 60
    cycle_input_dict["coordinates"] = (
        cycle_input_dict["coordinates"][0],
        scaling.scale_height(available_minister_display_y),
    )
    cycle_input_dict["keybind_id"] = pygame.K_s
    cycle_input_dict["image_id"] = "buttons/cycle_ministers_down_button.png"
    cycle_input_dict["direction"] = "right"
    cycle_right_button = constants.actor_creation_manager.create_interface_element(
        cycle_input_dict
    )


def trial_screen():
    """
    Description:
        Initializes static interface of trial screen
    Input:
        None
    Output:
        None
    """
    trial_display_default_y = 700
    button_separation = 100
    distance_to_center = 300
    distance_to_notification = 100

    defense_y = trial_display_default_y
    defense_x = (
        (constants.default_display_width / 2)
        + (distance_to_center - button_separation)
        + distance_to_notification
    )
    defense_current_y = 0
    status.defense_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (defense_x, defense_y),
                "width": 10,
                "height": 10,
                "modes": ["trial"],
                "init_type": "ordered collection",
                "is_info_display": True,
                "actor_type": "defense",
                "allow_minimize": False,
                "allow_move": False,
                "description": "defense information panel",
            }
        )
    )

    defense_type_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, defense_current_y),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "modes": ["trial"],
            "minister_type": "none",
            "attached_label": "none",
            "init_type": "minister type image",
            "parent_collection": status.defense_info_display,
        }
    )

    defense_current_y -= button_separation * 2
    defense_portrait_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, defense_current_y),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "init_type": "minister portrait image",
            "minister_type": "none",
            "color": "gray",
            "parent_collection": status.defense_info_display,
        }
    )

    defense_current_y -= 35
    input_dict = {
        "coordinates": scaling.scale_coordinates(0, defense_current_y),
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "message": "Defense",
        "init_type": "label",
        "parent_collection": status.defense_info_display,
    }
    defense_label = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["actor_type"] = "minister"
    del input_dict["message"]
    input_dict["init_type"] = "actor display label"
    defense_info_display_labels = ["minister_name", "minister_office", "evidence"]
    for current_actor_label_type in defense_info_display_labels:
        defense_current_y -= 35
        input_dict["coordinates"] = scaling.scale_coordinates(0, defense_current_y)
        input_dict["actor_label_type"] = current_actor_label_type
        constants.actor_creation_manager.create_interface_element(input_dict)

    prosecution_y = trial_display_default_y
    prosecution_x = (
        (constants.default_display_width / 2)
        - (distance_to_center + button_separation)
        - distance_to_notification
    )
    prosecution_current_y = 0

    status.prosecution_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (prosecution_x, prosecution_y),
                "width": 10,
                "height": 10,
                "modes": ["trial"],
                "init_type": "ordered collection",
                "is_info_display": True,
                "actor_type": "prosecution",
                "allow_minimize": False,
                "allow_move": False,
                "description": "prosecution information panel",
            }
        )
    )

    prosecution_type_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, prosecution_current_y),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "modes": ["trial"],
            "minister_type": "none",
            "attached_label": "none",
            "init_type": "minister type image",
            "parent_collection": status.prosecution_info_display,
        }
    )

    prosecution_current_y -= button_separation * 2
    prosecution_portrait_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(button_separation * 2 - 5),
                "height": scaling.scale_height(button_separation * 2 - 5),
                "init_type": "minister portrait image",
                "minister_type": "none",
                "color": "gray",
                "parent_collection": status.prosecution_info_display,
            }
        )
    )

    prosecution_current_y -= 35
    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "message": "Prosecution",
        "init_type": "label",
        "parent_collection": status.prosecution_info_display,
    }
    prosecution_label = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["actor_type"] = "minister"
    del input_dict["message"]
    input_dict["init_type"] = "actor display label"
    input_dict["parent_collection"] = status.prosecution_info_display
    prosecution_info_display_labels = ["minister_name", "minister_office"]
    for current_actor_label_type in prosecution_info_display_labels:
        prosecution_current_y -= 35
        input_dict["coordinates"] = scaling.scale_coordinates(0, prosecution_current_y)
        input_dict["actor_label_type"] = current_actor_label_type
        constants.actor_creation_manager.create_interface_element(input_dict)

    bribed_judge_indicator = constants.actor_creation_manager.create_interface_element(
        {
            "image_id": "misc/bribed_judge.png",
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2)
                - ((button_separation * 2 - 5) / 2),
                trial_display_default_y,
            ),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "modes": ["trial"],
            "indicator_type": "prosecution_bribed_judge",
            "init_type": "indicator image",
        }
    )

    non_bribed_judge_indicator = (
        constants.actor_creation_manager.create_interface_element(
            {
                "image_id": "misc/non_bribed_judge.png",
                "coordinates": scaling.scale_coordinates(
                    (constants.default_display_width / 2)
                    - ((button_separation * 2 - 5) / 2),
                    trial_display_default_y,
                ),
                "width": scaling.scale_width(button_separation * 2 - 5),
                "height": scaling.scale_height(button_separation * 2 - 5),
                "modes": ["trial"],
                "indicator_type": "not prosecution_bribed_judge",
                "init_type": "indicator image",
            }
        )
    )


def new_game_setup_screen():
    """
    Description:
        Initializes new game setup screen interface
    Input:
        None
    Output:
        None
    """
    current_country_index = 0
    country_image_width = 300
    country_image_height = 200
    country_separation = 50
    countries_per_row = 3
    input_dict = {
        "width": scaling.scale_width(country_image_width),
        "height": scaling.scale_height(country_image_height),
        "modes": ["new_game_setup"],
        "init_type": "country selection image",
    }
    for current_country in status.country_list:
        input_dict["coordinates"] = scaling.scale_coordinates(
            (constants.default_display_width / 2)
            - (countries_per_row * (country_image_width + country_separation) / 2)
            + (country_image_width + country_separation)
            * (current_country_index % countries_per_row)
            + country_separation / 2,
            constants.default_display_height / 2
            + 50
            - (
                (country_image_height + country_separation)
                * (current_country_index // countries_per_row)
            ),
        )
        input_dict["country"] = current_country
        constants.actor_creation_manager.create_interface_element(input_dict)
        current_country_index += 1


def mob_interface():
    """
    Description:
        Initializes mob selection interface
    Input:
        None
    Output:
        None
    """
    actor_display_top_y = constants.default_display_height - 205 + 125 + 10
    actor_display_current_y = actor_display_top_y
    constants.mob_ordered_list_start_y = actor_display_current_y

    status.mob_info_display = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(400),
            "height": scaling.scale_height(430),
            "modes": ["strategic", "europe"],
            "init_type": "ordered collection",
            "is_info_display": True,
            "actor_type": "mob",
            "description": "unit information panel",
            "parent_collection": status.info_displays_collection,
            #'resize_with_contents': True, #need to get resize to work with info displays - would prevent invisible things from taking space
            # - collection with 5 width/height should still take space because of its member rects - the fact that this is not happening means something about resizing is not working
        }
    )

    # mob background image's tooltip
    mob_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "minimum_width": scaling.scale_width(115),
                "height": scaling.scale_height(115),
                "image_id": "misc/empty.png",
                "actor_label_type": "tooltip",
                "actor_type": "mob",
                "init_type": "actor display label",
                "parent_collection": status.mob_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    # mob image
    mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": ["strategic", "europe"],
            "actor_image_type": "default",
            "init_type": "actor display free image",
            "parent_collection": status.mob_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(125, -115),
        "width": scaling.scale_width(35),
        "height": scaling.scale_height(35),
        "modes": ["strategic", "europe"],
        "image_id": "buttons/remove_minister_button.png",
        "init_type": "fire unit button",
        "parent_collection": status.mob_info_display,
        "member_config": {"order_exempt": True},
    }
    fire_unit_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["image_id"] = "buttons/free_slaves_button.png"
    input_dict["init_type"] = "free unit slaves button"
    status.free_unit_slaves_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    left_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(200, -105),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "europe"],
            "keybind_id": pygame.K_a,
            "image_id": "buttons/left_button.png",
            "init_type": "move left button",
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )
    down_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(245, -105),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "europe"],
            "keybind_id": pygame.K_s,
            "image_id": "buttons/down_button.png",
            "init_type": "move down button",
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )

    up_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(245, -60),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "europe"],
            "keybind_id": pygame.K_w,
            "image_id": "buttons/up_button.png",
            "init_type": "move up button",
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )

    right_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(290, -105),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "europe"],
            "keybind_id": pygame.K_d,
            "image_id": "buttons/right_button.png",
            "init_type": "move right button",
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )

    # mob info labels setup
    mob_info_display_labels = [
        "name",
        "minister",
        "officer",
        "workers",
        "movement",
        "canoes",
        "combat_strength",
        "preferred_terrains",
        "attitude",
        "controllable",
        "crew",
        "passengers",
        "current passenger",
    ]  # order of mob info display labels
    for current_actor_label_type in mob_info_display_labels:
        if current_actor_label_type == "minister":  # how far from edge of screen
            x_displacement = 40
        elif current_actor_label_type == "current passenger":
            x_displacement = 30
        else:
            x_displacement = 0
        input_dict = {  # should declare here to reinitialize dict and prevent extra parameters from being incorrectly retained between iterations
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "actor_label_type": current_actor_label_type,
            "actor_type": "mob",
            "parent_collection": status.mob_info_display,
            "member_config": {"order_x_offset": x_displacement},
        }
        if current_actor_label_type != "current passenger":
            input_dict["init_type"] = "actor display label"
            constants.actor_creation_manager.create_interface_element(input_dict)
        else:
            input_dict["init_type"] = "list item label"
            input_dict["list_type"] = "ship"
            for i in range(0, 3):  # 0, 1, 2
                # label for each passenger
                input_dict["list_index"] = i
                constants.actor_creation_manager.create_interface_element(input_dict)

    tab_collection_relative_coordinates = (450, -30)
    status.mob_tabbed_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    tab_collection_relative_coordinates[0],
                    tab_collection_relative_coordinates[1],
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "tabbed collection",
                "parent_collection": status.mob_info_display,
                "member_config": {"order_exempt": True},
                "description": "unit information tabs",
            }
        )
    )


def tile_interface():
    """
    Description:
        Initializes tile selection interface
    Input:
        None
    Output:
        None
    """
    status.tile_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(775),
                "height": scaling.scale_height(10),
                "modes": ["strategic", "europe"],
                "init_type": "ordered collection",
                "is_info_display": True,
                "actor_type": "tile",
                "description": "tile information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    separation = scaling.scale_height(3)
    same_tile_ordered_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(120, 0),
                "width": 10,
                "height": 10,
                "init_type": "ordered collection",
                "parent_collection": status.tile_info_display,
                "member_config": {"order_exempt": True},
                "separation": separation,
            }
        )
    )

    input_dict = {
        "coordinates": (0, 0),
        "width": scaling.scale_width(25),
        "height": scaling.scale_height(25),
        "modes": ["strategic", "europe"],
        "init_type": "same tile icon",
        "image_id": "buttons/default_button.png",
        "is_last": False,
        "color": "gray",
        "parent_collection": same_tile_ordered_collection,
    }

    for i in range(0, 3):  # add button to cycle through
        input_dict["index"] = i
        same_tile_icon = constants.actor_creation_manager.create_interface_element(
            input_dict
        )

    same_tile_icon = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": (0, 0),
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(15),
            "modes": ["strategic", "europe"],
            "init_type": "same tile icon",
            "image_id": "buttons/default_button.png",
            "index": 3,
            "is_last": True,
            "color": "gray",
            "parent_collection": same_tile_ordered_collection,
        }
    )

    cycle_same_tile_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, separation),
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(15),
            "modes": ["strategic", "europe"],
            "image_id": "buttons/cycle_passengers_down_button.png",
            "init_type": "cycle same tile button",
            "parent_collection": same_tile_ordered_collection,
        }
    )

    # tile background image's tooltip
    tile_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "minimum_width": scaling.scale_width(115),
                "height": scaling.scale_height(115),
                "image_id": "misc/empty.png",
                "actor_label_type": "tooltip",
                "actor_type": "tile",
                "init_type": "actor display label",
                "parent_collection": status.tile_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    tile_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(5, 5),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": ["strategic", "europe"],
            "actor_image_type": "default",
            "init_type": "actor display free image",
            "parent_collection": status.tile_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    # tile info labels setup
    tile_info_display_labels = [
        "coordinates",
        "terrain",
        "resource",
        "village",
        "native population",
        "native available workers",
        "native aggressiveness",
        "slave_traders_strength",
        "terrain features",
    ]
    for current_actor_label_type in tile_info_display_labels:
        if current_actor_label_type in [
            "native population",
            "native available workers",
            "native aggressiveness",
            "terrain features",
        ]:
            x_displacement = 25
        else:
            x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "actor_label_type": current_actor_label_type,
            "actor_type": "tile",
            "parent_collection": status.tile_info_display,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }

        if current_actor_label_type in [
            "native population",
            "native available workers",
            "native aggressiveness",
        ]:
            input_dict["init_type"] = current_actor_label_type + " label"
            constants.actor_creation_manager.create_interface_element(input_dict)
        elif current_actor_label_type == "terrain features":
            input_dict["init_type"] = "terrain feature label"
            for terrain_feature_type in status.terrain_feature_types:
                input_dict["terrain_feature_type"] = terrain_feature_type
                constants.actor_creation_manager.create_interface_element(input_dict)
        else:
            input_dict["init_type"] = "actor display label"
            constants.actor_creation_manager.create_interface_element(input_dict)

    tab_collection_relative_coordinates = (450, -30)

    status.tile_tabbed_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    tab_collection_relative_coordinates[0],
                    tab_collection_relative_coordinates[1],
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "tabbed collection",
                "parent_collection": status.tile_info_display,
                "member_config": {"order_exempt": True},
                "description": "tile information tabs",
            }
        )
    )


def inventory_interface():
    """
    Description:
        Initializes the commodity prices display and both mob/tile tabbed collections and inventory interfaces
    Input:
        None
    Output:
        None
    """
    commodity_prices_x, commodity_prices_y = (900, 100)
    commodity_prices_height = 35 + (30 * len(constants.commodity_types))
    commodity_prices_width = 200

    status.commodity_prices_label = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    commodity_prices_x, commodity_prices_y
                ),
                "minimum_width": scaling.scale_width(commodity_prices_width),
                "height": scaling.scale_height(commodity_prices_height),
                "modes": ["europe"],
                "image_id": "misc/commodity_prices_label.png",
                "init_type": "commodity prices label",
            }
        )
    )

    input_dict = {
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "modes": ["europe"],
        "init_type": "commodity button",
    }
    for current_index in range(
        len(constants.commodity_types)
    ):  # commodity prices in Europe
        input_dict["coordinates"] = scaling.scale_coordinates(
            commodity_prices_x - 35,
            commodity_prices_y + commodity_prices_height - 65 - (30 * current_index),
        )
        input_dict["image_id"] = [
            "misc/green_circle.png",
            "items/" + constants.commodity_types[current_index] + ".png",
        ]
        input_dict["commodity"] = constants.commodity_types[current_index]
        new_commodity_button = (
            constants.actor_creation_manager.create_interface_element(input_dict)
        )

    status.mob_inventory_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "ordered collection",
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/consumer goods.png", "size": 0.75},
                    ],
                    "identifier": "inventory",
                },
                "description": "unit inventory panel",
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "actor_label_type": "mob inventory capacity",
        "actor_type": "mob",
        "init_type": "actor display label",
        "parent_collection": status.mob_inventory_collection,
    }
    mob_inventory_capacity_label = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    inventory_cell_height = scaling.scale_height(34)
    inventory_cell_width = scaling.scale_width(34)

    status.mob_inventory_grid = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": (inventory_cell_height + scaling.scale_height(5)) * 3,
                "init_type": "inventory grid",
                "parent_collection": status.mob_inventory_collection,
                "second_dimension_increment": inventory_cell_width
                + scaling.scale_height(5),
            }
        )
    )
    for current_index in range(27):
        constants.actor_creation_manager.create_interface_element(
            {
                "width": inventory_cell_width,
                "height": inventory_cell_height,
                "image_id": "buttons/default_button.png",
                "init_type": "item icon",
                "parent_collection": status.mob_inventory_grid,
                "icon_index": current_index,
                "actor_type": "mob_inventory",
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.mob_inventory_grid.height,
                },
            }
        )

    status.mob_inventory_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "ordered collection",
                "is_info_display": True,
                "actor_type": "mob_inventory",
                "description": "mob inventory panel",
                "parent_collection": status.mob_inventory_collection,
                "member_config": {"calibrate_exempt": True},
            }
        )
    )

    # mob inventory background image's tooltip
    mob_inventory_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(90),
                "height": scaling.scale_height(90),
                "image_id": "misc/empty.png",
                "actor_label_type": "tooltip",
                "actor_type": "tile",
                "init_type": "actor display label",
                "parent_collection": status.mob_inventory_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    mob_inventory_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(5, 5),
            "width": scaling.scale_width(90),
            "height": scaling.scale_height(90),
            "modes": ["strategic", "europe"],
            "actor_image_type": "inventory_default",
            "init_type": "actor display free image",
            "parent_collection": status.mob_inventory_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    mob_info_display_labels = ["inventory_name", "inventory_quantity"]
    for current_actor_label_type in mob_info_display_labels:
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "actor_label_type": current_actor_label_type,
            "actor_type": "mob",
            "parent_collection": status.mob_inventory_info_display,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        input_dict["init_type"] = "actor display label"
        constants.actor_creation_manager.create_interface_element(input_dict)

    status.tile_inventory_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "ordered collection",
                "parent_collection": status.tile_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/consumer goods.png", "size": 0.75},
                    ],
                    "identifier": "inventory",
                },
                "description": "tile inventory panel",
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",  #'misc/underline.png',
        "actor_label_type": "tile inventory capacity",
        "actor_type": "tile",
        "init_type": "actor display label",
        "parent_collection": status.tile_inventory_collection,
    }
    tile_inventory_capacity_label = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    status.tile_inventory_grid = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": (inventory_cell_height + scaling.scale_height(5)) * 3,
                "init_type": "inventory grid",
                "parent_collection": status.tile_inventory_collection,
                "second_dimension_increment": inventory_cell_width
                + scaling.scale_height(5),
            }
        )
    )

    tile_scroll_up_button = constants.actor_creation_manager.create_interface_element(
        {
            "width": inventory_cell_width,
            "height": inventory_cell_height,
            "parent_collection": status.tile_inventory_grid,
            "image_id": "buttons/cycle_ministers_up_button.png",
            "value_name": "inventory_page",
            "increment": -1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-1.3 * inventory_cell_width),
                "y_offset": status.tile_inventory_grid.height
                - ((inventory_cell_height + scaling.scale_height(5)) * 3)
                + scaling.scale_height(5),
            },
            "init_type": "scroll button",
        }
    )

    tile_scroll_down_button = constants.actor_creation_manager.create_interface_element(
        {
            "width": inventory_cell_width,
            "height": inventory_cell_height,
            "parent_collection": status.tile_inventory_grid,
            "image_id": "buttons/cycle_ministers_down_button.png",
            "value_name": "inventory_page",
            "increment": 1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-1.3 * inventory_cell_width),
                "y_offset": status.tile_inventory_grid.height - (inventory_cell_height),
            },
            "init_type": "scroll button",
        }
    )

    for current_index in range(27):
        constants.actor_creation_manager.create_interface_element(
            {
                "width": inventory_cell_width,
                "height": inventory_cell_height,
                "image_id": "buttons/default_button.png",
                "init_type": "item icon",
                "parent_collection": status.tile_inventory_grid,
                "icon_index": current_index,
                "actor_type": "tile_inventory",
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.tile_inventory_grid.height,
                },
            }
        )

    status.tile_inventory_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "ordered collection",
                "is_info_display": True,
                "actor_type": "tile_inventory",
                "description": "tile inventory panel",
                "parent_collection": status.tile_inventory_collection,
                "member_config": {"calibrate_exempt": True},
            }
        )
    )

    # tile inventory background image's tooltip
    tile_inventory_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(90),
                "height": scaling.scale_height(90),
                "image_id": "misc/empty.png",
                "actor_label_type": "tooltip",
                "actor_type": "tile",
                "init_type": "actor display label",
                "parent_collection": status.tile_inventory_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    tile_inventory_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(5, 5),
            "width": scaling.scale_width(90),
            "height": scaling.scale_height(90),
            "modes": ["strategic", "europe"],
            "actor_image_type": "inventory_default",
            "init_type": "actor display free image",
            "parent_collection": status.tile_inventory_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    tile_info_display_labels = ["inventory_name", "inventory_quantity"]
    for current_actor_label_type in tile_info_display_labels:
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "actor_label_type": current_actor_label_type,
            "actor_type": "tile",
            "parent_collection": status.tile_inventory_info_display,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        input_dict["init_type"] = "actor display label"
        constants.actor_creation_manager.create_interface_element(input_dict)


def settlement_interface():
    """
    Description:
        Initializes the settlement interface as part of the tile tabbed collection
    Input:
        None
    Output:
        None
    """
    status.settlement_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "ordered collection",
                "parent_collection": status.tile_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "buttons/crew_train_button.png",
                    "identifier": "settlement",
                },
                "description": "settlement panel",
            }
        )
    )
    settlement_info_display_labels = [
        "settlement",
        "port",
        "train_station",
        "resource building",
        "building efficiency",
        "building work crews",
        "current building work crew",
        "fort",
        "slums",
        "trading_post",
        "mission",
        "infrastructure",
    ]
    for current_actor_label_type in settlement_info_display_labels:
        if current_actor_label_type in [
            "settlement",
            "trading_post",
            "mission",
            "infrastructure",
        ]:  # Left align any top-level buildings
            x_displacement = 0
        elif current_actor_label_type == "current building work crew":
            x_displacement = 75
        elif current_actor_label_type in ["building efficiency", "building work crews"]:
            x_displacement = 50
        else:
            x_displacement = 25
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "actor_label_type": current_actor_label_type,
            "actor_type": "tile",
            "parent_collection": status.settlement_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }

        if current_actor_label_type == "building efficiency":
            input_dict["init_type"] = "building efficiency label"
            input_dict["building_type"] = "resource"
            constants.actor_creation_manager.create_interface_element(input_dict)
        elif current_actor_label_type == "building work crews":
            input_dict["init_type"] = "building work crews label"
            input_dict["building_type"] = "resource"
            constants.actor_creation_manager.create_interface_element(input_dict)
        elif current_actor_label_type == "current building work crew":
            input_dict["init_type"] = "list item label"
            input_dict["list_type"] = "resource building"
            for i in range(0, 3):
                input_dict["list_index"] = i
                constants.actor_creation_manager.create_interface_element(input_dict)
        else:
            input_dict["init_type"] = "actor display label"
            constants.actor_creation_manager.create_interface_element(input_dict)


def unit_organization_interface():
    """
    Description:
        Initializes the unit organization interface as part of the mob tabbed collection
    Input:
        None
    Output:
        None
    """
    image_height = 75
    lhs_x_offset = 35
    rhs_x_offset = image_height + 80

    status.mob_reorganization_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(-30, -1 * image_height - 115),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": "autofill collection",
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "buttons/merge_button.png",
                    "identifier": "reorganization",
                },
                "description": "unit organization panel",
                "direction": "horizontal",
                "autofill_targets": {"officer": [], "worker": [], "group": []},
            }
        )
    )

    # mob background image's tooltip
    lhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(lhs_x_offset, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": "mob",
            "init_type": "actor tooltip label",
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
        }
    )
    status.mob_reorganization_collection.autofill_targets["officer"].append(
        lhs_top_tooltip
    )

    # mob image
    lhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": ["strategic", "europe"],
            "actor_image_type": "default",
            "default_image_id": "mobs/default/mock_officer.png",
            "init_type": "actor display free image",
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(lhs_x_offset),
            },
        }
    )
    status.mob_reorganization_collection.autofill_targets["officer"].append(
        lhs_top_mob_free_image
    )

    # mob background image's tooltip
    lhs_bottom_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                lhs_x_offset, -1 * (image_height - 5)
            ),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": "mob",
            "init_type": "actor tooltip label",
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
        }
    )
    status.mob_reorganization_collection.autofill_targets["worker"].append(
        lhs_bottom_tooltip
    )

    # mob image
    default_image_id = [
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "left", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "right", to_front=True
        ),
    ]
    lhs_bottom_mob_free_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(image_height - 10),
                "height": scaling.scale_height(image_height - 10),
                "modes": ["strategic", "europe"],
                "actor_image_type": "default",
                "default_image_id": default_image_id,
                "init_type": "actor display free image",
                "parent_collection": status.mob_reorganization_collection,
                "member_config": {
                    "calibrate_exempt": True,
                    "x_offset": scaling.scale_width(lhs_x_offset),
                    "y_offset": scaling.scale_height(-1 * (image_height - 5)),
                },
            }
        )
    )
    status.mob_reorganization_collection.autofill_targets["worker"].append(
        lhs_bottom_mob_free_image
    )

    # right side
    # mob background image's tooltip
    rhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": "mob",
            "init_type": "actor tooltip label",
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(lhs_x_offset + rhs_x_offset),
                "y_offset": -0.5 * (image_height - 5),
            },
        }
    )
    status.mob_reorganization_collection.autofill_targets["group"].append(
        rhs_top_tooltip
    )

    # mob image
    default_image_id = [
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group left", to_front=True
        )
    ]
    default_image_id.append(
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group right", to_front=True
        )
    )
    default_image_id.append(
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_officer.png", "center", to_front=True
        )
    )
    rhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": ["strategic", "europe"],
            "actor_image_type": "default",
            "default_image_id": default_image_id,
            "init_type": "actor display free image",
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(lhs_x_offset + rhs_x_offset),
                "y_offset": -0.5 * (image_height - 5),
            },
        }
    )
    status.mob_reorganization_collection.autofill_targets["group"].append(
        rhs_top_mob_free_image
    )

    # reorganize unit to right button
    status.reorganize_unit_right_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    lhs_x_offset + rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 30,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": "reorganize unit button",
                "parent_collection": status.mob_reorganization_collection,
                "image_id": "buttons/cycle_units_button.png",
                "allowed_procedures": ["merge", "crew"],
                "keybind_id": pygame.K_m,
                "enable_shader": True,
            }
        )
    )

    # reorganize unit to left button
    status.reorganize_unit_left_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    lhs_x_offset + rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": "reorganize unit button",
                "parent_collection": status.mob_reorganization_collection,
                "image_id": "buttons/cycle_units_reverse_button.png",
                "allowed_procedures": ["split", "uncrew"],
                "keybind_id": pygame.K_n,
                "enable_shader": True,
            }
        )
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            lhs_x_offset - 35, -1 * (image_height - 15) + 95 - 35 / 2
        ),
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "init_type": "cycle autofill button",
        "parent_collection": status.mob_reorganization_collection,
        "image_id": "buttons/reset_button.png",
        "autofill_target_type": "officer",
    }
    cycle_autofill_officer_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            lhs_x_offset - 35, -1 * (image_height - 15) + 25 - 35 / 2
        ),
        "width": input_dict["width"],  # copies most attributes from previous button
        "height": input_dict["height"],
        "init_type": input_dict["init_type"],
        "parent_collection": input_dict["parent_collection"],
        "image_id": input_dict["image_id"],
        "autofill_target_type": "worker",
    }
    cycle_autofill_worker_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )


def minister_interface():
    """
    Description:
        Initializes minister selection interface
    Input:
        None
    Output:
        int actor_display_current_y: Value that tracks the location of interface as it is created, used by other setup functions
    """
    # minister info images setup
    minister_display_top_y = constants.mob_ordered_list_start_y
    minister_display_current_y = 0

    status.minister_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (5, -5),
                "width": 10,
                "height": 10,
                "modes": ["ministers"],
                "init_type": "ordered collection",
                "is_info_display": True,
                "actor_type": "minister",
                "allow_minimize": False,
                "allow_move": False,
                "description": "minister information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    # minister background image
    minister_free_image_background = (
        constants.actor_creation_manager.create_interface_element(
            {
                "image_id": "misc/mob_background.png",
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(125),
                "height": scaling.scale_height(125),
                "modes": ["ministers"],
                "init_type": "minister background image",
                "parent_collection": status.minister_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    # minister image
    minister_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": ["ministers"],
            "actor_image_type": "minister_default",
            "init_type": "actor display free image",
            "parent_collection": status.minister_info_display,
            "member_config": {
                "order_overlap": True,
                "order_x_offset": 5,
                "order_y_offset": -5,
            },
        }
    )

    # minister background image's tooltip
    minister_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, minister_display_current_y),
                "minimum_width": scaling.scale_width(125),
                "height": scaling.scale_height(125),
                "image_id": "misc/empty.png",
                "actor_label_type": "tooltip",
                "actor_type": "minister",
                "init_type": "actor display label",
                "parent_collection": status.minister_info_display,
                "member_config": {"order_overlap": False},
            }
        )
    )

    minister_display_current_y -= 35
    # minister info images setup

    input_dict = {
        "coordinates": scaling.scale_coordinates(0, 0),
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "actor_type": "minister",
        "init_type": "actor display label",
        "parent_collection": status.minister_info_display,
    }

    # minister info labels setup
    minister_info_display_labels = (
        [
            "minister_name",
            "minister_office",
            "background",
            "social status",
            "interests",
            "loyalty",
            "ability",
        ]
        + constants.skill_types
        + ["evidence"]
    )
    for current_actor_label_type in minister_info_display_labels:
        if current_actor_label_type in constants.skill_types:
            x_displacement = 25
        else:
            x_displacement = 0
        input_dict["member_config"] = {"order_x_offset": x_displacement}
        input_dict["actor_label_type"] = current_actor_label_type
        constants.actor_creation_manager.create_interface_element(input_dict)
    # minister info labels setup


def country_interface():
    """
    Description:
        Initializes country selection interface
    Input:
        None
    Output:
        int actor_display_current_y: Value that tracks the location of interface as it is created, used by other setup functions
    """

    status.country_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (5, -5),
                "width": 10,
                "height": 10,
                "modes": ["new_game_setup"],
                "init_type": "ordered collection",
                "is_info_display": True,
                "actor_type": "country",
                "allow_minimize": False,
                "allow_move": False,
                "description": "country information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    # country background image
    country_free_image_background = (
        constants.actor_creation_manager.create_interface_element(
            {
                "image_id": "misc/mob_background.png",
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(125),
                "height": scaling.scale_height(125),
                "modes": ["new_game_setup"],
                "init_type": "mob background image",
                "parent_collection": status.country_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    # country image
    country_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": ["new_game_setup"],
            "actor_image_type": "country_default",
            "init_type": "actor display free image",
            "parent_collection": status.country_info_display,
            "member_config": {
                "order_overlap": True,
                "order_x_offset": 5,
                "order_y_offset": -5,
            },
        }
    )

    # country background image's tooltip
    country_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(125),
                "height": scaling.scale_height(125),
                "image_id": "misc/empty.png",
                "actor_label_type": "tooltip",
                "actor_type": "country",
                "init_type": "actor display label",
                "parent_collection": status.country_info_display,
                "member_config": {"order_overlap": False},
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "actor_type": "country",
        "init_type": "actor display label",
        "parent_collection": status.country_info_display,
    }
    # country info labels setup
    country_info_display_labels = ["country_name", "country_effect"]
    for current_actor_label_type in country_info_display_labels:
        x_displacement = 0
        input_dict["coordinates"] = scaling.scale_coordinates(x_displacement, 0)
        input_dict["actor_label_type"] = current_actor_label_type
        constants.actor_creation_manager.create_interface_element(input_dict)


def manage_crash(exception):
    """
    Description:
        Uses an exception to write a crash log and exit the game
    Input:
        Exception exception: Exception that caused the crash
    Output:
        None
    """
    crash_log_file = open("notes/Crash Log.txt", "w")
    crash_log_file.write("")  # clears crash report file
    console = (
        logging.StreamHandler()
    )  # sets logger to go to both console and crash log file
    logging.basicConfig(filename="notes/Crash Log.txt")
    logging.getLogger("").addHandler(console)

    logging.error(
        exception, exc_info=True
    )  # sends error message to console and crash log file

    crash_log_file.close()
    pygame.quit()
