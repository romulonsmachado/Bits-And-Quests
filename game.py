import thumby, time, random, gc, sys

GAME_DIR = "/Games/Bits & Quests"
if GAME_DIR not in sys.path:
    sys.path.append(GAME_DIR)

def obter_resultado_titulo():
    try:
        return titulo_result
    except NameError:
        pass
    try:
        r = sys.bq_title_result
        try:
            delattr(sys, "bq_title_result")
        except:
            sys.bq_title_result = None
        if r is not None:
            return r
    except:
        pass
    import title
    r = title.run(GAME_DIR)
    if "title" in sys.modules:
        del sys.modules["title"]
    del title
    gc.collect()
    return r

titulo_result = obter_resultado_titulo()
del obter_resultado_titulo
try:
    delattr(sys, "bq_title_result")
except:
    pass
gc.collect()

from ui import (
    FONT_H, DIALOG_SCROLL_AUTO_MS, DIALOG_SCROLL_SLOW_MS,
    fonte_normal,
    desenhar_linha_centrada_8x8,
    largura_texto_5x7, wrap_texto_5x7,
    desenhar_texto_scroll, desenhar_linha_centrada_ou_scroll,
    preparar_dialogo_personagem, desenhar_dialogo_personagem,
    desenhar_linhas_centralizadas_5x7,
    tamanho_icone, desenhar_icone)

thumby.display.setFPS(30)
BUILD_TAG = "v186_dungeon_menu_preload"

LOCAL_CAVE_DUNGEON_ID = 0
LOCAL_CAVE_NAME = "Wurms' Cave"
LOCAL_VILLAGE_ID = 0
LOCAL_VILLAGE_NAME = "Farlily"

icon_hp           = bytearray([30,63,127,254,190,95,39,30])
icon_mp           = bytearray([5,144,44,154,89,53,128,81])
icon_potion       = bytearray([0,96,146,239,255,242,96,0])
icon_stone_tablet = bytearray([0,118,233,151,213,187,94,0])
icon_herb         = bytearray([128,120,36,82,74,101,49,31])
icon_magia        = bytearray([0,24,60,126,60,24,0])
icon_strike       = bytearray([17,66,36,157,56,34,73,136])
icon_flee_txt     = bytearray([31,5,5,0,31,16,16,0,31,21,21,0,31,21,21])
icon_seta_esq     = bytearray([8,28,62])
icon_seta_dir     = bytearray([62,28,8])
icon_weapon       = bytearray([3,5,10,84,104,48,88,128])
icon_armor        = bytearray([6,29,231,178,90,239,29,6])
icon_shield       = bytearray([0,62,97,241,217,109,62,0])
icon_gold         = bytearray([62,127,69,126,228,174,74,4])
icon_poison       = bytearray([0,0,112,236,183,204,112,0])

REGION_FARLILY = 0
REGION_WILDERNESS = 1
REGION_DUNGEON = 2
REGION_STING_FOREST = 3
WORLD_FLAG_WURMS_FOUND = 1
WORLD_FLAG_INTRO_DONE = 2
WORLD_FLAG_TEMPLE_SWORD = 4
WORLD_FLAG_TEMPLE_REQUEST = 8
WORLD_FLAG_TEMPLE_RELIC = 16

DUNGEON_ID_WURMS = LOCAL_CAVE_DUNGEON_ID
DUNGEON_STATE_SLOTS = 8
DUNGEON_ENTRY_MAIN = (2, 0)
DUNGEON_MAP_COLS_DEFAULT = 9
DMAP_CELL = 8
DMAP_AREA_H = 40
LANDSLIP_POS = (2, 5)
LANDSLIP_ITEM = "Pickaxe"
LANDSLIP_OPEN_DIR = "U"
LANDSLIP_EVENT_BIT = 1
DUNGEON_EVENT_OPEN_POS = ((LANDSLIP_POS,),)
DUNGEON_EVENT_OPEN_DIR = ((LANDSLIP_OPEN_DIR,),)
DUNGEON_EVENT_OPEN_BIT = ((LANDSLIP_EVENT_BIT,),)
DMAP_EXITS = ("", "U", "D", "DU", "L", "LU", "DL", "DLU",
              "R", "RU", "DR", "DRU", "LR", "LRU", "DLR", "DLRU")

GFX_DIR = GAME_DIR + "/gfx/"
BACKGROUNDS_BIN = "backgrounds.bin"
PORTRAITS_BIN = "portraits.bin"
BG_BYTES = 360
PORTRAIT_BYTES = 72
BG_FOREST = 0
BG_GRASSLAND = 1
BG_MOUNTAIN = 2
BG_CAVE1 = 3
BG_CAVE2 = 4
BG_CAVE_ENTRANCE = 6

MUSICA_WILDERNESS = ((6,12),(18,4),(16,14),(13,1),(11,1),(13,16))
MUSICA_DUNGEON = ((-12,8),(-5,8),(-3,8),(-6,8),(-5,16),(-1,4))
MUSICA_BATALHA = ((7,2),(10,2),(14,3),(19,5),(14,2),(19,8))
MUSICA_VITORIA = ((0,2),(4,2),(7,2),(12,4),(14,4),(12,8))
MUSICA_DERROTA = ((7,2),(5,2),(3,2),(0,3),(-5,3),(-12,4))

HERO_NAME = "THUMBOR"
LEVEL_ATK_MAIN = (0,0,0,0,1,1,1,1,1,2)
MAX_LEVEL_MAIN = 10
SHOP_ICONS = (icon_gold, icon_herb, icon_weapon, icon_armor, icon_shield,
              icon_potion, icon_stone_tablet, icon_magia, icon_strike)

def coletar_gc():
    gc.collect()
    try:
        livre = gc.mem_free()
        if livre > 0:
            limite = livre // 4
            if limite < 512:
                limite = 512
            gc.threshold(limite)
    except:
        pass

def read_file_into(path, offset, data):
    f = open(path, "rb")
    try:
        f.seek(offset)
        try:
            n = f.readinto(data)
            if n is not None and n < len(data):
                for i in range(n, len(data)):
                    data[i] = 0
        except AttributeError:
            raw = f.read(len(data))
            n = len(raw)
            for i in range(n):
                data[i] = raw[i]
            for i in range(n, len(data)):
                data[i] = 0
    finally:
        f.close()

def load_pack(name, offset, size):
    data = bytearray(size)
    read_file_into(GFX_DIR + name, offset, data)
    return data

def load_background(bg_id):
    return load_pack(BACKGROUNDS_BIN, bg_id * BG_BYTES, BG_BYTES)

battle = None
dng = None
village_mod = None
items_mod = None
menu_mod = None
menu_update_fn = None
scenes_mod = None
story_mod = None
saveui_mod = None
hero_portrait = None
hero_portrait_talk = None
npc_portrait = None
npc_portrait_talk = None
bm_BG1 = None
bm_BG2 = None
bm_BG3 = None
bitmap7 = None
bitmap8 = None
DUNGEON_BGS = None
cave_entrance_bg = None
wilderness_bg = None
sting_forest_bg = None
bg_batalha_atual = None
bg_batalha_id = BG_GRASSLAND

def carregar_dungeon_mod(dungeon_id=None):
    global dng
    if dng is None:
        import dungeons as _dng
        dng = _dng
        del _dng
        coletar_gc()
    if dungeon_id is None:
        dungeon_id = dungeon_id_atual
    dng.load(dungeon_id)
    return dng

def descarregar_dungeon_mod(total=False):
    global dng
    if not total or dng is None:
        return
    try:
        names = dng.module_names()
        dng.unload()
    except:
        names = ()
    for m in ("dungeons",) + tuple(names):
        if m in sys.modules:
            del sys.modules[m]
    dng = None
    coletar_gc()

def carregar_battle_mod():
    global battle
    if battle is None:
        import battle as _battle
        battle = _battle
        battle.configurar_icones(icon_hp, icon_mp, icon_potion, icon_herb,
                                 icon_magia, icon_strike, icon_flee_txt)
        del _battle
        coletar_gc()
    return battle

def descarregar_battle_mod_total():
    global battle
    if battle is None:
        return
    battle.limpar_assets_batalha(True)
    for m in ("battle", "status"):
        if m in sys.modules:
            del sys.modules[m]
    battle = None
    coletar_gc()

