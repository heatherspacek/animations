from mess.animations._rs import data_dump, HitBoxProcessed, HurtBoxProcessed, dump_one_character

"""
- remove duplicates
- remove non-animated
- transform character names
- transform move names
"""

# fmt: off
INTERNAL_NAMES = [
    'Mario', 'Fox', 'Captain', 'Donkey', 'Kirby', 'Koopa', 'Link',
    'Seak', 'Ness', 'Peach', 'Popo', 'Nana', 'Pikachu', 'Samus',
    'Yoshi', 'Purin', 'Mewtwo', 'Luigi', 'Mars', 'Zelda', 'Clink',
    'Drmario', 'Falco', 'Pichu', 'Gamewatch', 'Ganon', 'Emblem'
]
# fmt: on
ALIAS_MAP = {
    "Captain Falcon": 'Captain',
    "Donkey Kong": 'Donkey',
    "Bowser": 'Koopa',
    "Sheik": 'Seak',
    "Jigglypuff": 'Purin',
    "Marth": 'Mars',
    "Young Link": 'Clink',
    "Dr. Mario": 'Drmario',
    "Mr. Game and Watch": 'Gamewatch',
    "Ganondorf": 'Ganon',
    "Roy": 'Emblem'
}
LEGAL_NAMES = INTERNAL_NAMES + list(ALIAS_MAP.keys())

"""
"prio" moves are ones that should get a convenient name and go to the
top of the list.
anything not in the prio translation keeps its internal name.
"""


MOVE_ALIAS_MAP = {
    'Attack11': "Jab 1",
    'Attack12': "Jab 2",
    'Attack13': "Jab 3",
    'Attack100Loop': "Rapid Jabs",
    'AttackAirB': "☁️⬅️ Back Air",
    'AttackAirF': "☁️➡️ Forward Air",
    'AttackAirHi': "☁️⬆️ Up Air",
    'AttackAirLw': "☁️⬇️ Down Air",
    'AttackAirN': "☁️🅰️ Neutral Air",
    'AttackHi3': "⬆️🅰️ Up Tilt",
    'AttackLw3': "⬇️🅰️ Down Tilt",
    'AttackS3S': "➡️🅰️ Fwd Tilt",
    'AttackDash': "⏭️ Dash Attack",
    'AttackHi4': "⏫ Up Smash",
    'AttackLw4': "⏬ Down Smash",
    'AttackS4': "⏩ Fwd Smash",
    'Catch': "Grab",
    'CatchAttack': "Pummel",
    'CatchDash': "Dash Grab",

    'ThrowB': "Back Throw",
    'ThrowF': "Fwd Throw",
    'ThrowHi': "Up Throw",
    'ThrowLw': "Down Throw",

    'SpecialHi': "⬆️🅱️ Up-Special",
    'SpecialLw': "⬇️🅱️ Dwn-Special",
    'SpecialS': "➡️🅱️ Side-Special",
    'SpecialN': "🅱️ Neutral Special",

    'EscapeAir': "Airdodge",
    'EscapeB': "Roll Backwards",
    'EscapeF': "Roll Forwards",
    'EscapeN': "Spotdodge",

    'Dash': "Dash",
    'Run': "Run",
    'WalkFast': "Walk (fast)",
    'WalkMiddle': "Walk (mid)",
    'WalkSlow': "Walk (slow)",
    'Appeal': "Taunt",

    'CliffAttackQuick': "Ledge Attack",
    'CliffClimbQuick': "Ledge Get-up",
    'CliffEscapeQuick': "Ledge Roll",
    'CliffAttackSlow': "Ledge Attack (Slow)",
    'CliffClimbSlow': "Ledge Get-up (Slow)",
    'CliffEscapeSlow': "Ledge Roll (Slow)",
    'CliffWait': "Ledge-hang",

    'DownAttackD': "Get-up Attack (stomach)",
    'DownAttackU': "Get-up Attack (back)",

    'FuraFura': "Shield broken woozy",
    'OttottoWait': "Teetering",

    'Wait1': "Idle (1)",
    'Wait2': "Idle (2)",

    'AttackS3Hi': "F-Tilt (highest angle)",
    'AttackS3HiS': "F-Tilt (high angle)",
    'AttackS3Lw': "F-Tilt (lowest angle)",
    'AttackS3LwS': "F-Tilt (low angle)",

    'JumpAerialB': "Double-jump (Back)",
    'JumpAerialF': "Double-jump (Fwds)",
    'JumpB': "Jump (Back)",
    'JumpF': "Jump (Fwds)",

    'Passive': "Tech-in-place",
    'PassiveStandB': "Tech-roll back",
    'PassiveStandF': "Tech-roll fwds",
    'PassiveWall': "Wall-tech",
    'PassiveWallJump': "Wall-tech-jump",
    'PassiveCeil': "Ceiling Tech",

    'Pass': "Drop through platform",
    'Rebound': "Clank recoil",

    'Squat': "Crouch begin",
    'SquatRv': "Crouch end",
    'SquatWait': "Crouch loop",
}


def decorate_action_names(names_list, hurts_lists):
    # natural ordering by iterating over desired-order:
    first = [v for k, v in MOVE_ALIAS_MAP.items() if k in names_list]
    second = [
        n
        for n, h in zip(names_list, hurts_lists)
        if n
        and h
        and n not in MOVE_ALIAS_MAP.keys()
    ]
    return first + second


def resolve_original_name(name_in):
    ...


def name_to_internal_id(name_in):
    if name_in not in LEGAL_NAMES:
        raise ValueError(f"Character not recognized. Use one of: {LEGAL_NAMES}")
    try:
        return INTERNAL_NAMES.index(name_in)
    except ValueError:
        return INTERNAL_NAMES.index(ALIAS_MAP[name_in])


_data_cache = {}


def retrieve_move_data(iso_path: str, character_id: int, move_id: int) -> tuple[list, list]:
    ...
    _, hurts, hits = retrieve_character_data(iso_path, character_id)
    return hurts[move_id], hits[move_id]


def retrieve_character_data(iso_path, character_id) -> tuple[list, list, list]:
    if character_id in _data_cache:
        return _data_cache[character_id]

    _data_cache[character_id] = dump_one_character(
        iso_path,
        character_id
    )
    return retrieve_character_data(iso_path, character_id)


if __name__ == "__main__":
    ...
