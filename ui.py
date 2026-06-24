import thumby, time
FONT_5X7 = "/lib/font5x7.bin"
FONT_3X5 = "/lib/font3x5.bin"
FONT_8X8 = "/lib/font8x8.bin"
FONT_W = 5
FONT_H = 7
FONT_SPACING = 1
FONT_STEP = FONT_W + FONT_SPACING
DIALOG_SCROLL_AUTO_MS = 18
DIALOG_SCROLL_SLOW_MS = 48
TEXT_SCROLL_PIXEL_MS = 85
TEXT_SCROLL_START_MS = 850
TEXT_SCROLL_END_MS = 950

def fonte_normal():
    thumby.display.setFont(FONT_5X7, 5, 7, 1)
def fonte_grande():
    thumby.display.setFont(FONT_8X8, 8, 8, 0)
def largura_texto_8x8(texto):
    return len(texto) * 8 if texto else 0
def desenhar_linha_centrada_8x8(texto, y, cor=1):
    fonte_grande()
    x = (72 - largura_texto_8x8(texto)) // 2
    if x < 0: x = 0
    thumby.display.drawText(texto, x, y, cor)
def desenhar_texto_contornado_8x8(texto, x, y):
    fonte_grande()
    thumby.display.drawText(texto, x-2, y, 0)
    thumby.display.drawText(texto, x+2, y, 0)
    thumby.display.drawText(texto, x, y-2, 0)
    thumby.display.drawText(texto, x, y+2, 0)
    thumby.display.drawText(texto, x-1, y-1, 0)
    thumby.display.drawText(texto, x+1, y-1, 0)
    thumby.display.drawText(texto, x-1, y+1, 0)
    thumby.display.drawText(texto, x+1, y+1, 0)
    thumby.display.drawText(texto, x, y, 1)
def desenhar_texto_centralizado_contornado_8x8(texto, y):
    if not texto:
        return
    x = (72 - largura_texto_8x8(texto)) // 2
    if x < 0: x = 0
    desenhar_texto_contornado_8x8(texto, x, y)
def desenhar_retangulo_selecao(x, y, w, h):
    thumby.display.drawFilledRectangle(x, y, w, h, 1)
    thumby.display.drawFilledRectangle(x, y, 1, 1, 0)
    thumby.display.drawFilledRectangle(x+w-1, y, 1, 1, 0)
    thumby.display.drawFilledRectangle(x, y+h-1, 1, 1, 0)
    thumby.display.drawFilledRectangle(x+w-1, y+h-1, 1, 1, 0)
def desenhar_texto_selecionado_8x8(texto, x, y):
    w = largura_texto_8x8(texto)
    bx = x - 2
    bw = w + 4
    if bx < 0: bx = 0
    if bx + bw > 72: bw = 72 - bx
    desenhar_retangulo_selecao(bx, y-1, bw, 10)
    fonte_grande()
    thumby.display.drawText(texto, x, y, 0)
def tamanho_icone(icone):
    if len(icone) == 8: return 8, 8
    if len(icone) == 7: return 7, 7
    if len(icone) == 5: return 5, 7
    if len(icone) == 3: return 3, 7
    return 8, 8
def desenhar_icone(icone, x, y):
    iw, ih = tamanho_icone(icone)
    thumby.display.blit(icone, x, y, iw, ih, -1, 0, 0)
def desenhar_icone_contornado(icone, x, y):
    iw, ih = tamanho_icone(icone)
    thumby.display.drawFilledRectangle(x-2, y-2, iw+4, ih+4, 0)
    desenhar_icone(icone, x, y)
def largura_texto_5x7(texto):
    if not texto: return 0
    return len(texto) * FONT_STEP - FONT_SPACING