def limpar_assets_battle_mod():
    if battle is not None:
        battle.limpar_assets_batalha(True)

def carregar_village_mod():
    global village_mod
    if village_mod is None:
        import villages as _village
        village_mod = _village
        del _village
        coletar_gc()
    return village_mod

def descarregar_village_mod(total=False):
    global village_mod
    if village_mod is None:
        return
    try:
        names = village_mod.module_names()
    except:
        names = ()
    village_mod.unload()
    if total:
        for m in ("villages",) + tuple(names):
            if m in sys.modules:
                del sys.modules[m]
        village_mod = None
    coletar_gc()

def carregar_items_mod():
    global items_mod
    if items_mod is None:
        import items as _items
        items_mod = _items
        del _items
        coletar_gc()
    return items_mod

def descarregar_items_mod():
    global items_mod
    if items_mod is None:
        return
    if "items" in sys.modules:
        del sys.modules["items"]
    items_mod = None
    coletar_gc()


MENU_SCRIPT_NAMES = (
    "_menu_w", "_menu_center", "_menu_title",
    "_menu_bars", "_menu_icon", "_menu_draw_stats", "_menu_eq_slot",
    "_menu_eq_key", "_menu_eq_count", "_menu_eq_ref", "_menu_draw_eq_items",
    "_menu_draw_equipment", "_menu_draw_magic", "_menu_draw_items",
    "_menu_draw_map", "_menu_remove_item", "_menu_use_item",
    "_menu_handle_equip_mode", "atualizar_menu", "map_scroll_hero_local",
    "MENU_SYNC_KEYS", "_menu_bind", "_menu_sync",
    "MENU_TABS", "MENU_SLOTS", "MENU_KEYS",
    "menu_update",
)

def parar_audio_antes_carga():
    global sfx_ate, proxima_nota_pronta
    thumby.audio.stop()
    sfx_ate = 0
    proxima_nota_pronta = False

def carregar_menu_dungeon_abas():
    carregar_menu_mod()
    carregar_hero_portraits()

def carregar_menu_mod():
    global menu_mod, menu_update_fn
    if menu_update_fn is None:
        parar_audio_antes_carga()
        try:
            ef = execfile
        except NameError:
            import menu as _menu
            menu_mod = _menu
            menu_update_fn = _menu.menu_update
            del _menu
        else:
            g = globals()
            try:
                ef(GAME_DIR + "/menu.py", g, g)
            except TypeError:
                try:
                    ef(GAME_DIR + "/menu.py", g)
                except TypeError:
                    ef(GAME_DIR + "/menu.py")
            menu_mod = None
            menu_update_fn = g["menu_update"]
            try:
                del g["menu_update"]
            except:
                pass
        coletar_gc()
    return menu_update_fn

def descarregar_menu_mod(total=False):
    global menu_mod, menu_update_fn
    if menu_mod is None and menu_update_fn is None:
        return
    if not total:
        return
    parar_audio_antes_carga()
    if "menu" in sys.modules:
        del sys.modules["menu"]
    if "dungeonmap" in sys.modules:
        del sys.modules["dungeonmap"]
    menu_mod = None
    menu_update_fn = None
    g = globals()
    for k in MENU_SCRIPT_NAMES:
        if k in g:
            del g[k]
    coletar_gc()

def carregar_scenes_mod():
    global scenes_mod
    if scenes_mod is None:
        import scenes as _scenes
        scenes_mod = _scenes
        del _scenes
        coletar_gc()
    return scenes_mod

def descarregar_scenes_mod(total=False):
    global scenes_mod
    if scenes_mod is None or not total:
        return
    if "scenes" in sys.modules:
        del sys.modules["scenes"]
    scenes_mod = None
    coletar_gc()

def scene_call(name, *args):
    return carregar_scenes_mod().call(globals(), name, *args)

def scene_draw(name):
    carregar_scenes_mod().draw(globals(), name)

def draw_wilderness_scene():
    scene_draw("desenhar_wilderness")

def draw_sting_forest_scene():
    scene_draw("desenhar_sting_forest")

def draw_cave_entrance_scene():
    scene_draw("desenhar_cave_entrance")

def carregar_story_mod():
    global story_mod
    if story_mod is None:
        import story as _story
        story_mod = _story
        del _story
        coletar_gc()
    return story_mod

def descarregar_story_mod(total=False):
    global story_mod
    if story_mod is None or not total:
        return
    if "story" in sys.modules:
        del sys.modules["story"]
    story_mod = None
    coletar_gc()

def story_call(name, *args):
    return carregar_story_mod().call(globals(), name, *args)

def abrir_intro_se_preciso():
    if novo_jogo_atual and not flag_on(WORLD_FLAG_INTRO_DONE):
        story_call("abrir_intro_inicial_se_preciso")

def carregar_saveui_mod():
    global saveui_mod
    if saveui_mod is None:
        import saveui as _saveui
        saveui_mod = _saveui
        del _saveui
        coletar_gc()
    return saveui_mod

def descarregar_saveui_mod(total=False):
    global saveui_mod
    if saveui_mod is None or not total:
        return
    if "saveui" in sys.modules:
        del sys.modules["saveui"]
    saveui_mod = None
    coletar_gc()

def entrar_vila(reset_menu=True):
    global estado_jogo, region_id_atual, estado_retorno_batalha
    limpar_wilderness_bg()
    limpar_sting_forest_bg()
    limpar_bgs_dungeon(True)
    descarregar_dungeon_mod(True)
    v = carregar_village_mod()
    if reset_menu:
        v.reset()
    v.load_assets(GAME_DIR, LOCAL_VILLAGE_ID)
    carregar_musica(v.MUSIC, v.BPM)
    del v
    region_id_atual = REGION_FARLILY
    estado_retorno_batalha = "WILDERNESS"
    estado_jogo = "VILLAGE"
    coletar_gc()

def carregar_hero_portraits():
    global hero_portrait, hero_portrait_talk
    if hero_portrait is None:
        hero_portrait = load_pack(PORTRAITS_BIN, 0, PORTRAIT_BYTES)
    if hero_portrait_talk is None:
        hero_portrait_talk = load_pack(PORTRAITS_BIN, PORTRAIT_BYTES, PORTRAIT_BYTES)
    return hero_portrait, hero_portrait_talk

def limpar_hero_portraits():
    global hero_portrait, hero_portrait_talk
    if hero_portrait is not None or hero_portrait_talk is not None:
        hero_portrait = None
        hero_portrait_talk = None
        coletar_gc()

def carregar_npc_portraits(idx):
    global npc_portrait, npc_portrait_talk
    base = (2 + idx * 2) * PORTRAIT_BYTES
    if npc_portrait is None:
        npc_portrait = load_pack(PORTRAITS_BIN, base, PORTRAIT_BYTES)
    if npc_portrait_talk is None:
        npc_portrait_talk = load_pack(PORTRAITS_BIN, base + PORTRAIT_BYTES, PORTRAIT_BYTES)
    return npc_portrait, npc_portrait_talk

def limpar_npc_portraits():
    global npc_portrait, npc_portrait_talk
    if npc_portrait is not None or npc_portrait_talk is not None:
        npc_portrait = None
        npc_portrait_talk = None
        coletar_gc()

def carregar_bg_batalha(bg_id):
    global bm_BG1, bm_BG2, bm_BG3, bg_batalha_atual, bg_batalha_id
    bg_batalha_id = bg_id
    if bg_id == BG_FOREST:
        if bm_BG1 is None:
            bm_BG1 = load_background(BG_FOREST)
        bg_batalha_atual = bm_BG1
    elif bg_id == BG_MOUNTAIN:
        if bm_BG3 is None:
            bm_BG3 = load_background(BG_MOUNTAIN)
        bg_batalha_atual = bm_BG3
    else:
        if bm_BG2 is None:
            bm_BG2 = load_background(BG_GRASSLAND)
        bg_batalha_atual = bm_BG2
    return bg_batalha_atual

def limpar_bgs_batalha_mapa(liberar=False):
    global bm_BG1, bm_BG2, bm_BG3, bg_batalha_atual
    if liberar:
        bm_BG1 = None
        bm_BG2 = None
        bm_BG3 = None
        bg_batalha_atual = None

