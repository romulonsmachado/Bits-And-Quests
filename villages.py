import gc, sys, thumby, time
from ui import (
    DIALOG_SCROLL_AUTO_MS, DIALOG_SCROLL_SLOW_MS, fonte_normal, fonte_grande,
    largura_texto_5x7, largura_texto_8x8, desenhar_linha_centrada_8x8,
    desenhar_texto_selecionado_8x8, desenhar_dialogo_personagem,
    preparar_dialogo_personagem, desenhar_icone)

ACTION_NONE=0
ACTION_LEAVE=1
ACTION_MENU=2
ACTION_REST_SAVE=3
ACTION_TEMPLE=4
TOWN_NAMES=("Farlily",)
TOWN_COUNT=len(TOWN_NAMES)
TOWN_DATA=(
    (
        ((0,8),(4,8),(7,16),(-1,4),(7,8),(4,8),(2,16),(-1,4),
         (-3,8),(0,8),(4,16),(-1,4),(2,8),(0,8),(-5,20),(-1,8)),
        92,
        ("INN","TEMPLE","TAVERN","MARKET","BLACKSMITH","SQUARE","LEAVE"),
        ("INNKEEPER","BLACKSMITH"),
        5,
        2,
        (107,160),
        (43,30),
        2,
    ),
)
BB=360
PB=72
current_id=-1
MUSIC=()
BPM=90
OP=()
NN=()
BO=0
NO=0
COST=0
DO=()
DL=()
bg=None
pi=None
pt=None
gd=""
shop_mod=None
s=0
m=0
npc=0
yn=0
shop_kind=0
scr=0
sd=1
pa=0
ls=0
dialog_lines=()
dialog_max=0
dialog_scroll=0
dialog_timer=0
msg=""
mu=0
saved_phase=-1

def module_names():
    return ()

def module(town_id):
    return ""

def name(town_id):
    if town_id < 0 or town_id >= TOWN_COUNT:
        return TOWN_NAMES[0]
    return TOWN_NAMES[town_id]

def load(town_id=0):
    global current_id, MUSIC, BPM, OP, NN, BO, NO, COST, DO, DL
    if current_id == town_id and OP:
        return
    if town_id < 0 or town_id >= TOWN_COUNT:
        town_id = 0
    data = TOWN_DATA[town_id]
    MUSIC = data[0]
    BPM = data[1]
    OP = data[2]
    NN = data[3]
    BO = data[4] * BB
    COST = data[5]
    DO = data[6]
    DL = data[7]
    NO = data[8] * PB
    current_id = town_id
    gc.collect()

def _r(p,o,d):
    f=open(p,"rb")
    try:
        f.seek(o)
        try:
            q=f.readinto(d)
            if q is not None:
                for i in range(q,len(d)): d[i]=0
        except AttributeError:
            raw=f.read(len(d)); q=len(raw)
            for i in range(q): d[i]=raw[i]
            for i in range(q,len(d)): d[i]=0
    finally:
        f.close()

def load_assets(game_dir, town_id=0):
    global bg,gd
    load(town_id)
    gd=game_dir
    if bg is None:
        bg=bytearray(BB)
        _r(game_dir+"/gfx/backgrounds.bin",BO,bg)

def unload():
    global bg,pi,pt,current_id,MUSIC,BPM,OP,NN,BO,NO,COST,DO,DL
    bg=None; pi=None; pt=None
    current_id=-1
    MUSIC=(); BPM=90; OP=(); NN=()
    BO=0; NO=0; COST=0; DO=(); DL=()
    _unload_shop()

def reset():
    global s,m,npc,yn,shop_kind
    global scr,sd,pa,ls,dialog_lines,dialog_max,dialog_scroll,dialog_timer,msg,mu,saved_phase
    s=0; m=0; npc=0; yn=0; shop_kind=0
    scr=0; sd=1; pa=0; ls=0
    dialog_lines=(); dialog_max=0; dialog_scroll=0; dialog_timer=0
    msg=""; mu=0; saved_phase=-1

def _w(t):
    return largura_texto_5x7(t)

def _npc_text(idx):
    try:
        f=open(gd+"/gfx/dialogs.bin","rb")
    except OSError:
        return ""
    try:
        f.seek(DO[idx])
        return f.read(DL[idx]).decode()
    finally:
        f.close()

def _load_portrait(idx,now):
    global pi,pt,npc,dialog_lines,dialog_max,dialog_scroll,dialog_timer
    npc=idx
    _text=_npc_text(idx)
    if pi is None: pi=bytearray(PB)
    if pt is None: pt=bytearray(PB)
    o=NO+idx*PB*2
    _r(gd+"/gfx/portraits.bin",o,pi)
    _r(gd+"/gfx/portraits.bin",o+PB,pt)
    dialog_lines,dialog_max=preparar_dialogo_personagem(_text)
    dialog_scroll=0
    dialog_timer=now

def _dir():
    return thumby.buttonL.justPressed() or thumby.buttonR.justPressed() or thumby.buttonU.justPressed() or thumby.buttonD.justPressed()

def _choice(a,b,sel,y):
    ax=10; bx=72-largura_texto_8x8(b)-10
    fonte_grande()
    if sel==0:
        desenhar_texto_selecionado_8x8(a,ax,y)
        thumby.display.drawText(b,bx,y,1)
    else:
        thumby.display.drawText(a,ax,y,1)
        desenhar_texto_selecionado_8x8(b,bx,y)

def _draw_price(icons, price, x, y):
    desenhar_icone(icons[0],x,y)
    thumby.display.drawText(str(price),x+9,y+1,1)

