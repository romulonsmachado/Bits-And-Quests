# Exploration/menu scenes loaded by game.py when needed.

def entrar_wilderness(reset_menu=True):
    global estado_jogo, region_id_atual, wilderness_sel
    global estado_retorno_batalha
    descarregar_village_mod(True)
    limpar_sting_forest_bg()
    limpar_bgs_dungeon(True)
    descarregar_dungeon_mod(True)
    carregar_wilderness_bg()
    if reset_menu:
        wilderness_sel = 0
    carregar_musica(MUSICA_WILDERNESS, 130)
    region_id_atual = REGION_WILDERNESS
    estado_retorno_batalha = "WILDERNESS"
    estado_jogo = "WILDERNESS"
    coletar_gc()

def entrar_sting_forest(reset_menu=True):
    global estado_jogo, region_id_atual, sting_forest_sel, estado_retorno_batalha
    descarregar_village_mod(True)
    limpar_wilderness_bg()
    limpar_bgs_dungeon(True)
    descarregar_dungeon_mod(True)
    carregar_sting_forest_bg()
    if reset_menu:
        sting_forest_sel = 0
    carregar_musica(MUSICA_WILDERNESS, 130)
    region_id_atual = REGION_STING_FOREST
    estado_retorno_batalha = "STING_FOREST"
    estado_jogo = "STING_FOREST"
    coletar_gc()

def entrar_cave_entrance(reset_menu=True):
    global estado_jogo, cave_entrance_sel, region_id_atual
    limpar_wilderness_bg()
    limpar_sting_forest_bg()
    descarregar_village_mod(True)
    limpar_bgs_batalha_mapa(True)
    descarregar_battle_mod_total()
    carregar_cave_entrance_bg()
    parar_musica_total()
    if reset_menu:
        cave_entrance_sel = 0
    region_id_atual = REGION_WILDERNESS
    estado_jogo = "CAVE_ENTRANCE"
    coletar_gc()

def iniciar_batalha_wilderness(retorno):
    global origem_batalha, estado_retorno_batalha
    global estado_jogo, bg_batalha_id, bg_batalha_atual
    origem_batalha = "WILDERNESS"
    estado_retorno_batalha = retorno
    bg_batalha_id = BG_GRASSLAND
    bg_batalha_atual = None
    estado_jogo = "TRANSICAO_IN"

def iniciar_batalha_sting_forest():
    global origem_batalha, estado_retorno_batalha
    global estado_jogo, bg_batalha_id, bg_batalha_atual
    origem_batalha = "STING_FOREST"
    estado_retorno_batalha = "STING_FOREST"
    bg_batalha_id = BG_FOREST
    bg_batalha_atual = None
    estado_jogo = "TRANSICAO_IN"

def wilderness_options():
    if wilderness_found_cave:
        return ("EXPLORE", LOCAL_CAVE_NAME.upper(), "STING FOREST", "FARLILY", "CAMP")
    return ("EXPLORE", "STING FOREST", "FARLILY", "CAMP")

def encontrar_healing_herb(agora):
    adicionar_item_id(carregar_items_mod().ITEM_HERB, 1)
    descarregar_items_mod()
    abrir_item_encontrado("Healing Herb", icon_herb, "WILDERNESS")

