import thumby, time
from ui import (
    fonte_normal, fonte_grande, desenhar_linha_centrada_8x8,
    desenhar_texto_selecionado_8x8)

_SYNC_KEYS = (
    "estado_jogo", "save_prompt_sel", "save_msg", "save_msg_timer",
    "save_msg_blink_phase",
)

def _bind(ctx):
    g = globals()
    for k in ctx:
        if not k.startswith("_"):
            g[k] = ctx[k]

def _sync(ctx):
    g = globals()
    for k in _SYNC_KEYS:
        if k in g:
            ctx[k] = g[k]

def _draw_prompt():
    thumby.display.fill(0)
    desenhar_linha_centrada_8x8("SAVE AND", 1, 1)
    desenhar_linha_centrada_8x8("REST?", 11, 1)
    if save_prompt_sel == 0:
        desenhar_texto_selecionado_8x8("YES", 10, 28)
        fonte_grande()
        thumby.display.drawText("NO", 47, 28, 1)
    else:
        fonte_grande()
        thumby.display.drawText("YES", 10, 28, 1)
        desenhar_texto_selecionado_8x8("NO", 47, 28)
    fonte_normal()

def _draw_msg():
    thumby.display.fill(0)
    if save_msg == "SAVED" and ((time.ticks_ms() // 80) & 1):
        return
    desenhar_linha_centrada_8x8(save_msg, 16, 1)

def _sound_msg(agora):
    global save_msg_blink_phase
    if save_msg != "SAVED":
        return
    phase = (agora // 80) & 1
    if phase != save_msg_blink_phase:
        save_msg_blink_phase = phase
        if phase == 0:
            tocar_som_efeito(760 + ((agora // 160) & 1) * 120, 35)

def update(ctx, agora):
    global save_prompt_sel, save_msg, save_msg_timer, save_msg_blink_phase
    global estado_jogo
    _bind(ctx)
    if estado_jogo == "SAVE_PROMPT":
        _draw_prompt()
        if thumby.buttonL.justPressed() or thumby.buttonR.justPressed() or thumby.buttonU.justPressed() or thumby.buttonD.justPressed():
            save_prompt_sel = 1 - save_prompt_sel
            tocar_som_navegacao()
        if thumby.buttonB.justPressed():
            estado_jogo = save_prompt_return
            drenar_botoes()
        elif thumby.buttonA.justPressed():
            if save_prompt_sel == 0:
                if save_prompt_return == "WILDERNESS" or save_prompt_return == "STING_FOREST":
                    restaurar_hp_total()
                else:
                    restaurar_hp_mp_total()
                if salvar_jogo_atual():
                    save_msg = "SAVED"
                    save_msg_blink_phase = -1
                else:
                    save_msg = "ERROR"
                    tocar_som_efeito(120, 120)
                save_msg_timer = time.ticks_add(agora, 900)
                estado_jogo = "SAVE_MSG"
            else:
                estado_jogo = save_prompt_return
            drenar_botoes()
    else:
        _draw_msg()
        _sound_msg(agora)
        if thumby.buttonA.justPressed() or thumby.buttonB.justPressed() or time.ticks_diff(agora, save_msg_timer) >= 0:
            estado_jogo = save_prompt_return
            drenar_botoes()
    _sync(ctx)
