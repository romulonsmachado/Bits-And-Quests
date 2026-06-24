import gc, sys

DUNGEON_STATE_SLOTS = 8
REGION_FARLILY = 0
REGION_WILDERNESS = 1
REGION_DUNGEON = 2
REGION_STING_FOREST = 3
WORLD_FLAG_WURMS_FOUND = 1

def normalizar_dungeon_states(values):
    out = [0] * DUNGEON_STATE_SLOTS
    try:
        if isinstance(values, int):
            out[0] = values
            return out
        n = len(values)
        if n > DUNGEON_STATE_SLOTS:
            n = DUNGEON_STATE_SLOTS
        for i in range(n):
            out[i] = int(values[i])
    except Exception:
        pass
    return out

def _world_flags(ctx):
    return ctx["world_flags_extra"] | (WORLD_FLAG_WURMS_FOUND if ctx["wilderness_found_cave"] else 0)

def _set_world_flags(ctx, flags):
    flags = int(flags)
    ctx["wilderness_found_cave"] = (flags & WORLD_FLAG_WURMS_FOUND) != 0
    ctx["world_flags_extra"] = flags & ~WORLD_FLAG_WURMS_FOUND

def _sync_region_for_save(ctx):
    st = ctx["estado_jogo"]
    if st in ("MENU", "DUNGEON_MAP_MENU", "DUNGEON_MENU_LOAD", "DUNGEON_MENU_PREP_LOAD"):
        st = ctx["estado_jogo_antes_menu"]
    if st == "SAVE_PROMPT" or st == "SAVE_MSG":
        st = ctx["save_prompt_return"]
    if st == "DUNGEON" or st == "DUNGEON_MENU_PREP":
        ctx["region_id_atual"] = REGION_DUNGEON
    elif st == "STING_FOREST":
        ctx["region_id_atual"] = REGION_STING_FOREST
    elif st == "WILDERNESS" or st == "CAVE_ENTRANCE":
        ctx["region_id_atual"] = REGION_WILDERNESS
    else:
        ctx["region_id_atual"] = REGION_FARLILY

def _unload_saves(saves_mod):
    if "saves" in sys.modules:
        del sys.modules["saves"]
    del saves_mod
    gc.collect()

def save(ctx):
    import saves
    try:
        ctx["guardar_estado_dungeon_atual"]()
        _sync_region_for_save(ctx)
        saves.save(ctx["GAME_DIR"], ctx["slot_atual"], 0, 0, ctx["heroi"],
                   ctx["dungeon_items_todos"], ctx["dungeon_visitados"],
                   ctx["dungeon_events_todos"], ctx["region_id_atual"],
                   _world_flags(ctx))
        ok = True
    except Exception:
        ok = False
    _unload_saves(saves)
    return ok

def load_slot(ctx, slot):
    import saves
    try:
        data = saves.load(ctx["GAME_DIR"], slot)
    except Exception:
        _unload_saves(saves)
        return False
    _unload_saves(saves)

    ctx["heroi"] = data[3]
    ctx["normalizar_status_heroi"]()
    ctx["recalcular_atk_total"]()
    ctx["dungeon_items_todos"] = normalizar_dungeon_states(data[4])
    ctx["dungeon_visitados"] = normalizar_dungeon_states(data[5])
    ctx["dungeon_events_todos"] = (
        normalizar_dungeon_states(data[6]) if len(data) > 6 else [0] * DUNGEON_STATE_SLOTS
    )
    ctx["region_id_atual"] = int(data[7]) if len(data) > 7 else REGION_FARLILY
    _set_world_flags(ctx, data[8] if len(data) > 8 else 0)
    ctx["dungeon_id_atual"] = ctx["DUNGEON_ID_WURMS"]
    did = ctx["dungeon_id_atual"]
    ctx["dungeon_items_coletados"] = ctx["dungeon_items_todos"][did]
    ctx["dungeon_visitado"] = ctx["dungeon_visitados"][did]
    ctx["dungeon_events"] = ctx["dungeon_events_todos"][did]
    if ctx["region_id_atual"] == REGION_DUNGEON:
        ctx["estado_jogo"] = "DUNGEON"
    elif ctx["region_id_atual"] == REGION_STING_FOREST:
        ctx["estado_jogo"] = "STING_FOREST"
    elif ctx["region_id_atual"] == REGION_WILDERNESS:
        ctx["estado_jogo"] = "WILDERNESS"
    else:
        ctx["estado_jogo"] = "VILLAGE"
    return True