def desenhar_cave_entrance():
    bg = carregar_cave_entrance_bg()
    thumby.display.blit(bg, 0, 0, 72, 40, -1, 0, 0)
    opts = ("ENTER", "LEAVE")
    fonte_normal()
    thumby.display.drawFilledRectangle(0, 31, 72, 9, 0)
    thumby.display.blit(icon_seta_esq, 2, 32, 3, 7, -1, 0, 0)
    thumby.display.blit(icon_seta_dir, 67, 32, 3, 7, -1, 0, 0)
    txt = opts[cave_entrance_sel]
    thumby.display.drawText(txt, (72 - largura_texto_5x7(txt)) // 2, 32, 1)

def abrir_menu_da_cena(origem):
    global estado_jogo_antes_menu, estado_jogo, menu_aba, stats_pagina, equip_sel
    global items_sel, items_scroll, magic_sel, magic_scroll, equip_modo
    global equip_item_sel, equip_item_scroll, menu_input_lock
    pausar_musica()
    estado_jogo_antes_menu = origem
    estado_jogo = "MENU"
    menu_aba = 0
    stats_pagina = 0
    equip_sel = 0
    items_sel = 0
    items_scroll = 0
    magic_sel = 0
    magic_scroll = 0
    equip_modo = False
    equip_item_sel = 0
    equip_item_scroll = 0
    menu_input_lock = 2
    drenar_botoes()
    fonte_normal()
    liberar_assets_para_menu(origem)

def update_cave_entrance():
    global cave_entrance_sel, estado_jogo
    desenhar_cave_entrance()
    if thumby.buttonR.justPressed() or thumby.buttonL.justPressed():
        cave_entrance_sel = 1 - cave_entrance_sel
        tocar_som_navegacao()
    elif thumby.buttonA.justPressed():
        if cave_entrance_sel == 0:
            if turno_exploracao_ou_gameover():
                return
            estado_jogo = "TRANSICAO_CAVERNA_IN"
        else:
            if turno_exploracao_ou_gameover():
                return
            estado_jogo = "TRANSICAO_WILDERNESS_IN"
        drenar_botoes()
    elif thumby.buttonB.justPressed():
        abrir_menu_da_cena("CAVE_ENTRANCE")

def desenhar_wilderness():
    bg = carregar_wilderness_bg()
    thumby.display.blit(bg, 0, 0, 72, 40, -1, 0, 0)
    fonte_normal()
    if wilderness_msg:
        thumby.display.drawFilledRectangle(0, 14, 72, 13, 0)
        desenhar_linha_centrada_ou_scroll(wilderness_msg, 17, 68, 1)
        return
    opts = wilderness_options()
    thumby.display.drawFilledRectangle(0, 31, 72, 9, 0)
    thumby.display.blit(icon_seta_esq, 2, 32, 3, 7, -1, 0, 0)
    thumby.display.blit(icon_seta_dir, 67, 32, 3, 7, -1, 0, 0)
    txt = opts[wilderness_sel]
    if largura_texto_5x7(txt) > 56:
        desenhar_texto_scroll(txt, 8, 32, 56, 1)
    else:
        thumby.display.drawText(txt, (72 - largura_texto_5x7(txt)) // 2, 32, 1)

def update_wilderness(agora):
    global wilderness_sel, wilderness_msg, wilderness_msg_timer
    global wilderness_found_cave, estado_jogo, save_prompt_return
    global estado_jogo_antes_menu, menu_aba, stats_pagina, equip_sel
    global items_sel, items_scroll, magic_sel, magic_scroll, equip_modo, equip_item_sel
    global equip_item_scroll, menu_input_lock, save_prompt_sel
    desenhar_wilderness()
    if wilderness_msg:
        if time.ticks_diff(agora, wilderness_msg_timer) >= 0 or thumby.buttonA.justPressed() or thumby.buttonB.justPressed():
            wilderness_msg = ""
            drenar_botoes()
        return
    opts = wilderness_options()
    if wilderness_sel >= len(opts):
        wilderness_sel = 0
    if thumby.buttonR.justPressed():
        wilderness_sel = (wilderness_sel + 1) % len(opts)
        tocar_som_navegacao()
    elif thumby.buttonL.justPressed():
        wilderness_sel = (wilderness_sel - 1) % len(opts)
        tocar_som_navegacao()
    elif thumby.buttonB.justPressed():
        abrir_menu_da_cena("WILDERNESS")
    elif thumby.buttonA.justPressed():
        opt = opts[wilderness_sel]
        if opt == "EXPLORE":
            if turno_exploracao_ou_gameover():
                return
            r = random.random()
            if wilderness_found_cave:
                if r < 0.90:
                    iniciar_batalha_wilderness("WILDERNESS")
                else:
                    encontrar_healing_herb(agora)
            elif r < 0.50:
                wilderness_found_cave = True
                estado_jogo = "TRANSICAO_CAVE_ENTRANCE_IN"
            elif r < 0.95:
                iniciar_batalha_wilderness("WILDERNESS")
            else:
                encontrar_healing_herb(agora)
        elif opt == LOCAL_CAVE_NAME.upper():
            if turno_exploracao_ou_gameover():
                return
            estado_jogo = "TRANSICAO_CAVE_ENTRANCE_IN"
        elif opt == "STING FOREST":
            if turno_exploracao_ou_gameover():
                return
            estado_jogo = "TRANSICAO_STING_FOREST_IN"
        elif opt == "FARLILY":
            if turno_exploracao_ou_gameover():
                return
            if random.random() < 0.17:
                iniciar_batalha_wilderness("VILLAGE")
            else:
                estado_jogo = "TRANSICAO_VILLAGE_IN"
        else:
            save_prompt_return = "WILDERNESS"
            save_prompt_sel = 0
            estado_jogo = "SAVE_PROMPT"
        drenar_botoes()

def sting_forest_options():
    return ("EXPLORE", "LEAVE")

def desenhar_sting_forest():
    bg = carregar_sting_forest_bg()
    thumby.display.blit(bg, 0, 0, 72, 40, -1, 0, 0)
    fonte_normal()
    if sting_forest_msg:
        thumby.display.drawFilledRectangle(0, 14, 72, 13, 0)
        desenhar_linha_centrada_ou_scroll(sting_forest_msg, 17, 68, 1)
        return
    opts = sting_forest_options()
    thumby.display.drawFilledRectangle(0, 31, 72, 9, 0)
    thumby.display.blit(icon_seta_esq, 2, 32, 3, 7, -1, 0, 0)
    thumby.display.blit(icon_seta_dir, 67, 32, 3, 7, -1, 0, 0)
    txt = opts[sting_forest_sel]
    thumby.display.drawText(txt, (72 - largura_texto_5x7(txt)) // 2, 32, 1)

def update_sting_forest(agora):
    global sting_forest_sel, sting_forest_msg, sting_forest_msg_timer
    global estado_jogo, save_prompt_return, save_prompt_sel
    desenhar_sting_forest()
    if sting_forest_msg:
        if time.ticks_diff(agora, sting_forest_msg_timer) >= 0 or thumby.buttonA.justPressed() or thumby.buttonB.justPressed():
            sting_forest_msg = ""
            drenar_botoes()
        return
    opts = sting_forest_options()
    if sting_forest_sel >= len(opts):
        sting_forest_sel = 0
    if thumby.buttonR.justPressed():
        sting_forest_sel = (sting_forest_sel + 1) % len(opts)
        tocar_som_navegacao()
    elif thumby.buttonL.justPressed():
        sting_forest_sel = (sting_forest_sel - 1) % len(opts)
        tocar_som_navegacao()
    elif thumby.buttonB.justPressed():
        abrir_menu_da_cena("STING_FOREST")
    elif thumby.buttonA.justPressed():
        opt = opts[sting_forest_sel]
        if opt == "EXPLORE":
            if turno_exploracao_ou_gameover():
                return
            iniciar_batalha_sting_forest()
        else:
            if turno_exploracao_ou_gameover():
                return
            estado_jogo = "TRANSICAO_WILDERNESS_IN"
        drenar_botoes()


_SYNC_KEYS = (
    "estado_jogo", "estado_jogo_antes_menu", "estado_retorno_batalha", "origem_batalha",
    "region_id_atual", "wilderness_found_cave", "wilderness_sel", "wilderness_msg",
    "wilderness_msg_timer", "sting_forest_sel", "sting_forest_msg", "sting_forest_msg_timer",
    "cave_entrance_sel", "save_prompt_return", "save_prompt_sel", "bg_batalha_id",
    "menu_aba", "stats_pagina", "items_sel", "items_scroll", "magic_sel", "magic_scroll",
    "equip_sel", "equip_modo", "equip_item_sel", "equip_item_scroll", "menu_input_lock",
)

def _bind(ctx):
    g = globals()
    for k in ctx:
        if not k.startswith("_"):
            g[k] = ctx[k]

def _sync(ctx, skip=()):
    g = globals()
    for k in _SYNC_KEYS:
        if k in skip:
            continue
        if k in g:
            ctx[k] = g[k]

def call(ctx, name, *args):
    before = ctx.get("estado_jogo", None)
    _bind(ctx)
    r = globals()[name](*args)
    local = globals().get("estado_jogo", None)
    skip = ("estado_jogo",) if ctx.get("estado_jogo", None) != before and local == before else ()
    _sync(ctx, skip)
    return r

def draw(ctx, name):
    before = ctx.get("estado_jogo", None)
    _bind(ctx)
    globals()[name]()
    local = globals().get("estado_jogo", None)
    skip = ("estado_jogo",) if ctx.get("estado_jogo", None) != before and local == before else ()
    _sync(ctx, skip)