def carregar_bgs_dungeon():
    global bitmap7, bitmap8, DUNGEON_BGS
    if bitmap7 is None:
        bitmap7 = load_background(BG_CAVE1)
    if bitmap8 is None:
        bitmap8 = load_background(BG_CAVE2)
    if DUNGEON_BGS is None:
        DUNGEON_BGS = (bitmap7, bitmap8, bitmap7, bitmap8)
    return DUNGEON_BGS

def limpar_bgs_dungeon(liberar=False):
    global bitmap7, bitmap8, DUNGEON_BGS
    if liberar:
        bitmap7 = None
        bitmap8 = None
        DUNGEON_BGS = None

def limpar_cave_entrance_bg():
    global cave_entrance_bg
    cave_entrance_bg = None

def carregar_cave_entrance_bg():
    global cave_entrance_bg
    if cave_entrance_bg is None:
        cave_entrance_bg = load_background(BG_CAVE_ENTRANCE)
    return cave_entrance_bg

def carregar_wilderness_bg():
    global wilderness_bg
    if wilderness_bg is None:
        wilderness_bg = load_background(BG_GRASSLAND)
    return wilderness_bg

def limpar_wilderness_bg():
    global wilderness_bg
    wilderness_bg = None

def carregar_sting_forest_bg():
    global sting_forest_bg
    if sting_forest_bg is None:
        sting_forest_bg = load_background(BG_FOREST)
    return sting_forest_bg

def limpar_sting_forest_bg():
    global sting_forest_bg
    sting_forest_bg = None

def liberar_assets_para_menu(origem):
    descarregar_menu_mod(True)
    descarregar_saveui_mod(True)
    descarregar_story_mod(True)
    descarregar_battle_mod_total()
    limpar_bgs_batalha_mapa(True)
    limpar_hero_portraits()
    limpar_npc_portraits()
    descarregar_items_mod()
    if origem == "VILLAGE":
        descarregar_village_mod(True)
    elif origem == "WILDERNESS":
        limpar_wilderness_bg()
    elif origem == "STING_FOREST":
        limpar_sting_forest_bg()
    elif origem == "CAVE_ENTRANCE":
        limpar_cave_entrance_bg()
    elif origem == "DUNGEON":
        limpar_bgs_dungeon(True)
    if "status" in sys.modules:
        del sys.modules["status"]
    coletar_gc()

def restaurar_apos_menu():
    descarregar_menu_mod(True)
    limpar_hero_portraits()
    if estado_jogo == "VILLAGE":
        v = carregar_village_mod()
        v.load_assets(GAME_DIR, LOCAL_VILLAGE_ID)
        del v
    elif estado_jogo == "WILDERNESS":
        carregar_wilderness_bg()
    elif estado_jogo == "STING_FOREST":
        carregar_sting_forest_bg()
    elif estado_jogo == "CAVE_ENTRANCE":
        carregar_cave_entrance_bg()
    elif estado_jogo == "DUNGEON":
        carregar_dungeon_mod()
        if DUNGEON_BGS is None:
            carregar_bgs_dungeon()
    coletar_gc()

musicTitle = ()
musicDurations = 0
indice_nota = 0
tempo_ultima_nota = 0
proxima_nota_pronta = True
music_pausada = False
music_pause_elapsed = 0
music_loop = True
sfx_ate = 0
_freq_table = (128,135,143,152,161,170,181,191,203,215,228,241,256,271,287,304,322,341,362,383,406,430,456,483,512,542,574,608,645,683,724,767,812,861,912,966,1024,1084,1149,1217,1290,1366,1448,1534,1625,1722,1824,1933,2048)

def tocar_som_efeito(freq, duracao):
    global sfx_ate, proxima_nota_pronta
    if som_ligado:
        sfx_ate = time.ticks_add(time.ticks_ms(), duracao)
        proxima_nota_pronta = True
        thumby.audio.play(freq, duracao)

def tocar_som_navegacao():
    tocar_som_efeito(520, 35)

def tocar_som_recompensa():
    tocar_som_efeito(880, 90)

def carregar_musica(partitura, bpm, loop=True):
    global musicTitle, musicDurations, indice_nota, tempo_ultima_nota
    global proxima_nota_pronta, music_pausada, sfx_ate, music_loop
    musicTitle = partitura
    musicDurations = int((60000 / bpm) / 4)
    indice_nota = 0
    tempo_ultima_nota = time.ticks_ms()
    proxima_nota_pronta = True
    music_pausada = False
    music_loop = loop
    sfx_ate = 0
    thumby.audio.stop()

def parar_musica_total():
    global musicTitle, musicDurations, indice_nota, tempo_ultima_nota
    global proxima_nota_pronta, music_pausada, music_loop, sfx_ate
    thumby.audio.stop()
    musicTitle = ()
    musicDurations = 0
    indice_nota = 0
    tempo_ultima_nota = 0
    proxima_nota_pronta = False
    music_pausada = False
    music_loop = True
    sfx_ate = 0

def pausar_musica():
    global music_pausada, music_pause_elapsed
    if musicTitle and not music_pausada:
        agora = time.ticks_ms()
        dur = musicTitle[indice_nota][1] * musicDurations
        music_pause_elapsed = time.ticks_diff(agora, tempo_ultima_nota)
        if music_pause_elapsed < 0:
            music_pause_elapsed = 0
        if music_pause_elapsed >= dur:
            music_pause_elapsed = dur - 1
        music_pausada = True
        thumby.audio.stop()

def retomar_musica():
    global music_pausada, tempo_ultima_nota, proxima_nota_pronta, sfx_ate
    if musicTitle and music_pausada:
        tempo_ultima_nota = time.ticks_ms() - music_pause_elapsed
        proxima_nota_pronta = True
        music_pausada = False
        sfx_ate = 0

def atualizar_musica(agora=None):
    global indice_nota, tempo_ultima_nota, proxima_nota_pronta
    global musicTitle, musicDurations
    if not musicTitle or music_pausada:
        return
    if agora is None:
        agora = time.ticks_ms()
    avancos = 0
    while musicTitle:
        dur = musicTitle[indice_nota][1] * musicDurations
        if time.ticks_diff(agora, tempo_ultima_nota) < dur:
            break
        tempo_ultima_nota = time.ticks_add(tempo_ultima_nota, dur)
        indice_nota += 1
        if indice_nota >= len(musicTitle):
            if music_loop:
                indice_nota = 0
            else:
                musicTitle = ()
                musicDurations = 0
                proxima_nota_pronta = False
                thumby.audio.stop()
                return
        proxima_nota_pronta = True
        avancos += 1
        if avancos >= 16:
            tempo_ultima_nota = agora
            break
    if musicTitle and proxima_nota_pronta and time.ticks_diff(sfx_ate, agora) <= 0:
        nota = musicTitle[indice_nota][0]
        if nota != -1 and som_ligado:
            thumby.audio.play(_freq_table[nota + 12] if -12 <= nota < 37 else 440, 99999)
        else:
            thumby.audio.stop()
        proxima_nota_pronta = False

def icone_item_chave(key, default=None):
    if key == "herb":
        return icon_herb
    if key == "weapon" or key == "pickaxe":
        return icon_weapon
    if key == "armor":
        return icon_armor
    if key == "shield":
        return icon_shield
    if key == "stone_tablet":
        return icon_stone_tablet
    if key == "magia":
        return icon_magia
    if key == "strike":
        return icon_strike
    if key == "potion":
        return icon_potion
    return default

def calc_heal_hp(obj):
    return carregar_items_mod().calc_heal_hp(heroi, obj)
def calc_heal_mp(obj):
    return carregar_items_mod().calc_heal_mp(heroi, obj)
def tem_cura_hp(obj):
    return carregar_items_mod().has_heal_hp(obj)
def tem_cura_mp(obj):
    return carregar_items_mod().has_heal_mp(obj)
def cura_bloqueada_por_cheio(obj):
    return carregar_items_mod().heal_blocked(heroi, obj)
def recalcular_atk_total():
    lvl = heroi.get("LVL", 1)
    if lvl < 1:
        lvl = 1
    elif lvl > MAX_LEVEL_MAIN:
        lvl = MAX_LEVEL_MAIN
    w = heroi.get("Weapon", "None")
    bonus = 1 if w == "Short Sword" else (2 if w == "Sword" else 0)
    heroi["ATK"] = LEVEL_ATK_MAIN[lvl - 1] + bonus