def _load_shop(kind):
    global shop_mod,shop_kind,m
    shop_kind=kind
    if shop_mod is None:
        import shop as _shop
        shop_mod=_shop
        del _shop
    shop_mod.enter(kind)
    m=3

def _unload_shop():
    global shop_mod
    if shop_mod is None:
        return
    if "shop" in sys.modules:
        del sys.modules["shop"]
    if "items" in sys.modules:
        del sys.modules["items"]
    shop_mod=None
    gc.collect()

def _dialog_scroll(now):
    global dialog_scroll,dialog_timer
    if dialog_max<=0:
        return
    ms=DIALOG_SCROLL_AUTO_MS
    if thumby.buttonR.pressed():
        ms=8
    elif thumby.buttonL.pressed():
        ms=DIALOG_SCROLL_SLOW_MS
    dt=time.ticks_diff(now,dialog_timer)
    if dialog_scroll==0:
        if dt<500: return
        dt-=500
    elif dialog_scroll>=dialog_max:
        if dt<500: return
        dialog_scroll=0; dialog_timer=now; return
    if dt>=ms:
        dialog_scroll+=dt//ms
        if dialog_scroll>dialog_max: dialog_scroll=dialog_max
        dialog_timer=now

def _rest(now,hero,icons,nav,sfx):
    global m,yn,msg,mu,saved_phase
    thumby.display.fill(0)
    desenhar_linha_centrada_8x8("REST AND",0,1)
    desenhar_linha_centrada_8x8("SAVE?",10,1)
    if msg and time.ticks_diff(mu,now)>0:
        desenhar_linha_centrada_8x8(msg,20,1)
    else:
        _px=(72-(8+1+largura_texto_5x7(str(COST))))//2
        _draw_price(icons,COST,_px,20)
    _choice("YES","NO",yn,30)
    if _dir(): yn=1-yn; nav()
    if thumby.buttonB.justPressed(): m=0; nav(); return ACTION_NONE
    elif thumby.buttonA.justPressed():
        if yn: m=0; nav(); return ACTION_NONE
        elif hero.get("Gold",0)>=COST:
            hero["Gold"]-=COST; hero["HP"]=hero["HP_MAX"]; hero["MP"]=hero["MP_MAX"]
            import status
            status.clear_all(hero)
            if "status" in sys.modules:
                del sys.modules["status"]
            gc.collect()
            msg="SAVED"; mu=time.ticks_add(now,900); saved_phase=-1; m=8
            return ACTION_REST_SAVE
        else:
            msg="NO BITS"; mu=time.ticks_add(now,900); sfx(120,120)
    return ACTION_NONE

def update(now,hero,il,ir,icons,nav,sfx):
    global s,m,yn,shop_kind,scr,sd,pa,ls,msg,saved_phase
    if bg is None:
        return ACTION_NONE
    if m==1:
        thumby.display.blit(bg,0,0,72,40,-1,0,0)
        _dialog_scroll(now)
        desenhar_dialogo_personagem(dialog_lines,dialog_scroll,dialog_max,"",pi,pt,False,False)
        if thumby.buttonB.justPressed(): m=0; nav()
        elif thumby.buttonA.justPressed():
            if npc==1:
                _load_shop(1); msg=""
            else:
                m=2; yn=0; msg=""
            nav()
        return ACTION_NONE
    if m==2:
        return _rest(now,hero,icons,nav,sfx)
    if m==3:
        if shop_mod is None:
            _load_shop(shop_kind)
        if shop_mod.update(now,hero,icons,nav,sfx):
            _unload_shop()
            m=0
        return ACTION_NONE
    if m==8:
        thumby.display.fill(0)
        _phase=(now//80)&1
        if _phase!=saved_phase:
            saved_phase=_phase
            if _phase==0:
                sfx(760+((now//160)&1)*120,35)
        if _phase==0:
            desenhar_linha_centrada_8x8("SAVED",16,1)
        if time.ticks_diff(now,mu)>=0 or thumby.buttonA.justPressed() or thumby.buttonB.justPressed():
            m=0
            nav()
        return ACTION_NONE
    if ls==0: ls=now
    dt=time.ticks_diff(now,ls); ls=now
    if dt>100: dt=100
    if not pa or time.ticks_diff(pa,now)<=0:
        pa=0; scr+=sd*dt*6
        if scr>=9000: scr=9000; sd=-1; pa=time.ticks_add(now,1100)
        elif scr<=0: scr=0; sd=1; pa=time.ticks_add(now,1100)
    thumby.display.blit(bg,0,-(scr//1000),72,40,-1,0,0)
    fonte_normal()
    thumby.display.drawFilledRectangle(0,31,72,9,0)
    thumby.display.blit(il,2,32,3,7,-1,0,0)
    thumby.display.blit(ir,67,32,3,7,-1,0,0)
    thumby.display.drawText(OP[s],(72-_w(OP[s]))//2,32,1)
    if thumby.buttonR.justPressed(): s=(s+1)%len(OP); nav()
    elif thumby.buttonL.justPressed(): s=(s-1)%len(OP); nav()
    if thumby.buttonB.justPressed(): return ACTION_MENU
    if thumby.buttonA.justPressed():
        if s==0:
            _load_portrait(0,now); m=1
        elif s==1:
            return ACTION_TEMPLE
        elif s==3:
            _load_shop(0); msg=""
        elif s==4:
            shop_kind=1; _load_portrait(1,now); m=1
        elif s==6:
            return ACTION_LEAVE
        nav()
    return ACTION_NONE
