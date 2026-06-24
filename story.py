# Story and quest dialogue engine loaded only while story dialogue is active.

story_lines = ()
story_idx = 0
story_scroll = 0
story_scroll_max = 0
story_scroll_timer = 0
story_return = "VILLAGE"
story_action = 0
story_portrait_idx = 1
STORY_NONE = 0
STORY_INTRO = 1
STORY_TEMPLE_SWORD = 2
STORY_TEMPLE_REQUEST = 3
STORY_TEMPLE_RELIC = 4

INTRO_LINES = (
    "You haven't paid rent in a long time.",
    "There's nothing I can do, I need to kick you out.",
    "Perhaps praying in the temple will bring you some enlightenment. Goodbye!",
)
TEMPLE_SWORD_LINES = (
    "Ah, my child, we are so small before the greater divinity.",
    "Don't let the world's tribulations disturb you; conquer your freedom.",
    "Grab this sword, defeat the evil creatures, and grow stronger and stronger!",
    "Now go!",
)
TEMPLE_REQUEST_LINES = (
    "Warrior! Listen... There's a cave nearby, full of wurms.",
    "It is said that an ancient relic is hidden there.",
    "Would you be able to retrieve it for me?",
)
TEMPLE_REPEAT_LINES = ("Retrieve the ancient relic in the wurms' cave.",)
TEMPLE_RELIC_LINES = (
    "Ah, wonderful! That's it! Thank you my child!",
    "Please accept these Bits as a token of gratitude.",
)
TEMPLE_DONE_LINES = ("I'm studying that stone tablet, it's fascinating!",)
TEMPLE_REWARD_BITS = 20


def _story_prepare_line():
    global story_scroll_max, story_scroll, story_scroll_timer
    line = story_lines[story_idx] if story_idx < len(story_lines) else ""
    _, story_scroll_max = preparar_dialogo_personagem(line)
    story_scroll = 0
    story_scroll_timer = time.ticks_ms()

def iniciar_dialogo_story(lines, action=STORY_NONE, portrait_idx=1, pause_music=False):
    global story_lines, story_idx, story_return, story_action, story_portrait_idx
    global estado_jogo
    story_lines = lines
    story_idx = 0
    story_return = "VILLAGE"
    story_action = action
    story_portrait_idx = portrait_idx
    if pause_music:
        pausar_musica()
    carregar_npc_portraits(portrait_idx)
    _story_prepare_line()
    estado_jogo = "STORY_DIALOG"

def finalizar_dialogo_story():
    global estado_jogo
    reward_name = ""
    reward_icon = None
    if story_action == STORY_INTRO:
        set_flag(WORLD_FLAG_INTRO_DONE)
    elif story_action == STORY_TEMPLE_SWORD:
        adicionar_item_id(carregar_items_mod().ITEM_SHORT_SWORD, 1)
        descarregar_items_mod()
        set_flag(WORLD_FLAG_TEMPLE_SWORD)
        reward_name = "Short Sword"
        reward_icon = icon_weapon
    elif story_action == STORY_TEMPLE_REQUEST:
        set_flag(WORLD_FLAG_TEMPLE_REQUEST)
    elif story_action == STORY_TEMPLE_RELIC:
        remover_item_nome("Stone Tablet")
        heroi["Gold"] = heroi.get("Gold", 0) + TEMPLE_REWARD_BITS
        set_flag(WORLD_FLAG_TEMPLE_RELIC)
        reward_name = str(TEMPLE_REWARD_BITS) + " Bits"
        reward_icon = icon_gold
    limpar_npc_portraits()
    retomar_musica()
    if reward_name:
        abrir_item_encontrado(reward_name, reward_icon, story_return)
    else:
        estado_jogo = story_return

def atualizar_scroll_story(agora):
    global story_scroll, story_scroll_timer
    if story_scroll_max <= 0:
        return
    ms = DIALOG_SCROLL_AUTO_MS
    if thumby.buttonR.pressed():
        ms = max(8, ms // 3)
    elif thumby.buttonL.pressed():
        ms = DIALOG_SCROLL_SLOW_MS
    dt = time.ticks_diff(agora, story_scroll_timer)
    if story_scroll == 0:
        if dt < 500:
            return
        dt -= 500
    elif story_scroll >= story_scroll_max:
        if dt < 500:
            return
        story_scroll = 0
        story_scroll_timer = agora
        return
    if dt >= ms:
        story_scroll += dt // ms
        if story_scroll > story_scroll_max:
            story_scroll = story_scroll_max
        story_scroll_timer = agora

def desenhar_village_bg_se_possivel():
    if village_mod is not None and getattr(village_mod, "bg", None) is not None:
        thumby.display.blit(village_mod.bg, 0, 0, 72, 40, -1, 0, 0)
    else:
        thumby.display.fill(0)

def update_story_dialog(agora):
    global story_idx, story_scroll, story_scroll_timer
    desenhar_village_bg_se_possivel()
    atualizar_scroll_story(agora)
    if thumby.buttonB.justPressed():
        story_scroll = 0
    line = story_lines[story_idx] if story_idx < len(story_lines) else ""
    desenhar_dialogo_personagem((line,), story_scroll, story_scroll_max, "",
                                npc_portrait, npc_portrait_talk, False, False)
    if thumby.buttonA.justPressed():
        story_idx += 1
        if story_idx >= len(story_lines):
            finalizar_dialogo_story()
        else:
            _story_prepare_line()
        drenar_botoes()

def abrir_intro_inicial_se_preciso():
    if novo_jogo_atual and not flag_on(WORLD_FLAG_INTRO_DONE):
        iniciar_dialogo_story(INTRO_LINES, STORY_INTRO, 1, False)

def abrir_templo():
    tem_stone = heroi_tem_item_nome("Stone Tablet")
    descarregar_items_mod()
    if tem_stone and flag_on(WORLD_FLAG_TEMPLE_SWORD) and not flag_on(WORLD_FLAG_TEMPLE_RELIC):
        iniciar_dialogo_story(TEMPLE_RELIC_LINES, STORY_TEMPLE_RELIC, 2, True)
    elif flag_on(WORLD_FLAG_TEMPLE_RELIC):
        iniciar_dialogo_story(TEMPLE_DONE_LINES, STORY_NONE, 2, True)
    elif not flag_on(WORLD_FLAG_TEMPLE_SWORD):
        iniciar_dialogo_story(TEMPLE_SWORD_LINES, STORY_TEMPLE_SWORD, 2, True)
    elif not flag_on(WORLD_FLAG_TEMPLE_REQUEST):
        iniciar_dialogo_story(TEMPLE_REQUEST_LINES, STORY_TEMPLE_REQUEST, 2, True)
    else:
        iniciar_dialogo_story(TEMPLE_REPEAT_LINES, STORY_NONE, 2, True)


_SYNC_KEYS = ("estado_jogo", "story_return")

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