def desequipar_slot(slot):
    return carregar_items_mod().desequip_slot(heroi, slot)
def equipar_item_slot(slot, ref):
    carregar_items_mod().equip_item_slot(heroi, slot, ref)
def texto_efeito_equip(slot_key, nome):
    return carregar_items_mod().equip_effect(slot_key, nome)
def adicionar_item_inventario(item):
    return carregar_items_mod().add_to_inventory(heroi, item)
def criar_item_chave(icon_key, nome, qtd=1):
    return carregar_items_mod().make_key_item(icon_key, nome, qtd)
def heroi_tem_item_nome(nome):
    return carregar_items_mod().has_item_name(heroi, nome)

def atualizar_scroll_dialogo(agora):
    global dungeon_dialog_scroll, dungeon_dialog_scroll_timer, dungeon_dialog_auto_ms
    if dungeon_dialog_scroll_max <= 0:
        return
    ms = dungeon_dialog_auto_ms
    if thumby.buttonR.pressed():
        ms = max(8, ms // 3)
    elif thumby.buttonL.pressed():
        ms = DIALOG_SCROLL_SLOW_MS
    dt = time.ticks_diff(agora, dungeon_dialog_scroll_timer)
    if dungeon_dialog_scroll == 0:
        if dt < 500:
            return
        dt -= 500
    elif dungeon_dialog_scroll >= dungeon_dialog_scroll_max:
        if dt < 500:
            return
        dungeon_dialog_scroll = 0
        dungeon_dialog_scroll_timer = agora
        return
    if dt >= ms:
        dungeon_dialog_scroll += dt // ms
        if dungeon_dialog_scroll > dungeon_dialog_scroll_max:
            dungeon_dialog_scroll = dungeon_dialog_scroll_max
        dungeon_dialog_scroll_timer = agora

_last_info_nome = None
_last_info_linhas = None
_last_item_nome = None
_last_item_icone = None
_last_item_linhas = None

def desenhar_info_equip(nome, icone, efeito):
    global _last_info_nome, _last_info_linhas
    fonte_normal()
    if nome != _last_info_nome:
        _last_info_nome = nome
        linhas_cache = wrap_texto_5x7(nome, 58)
        if len(linhas_cache) > 2:
            linhas_cache = linhas_cache[:2]
        _last_info_linhas = linhas_cache
    linhas = _last_info_linhas
    iw, ih = tamanho_icone(icone)
    row_h = ih if ih > FONT_H else FONT_H
    total_h = row_h + 2 + (len(linhas) - 1) * 9 + 9
    y = (40 - total_h) // 2
    if y < 0:
        y = 0
    row_w = iw + 2 + largura_texto_5x7(linhas[0])
    x = (72 - row_w) // 2
    if x < 0:
        x = 0
    desenhar_icone(icone, x, y + (row_h - ih) // 2)
    thumby.display.drawText(linhas[0], x + iw + 2, y + (row_h - FONT_H) // 2, 1)
    y += row_h + 2
    if len(linhas) > 1:
        desenhar_linha_centrada_ou_scroll(linhas[1], y, 68, 1)
        y += 9
    desenhar_linha_centrada_ou_scroll(efeito, y, 68, 1)

def desenhar_dialogo_item_centralizado(nome, icone=None):
    global _last_item_nome, _last_item_icone, _last_item_linhas
    iw, ih = tamanho_icone(icone) if icone is not None else (0, 0)
    if nome != _last_item_nome or icone is not _last_item_icone:
        _last_item_nome = nome
        _last_item_icone = icone
        _last_item_linhas = wrap_texto_5x7(nome, 52 if icone is not None else 68)
    linhas = _last_item_linhas
    line_h = 9
    row_h = ih if ih > FONT_H else FONT_H
    total_h = line_h + 2 + row_h
    if len(linhas) > 1:
        total_h += (len(linhas) - 1) * line_h
    y = (40 - total_h) // 2
    if y < 0:
        y = 0
    desenhar_linhas_centralizadas_5x7(["You Got"], y, line_h)
    y += line_h + 2
    if icone is None:
        desenhar_linhas_centralizadas_5x7(linhas, y, line_h)
        return
    row_w = iw + 2 + largura_texto_5x7(linhas[0])
    x = (72 - row_w) // 2
    if x < 0:
        x = 0
    desenhar_icone(icone, x, y + (row_h - ih) // 2)
    thumby.display.drawText(linhas[0], x + iw + 2, y + (row_h - FONT_H) // 2, 1)
    if len(linhas) > 1:
        desenhar_linhas_centralizadas_5x7(linhas[1:], y + row_h + 1, line_h)

def abrir_item_encontrado(nome, icone, retorno):
    global found_item_name, found_item_icon, found_item_return, estado_jogo
    found_item_name = nome
    found_item_icon = icone
    found_item_return = retorno
    tocar_som_recompensa()
    estado_jogo = "ITEM_FOUND"


def transicao_fechar_preto(ms=8, step=2, musica=True):
    for i in range(0, 22, step):
        thumby.display.drawFilledRectangle(0, 0, 72, i, 0)
        thumby.display.drawFilledRectangle(0, 40 - i, 72, i, 0)
        if musica:
            atualizar_musica(time.ticks_ms())
        thumby.display.update()
        time.sleep(ms / 1000)
    thumby.display.fill(0)
    thumby.display.update()

def transicao_abrir_preto(draw_cb=None, ms=8, step=2, musica=True):
    for i in range(20, -2, -step):
        thumby.display.fill(0)
        if draw_cb:
            draw_cb()
        thumby.display.drawFilledRectangle(0, 0, 72, i, 0)
        thumby.display.drawFilledRectangle(0, 40 - i, 72, i, 0)
        if musica:
            atualizar_musica(time.ticks_ms())
        thumby.display.update()
        time.sleep(ms / 1000)

def desenhar_bg_batalha_atual():
    if bg_batalha_atual is not None:
        thumby.display.blit(bg_batalha_atual, 0, 0, 72, 40, -1, 0, 0)

def desenhar_dungeon_bg_atual():
    if DUNGEON_BGS is None:
        return
    sala = sala_dungeon(dungeon_pos)
    bg = sala[3]
    thumby.display.blit(DUNGEON_BGS[bg] if bg < len(DUNGEON_BGS) else DUNGEON_BGS[0], 0, 0, 72, 40, -1, 0, 0)

def dmap_bit(x, y):
    return 1 << (x + y * dungeon_map_cols)

def dmap_visitado_atual():
    return dungeon_visitado | dmap_bit(dungeon_pos[0], dungeon_pos[1])

def dmap_bounds_visitados(visitado):
    rooms = dungeon_map_rooms
    found = False
    min_y = 0
    max_y = 0
    for i in range(0, len(rooms), 6):
        rx = rooms[i]
        ry = rooms[i + 1]
        if rx >= dungeon_map_cols:
            continue
        if not (visitado & dmap_bit(rx, ry)):
            continue
        if not found:
            min_y = ry
            max_y = ry
            found = True
        else:
            if ry < min_y:
                min_y = ry
            if ry > max_y:
                max_y = ry
    if not found:
        min_y = dungeon_pos[1]
        max_y = dungeon_pos[1]
    return min_y, max_y

def dmap_scroll_limits(visitado):
    min_y, max_y = dmap_bounds_visitados(visitado)
    entry_y = dungeon_map_entry[1]
    center = (DMAP_AREA_H - DMAP_CELL) // 2
    return ((min_y - entry_y) * DMAP_CELL - center,
            (max_y - entry_y) * DMAP_CELL - center)

def dmap_scroll_hero():
    visitado = dmap_visitado_atual()
    entry_y = dungeon_map_entry[1]
    center = (DMAP_AREA_H - DMAP_CELL) // 2
    v = (dungeon_pos[1] - entry_y) * DMAP_CELL - center
    low, high = dmap_scroll_limits(visitado)
    if v < low:
        return low
    if v > high:
        return high
    return v

def dmap_scroll_step(v, d):
    v += d * DMAP_CELL
    low, high = dmap_scroll_limits(dmap_visitado_atual())
    if v < low:
        return low
    if v > high:
        return high
    return v

def dungeon_exits_evento_xy(x, y, exits):
    did = dungeon_id_atual
    if did < 0 or did >= len(DUNGEON_EVENT_OPEN_POS):
        return exits, False
    pos_list = DUNGEON_EVENT_OPEN_POS[did]
    dir_list = DUNGEON_EVENT_OPEN_DIR[did]
    bit_list = DUNGEON_EVENT_OPEN_BIT[did]
    opened = False
    for i in range(len(pos_list)):
        pos = pos_list[i]
        if x == pos[0] and y == pos[1] and (dungeon_events & bit_list[i]):
            d = dir_list[i]
            if d not in exits:
                exits += d
            opened = True
    return exits, opened

def dmap_draw_room(x, y, exits, importante, atual, blink):
    thumby.display.drawRectangle(x, y, 8, 8, 1)
    thumby.display.drawFilledRectangle(x + 1, y + 1, 6, 6, 0)
    if "U" in exits:
        thumby.display.drawLine(x + 2, y, x + 5, y, 0)
    if "D" in exits:
        thumby.display.drawLine(x + 2, y + 7, x + 5, y + 7, 0)
    if "L" in exits:
        thumby.display.drawLine(x, y + 2, x, y + 5, 0)
    if "R" in exits:
        thumby.display.drawLine(x + 7, y + 2, x + 7, y + 5, 0)
    if importante:
        thumby.display.drawFilledRectangle(x + 2, y + 2, 4, 4, 1)
    if atual:
        thumby.display.drawFilledRectangle(x + 3, y + 3, 2, 2, 1 if blink else 0)

def desenhar_menu_mapa_dungeon():
    global mapa_scroll_y
    thumby.display.fill(0)
    visitado = dmap_visitado_atual()
    low, high = dmap_scroll_limits(visitado)
    if mapa_scroll_y < low:
        mapa_scroll_y = low
    elif mapa_scroll_y > high:
        mapa_scroll_y = high
    entry_x = dungeon_map_entry[0]
    entry_y = dungeon_map_entry[1]
    base_y = DMAP_AREA_H - DMAP_CELL
    blink = ((time.ticks_ms() // 180) & 1) == 0
    rooms = dungeon_map_rooms
    for i in range(0, len(rooms), 6):
        rx = rooms[i]
        ry = rooms[i + 1]
        if rx >= dungeon_map_cols:
            continue
        if not (visitado & dmap_bit(rx, ry)):
            continue
        x = rx * DMAP_CELL
        y = base_y - (ry - entry_y) * DMAP_CELL + mapa_scroll_y
        if y < -DMAP_CELL or y >= 40:
            continue
        exits, opened = dungeon_exits_evento_xy(rx, ry, DMAP_EXITS[rooms[i + 2]])
        dmap_draw_room(x, y, exits, bool(rooms[i + 4]) or (rx == entry_x and ry == entry_y),
                       rx == dungeon_pos[0] and ry == dungeon_pos[1], blink)

def ir_menu_dungeon_de_mapa(aba):
    global menu_aba, menu_input_lock, estado_jogo
    menu_aba = aba
    menu_input_lock = 2
    if menu_update_fn is None:
        estado_jogo = "DUNGEON_MENU_LOAD"
    else:
        tocar_som_navegacao()
        estado_jogo = "MENU"
    drenar_botoes()

def atualizar_menu_mapa_dungeon(agora):
    global mapa_scroll_y, mapa_scroll_timer, menu_input_lock, estado_jogo
    desenhar_menu_mapa_dungeon()
    if menu_input_lock > 0:
        menu_input_lock -= 1
        return
    if thumby.buttonB.justPressed():
        mapa_scroll_y = 0
        mapa_scroll_timer = 0
        retomar_musica()
        estado_jogo = "DUNGEON"
        restaurar_apos_menu()
        drenar_botoes()
        return
    if thumby.buttonR.justPressed():
        ir_menu_dungeon_de_mapa(0)
        return
    if thumby.buttonL.justPressed():
        ir_menu_dungeon_de_mapa(3)
        return
    d = 0
    if thumby.buttonD.justPressed():
        d = -1
        mapa_scroll_timer = time.ticks_add(agora, 260)
    elif thumby.buttonU.justPressed():
        d = 1
        mapa_scroll_timer = time.ticks_add(agora, 260)
    elif thumby.buttonD.pressed() and time.ticks_diff(agora, mapa_scroll_timer) >= 0:
        d = -1
        mapa_scroll_timer = time.ticks_add(agora, 120)
    elif thumby.buttonU.pressed() and time.ticks_diff(agora, mapa_scroll_timer) >= 0:
        d = 1
        mapa_scroll_timer = time.ticks_add(agora, 120)
    elif (not thumby.buttonD.pressed()) and (not thumby.buttonU.pressed()):
        mapa_scroll_timer = 0
    if d:
        novo_scroll = dmap_scroll_step(mapa_scroll_y, d)
        if novo_scroll != mapa_scroll_y:
            mapa_scroll_y = novo_scroll
            tocar_som_navegacao()

def drenar_botoes():
    for _ in range(2):
        thumby.buttonA.justPressed(); thumby.buttonB.justPressed()
        thumby.buttonU.justPressed(); thumby.buttonD.justPressed()
        thumby.buttonL.justPressed(); thumby.buttonR.justPressed()

def novo_heroi():
    return {
        "LVL": 1, "XP": 0, "XP_MAX": 3,
        "HP": 7, "HP_MAX": 7, "ATK": 0, "DEF": 0, "MP": 0, "MP_MAX": 0,
        "Gold": 0,
        "StatusBits": 0, "PoisonPower": 0, "PoisonTurns": 0, "PoisonTick": 0,
        "Weapon": "None", "Armor": "None", "Shield": "None",
        "Weapon_icon": "", "Armor_icon": "", "Shield_icon": "",
        "Magias": [],
        "Inventory": []
    }

heroi = novo_heroi()
estado_jogo = "VILLAGE"
estado_jogo_antes_menu = "VILLAGE"
estado_retorno_batalha = "WILDERNESS"
origem_batalha = "WILDERNESS"
menu_aba = 0
stats_pagina = 0
menu_input_lock = 0
items_sel = items_scroll = 0
magic_sel = magic_scroll = 0
equip_sel = 0
equip_modo = False
equip_item_sel = 0
equip_item_scroll = 0
mapa_scroll_x = 0
mapa_scroll_y = 0
mapa_scroll_timer = 0
som_ligado = True
region_id_atual = REGION_FARLILY
wilderness_found_cave = False
wilderness_sel = 0
sting_forest_sel = 0
sting_forest_msg = ""
sting_forest_msg_timer = 0
wilderness_msg = ""
wilderness_msg_timer = 0
cave_entrance_sel = 0
save_prompt_return = "WILDERNESS"
save_prompt_sel = 0
save_msg = ""
save_msg_timer = 0
save_msg_blink_phase = -1
game_over_ready = False
dungeon_id_atual = DUNGEON_ID_WURMS
dungeon_pos = list(DUNGEON_ENTRY_MAIN)
dungeon_visitados = [0] * DUNGEON_STATE_SLOTS
dungeon_items_todos = [0] * DUNGEON_STATE_SLOTS
dungeon_events_todos = [0] * DUNGEON_STATE_SLOTS
dungeon_visitado = 0
dungeon_items_coletados = 0
dungeon_events = 0
dungeon_map_rooms = b""
dungeon_map_entry = DUNGEON_ENTRY_MAIN
dungeon_map_cols = DUNGEON_MAP_COLS_DEFAULT
dungeon_blink = 0
dungeon_blink_on = True
dungeon_dialog_active = False
dungeon_dialog_lines = []
dungeon_dialog_icon = None
dungeon_dialog_iname = ""
dungeon_dialog_scroll = 0
dungeon_dialog_scroll_max = 0
dungeon_dialog_scroll_timer = 0
dungeon_dialog_auto_ms = DIALOG_SCROLL_AUTO_MS
dungeon_dialog_show_name = False
dungeon_dialog_name = HERO_NAME
item_info_icon = icon_potion
item_info_name = ""
item_info_effect = ""
found_item_name = ""
found_item_icon = None
found_item_return = "VILLAGE"
slot_atual = 1
world_flags_extra = 0
novo_jogo_atual = False
def guardar_estado_dungeon_atual():
    if 0 <= dungeon_id_atual < DUNGEON_STATE_SLOTS:
        dungeon_visitados[dungeon_id_atual] = int(dungeon_visitado)
        dungeon_items_todos[dungeon_id_atual] = int(dungeon_items_coletados)
        dungeon_events_todos[dungeon_id_atual] = int(dungeon_events)

def carregar_estado_dungeon(dungeon_id, pos_entrada=True):
    global dungeon_id_atual, dungeon_pos, dungeon_visitado
    global dungeon_items_coletados, dungeon_events, dungeon_map_rooms, dungeon_map_entry
    global dungeon_map_cols
    guardar_estado_dungeon_atual()
    if dungeon_id < 0 or dungeon_id >= DUNGEON_STATE_SLOTS:
        dungeon_id = DUNGEON_ID_WURMS
    d = carregar_dungeon_mod(dungeon_id)
    dungeon_id_atual = dungeon_id
    dungeon_map_rooms = d.DUNGEON_ROOMS
    dungeon_map_entry = d.DUNGEON_ENTRY
    try:
        dungeon_map_cols = d.DUNGEON_MAP_COLS
    except:
        dungeon_map_cols = DUNGEON_MAP_COLS_DEFAULT
    if pos_entrada:
        dungeon_pos = list(d.DUNGEON_ENTRY)
    dungeon_visitado = dungeon_visitados[dungeon_id] | d.entry_bit()
    dungeon_items_coletados = dungeon_items_todos[dungeon_id]
    dungeon_events = dungeon_events_todos[dungeon_id]

def sala_dungeon(pos):
    sala = carregar_dungeon_mod().room_at(pos)
    exits, opened = dungeon_exits_evento_xy(pos[0], pos[1], sala[2])
    if opened:
        return (sala[0], sala[1], exits, sala[3], 0, "", sala[6], sala[7], sala[8])
    return sala

def sala_saida_dungeon(pos):
    return carregar_dungeon_mod().is_exit(pos)

def limpar_dialogo_temp():
    global dungeon_dialog_lines, dungeon_dialog_scroll_max, dungeon_dialog_scroll
    global dungeon_dialog_scroll_timer, dungeon_dialog_auto_ms, dungeon_dialog_icon
    global dungeon_dialog_iname, dungeon_dialog_name
    dungeon_dialog_lines = []
    dungeon_dialog_scroll_max = 0
    dungeon_dialog_scroll = 0
    dungeon_dialog_scroll_timer = 0
    dungeon_dialog_auto_ms = DIALOG_SCROLL_AUTO_MS
    dungeon_dialog_icon = None
    dungeon_dialog_iname = ""
    dungeon_dialog_name = HERO_NAME

def flag_on(flag):
    return (world_flags_extra & flag) != 0

def set_flag(flag):
    global world_flags_extra
    world_flags_extra |= flag

def remover_item_nome(nome):
    inv = heroi["Inventory"]
    for it in inv:
        if it.get("nome", "") == nome:
            if it.get("qtd", 1) > 1:
                it["qtd"] -= 1
            else:
                inv.remove(it)
            return True
    return False

def adicionar_item_id(item_id, qtd=1):
    it = carregar_items_mod().make_item(item_id, qtd)
    adicionar_item_inventario(it)
    descarregar_items_mod()

def salvar_jogo_atual():
    import saveflow
    ok = saveflow.save(globals())
    if "saveflow" in sys.modules:
        del sys.modules["saveflow"]
    coletar_gc()
    return ok

def restaurar_hp_mp_total():
    heroi["HP"] = heroi["HP_MAX"]
    heroi["MP"] = heroi["MP_MAX"]
    curar_status()

def restaurar_hp_total():
    heroi["HP"] = heroi["HP_MAX"]
    curar_status()

def normalizar_status_heroi():
    import status
    status.init(heroi)
    if "status" in sys.modules:
        del sys.modules["status"]
    gc.collect()

def curar_status():
    import status
    status.clear_all(heroi)
    if "status" in sys.modules:
        del sys.modules["status"]
    gc.collect()

def abrir_game_over():
    global estado_jogo, game_over_ready
    parar_musica_total()
    estado_jogo = "GAME_OVER"
    game_over_ready = False

def aplicar_poison_turno():
    import status
    dmg = status.tick(heroi)
    if "status" in sys.modules:
        del sys.modules["status"]
    gc.collect()
    return dmg

def passar_turno_exploracao():
    dmg = aplicar_poison_turno()
    if dmg and heroi["HP"] <= 0:
        abrir_game_over()
    return dmg

def turno_exploracao_ou_gameover():
    passar_turno_exploracao()
    if estado_jogo == "GAME_OVER":
        drenar_botoes()
        return True
    return False

def carregar_jogo_slot(slot):
    import saveflow
    ok = saveflow.load_slot(globals(), slot)
    if "saveflow" in sys.modules:
        del sys.modules["saveflow"]
    coletar_gc()
    return ok

def resetar_estado_novo_jogo(slot=1):
    global heroi, estado_jogo, estado_jogo_antes_menu, estado_retorno_batalha
    global origem_batalha, menu_aba, stats_pagina
    global menu_input_lock, items_sel, items_scroll, magic_sel, magic_scroll
    global equip_sel, equip_modo, equip_item_sel, equip_item_scroll
    global mapa_scroll_x, mapa_scroll_y, mapa_scroll_timer
    global region_id_atual, wilderness_found_cave, wilderness_sel
    global sting_forest_sel, sting_forest_msg, sting_forest_msg_timer
    global wilderness_msg, wilderness_msg_timer, dungeon_id_atual, dungeon_pos
    global dungeon_visitados, dungeon_items_todos, dungeon_events_todos
    global dungeon_visitado, dungeon_items_coletados, dungeon_events
    global dungeon_map_rooms, dungeon_map_entry, dungeon_map_cols
    global dungeon_blink, dungeon_blink_on, dungeon_dialog_active
    global dungeon_dialog_lines, dungeon_dialog_icon
    global dungeon_dialog_iname, dungeon_dialog_scroll, dungeon_dialog_scroll_max
    global dungeon_dialog_scroll_timer, dungeon_dialog_auto_ms
    global dungeon_dialog_show_name
    global dungeon_dialog_name, item_info_icon, item_info_name, item_info_effect
    global found_item_name, found_item_icon, found_item_return
    global bg_batalha_atual, bg_batalha_id, save_prompt_return, save_prompt_sel
    global save_msg, save_msg_timer, save_msg_blink_phase, slot_atual
    global game_over_ready, world_flags_extra, novo_jogo_atual
    slot_atual = slot
    novo_jogo_atual = True
    world_flags_extra = 0
    heroi = novo_heroi()
    estado_jogo = "VILLAGE"
    estado_jogo_antes_menu = "VILLAGE"
    estado_retorno_batalha = "WILDERNESS"
    origem_batalha = "WILDERNESS"
    menu_aba = 0
    stats_pagina = 0
    menu_input_lock = 0
    items_sel = items_scroll = 0
    magic_sel = magic_scroll = 0
    equip_sel = 0
    equip_modo = False
    equip_item_sel = 0
    equip_item_scroll = 0
    mapa_scroll_x = 0
    mapa_scroll_y = 0
    mapa_scroll_timer = 0
    region_id_atual = REGION_FARLILY
    wilderness_found_cave = False
    wilderness_sel = 0
    sting_forest_sel = 0
    sting_forest_msg = ""
    sting_forest_msg_timer = 0
    wilderness_msg = ""
    wilderness_msg_timer = 0
    dungeon_id_atual = DUNGEON_ID_WURMS
    dungeon_pos = list(DUNGEON_ENTRY_MAIN)
    dungeon_visitados = [0] * DUNGEON_STATE_SLOTS
    dungeon_items_todos = [0] * DUNGEON_STATE_SLOTS
    dungeon_events_todos = [0] * DUNGEON_STATE_SLOTS
    dungeon_visitado = 0
    dungeon_items_coletados = 0
    dungeon_events = 0
    dungeon_map_rooms = b""
    dungeon_map_entry = DUNGEON_ENTRY_MAIN
    dungeon_map_cols = DUNGEON_MAP_COLS_DEFAULT
    dungeon_blink = 0
    dungeon_blink_on = True
    dungeon_dialog_active = False
    dungeon_dialog_lines = []
    dungeon_dialog_icon = None
    dungeon_dialog_iname = ""
    dungeon_dialog_scroll = 0
    dungeon_dialog_scroll_max = 0
    dungeon_dialog_scroll_timer = 0
    dungeon_dialog_auto_ms = DIALOG_SCROLL_AUTO_MS
    dungeon_dialog_show_name = False
    dungeon_dialog_name = HERO_NAME
    item_info_icon = icon_potion
    item_info_name = ""
    item_info_effect = ""
    found_item_name = ""
    found_item_icon = None
    found_item_return = "VILLAGE"
    bg_batalha_atual = None
    bg_batalha_id = BG_GRASSLAND
    save_prompt_return = "WILDERNESS"
    save_prompt_sel = 0
    save_msg = ""
    save_msg_timer = 0
    save_msg_blink_phase = -1
    game_over_ready = False

def aplicar_resultado_titulo(resultado):
    global novo_jogo_atual
    acao = 0
    slot = 1
    if resultado:
        acao = resultado[0]
        slot = resultado[1]
    resetar_estado_novo_jogo(slot)
    if acao == 1:
        novo_jogo_atual = False
        carregar_jogo_slot(slot)

def voltar_para_tela_titulo():
    global musicTitle, musicDurations, indice_nota, tempo_ultima_nota
    global proxima_nota_pronta, music_pausada, music_pause_elapsed, music_loop
    global sfx_ate, bg_batalha_atual
    thumby.audio.stop()
    musicTitle = ()
    musicDurations = 0
    indice_nota = 0
    tempo_ultima_nota = 0
    proxima_nota_pronta = True
    music_pausada = False
    music_pause_elapsed = 0
    music_loop = True
    sfx_ate = 0
    bg_batalha_atual = None
    descarregar_menu_mod(True)
    descarregar_battle_mod_total()
    descarregar_items_mod()
    descarregar_saveui_mod(True)
    descarregar_scenes_mod(True)
    descarregar_story_mod(True)
    descarregar_village_mod(True)
    descarregar_dungeon_mod(True)
    limpar_bgs_batalha_mapa(True)
    limpar_bgs_dungeon(True)
    limpar_cave_entrance_bg()
    limpar_wilderness_bg()
    limpar_sting_forest_bg()
    limpar_hero_portraits()
    limpar_npc_portraits()
    coletar_gc()
    import title
    result = title.run(GAME_DIR)
    if "title" in sys.modules:
        del sys.modules["title"]
    del title
    coletar_gc()
    aplicar_resultado_titulo(result)
    del result
    coletar_gc()
    iniciar_estado_atual(True)
    abrir_intro_se_preciso()

def iniciar_estado_atual(reset_scene=False):
    if estado_jogo == "WILDERNESS":
        scene_call("entrar_wilderness", reset_scene)
    elif estado_jogo == "STING_FOREST":
        scene_call("entrar_sting_forest", reset_scene)
    elif estado_jogo == "DUNGEON":
        carregar_estado_dungeon(dungeon_id_atual, False)
        carregar_bgs_dungeon()
        carregar_musica(MUSICA_DUNGEON, 110)
    else:
        entrar_vila(reset_scene)

fonte_normal()
aplicar_resultado_titulo(titulo_result)
del titulo_result
descarregar_items_mod()
iniciar_estado_atual(True)
abrir_intro_se_preciso()

while True:
    agora = time.ticks_ms()
    atualizar_musica(agora)

    if estado_jogo == "VILLAGE":
        v = carregar_village_mod()
        if v.bg is None:
            v.load_assets(GAME_DIR, LOCAL_VILLAGE_ID)
        action = v.update(agora, heroi, icon_seta_esq, icon_seta_dir,
                          SHOP_ICONS, tocar_som_navegacao, tocar_som_efeito)
        if action == v.ACTION_LEAVE:
            if turno_exploracao_ou_gameover():
                continue
            estado_jogo = "TRANSICAO_WILDERNESS_IN"
            drenar_botoes()
        elif action == v.ACTION_TEMPLE:
            story_call("abrir_templo")
            drenar_botoes()
        elif action == v.ACTION_REST_SAVE:
            if not salvar_jogo_atual():
                tocar_som_efeito(120, 120)
        elif action == v.ACTION_MENU:
            pausar_musica()
            estado_jogo = "MENU"
            estado_jogo_antes_menu = "VILLAGE"
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
            v = None
            liberar_assets_para_menu("VILLAGE")
            coletar_gc()
        del v

    elif estado_jogo == "STORY_DIALOG":
        story_call("update_story_dialog", agora)
        if estado_jogo != "STORY_DIALOG":
            descarregar_story_mod(True)

    elif estado_jogo == "WILDERNESS":
        scene_call("update_wilderness", agora)
        if estado_jogo != "WILDERNESS":
            descarregar_scenes_mod(True)

    elif estado_jogo == "STING_FOREST":
        scene_call("update_sting_forest", agora)
        if estado_jogo != "STING_FOREST":
            descarregar_scenes_mod(True)

    elif estado_jogo == "CAVE_ENTRANCE":
        scene_call("update_cave_entrance")
        if estado_jogo != "CAVE_ENTRANCE":
            descarregar_scenes_mod(True)

    elif estado_jogo == "SAVE_PROMPT":
        carregar_saveui_mod().update(globals(), agora)
        if estado_jogo != "SAVE_PROMPT" and estado_jogo != "SAVE_MSG":
            descarregar_saveui_mod(True)

    elif estado_jogo == "SAVE_MSG":
        carregar_saveui_mod().update(globals(), agora)
        if estado_jogo != "SAVE_PROMPT" and estado_jogo != "SAVE_MSG":
            descarregar_saveui_mod(True)

    elif estado_jogo == "GAME_OVER":
        thumby.display.fill(0)
        desenhar_linha_centrada_8x8("GAME OVER", 16, 1)
        if not game_over_ready and (not thumby.buttonA.pressed()) and (not thumby.buttonB.pressed()):
            game_over_ready = True
        elif game_over_ready and (thumby.buttonA.justPressed() or thumby.buttonB.justPressed()):
            voltar_para_tela_titulo()
            drenar_botoes()

    elif estado_jogo == "ITEM_FOUND":
        thumby.display.fill(0)
        desenhar_dialogo_item_centralizado(found_item_name, found_item_icon)
        if thumby.buttonA.justPressed() or thumby.buttonB.justPressed():
            estado_jogo = found_item_return
            drenar_botoes()

    elif estado_jogo == "DIALOGO_ITEM":
        thumby.display.fill(0)
        if hero_portrait is None or hero_portrait_talk is None:
            carregar_hero_portraits()
        atualizar_scroll_dialogo(agora)
        if thumby.buttonB.justPressed():
            dungeon_dialog_scroll = 0
            dungeon_dialog_scroll_timer = agora
        desenhar_dialogo_personagem(dungeon_dialog_lines, dungeon_dialog_scroll,
                                    dungeon_dialog_scroll_max, dungeon_dialog_name,
                                    hero_portrait, hero_portrait_talk, False, False)
        if thumby.buttonA.justPressed():
            limpar_dialogo_temp()
            limpar_hero_portraits()
            estado_jogo = "MENU"
            menu_aba = 3
            menu_input_lock = 2
            drenar_botoes()

    elif estado_jogo == "INFO_EQUIP_ITEM":
        thumby.display.fill(0)
        desenhar_info_equip(item_info_name, item_info_icon, item_info_effect)
        if thumby.buttonA.justPressed():
            descarregar_items_mod()
            estado_jogo = "MENU"
            menu_aba = 3
            menu_input_lock = 2
            drenar_botoes()
        elif thumby.buttonB.justPressed():
            mapa_scroll_x = 0
            mapa_scroll_y = 0
            descarregar_items_mod()
            limpar_hero_portraits()
            retomar_musica()
            estado_jogo = estado_jogo_antes_menu
            restaurar_apos_menu()
            drenar_botoes()

    elif estado_jogo == "TRANSICAO_WILDERNESS_IN":
        transicao_fechar_preto()
        thumby.audio.stop()
        limpar_cave_entrance_bg()
        limpar_sting_forest_bg()
        descarregar_village_mod(True)
        limpar_bgs_batalha_mapa(True)
        limpar_bgs_dungeon(True)
        descarregar_dungeon_mod(True)
        coletar_gc()
        scene_call("entrar_wilderness", True)
        transicao_abrir_preto(draw_wilderness_scene)
        drenar_botoes()

    elif estado_jogo == "TRANSICAO_STING_FOREST_IN":
        transicao_fechar_preto()
        thumby.audio.stop()
        limpar_cave_entrance_bg()
        limpar_wilderness_bg()
        limpar_bgs_batalha_mapa(True)
        limpar_bgs_dungeon(True)
        descarregar_dungeon_mod(True)
        coletar_gc()
        scene_call("entrar_sting_forest", True)
        transicao_abrir_preto(draw_sting_forest_scene)
        drenar_botoes()

    elif estado_jogo == "TRANSICAO_VILLAGE_IN":
        transicao_fechar_preto()
        thumby.audio.stop()
        limpar_cave_entrance_bg()
        limpar_sting_forest_bg()
        limpar_wilderness_bg()
        limpar_bgs_batalha_mapa(True)
        limpar_bgs_dungeon(True)
        descarregar_dungeon_mod(True)
        coletar_gc()
        entrar_vila(True)
        transicao_abrir_preto(None)
        drenar_botoes()

    elif estado_jogo == "TRANSICAO_CAVE_ENTRANCE_IN":
        transicao_fechar_preto()
        limpar_wilderness_bg()
        limpar_sting_forest_bg()
        limpar_bgs_batalha_mapa(True)
        limpar_bgs_dungeon(False)
        coletar_gc()
        scene_call("entrar_cave_entrance", True)
        transicao_abrir_preto(draw_cave_entrance_scene, musica=False)
        drenar_botoes()

    elif estado_jogo == "TRANSICAO_CAVERNA_IN":
        estado_retorno_batalha = "WILDERNESS"
        origem_batalha = "WILDERNESS"
        transicao_fechar_preto()
        thumby.audio.stop()
        limpar_cave_entrance_bg()
        limpar_wilderness_bg()
        limpar_sting_forest_bg()
        descarregar_village_mod(True)
        limpar_bgs_batalha_mapa(True)
        descarregar_battle_mod_total()
        coletar_gc()
        carregar_estado_dungeon(DUNGEON_ID_WURMS, True)
        guardar_estado_dungeon_atual()
        carregar_bgs_dungeon()
        carregar_musica(MUSICA_DUNGEON, 110)
        estado_jogo = "DUNGEON"
        transicao_abrir_preto(desenhar_dungeon_bg_atual)
        drenar_botoes()

    elif estado_jogo == "TRANSICAO_IN":
        tocar_som_efeito(80, 300)
        transicao_fechar_preto()
        thumby.audio.stop()
        limpar_dialogo_temp()
        descarregar_items_mod()
        descarregar_village_mod(True)
        limpar_wilderness_bg()
        limpar_sting_forest_bg()
        limpar_hero_portraits()
        if origem_batalha == "DUNGEON":
            guardar_estado_dungeon_atual()
            limpar_bgs_dungeon(True)
            descarregar_dungeon_mod(True)
        else:
            limpar_bgs_dungeon(True)
            descarregar_dungeon_mod(True)
            carregar_bg_batalha(bg_batalha_id)
        coletar_gc()
        b = carregar_battle_mod()
        if origem_batalha == "DUNGEON":
            b.setar_inimigo(b.sortear_inimigo_dungeon())
        elif origem_batalha == "STING_FOREST":
            b.setar_inimigo(b.sortear_inimigo_sting_forest())
        else:
            b.setar_inimigo(b.sortear_inimigo_mapa())
        b.carregar_assets_batalha()
        coletar_gc()
        if bg_batalha_atual is None:
            carregar_bg_batalha(bg_batalha_id)
        transicao_abrir_preto(desenhar_bg_batalha_atual)
        carregar_musica(MUSICA_BATALHA, 180, False)
        b.iniciar_batalha(heroi)
        del b
        estado_jogo = "BATALHA"
        drenar_botoes()

    elif estado_jogo == "TRANSICAO_OUT":
        transicao_fechar_preto()
        thumby.audio.stop()
        limpar_assets_battle_mod()
        descarregar_battle_mod_total()
        limpar_bgs_batalha_mapa(True)
        guardar_estado_dungeon_atual()
        if origem_batalha == "DUNGEON":
            carregar_dungeon_mod()
            carregar_bgs_dungeon()
            carregar_musica(MUSICA_DUNGEON, 110)
            estado_jogo = "DUNGEON"
            transicao_abrir_preto(desenhar_dungeon_bg_atual)
        elif estado_retorno_batalha == "VILLAGE":
            entrar_vila(True)
            transicao_abrir_preto(None)
        elif estado_retorno_batalha == "STING_FOREST":
            scene_call("entrar_sting_forest", False)
            transicao_abrir_preto(draw_sting_forest_scene)
        else:
            scene_call("entrar_wilderness", False)
            transicao_abrir_preto(draw_wilderness_scene)
        drenar_botoes()

    elif estado_jogo == "BATTLE_FLEE_OUT":
        transicao_fechar_preto(8, 4, False)
        thumby.audio.stop()
        limpar_assets_battle_mod()
        descarregar_battle_mod_total()
        limpar_bgs_batalha_mapa(True)
        if origem_batalha == "DUNGEON":
            carregar_dungeon_mod()
            carregar_bgs_dungeon()
            carregar_musica(MUSICA_DUNGEON, 110)
            estado_jogo = "DUNGEON"
            transicao_abrir_preto(desenhar_dungeon_bg_atual, 8, 4, False)
        elif estado_retorno_batalha == "STING_FOREST":
            scene_call("entrar_sting_forest", False)
            transicao_abrir_preto(draw_sting_forest_scene, 8, 4, False)
        else:
            scene_call("entrar_wilderness", False)
            transicao_abrir_preto(draw_wilderness_scene, 8, 4, False)
        drenar_botoes()

    elif estado_jogo == "DUNGEON":
        carregar_dungeon_mod().update_scene(globals(), agora)
        if estado_jogo != "DUNGEON":
            limpar_bgs_dungeon(True)
            coletar_gc()

    elif estado_jogo == "DUNGEON_MENU_PREP":
        liberar_assets_para_menu("DUNGEON")
        descarregar_dungeon_mod(True)
        mapa_scroll_y = dmap_scroll_hero()
        desenhar_menu_mapa_dungeon()
        thumby.display.update()
        estado_jogo = "DUNGEON_MENU_PREP_LOAD"

    elif estado_jogo == "DUNGEON_MENU_PREP_LOAD":
        carregar_menu_dungeon_abas()
        coletar_gc()
        estado_jogo = "DUNGEON_MAP_MENU"

    elif estado_jogo == "DUNGEON_MAP_MENU":
        atualizar_menu_mapa_dungeon(agora)

    elif estado_jogo == "DUNGEON_MENU_LOAD":
        desenhar_menu_mapa_dungeon()
        thumby.display.update()
        carregar_menu_dungeon_abas()
        coletar_gc()
        tocar_som_navegacao()
        estado_jogo = "MENU"
        drenar_botoes()

    elif estado_jogo == "MENU":
        carregar_menu_mod()(globals(), agora)
        if estado_jogo != "MENU" and estado_jogo != "DUNGEON_MAP_MENU":
            restaurar_apos_menu()

    elif estado_jogo == "BATALHA":
        if bg_batalha_atual is None:
            carregar_bg_batalha(bg_batalha_id)
        prox = carregar_battle_mod().update(agora, heroi, bg_batalha_atual,
            tocar_som_efeito, tocar_som_navegacao, carregar_musica,
            MUSICA_VITORIA, MUSICA_DERROTA)
        if prox:
            if prox == "TITLE":
                voltar_para_tela_titulo()
                continue
            descarregar_battle_mod_total()
            estado_jogo = prox

    thumby.display.update()
