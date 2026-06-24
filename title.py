import thumby, time, gc

FONT_8X8 = "/lib/font8x8.bin"
MUSIC = (
    (256,4),(323,4),(384,4),(512,6),(483,2),
    (431,4),(384,4),(323,4),(384,4),(512,8),
    (575,4),(645,4),(767,8),(645,4),(575,4),
    (512,8),(384,4),(431,4),(483,4),(512,12)
)
ACTION_NEW = 0
ACTION_LOAD = 1
SLOT_COUNT = 3
SCREEN_TITLE = 0
SCREEN_FILES = 1
SCREEN_ERASE = 2
EFFECTS_BIN = "effects.bin"
TITLE_LOGO_BYTES = 210
TITLE_LOGO_OFFSET = 0
TITLE_LOGO_MASK_OFFSET = TITLE_LOGO_BYTES

def read_file_into(path, offset, data):
    f = open(path, "rb")
    try:
        f.seek(offset)
        try:
            _n = f.readinto(data)
            if _n is not None and _n < len(data):
                for _i in range(_n, len(data)):
                    data[_i] = 0
        except AttributeError:
            _raw = f.read(len(data))
            _n = len(_raw)
            for _i in range(_n):
                data[_i] = _raw[_i]
            for _i in range(_n, len(data)):
                data[_i] = 0
    finally:
        f.close()

def load_pack(path, offset, tamanho):
    data = bytearray(tamanho)
    read_file_into(path, offset, data)
    return data

def unload_saves(_saves):
    import sys
    if "saves" in sys.modules:
        del sys.modules["saves"]
    del sys
    del _saves
    gc.collect()

def read_save_summary(game_dir, slot):
    import saves
    try:
        return saves.summary_or_none(game_dir, slot)
    finally:
        unload_saves(saves)

def read_slot_summaries(game_dir):
    import saves
    try:
        return saves.summaries(game_dir)
    finally:
        unload_saves(saves)

def has_any_save(summaries):
    return summaries[0] is not None or summaries[1] is not None or summaries[2] is not None

def count_saves(summaries):
    return (1 if summaries[0] is not None else 0) + (1 if summaries[1] is not None else 0) + (1 if summaries[2] is not None else 0)

def first_save_slot(summaries):
    for i in range(SLOT_COUNT):
        if summaries[i] is not None:
            return i + 1
    return 1

def set_summary(summaries, idx, value):
    data = [summaries[0], summaries[1], summaries[2]]
    data[idx] = value
    return (data[0], data[1], data[2])

def delete_save_file(game_dir, slot):
    import saves
    try:
        return saves.delete(game_dir, slot)
    except Exception:
        return False
    finally:
        unload_saves(saves)

def drain_buttons():
    for _ in range(2):
        thumby.buttonA.justPressed(); thumby.buttonB.justPressed()
        thumby.buttonU.justPressed(); thumby.buttonD.justPressed()
        thumby.buttonL.justPressed(); thumby.buttonR.justPressed()

def draw_round_rect(x, y, w, h):
    thumby.display.drawFilledRectangle(x, y, w, h, 1)
    thumby.display.drawFilledRectangle(x, y, 1, 1, 0)
    thumby.display.drawFilledRectangle(x + w - 1, y, 1, 1, 0)
    thumby.display.drawFilledRectangle(x, y + h - 1, 1, 1, 0)
    thumby.display.drawFilledRectangle(x + w - 1, y + h - 1, 1, 1, 0)

def draw_selected_text_8(text, y):
    tw = len(text) * 8
    bw = tw + 4
    if bw > 72:
        bw = 72
    bx = (72 - bw) // 2
    tx = (72 - tw) // 2
    if tx < 0:
        tx = 0
    draw_round_rect(bx, y - 1, bw, 10)
    thumby.display.setFont(FONT_8X8, 8, 8, 0)
    thumby.display.drawText(text, tx, y, 0)

def draw_selected_text_8_at(text, x, y):
    tw = len(text) * 8
    bx = x - 2
    bw = tw + 4
    if bx < 0:
        bx = 0
    if bx + bw > 72:
        bw = 72 - bx
    draw_round_rect(bx, y - 1, bw, 10)
    thumby.display.setFont(FONT_8X8, 8, 8, 0)
    thumby.display.drawText(text, x, y, 0)

def draw_title(logo, logo_mask, sel, agora, can_continue):
    thumby.display.fill(0)
    bob = 0
    thumby.display.blit(logo_mask, 1, bob, 70, 21, 0, 0, 0)
    thumby.display.blit(logo,      1, bob, 70, 21, 1, 0, 0)
    thumby.display.setFont(FONT_8X8, 8, 8, 0)
    if sel == 0:
        draw_selected_text_8("CONTINUE", 22)
        draw_text_centered_8("START", 31, 1)
    else:
        draw_text_centered_8("CONTINUE", 22, 1)
        draw_selected_text_8("START", 31)

def draw_text_centered_8(text, y, color):
    x = (72 - len(text) * 8) // 2
    if x < 0: x = 0
    thumby.display.setFont(FONT_8X8, 8, 8, 0)
    thumby.display.drawText(text, x, y, color)

def slot_available(mode, summaries, idx):
    return mode == ACTION_NEW or summaries[idx] is not None

def move_slot(sel, summaries, mode, step):
    for _ in range(SLOT_COUNT):
        sel = (sel + step) % SLOT_COUNT
        if slot_available(mode, summaries, sel):
            return sel
    return sel

