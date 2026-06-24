import gc

DUNGEON_NAMES = ("Wurms' Cave",)
DUNGEON_COUNT = len(DUNGEON_NAMES)
DUNGEON_MAP_COLS = 9

_WURMS_ROOMS = (
    b"\x02\x00\x01\x00\x01\x00\x00\x01\x09\x01\x00\x00"
    b"\x01\x01\x0c\x00\x00\x00\x02\x01\x0e\x01\x00\x00"
    b"\x03\x01\x0c\x00\x00\x00\x04\x01\x0d\x01\x00\x00"
    b"\x05\x01\x05\x00\x00\x00\x00\x02\x03\x01\x00\x00"
    b"\x04\x02\x03\x01\x00\x00\x05\x02\x0a\x00\x00\x00"
    b"\x06\x02\x05\x01\x00\x00\x00\x03\x02\x00\x00\x01"
    b"\x03\x03\x08\x01\x00\x00\x04\x03\x07\x00\x00\x00"
    b"\x06\x03\x0a\x00\x00\x00\x07\x03\x04\x01\x00\x00"
    b"\x02\x04\x09\x00\x00\x00\x03\x04\x0c\x01\x00\x00"
    b"\x04\x04\x0e\x00\x00\x00\x05\x04\x05\x01\x00\x00"
    b"\x02\x05\x02\x01\x01\x00\x02\x06\x02\x00\x00\x00"
    b"\x05\x05\x03\x00\x00\x00\x05\x06\x03\x01\x00\x00"
    b"\x05\x07\x02\x00\x00\x02"
)
_WURMS_ITEMS = (
    ("", "", 0),
    ("shield", "Shield", 1),
    ("stone_tablet", "Stone Tablet", 1),
)
_WIDGET_BG = bytearray(18)
_WIDGET_SCRATCH = bytearray(18)
_SETA_U = bytearray([0,0,8,12,14,12,8,0,0,   0,0,0,0,0,0,0,0,0])
_SETA_D = bytearray([0,0,0,0,0,0,0,0,0,       0,0,8,24,56,24,8,0,0])
_SETA_L = bytearray([0,128,192,224,0,0,0,0,0, 0,0,1,3,0,0,0,0,0])
_SETA_R = bytearray([0,0,0,0,0,224,192,128,0, 0,0,0,0,0,3,1,0,0])
_WURMS_SETAS = (("U", _SETA_U), ("D", _SETA_D), ("L", _SETA_L), ("R", _SETA_R))
_DUNGEON_DATA = (
    (
        _WURMS_ROOMS,
        _WURMS_ITEMS,
        (0, 0, "", 0, 0, "", "", "", 0),
        (2, 0),
        "D",
        _WIDGET_BG,
        _WIDGET_SCRATCH,
        _WURMS_SETAS,
    ),
)

current_id = -1
DUNGEON_ROOMS = b""
DUNGEON_ROOM_ITEMS = (("", "", 0),)
DUNGEON_ROOM_DEFAULT = (0, 0, "", 0, 0, "", "", "", 0)
DUNGEON_ENTRY = (0, 0)
DUNGEON_EXIT_DIR = "D"
dungeon_widget_bg = bytearray(18)
dungeon_widget_scratch = bytearray(18)
DUNGEON_SETAS = ()
_EXITS = ("", "U", "D", "DU", "L", "LU", "DL", "DLU",
          "R", "RU", "DR", "DRU", "LR", "LRU", "DLR", "DLRU")

def module_names():
    return ()

def module(dungeon_id):
    return ""

def load(dungeon_id=0):
    global current_id
    global DUNGEON_ROOMS, DUNGEON_ROOM_ITEMS, DUNGEON_ROOM_DEFAULT, DUNGEON_ENTRY
    global DUNGEON_EXIT_DIR, dungeon_widget_bg, dungeon_widget_scratch, DUNGEON_SETAS
    if current_id == dungeon_id and DUNGEON_ROOMS:
        return
    if dungeon_id < 0 or dungeon_id >= DUNGEON_COUNT:
        dungeon_id = 0
    data = _DUNGEON_DATA[dungeon_id]
    DUNGEON_ROOMS = data[0]
    DUNGEON_ROOM_ITEMS = data[1]
    DUNGEON_ROOM_DEFAULT = data[2]
    DUNGEON_ENTRY = data[3]
    DUNGEON_EXIT_DIR = data[4]
    dungeon_widget_bg = data[5]
    dungeon_widget_scratch = data[6]
    DUNGEON_SETAS = data[7]
    current_id = dungeon_id
    gc.collect()

def unload():
    global current_id, DUNGEON_ROOMS, DUNGEON_ROOM_ITEMS, DUNGEON_SETAS
    global dungeon_widget_bg, dungeon_widget_scratch
    current_id = -1
    DUNGEON_ROOMS = b""
    DUNGEON_ROOM_ITEMS = (("", "", 0),)
    DUNGEON_SETAS = ()
    dungeon_widget_bg = bytearray(18)
    dungeon_widget_scratch = bytearray(18)
    gc.collect()

