from animations import data_dump, HitBoxProcessed, HurtBoxProcessed, dump_one_character

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


def name_to_internal_id(name_in):
    if name_in not in LEGAL_NAMES:
        raise ValueError(f"Character not recognized. Use one of: {LEGAL_NAMES}")
    try:
        return INTERNAL_NAMES.index(name_in)
    except ValueError:
        return INTERNAL_NAMES.index(ALIAS_MAP[name_in])


_data_cache = {}


def retrieve_move_data(character_id: int, move_id: int) -> tuple[list, list]:
    ...
    _, hurts, hits = retrieve_character_data(character_id)
    return hurts[move_id], hits[move_id]


def retrieve_character_data(character_id) -> tuple[list, list, list]:
    if character_id in _data_cache:
        return _data_cache[character_id]

    _data_cache[character_id] = dump_one_character(
        "/home/heather/Documents/Disk Images/Super Smash Bros. Melee (v1.02).iso",
        character_id
    )
    return retrieve_character_data(character_id)


if __name__ == "__main__":
    # breakpoint()
    (hu, hi) = retrieve_move_data(2, 55)

    breakpoint()
