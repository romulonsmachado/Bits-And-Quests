import thumby


SAVE_VERSION = 8
SAVE_NAME = "Bits & Quests"
SLOT_COUNT = 3
DUNGEON_OLD_COLS = 8
DUNGEON_V7_COLS = 12
DUNGEON_COLS = 9


def init():
    thumby.saveData.setName(SAVE_NAME)


def _slot_key(slot):
    if slot < 1 or slot > SLOT_COUNT:
        raise ValueError("save slot")
    return "slot" + str(slot)


def _coords_bits(coords, stride=DUNGEON_COLS):
    if isinstance(coords, int):
        return coords
    bits = 0
    for pos in coords:
        bits |= 1 << (int(pos[0]) + int(pos[1]) * stride)
    return bits

def _is_coord(value):
    try:
        return len(value) >= 2 and isinstance(value[0], int) and isinstance(value[1], int)
    except Exception:
        return False

def _bits_value(value, stride=DUNGEON_COLS):
    if isinstance(value, int):
        return value
    return _coords_bits(value, stride)

def _dungeon_bits(values, stride=DUNGEON_COLS):
    if isinstance(values, int):
        return (values,)
    if values is None:
        return ()
    try:
        if not values:
            return ()
        if _is_coord(values[0]):
            return (_coords_bits(values, stride),)
        return tuple(_bits_value(v, stride) for v in values)
    except Exception:
        return (0,)

def _convert_stride(bits, old_stride=DUNGEON_OLD_COLS, new_stride=DUNGEON_COLS):
    out = 0
    idx = 0
    bits = int(bits)
    while bits:
        if bits & 1:
            x = idx % old_stride
            y = idx // old_stride
            out |= 1 << (x + y * new_stride)
        bits >>= 1
        idx += 1
    return out

def _convert_dungeon_tuple(values):
    return tuple(_convert_stride(v) for v in values)


def _event_bits(events):
    if isinstance(events, int):
        return events
    bits = 0
    for ev in events:
        if ev == "landslip_open":
            bits |= 1
    return bits

def _dungeon_events(events):
    if isinstance(events, int):
        return (events,)
    if events is None:
        return ()
    try:
        if not events:
            return ()
        if isinstance(events[0], str):
            return (_event_bits(events),)
        return tuple(_event_bits(ev) for ev in events)
    except Exception:
        return (0,)


def _pack(px, py, heroi, dungeon_items, dungeon_visitado, dungeon_events=(), region_id=0, world_flags=0):
    return [
        SAVE_VERSION,
        int(px),
        int(py),
        heroi,
        _dungeon_bits(dungeon_items),
        _dungeon_bits(dungeon_visitado),
        _dungeon_events(dungeon_events),
        int(region_id),
        int(world_flags),
    ]


def _unpack(data):
    if data[0] != SAVE_VERSION and data[0] != 7 and data[0] != 6 and data[0] != 5 and data[0] != 4 and data[0] != 3 and data[0] != 2:
        raise ValueError("save version")
    if data[0] == SAVE_VERSION:
        return (
            SAVE_VERSION,
            int(data[1]),
            int(data[2]),
            data[3],
            _dungeon_bits(data[4]),
            _dungeon_bits(data[5]),
            _dungeon_events(data[6]) if len(data) > 6 else (),
            int(data[7]) if len(data) > 7 else 0,
            int(data[8]) if len(data) > 8 else 0,
        )
    if data[0] == 7:
        return (
            SAVE_VERSION,
            int(data[1]),
            int(data[2]),
            data[3],
            tuple(_convert_stride(v, DUNGEON_V7_COLS, DUNGEON_COLS) for v in _dungeon_bits(data[4], DUNGEON_V7_COLS)),
            tuple(_convert_stride(v, DUNGEON_V7_COLS, DUNGEON_COLS) for v in _dungeon_bits(data[5], DUNGEON_V7_COLS)),
            _dungeon_events(data[6]) if len(data) > 6 else (),
            int(data[7]) if len(data) > 7 else 0,
            int(data[8]) if len(data) > 8 else 0,
        )
    if data[0] == 6 or data[0] == 5 or data[0] == 4:
        return (
            SAVE_VERSION,
            int(data[1]),
            int(data[2]),
            data[3],
            _convert_dungeon_tuple(_dungeon_bits(data[4], DUNGEON_OLD_COLS)),
            _convert_dungeon_tuple(_dungeon_bits(data[5], DUNGEON_OLD_COLS)),
            _dungeon_events(data[6]) if len(data) > 6 else (),
            int(data[7]) if len(data) > 7 else 0,
            int(data[8]) if len(data) > 8 else 0,
        )
    return (
        SAVE_VERSION,
        int(data[1]),
        int(data[2]),
        data[3],
        (_convert_stride(_coords_bits(data[4], DUNGEON_OLD_COLS)),),
        (_convert_stride(_coords_bits(data[5], DUNGEON_OLD_COLS)),),
        (_event_bits(data[6]) if len(data) > 6 else 0,),
        0,
        0,
    )


def _read_item(slot):
    init()
    key = _slot_key(slot)
    try:
        if not thumby.saveData.hasItem(key):
            return None
    except AttributeError:
        pass
    try:
        return thumby.saveData.getItem(key)
    except Exception:
        return None


def _write_item(slot, data):
    init()
    thumby.saveData.setItem(_slot_key(slot), data)
    thumby.saveData.save()


def _delete_item(slot):
    init()
    key = _slot_key(slot)
    try:
        if thumby.saveData.hasItem(key):
            thumby.saveData.delItem(key)
            thumby.saveData.save()
            return True
    except AttributeError:
        try:
            thumby.saveData.setItem(key, None)
            thumby.saveData.save()
            return True
        except Exception:
            return False
    except Exception:
        return False
    return False


def exists(game_dir, slot):
    try:
        load(game_dir, slot)
        return True
    except Exception:
        return False


def save(game_dir, slot, px, py, heroi, dungeon_items, dungeon_visitado, dungeon_events=(), region_id=0, world_flags=0):
    _write_item(slot, _pack(px, py, heroi, dungeon_items, dungeon_visitado, dungeon_events, region_id, world_flags))


def load(game_dir, slot):
    data = _read_item(slot)
    if data is None:
        raise OSError("save slot")
    return _unpack(data)


def summary(game_dir, slot):
    data = load(game_dir, slot)
    hero = data[3]
    return (hero.get("LVL", 1), hero.get("HP", 1), hero.get("HP_MAX", 1))


def summary_or_none(game_dir, slot):
    try:
        return summary(game_dir, slot)
    except Exception:
        return None


def summaries(game_dir):
    return (
        summary_or_none(game_dir, 1),
        summary_or_none(game_dir, 2),
        summary_or_none(game_dir, 3),
    )


def delete(game_dir, slot):
    return _delete_item(slot)