def name(dungeon_id):
    if dungeon_id < 0 or dungeon_id >= DUNGEON_COUNT:
        return DUNGEON_NAMES[0]
    return DUNGEON_NAMES[dungeon_id]

def entry_bit():
    return 1 << (DUNGEON_ENTRY[0] + DUNGEON_ENTRY[1] * DUNGEON_MAP_COLS)

def bit(pos):
    return 1 << (pos[0] + pos[1] * DUNGEON_MAP_COLS)

def room_at(pos):
    if not DUNGEON_ROOMS:
        load(0)
    x = pos[0]
    y = pos[1]
    rooms = DUNGEON_ROOMS
    for i in range(0, len(rooms), 6):
        if rooms[i] == x and rooms[i + 1] == y:
            item = DUNGEON_ROOM_ITEMS[rooms[i + 5]]
            return (x, y, _EXITS[rooms[i + 2]], rooms[i + 3],
                    rooms[i + 4], "", item[0], item[1], item[2])
    return DUNGEON_ROOM_DEFAULT

def is_exit(pos):
    return pos[0] == DUNGEON_ENTRY[0] and pos[1] == DUNGEON_ENTRY[1]

_DO = (0, 28)
_DL = (28, 41)
_LANDSLIP_BIT = 1

def _dlg(gfx_dir, idx):
    try:
        f = open(gfx_dir + "dialogs.bin", "rb")
    except OSError:
        return ""
    try:
        f.seek(_DO[idx])
        return f.read(_DL[idx]).decode()
    finally:
        f.close()