def wrap_texto_5x7(texto, max_px=68):
    max_chars = max(1, (max_px + FONT_SPACING) // FONT_STEP)
    linhas = []
    for bloco in texto.split("\n"):
        palavras = bloco.split(" ")
        linha = ""
        for palavra in palavras:
            teste = palavra if not linha else linha + " " + palavra
            if len(teste) <= max_chars:
                linha = teste
            else:
                if linha:
                    linhas.append(linha)
                while len(palavra) > max_chars:
                    linhas.append(palavra[:max_chars])
                    palavra = palavra[max_chars:]
                linha = palavra
        if linha:
            linhas.append(linha)
    return linhas if linhas else [""]
def texto_scroll_offset_por_largura(largura, max_px):
    if largura <= max_px:
        return 0
    max_shift = largura - max_px
    pausa_ini = max(1, TEXT_SCROLL_START_MS // TEXT_SCROLL_PIXEL_MS)
    pausa_fim = max(1, TEXT_SCROLL_END_MS // TEXT_SCROLL_PIXEL_MS)
    total = pausa_ini + max_shift + pausa_fim + max_shift
    passo = (time.ticks_ms() // TEXT_SCROLL_PIXEL_MS) % total
    if passo < pausa_ini:
        return 0
    passo -= pausa_ini
    if passo < max_shift:
        return passo
    passo -= max_shift
    if passo < pausa_fim:
        return max_shift
    passo -= pausa_fim
    return max_shift - passo
def texto_scroll_offset_px(texto, max_px):
    return texto_scroll_offset_por_largura(largura_texto_5x7(texto), max_px)
def desenhar_texto_scroll(texto, x, y, max_px, cor=1):
    if not texto: return
    largura = largura_texto_5x7(texto)
    if largura <= max_px:
        thumby.display.drawText(texto, x, y, cor)
        return
    shift = texto_scroll_offset_px(texto, max_px)
    char_ini = shift // FONT_STEP
    pixel_off = shift % FONT_STEP
    max_chars = max(1, (max_px + FONT_SPACING) // FONT_STEP)
    if pixel_off > 0:
        max_chars += 1
    thumby.display.drawText(texto[char_ini:char_ini+max_chars], x - pixel_off, y, cor)
def desenhar_linha_centrada_ou_scroll(texto, y, max_px=68, cor=1):
    largura = largura_texto_5x7(texto)
    if largura <= max_px:
        thumby.display.drawText(texto, (72-largura)//2, y, cor)
    else:
        desenhar_texto_scroll(texto, (72-max_px)//2, y, max_px, cor)
def desenhar_texto_janela_com_shift(texto, x, y, max_px, shift, cor=1):
    if not texto:
        return
    char_ini = shift // FONT_STEP
    pixel_off = shift % FONT_STEP
    max_chars = max(1, (max_px + FONT_SPACING) // FONT_STEP)
    if pixel_off > 0:
        max_chars += 1
    thumby.display.drawText(texto[char_ini:char_ini+max_chars], x - pixel_off, y, cor)
def largura_texto_dialogo_8x8(texto):
    if not texto: return 0
    return len(texto) * 8
def desenhar_texto_dialogo_8x8_shift(texto, x, y, max_px, shift, cor=0):
    if not texto:
        return
    fonte_grande()
    char_step = 8
    char_ini = shift // char_step
    pixel_off = shift % char_step
    max_chars = max(1, max_px // char_step)
    if pixel_off > 0:
        max_chars += 1
    thumby.display.drawText(texto[char_ini:char_ini+max_chars], x - pixel_off, y, cor)
def preparar_dialogo_personagem(texto):
    texto_w = 68
    return [texto], max(0, largura_texto_dialogo_8x8(texto) - texto_w)
def desenhar_dialogo_personagem(linhas, scroll_px=0, max_shift=0, nome="THUMBOR", portrait1=None, portrait2=None, show_name=True, portrait_right=False):
    agora = time.ticks_ms()
    portrait_atual = portrait1 if (agora // 500) % 2 == 0 else portrait2
    texto = linhas[0] if linhas else ""
    if scroll_px < 0: scroll_px = 0
    if scroll_px > max_shift: scroll_px = max_shift
    bx = 0; by = 0; bw = 72; bh = 15
    thumby.display.drawFilledRectangle(bx, by, bw, bh, 0)
    thumby.display.drawFilledRectangle(bx+1, by+1, bw-2, bh-2, 1)
    thumby.display.drawFilledRectangle(bx+1, by+1, 1, 1, 0)
    thumby.display.drawFilledRectangle(bx+bw-2, by+1, 1, 1, 0)
    thumby.display.drawFilledRectangle(bx+1, by+bh-2, 1, 1, 0)
    thumby.display.drawFilledRectangle(bx+bw-2, by+bh-2, 1, 1, 0)
    desenhar_texto_dialogo_8x8_shift(texto, 2, by+4, 68, scroll_px, 0)
    thumby.display.drawRectangle(bx, by, bw, bh, 0)
    thumby.display.drawFilledRectangle(bx+1, by+1, 1, 1, 0)
    thumby.display.drawFilledRectangle(bx+bw-2, by+1, 1, 1, 0)
    thumby.display.drawFilledRectangle(bx+1, by+bh-2, 1, 1, 0)
    thumby.display.drawFilledRectangle(bx+bw-2, by+bh-2, 1, 1, 0)
    if portrait_atual is not None:
        thumby.display.blit(portrait_atual, 2, 16, 24, 24, -1, 0, 0)
    if show_name:
        thumby.display.setFont(FONT_3X5, 3, 5, 1)
        thumby.display.drawFilledRectangle(27, 16, 45, 7, 0)
        thumby.display.drawText(nome.upper(), 29, 17, 1)
    fonte_normal()
def desenhar_linhas_centralizadas_5x7(linhas, y_ini, line_h=9):
    for i, linha in enumerate(linhas):
        x = (72 - largura_texto_5x7(linha)) // 2
        if x < 0: x = 0
        thumby.display.drawText(linha, x, y_ini + i * line_h, 1)