def summary_text(summary):
    lvl = str(summary[0])
    hp = str(summary[1])
    txt = "LV " + lvl + " HP " + hp
    if len(txt) <= 9:
        return txt
    return "LV" + lvl + " HP" + hp

def draw_slots(summaries, mode, sel):
    thumby.display.fill(0)
    for i in range(SLOT_COUNT):
        y = 5 + i * 11
        slot = i + 1
        summary = summaries[i]
        if mode == ACTION_LOAD and summary is None:
            continue
        if summary is None:
            if i == sel:
                draw_selected_text_8("FILE " + str(slot), y)
            else:
                draw_text_centered_8("FILE " + str(slot), y, 1)
        else:
            if i == sel:
                draw_selected_text_8(summary_text(summary), y)
            else:
                draw_text_centered_8(summary_text(summary), y, 1)

def draw_erase_confirm(sel, slot):
    thumby.display.fill(0)
    draw_text_centered_8("ERASE", 1, 1)
    draw_text_centered_8("FILE " + str(slot) + "?", 11, 1)
    if sel == 0:
        draw_selected_text_8_at("YES", 10, 28)
        thumby.display.drawText("NO", 47, 28, 1)
    else:
        thumby.display.drawText("YES", 10, 28, 1)
        draw_selected_text_8_at("NO", 47, 28)

def run(game_dir):
    gfx = game_dir + "/gfx/"
    effects_path = gfx + EFFECTS_BIN
    logo = load_pack(effects_path, TITLE_LOGO_OFFSET, TITLE_LOGO_BYTES)
    logo_mask = load_pack(effects_path, TITLE_LOGO_MASK_OFFSET, TITLE_LOGO_BYTES)
    mode = ACTION_NEW
    slot_summaries = read_slot_summaries(game_dir)
    sel = 0 if has_any_save(slot_summaries) else 1
    screen = SCREEN_TITLE
    erase_sel = 1
    idx = 0
    bpm_ms = int((60000 / 170) / 4)
    last_note = time.ticks_ms()
    sfx_ate = 0
    playing_idx = 0
    thumby.audio.stop()
    thumby.audio.play(MUSIC[0][0], 99999)
    while True:
        agora = time.ticks_ms()
        while time.ticks_diff(agora, last_note) >= MUSIC[idx][1] * bpm_ms:
            last_note = time.ticks_add(last_note, MUSIC[idx][1] * bpm_ms)
            idx = (idx + 1) % len(MUSIC)
        if time.ticks_diff(sfx_ate, agora) > 0:
            playing_idx = -1
        elif playing_idx != idx:
            thumby.audio.play(MUSIC[idx][0], 99999)
            playing_idx = idx
        if screen == SCREEN_TITLE:
            can_continue = has_any_save(slot_summaries)
            draw_title(logo, logo_mask, sel, agora, can_continue)
            if thumby.buttonU.justPressed() or thumby.buttonD.justPressed() or thumby.buttonL.justPressed() or thumby.buttonR.justPressed():
                sel = 1 - sel
            if thumby.buttonA.justPressed():
                slot_summaries = read_slot_summaries(game_dir)
                can_continue = has_any_save(slot_summaries)
                if sel == 0:
                    if not can_continue:
                        pass
                    elif count_saves(slot_summaries) == 1:
                        thumby.audio.stop()
                        logo = None
                        logo_mask = None
                        gc.collect()
                        drain_buttons()
                        return (ACTION_LOAD, first_save_slot(slot_summaries))
                    else:
                        mode = ACTION_LOAD
                        sel = 0
                        while slot_summaries[sel] is None:
                            sel += 1
                        screen = SCREEN_FILES
                        drain_buttons()
                else:
                    mode = ACTION_NEW
                    sel = 0
                    screen = SCREEN_FILES
                    drain_buttons()
        elif screen == SCREEN_FILES:
            draw_slots(slot_summaries, mode, sel)
            if thumby.buttonD.justPressed() or thumby.buttonR.justPressed():
                sel = move_slot(sel, slot_summaries, mode, 1)
            if thumby.buttonU.justPressed() or thumby.buttonL.justPressed():
                sel = move_slot(sel, slot_summaries, mode, -1)
            if thumby.buttonB.justPressed():
                sel = 0 if has_any_save(slot_summaries) else 1
                screen = SCREEN_TITLE
                drain_buttons()
            if thumby.buttonA.justPressed():
                slot = sel + 1
                if mode == ACTION_NEW and slot_summaries[sel] is not None:
                    erase_sel = 1
                    screen = SCREEN_ERASE
                    drain_buttons()
                elif slot_available(mode, slot_summaries, sel):
                    thumby.audio.stop()
                    logo = None
                    logo_mask = None
                    gc.collect()
                    drain_buttons()
                    return (mode, slot)
                else:
                    sfx_ate = time.ticks_add(agora, 80)
                    thumby.audio.play(120, 80)
        else:
            draw_erase_confirm(erase_sel, sel + 1)
            if thumby.buttonL.justPressed() or thumby.buttonR.justPressed() or thumby.buttonU.justPressed() or thumby.buttonD.justPressed():
                erase_sel = 1 - erase_sel
            if thumby.buttonB.justPressed():
                screen = SCREEN_FILES
                drain_buttons()
            if thumby.buttonA.justPressed():
                if erase_sel == 0:
                    if delete_save_file(game_dir, sel + 1):
                        slot_summaries = set_summary(slot_summaries, sel, None)
                    screen = SCREEN_FILES
                else:
                    screen = SCREEN_FILES
                drain_buttons()
        thumby.display.update()
