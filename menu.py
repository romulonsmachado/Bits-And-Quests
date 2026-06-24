MENU_TABS = ("STATS", "EQUIPMENT", "MAGIC", "ITEMS", "MAP")
MENU_SLOTS = ("Weapon", "Armor", "Shield")
MENU_KEYS = ("weapon", "armor", "shield")

def _menu_w(txt):
    return largura_texto_5x7(txt)

def _menu_center(txt, y):
    thumby.display.drawText(txt, (72 - _menu_w(txt)) // 2, y, 1)

def _menu_title(txt):
    fonte_normal()
    thumby.display.drawText(txt, (72 - _menu_w(txt)) // 2, 2, 1)
    thumby.display.blit(icon_seta_esq, 2, 2, 3, 7, -1, 0, 0)
    thumby.display.blit(icon_seta_dir, 67, 2, 3, 7, -1, 0, 0)

def _menu_bars(y):
    thumby.display.drawFilledRectangle(0, y, 1, 8, 1)
    thumby.display.drawFilledRectangle(71, y, 1, 8, 1)

def _menu_icon(key, default=None):
    return icone_item_chave(key, default)

def _menu_draw_stats():
    h = heroi
    if stats_pagina == 0:
        p = carregar_hero_portraits()[0]
        thumby.display.blit(p, 2, 13, 24, 24, -1, 0, 0)
        if (h.get("StatusBits", 0) & 1) and ((time.ticks_ms() // 180) & 1) == 0:
            desenhar_icone(icon_poison, 18, 13)
        desenhar_texto_scroll("Level " + str(h["LVL"]), 29, 12, 42, 1)
        col = 1 if h["HP"] > h["HP_MAX"] * 0.20 or (time.ticks_ms() // 300) % 2 == 0 else 0
        desenhar_texto_scroll("HP " + str(h["HP"]) + "/" + str(h["HP_MAX"]), 29, 21, 42, col)
        desenhar_texto_scroll("MP " + str(h["MP"]) + "/" + str(h["MP_MAX"]), 29, 30, 42, 1)
        return
    atk = "ATK " + str(h["ATK"])
    df = "DEF " + str(h["DEF"])
    thumby.display.drawText(atk, 2, 13, 1)
    thumby.display.drawText(df, 72 - _menu_w(df) - 2, 13, 1)
    if h["XP_MAX"] > 0:
        desenhar_texto_scroll("XP " + str(h["XP"]) + "/" + str(h["XP_MAX"]), 2, 22, 68, 1)
    else:
        desenhar_texto_scroll("XP MAX", 2, 22, 68, 1)
    thumby.display.drawText("Bits", 2, 32, 1)
    desenhar_icone(icon_gold, 31, 31)
    thumby.display.drawText(str(h["Gold"]), 40, 32, 1)

def _menu_eq_slot():
    return MENU_SLOTS[equip_sel]

def _menu_eq_key():
    return MENU_KEYS[equip_sel]

def _menu_eq_count():
    h = heroi
    slot = _menu_eq_slot()
    key = _menu_eq_key()
    n = 1 if h[slot] != "None" else 0
    for it in h["Inventory"]:
        if it.get("icon_key", "") == key:
            n += 1
    return n

def _menu_eq_ref(pos):
    h = heroi
    slot = _menu_eq_slot()
    key = _menu_eq_key()
    if h[slot] != "None":
        if pos == 0:
            return None
        pos -= 1
    for it in h["Inventory"]:
        if it.get("icon_key", "") == key:
            if pos == 0:
                return it
            pos -= 1
    return None

def _menu_draw_eq_items():
    global equip_item_sel, equip_item_scroll
    total = _menu_eq_count()
    if total <= 0:
        _menu_center("Empty", 20)
        return
    if equip_item_sel >= total:
        equip_item_sel = total - 1
    if equip_item_sel < 0:
        equip_item_sel = 0
    if equip_item_sel < equip_item_scroll:
        equip_item_scroll = equip_item_sel
    if equip_item_sel >= equip_item_scroll + 3:
        equip_item_scroll = equip_item_sel - 2
    key = _menu_eq_key()
    for i in range(3):
        idx = equip_item_scroll + i
        if idx >= total:
            break
        y = 13 + i * 9
        ref = _menu_eq_ref(idx)
        if ref is None:
            desenhar_texto_scroll("None", 12, y + 1, 58, 1)
        else:
            show = idx != equip_item_sel or ((time.ticks_ms() // 180) & 1) == 0
            if show:
                desenhar_icone(_menu_icon(key, icon_potion), 3, y)
            desenhar_texto_scroll(ref["nome"], 13, y + 1, 46, 1)
            if ref.get("qtd", 1) > 1 and show:
                q = str(ref.get("qtd", 1))
                thumby.display.drawText(q, 68 - _menu_w(q), y + 1, 1)
        if idx == equip_item_sel:
            _menu_bars(y)

def _menu_draw_equipment():
    if equip_modo:
        _menu_draw_eq_items()
        return
    y = 13
    blink = ((time.ticks_ms() // 180) & 1) == 0
    for i in range(3):
        slot = MENU_SLOTS[i]
        key = heroi.get(slot + "_icon", "")
        ico = _menu_icon(key, None) if key else None
        show = i != equip_sel or blink
        if ico and show:
            desenhar_icone(ico, 2, y)
        desenhar_texto_scroll(heroi[slot], 12, y + 1, 58, 1)
        if i == equip_sel:
            _menu_bars(y)
        y += 9

def _menu_draw_magic():
    global magic_sel, magic_scroll
    spells = heroi["Magias"]
    if not spells:
        _menu_center("Empty", 20)
        return
    if magic_sel >= len(spells):
        magic_sel = len(spells) - 1
    if magic_sel < 0:
        magic_sel = 0
    if magic_sel < magic_scroll:
        magic_scroll = magic_sel
    if magic_sel >= magic_scroll + 3:
        magic_scroll = magic_sel - 2
    blink = ((time.ticks_ms() // 180) & 1) == 0
    for i in range(3):
        idx = magic_scroll + i
        if idx >= len(spells):
            break
        m = spells[idx]
        y = 13 + i * 9
        show = idx != magic_sel or blink
        if show:
            desenhar_icone(_menu_icon(m.get("icon_key", "magia"), icon_magia), 3, y)
        desenhar_texto_scroll(m["nome"], 13, y + 1, 42, 1)
        if show:
            thumby.display.drawText(str(m.get("custo", 0)), 61, y + 1, 1)
        if idx == magic_sel:
            _menu_bars(y)

def _menu_draw_items():
    global items_sel, items_scroll
    inv = heroi["Inventory"]
    if not inv:
        _menu_center("Empty", 20)
        return
    if items_sel >= len(inv):
        items_sel = len(inv) - 1
    if items_sel < 0:
        items_sel = 0
    if items_sel < items_scroll:
        items_scroll = items_sel
    if items_sel >= items_scroll + 3:
        items_scroll = items_sel - 2
    for i in range(3):
        idx = items_scroll + i
        if idx >= len(inv):
            break
        it = inv[idx]
        y = 13 + i * 9
        show = idx != items_sel or ((time.ticks_ms() // 180) & 1) == 0
        if show:
            desenhar_icone(_menu_icon(it.get("icon_key", ""), icon_potion), 3, y)
        desenhar_texto_scroll(it["nome"], 13, y + 1, 46, 1)
        if show:
            q = str(it.get("qtd", 1))
            thumby.display.drawText(q, 68 - _menu_w(q), y + 1, 1)
        if idx == items_sel:
            _menu_bars(y)

def _menu_draw_map():
    return

def _menu_remove_item(ref):
    inv = heroi["Inventory"]
    if ref.get("qtd", 1) > 1:
        ref["qtd"] -= 1
    elif ref in inv:
        inv.remove(ref)

def _menu_use_item():
    global item_info_name, item_info_icon, item_info_effect, estado_jogo
    global menu_aba, menu_input_lock, dungeon_dialog_lines
    global dungeon_dialog_scroll_max, dungeon_dialog_icon, dungeon_dialog_iname
    global dungeon_dialog_show_name
    global dungeon_dialog_name, dungeon_dialog_scroll, dungeon_dialog_scroll_timer
    global dungeon_dialog_auto_ms
    inv = heroi["Inventory"]
    if not inv or items_sel >= len(inv):
        return
    it = inv[items_sel]
    key = it.get("icon_key", "")
    if key == "weapon" or key == "armor" or key == "shield":
        item_info_name = it.get("nome", "")
        item_info_icon = _menu_icon(key, icon_potion)
        item_info_effect = texto_efeito_equip(key, item_info_name)
        estado_jogo = "INFO_EQUIP_ITEM"
        menu_aba = 3
        menu_input_lock = 2
        drenar_botoes()
        return
    if key == "stone_tablet":
        descarregar_items_mod()
        dungeon_dialog_lines, dungeon_dialog_scroll_max = preparar_dialogo_personagem("An ancient text I can't read.")
        dungeon_dialog_icon = None
        dungeon_dialog_iname = ""
        dungeon_dialog_show_name = False
        dungeon_dialog_name = HERO_NAME
        dungeon_dialog_scroll = 0
        dungeon_dialog_scroll_timer = time.ticks_ms()
        dungeon_dialog_auto_ms = DIALOG_SCROLL_AUTO_MS
        carregar_hero_portraits()
        estado_jogo = "DIALOGO_ITEM"
        menu_aba = 3
        drenar_botoes()
        return
    if tem_cura_hp(it) or tem_cura_mp(it):
        if cura_bloqueada_por_cheio(it):
            descarregar_items_mod()
            tocar_som_efeito(120, 80)
            return
        if tem_cura_hp(it):
            heroi["HP"] += calc_heal_hp(it)
            if heroi["HP"] > heroi["HP_MAX"]:
                heroi["HP"] = heroi["HP_MAX"]
        if tem_cura_mp(it):
            heroi["MP"] += calc_heal_mp(it)
            if heroi["MP"] > heroi["MP_MAX"]:
                heroi["MP"] = heroi["MP_MAX"]
        _menu_remove_item(it)
        descarregar_items_mod()
        tocar_som_efeito(600, 100)
    else:
        descarregar_items_mod()
        tocar_som_efeito(120, 80)

def _menu_handle_equip_mode():
    global equip_modo, equip_item_sel, equip_item_scroll
    total = _menu_eq_count()
    if thumby.buttonB.justPressed():
        equip_modo = False
        equip_item_sel = 0
        equip_item_scroll = 0
        tocar_som_navegacao()
        drenar_botoes()
        return True
    if total <= 0:
        return False
    if thumby.buttonD.justPressed():
        equip_item_sel = (equip_item_sel + 1) % total
        tocar_som_navegacao()
        return True
    if thumby.buttonU.justPressed():
        equip_item_sel = (equip_item_sel - 1) % total
        tocar_som_navegacao()
        return True
    if thumby.buttonA.justPressed():
        slot = _menu_eq_slot()
        ref = _menu_eq_ref(equip_item_sel)
        if ref is None:
            ok = desequipar_slot(slot)
        else:
            equipar_item_slot(slot, ref)
            ok = True
        tocar_som_efeito(620 if ok else 120, 90 if ok else 80)
        equip_modo = False
        equip_item_sel = 0
        equip_item_scroll = 0
        drenar_botoes()
        return True
    return False

def atualizar_menu(agora):
    global menu_aba, stats_pagina, equip_sel, equip_modo, equip_item_sel
    global equip_item_scroll, items_sel, items_scroll, magic_sel, magic_scroll
    global mapa_scroll_x, mapa_scroll_y, mapa_scroll_timer, menu_input_lock, estado_jogo
    thumby.display.fill(0)
    tab = menu_aba
    if tab == 4 and estado_jogo_antes_menu == "DUNGEON":
        estado_jogo = "DUNGEON_MAP_MENU"
        return
    title = _menu_eq_slot().upper() if tab == 1 and equip_modo else MENU_TABS[tab]
    mapa_cheio = tab == 4 and estado_jogo_antes_menu == "DUNGEON"
    if not mapa_cheio:
        _menu_title(title)
    input_ok = menu_input_lock <= 0
    if menu_input_lock > 0:
        menu_input_lock -= 1
    if tab == 0:
        _menu_draw_stats()
    elif tab == 1:
        _menu_draw_equipment()
    elif tab == 2:
        _menu_draw_magic()
    elif tab == 3:
        _menu_draw_items()
    else:
        _menu_draw_map()
    if not input_ok:
        return
    if tab == 1 and equip_modo:
        _menu_handle_equip_mode()
        return
    if thumby.buttonR.justPressed():
        menu_aba = (tab + 1) % 5
        if menu_aba == 0:
            stats_pagina = 0
        if menu_aba == 4 and estado_jogo_antes_menu == "DUNGEON":
            tocar_som_navegacao()
            estado_jogo = "DUNGEON_MAP_MENU"
            drenar_botoes()
            return
        equip_modo = False
        equip_item_sel = 0
        equip_item_scroll = 0
        tocar_som_navegacao()
    elif thumby.buttonL.justPressed():
        menu_aba = (tab - 1) % 5
        if menu_aba == 0:
            stats_pagina = 0
        if menu_aba == 4 and estado_jogo_antes_menu == "DUNGEON":
            tocar_som_navegacao()
            estado_jogo = "DUNGEON_MAP_MENU"
            drenar_botoes()
            return
        equip_modo = False
        equip_item_sel = 0
        equip_item_scroll = 0
        tocar_som_navegacao()
    elif tab == 0 and (thumby.buttonU.justPressed() or thumby.buttonD.justPressed()):
        stats_pagina = 1 - stats_pagina
        tocar_som_navegacao()
    elif tab == 1:
        if thumby.buttonD.justPressed():
            equip_sel = (equip_sel + 1) % 3
            tocar_som_navegacao()
        elif thumby.buttonU.justPressed():
            equip_sel = (equip_sel - 1) % 3
            tocar_som_navegacao()
        elif thumby.buttonA.justPressed():
            slot = _menu_eq_slot()
            if heroi[slot] != "None":
                ok = desequipar_slot(slot)
                tocar_som_efeito(620 if ok else 120, 90 if ok else 80)
                descarregar_items_mod()
                drenar_botoes()
            elif _menu_eq_count() > 0:
                equip_modo = True
                equip_item_sel = 0
                equip_item_scroll = 0
                tocar_som_navegacao()
                drenar_botoes()
            else:
                tocar_som_efeito(120, 80)
            return
    elif tab == 2 and heroi["Magias"]:
        mlen = len(heroi["Magias"])
        if thumby.buttonD.justPressed():
            magic_sel = (magic_sel + 1) % mlen
            tocar_som_navegacao()
        elif thumby.buttonU.justPressed():
            magic_sel = (magic_sel - 1) % mlen
            tocar_som_navegacao()
    elif tab == 3 and heroi["Inventory"]:
        inv_len = len(heroi["Inventory"])
        if thumby.buttonD.justPressed():
            items_sel = (items_sel + 1) % inv_len
            tocar_som_navegacao()
        elif thumby.buttonU.justPressed():
            items_sel = (items_sel - 1) % inv_len
            tocar_som_navegacao()
        elif thumby.buttonA.justPressed():
            _menu_use_item()
            return
    if thumby.buttonB.justPressed():
        mapa_scroll_x = 0
        mapa_scroll_y = 0
        limpar_dialogo_temp()
        descarregar_items_mod()
        limpar_hero_portraits()
        retomar_musica()
        estado_jogo = estado_jogo_antes_menu
        drenar_botoes()

MENU_SYNC_KEYS = (
    "menu_aba", "stats_pagina", "menu_input_lock",
    "items_sel", "items_scroll", "magic_sel", "magic_scroll",
    "equip_sel", "equip_modo", "equip_item_sel", "equip_item_scroll",
    "mapa_scroll_x", "mapa_scroll_y", "mapa_scroll_timer", "estado_jogo",
    "item_info_icon", "item_info_name", "item_info_effect",
    "dungeon_dialog_lines", "dungeon_dialog_icon", "dungeon_dialog_iname",
    "dungeon_dialog_scroll", "dungeon_dialog_scroll_max", "dungeon_dialog_scroll_timer",
    "dungeon_dialog_auto_ms", "dungeon_dialog_show_name", "dungeon_dialog_name",
)

def _menu_bind(ctx):
    globals().update(ctx)

def _menu_sync(ctx):
    g = globals()
    for k in MENU_SYNC_KEYS:
        if k in g:
            ctx[k] = g[k]

def menu_update(ctx, agora):
    _menu_bind(ctx)
    atualizar_menu(agora)
    _menu_sync(ctx)