def update_scene(ctx, agora):
    thumby = ctx["thumby"]
    random = ctx["random"]
    if ctx["DUNGEON_BGS"] is None:
        ctx["carregar_bgs_dungeon"]()
    bgs = ctx["DUNGEON_BGS"]
    pos = ctx["dungeon_pos"]

    if ctx["dungeon_dialog_active"]:
        ctx["fonte_normal"]()
        if ctx["dungeon_dialog_iname"]:
            thumby.display.fill(0)
            ctx["desenhar_dialogo_item_centralizado"](
                ctx["dungeon_dialog_iname"], ctx["dungeon_dialog_icon"])
        else:
            sala_dlg = ctx["sala_dungeon"](pos)
            bg_dlg = sala_dlg[3]
            thumby.display.blit(bgs[bg_dlg] if bg_dlg < len(bgs) else bgs[0],
                                0, 0, 72, 40, -1, 0, 0)
            if ctx["hero_portrait"] is None or ctx["hero_portrait_talk"] is None:
                ctx["carregar_hero_portraits"]()
            ctx["atualizar_scroll_dialogo"](agora)
            if thumby.buttonB.justPressed():
                ctx["dungeon_dialog_scroll"] = 0
                ctx["dungeon_dialog_scroll_timer"] = agora
            ctx["desenhar_dialogo_personagem"](
                ctx["dungeon_dialog_lines"], ctx["dungeon_dialog_scroll"],
                ctx["dungeon_dialog_scroll_max"], ctx["dungeon_dialog_name"],
                ctx["hero_portrait"], ctx["hero_portrait_talk"],
                ctx["dungeon_dialog_show_name"], False)
        if thumby.buttonA.justPressed():
            ctx["dungeon_dialog_active"] = False
            ctx["dungeon_dialog_scroll"] = 0
            ctx["dungeon_dialog_scroll_max"] = 0
            ctx["dungeon_dialog_scroll_timer"] = 0
            ctx["dungeon_dialog_auto_ms"] = ctx["DIALOG_SCROLL_AUTO_MS"]
            ctx["limpar_hero_portraits"]()
            ctx["drenar_botoes"]()
        return

    thumby.display.fill(0)
    sala = ctx["sala_dungeon"](pos)
    saidas = sala[2]
    na_entrada = is_exit(pos)
    bg_idx = sala[3]
    thumby.display.blit(bgs[bg_idx] if bg_idx < len(bgs) else bgs[0],
                        0, 0, 72, 40, -1, 0, 0)

    blink = ctx["dungeon_blink"] + 1
    blink_on = ctx["dungeon_blink_on"]
    if blink >= 6:
        blink = 0
        blink_on = not blink_on
    ctx["dungeon_blink"] = blink
    ctx["dungeon_blink_on"] = blink_on

    w = dungeon_widget_scratch
    for i in range(18):
        w[i] = dungeon_widget_bg[i]
    for d, bm in DUNGEON_SETAS:
        mostrar = (d in saidas) or (na_entrada and d == DUNGEON_EXIT_DIR)
        if mostrar and blink_on:
            for i in range(18):
                w[i] |= bm[i]
    thumby.display.blit(w, 0, 0, 9, 16, -1, 0, 0)

    moved = None
    leaving = False
    if thumby.buttonU.justPressed():
        if "U" in saidas:
            moved = "U"
        elif na_entrada and DUNGEON_EXIT_DIR == "U":
            leaving = True
    if thumby.buttonD.justPressed():
        if "D" in saidas:
            moved = "D"
        elif na_entrada and DUNGEON_EXIT_DIR == "D":
            leaving = True
    if thumby.buttonL.justPressed():
        if "L" in saidas:
            moved = "L"
        elif na_entrada and DUNGEON_EXIT_DIR == "L":
            leaving = True
    if thumby.buttonR.justPressed():
        if "R" in saidas:
            moved = "R"
        elif na_entrada and DUNGEON_EXIT_DIR == "R":
            leaving = True

    if leaving:
        ctx["passar_turno_exploracao"]()
        if ctx["estado_jogo"] == "GAME_OVER":
            return
        ctx["origem_batalha"] = "WILDERNESS"
        ctx["estado_jogo"] = "TRANSICAO_OUT"
        return

    if moved:
        if moved == "U":
            pos[1] += 1
        elif moved == "D":
            pos[1] -= 1
        elif moved == "L":
            pos[0] -= 1
        elif moved == "R":
            pos[0] += 1
        ctx["dungeon_visitado"] |= bit(pos)
        ctx["tocar_som_efeito"](300, 80)
        ctx["passar_turno_exploracao"]()
        if ctx["estado_jogo"] == "GAME_OVER":
            return
        nova_sala = ctx["sala_dungeon"](pos)
        if (not ctx["sala_saida_dungeon"](pos)) and random.random() < 0.17:
            nova_bg = nova_sala[3]
            ctx["bg_batalha_atual"] = bgs[nova_bg] if nova_bg < len(bgs) else bgs[0]
            ctx["estado_jogo"] = "TRANSICAO_IN"
            ctx["origem_batalha"] = "DUNGEON"

    if thumby.buttonA.justPressed():
        landslip_pos = ctx["LANDSLIP_POS"]
        is_landslip = pos[0] == landslip_pos[0] and pos[1] == landslip_pos[1]
        if is_landslip and not (ctx["dungeon_events"] & _LANDSLIP_BIT):
            ctx["dungeon_dialog_active"] = True
            has_item = ctx["heroi_tem_item_nome"](ctx["LANDSLIP_ITEM"])
            ctx["descarregar_items_mod"]()
            if has_item:
                ctx["dungeon_events"] |= _LANDSLIP_BIT
                text = "The pickaxe should clear the path here! Done!"
                ctx["dungeon_dialog_lines"], ctx["dungeon_dialog_scroll_max"] = (
                    ctx["preparar_dialogo_personagem"](text))
                ctx["tocar_som_efeito"](700, 160)
            else:
                text = _dlg(ctx["GFX_DIR"], 1)
                ctx["dungeon_dialog_lines"], ctx["dungeon_dialog_scroll_max"] = (
                    ctx["preparar_dialogo_personagem"](text))
                ctx["tocar_som_efeito"](120, 80)
            ctx["dungeon_dialog_icon"] = None
            ctx["dungeon_dialog_iname"] = ""
            ctx["dungeon_dialog_show_name"] = False
            ctx["dungeon_dialog_name"] = ctx["HERO_NAME"]
            ctx["dungeon_dialog_scroll"] = 0
            ctx["dungeon_dialog_scroll_timer"] = agora
            ctx["dungeon_dialog_auto_ms"] = ctx["DIALOG_SCROLL_AUTO_MS"]
            ctx["carregar_hero_portraits"]()
        elif sala[7] and not (ctx["dungeon_items_coletados"] & bit(pos)):
            ctx["dungeon_items_coletados"] |= bit(pos)
            data = {"icon_key": sala[6], "nome": sala[7], "qtd": sala[8]}
            if data["icon_key"] == "stone_tablet":
                data = ctx["criar_item_chave"](data["icon_key"], data["nome"], sala[8])
            ctx["adicionar_item_inventario"](data)
            ctx["descarregar_items_mod"]()
            ctx["dungeon_dialog_active"] = True
            ctx["dungeon_dialog_lines"] = ["You Got"]
            ctx["dungeon_dialog_icon"] = ctx["icone_item_chave"](
                data["icon_key"], ctx["icon_potion"])
            ctx["dungeon_dialog_iname"] = data["nome"]
            ctx["dungeon_dialog_scroll"] = 0
            ctx["dungeon_dialog_scroll_max"] = 0
            ctx["dungeon_dialog_scroll_timer"] = 0
            ctx["tocar_som_recompensa"]()

    if thumby.buttonB.justPressed():
        ctx["pausar_musica"]()
        ctx["estado_jogo"] = "DUNGEON_MENU_PREP"
        ctx["estado_jogo_antes_menu"] = "DUNGEON"
        ctx["menu_aba"] = 4
        ctx["stats_pagina"] = 0
        ctx["magic_sel"] = 0
        ctx["magic_scroll"] = 0
        ctx["equip_modo"] = False
        ctx["equip_item_sel"] = 0
        ctx["equip_item_scroll"] = 0
        ctx["mapa_scroll_timer"] = 0
        ctx["mapa_scroll_x"] = 0
        ctx["mapa_scroll_y"] = 0
        ctx["menu_input_lock"] = 2
        ctx["drenar_botoes"]()
        ctx["fonte_normal"]()
