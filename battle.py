import thumby, random, gc
import status
from ui import (
    fonte_normal, desenhar_icone, desenhar_texto_contornado_8x8,
    desenhar_texto_centralizado_contornado_8x8 as txt8c)

GFX_DIR = "/Games/Bits & Quests/gfx/"
MONSTERS_BIN = "monsters.bin"
EFFECTS_BIN = "effects.bin"
MONSTER_BYTES = 200
EFFECT_SWORD_OFFSET = 420
EFFECT_SWORD_MASK_OFFSET = 620

ABILITY_NONE = 0
ABILITY_WEAK_POISON = 1
_MONSTERS = (
    (0, "OGRIN", 2, 3, 3, 1, 0, 1, 1, 0, ABILITY_NONE),
    (1, "SKALY", 3, 4, 4, 2, 0, 2, 2, 0, ABILITY_NONE),
    (2, "WURM",  4, 5, 5, 3, 0, 3, 1, 0, ABILITY_NONE),
    (3, "BUZZER", 5, 5, 5, 3, 1, 5, 2, 1, ABILITY_WEAK_POISON),
    (4, "ARACHNE", 5, 6, 6, 3, 2, 5, 2, 2, ABILITY_WEAK_POISON),
)
_ENCOUNTER_MAP = ((0, 60), (1, 100))
_ENCOUNTER_DUNGEON_WURMS = ((1, 25), (2, 100))
_ENCOUNTER_STING_FOREST = ((3, 60), (4, 100))

LEVEL_HP  = (7,8,8,8,8,9,9,9,10,10)
LEVEL_MP  = (0,1,2,2,2,3,4,5,5,5)
LEVEL_ATK = (0,0,0,0,1,1,1,1,1,2)
LEVEL_DEF = (0,0,0,1,1,1,1,1,1,1)
XP_NEXT   = (3,7,15,25,40,60,80,110,140,0)
MAX_LEVEL = 10

WAIT=0; HERO=1; ENEMY_WAIT=2; ENEMY=3; VICTORY=4; LEVELUP=5; DEFEAT=6; FLEE=7; DEATH=8; HERO_DEATH=9
FRAME_MS=33; HERO_MS=430; ENEMY_WAIT_MS=480; ENEMY_MS=300
POP_MS=620; DEATH_MS=520; VICT_MS=2100; LV_MS=2300; DEF_MS=1300; FLEE_MS=360

icon_hp=icon_mp=icon_potion=icon_herb=icon_magia=icon_strike=icon_flee_txt=None
bm_enemy=bm_enemy_mask=bm_sword=bm_sword_mask=None
eidx=0; elvl=ehp=ehpmax=eatk=edef=expdrop=golddrop=0
emp=empmax=eability=0
enemy_name=""; enemy_name_x=0
state=WAIT; timer=0; last_ms=0
hud=False; hud_y=9; sel=0
popup_txt=""; popup_x=0; popup_y=0; popup_y_fp=0; popup_t=0
gold_drop=0; hero_done=False; enemy_done=False
victory_applied=False; skip_ready=False
level_pending=False; level_l1=""; level_l2=""
sword_t=-1

def configurar_icones(hp, mp, potion, herb, magia, strike, flee):
    global icon_hp,icon_mp,icon_potion,icon_herb,icon_magia,icon_strike,icon_flee_txt
    icon_hp=hp; icon_mp=mp; icon_potion=potion; icon_herb=herb
    icon_magia=magia; icon_strike=strike; icon_flee_txt=flee

def _read(path, off, data):
    f=open(path,"rb")
    try:
        f.seek(off)
        try:
            n=f.readinto(data)
            if n is not None:
                for i in range(n,len(data)): data[i]=0
        except AttributeError:
            raw=f.read(len(data)); n=len(raw)
            for i in range(n): data[i]=raw[i]
            for i in range(n,len(data)): data[i]=0
    finally:
        f.close()

def _load(name, off, size):
    data=bytearray(size)
    _read(GFX_DIR+name, off, data)
    return data

def limpar_assets_batalha(liberar=False):
    global bm_enemy,bm_enemy_mask,bm_sword,bm_sword_mask
    if liberar:
        bm_enemy=None; bm_enemy_mask=None; bm_sword=None; bm_sword_mask=None
        gc.collect()

def carregar_assets_batalha():
    global bm_enemy,bm_enemy_mask
    if bm_enemy is None or bm_enemy_mask is None:
        try:
            off=eidx*MONSTER_BYTES*2
            bm_enemy=_load(MONSTERS_BIN, off, MONSTER_BYTES)
            bm_enemy_mask=_load(MONSTERS_BIN, off+MONSTER_BYTES, MONSTER_BYTES)
        except MemoryError:
            bm_enemy=None; bm_enemy_mask=None
            gc.collect()

def _load_sword():
    global bm_sword,bm_sword_mask
    if bm_sword is None or bm_sword_mask is None:
        try:
            bm_sword=_load(EFFECTS_BIN, EFFECT_SWORD_OFFSET, MONSTER_BYTES)
            bm_sword_mask=_load(EFFECTS_BIN, EFFECT_SWORD_MASK_OFFSET, MONSTER_BYTES)
        except MemoryError:
            bm_sword=None; bm_sword_mask=None
            gc.collect()

def _mon_get(monster_id):
    if 0 <= monster_id < len(_MONSTERS):
        return _MONSTERS[monster_id]
    return _MONSTERS[0]

def _mon_roll(table):
    r = int(random.random() * 100)
    for item in table:
        if r < item[1]:
            return _mon_get(item[0])
    return _mon_get(table[-1][0])

def sortear_inimigo_dungeon():
    return _mon_roll(_ENCOUNTER_DUNGEON_WURMS)

def sortear_inimigo_mapa():
    return _mon_roll(_ENCOUNTER_MAP)

def sortear_inimigo_sting_forest():
    return _mon_roll(_ENCOUNTER_STING_FOREST)

def setar_inimigo(mon):
    global eidx,elvl,ehp,ehpmax,eatk,edef,expdrop,golddrop
    global emp,empmax,eability
    global enemy_name,enemy_name_x,bm_enemy,bm_enemy_mask
    old=eidx
    eidx=mon[0]; enemy_name=mon[1]; elvl=mon[2]; ehp=mon[3]; ehpmax=mon[4]
    eatk=mon[5]; edef=mon[6]; expdrop=mon[7]; golddrop=mon[8]
    empmax=mon[9] if len(mon)>9 else 0
    eability=mon[10] if len(mon)>10 else ABILITY_NONE
    emp=empmax
    enemy_name_x=(72-len(enemy_name)*6)//2
    if enemy_name_x<0: enemy_name_x=0
    if old!=eidx:
        bm_enemy=None; bm_enemy_mask=None

def _dt(now):
    global last_ms
    if not last_ms:
        last_ms=now; return FRAME_MS
    d=now-last_ms
    if d<FRAME_MS:
        return 0
    last_ms=now
    return FRAME_MS

def _gold(base):
    if base<=0: return 0
    v=base//4
    if v<1: v=1
    m=base-v
    if m<0: m=0
    return random.randint(m, base+v)

def _atk(atk, defs, alv, dlv):
    miss=0.08
    if alv>dlv: miss=0.04
    elif alv<dlv: miss=0.10
    if random.random()<miss: return 0,"MISS"
    base=max(1,atk-defs)
    dmg=max(1,(base*random.randint(85,115)+99)//100)
    crit=random.random()<0.05
    if crit: dmg*=2
    return dmg, str(dmg)+("!" if crit else "")

def _has_spell(hero,nome):
    for m in hero["Magias"]:
        if m.get("nome")==nome: return True
    return False

def _learn(hero):
    if hero["LVL"]==3 and not _has_spell(hero,"Strike"):
        hero["Magias"].append({"nome":"Strike","custo":2,"atk_bonus":2,"icon_key":"strike"})
        return "STRIKE"
    if hero["LVL"]==7 and not _has_spell(hero,"Weaken"):
        hero["Magias"].append({"nome":"Weaken","custo":3,"atk_down":1})
        return "WEAKEN"
    return ""

def _start_round(hero):
    global state,timer,hero_done,enemy_done
    hero_done=False; enemy_done=False
    if random.random() < (0.8 if hero["LVL"]>elvl else (0.6 if hero["LVL"]<elvl else 0.7)):
        state=WAIT; timer=0
    else:
        state=ENEMY_WAIT; timer=ENEMY_WAIT_MS

def _end_hero_turn(hero):
    global state,timer,hero_done
    hero_done=True
    if enemy_done:
        _finish_round(hero)
    else:
        state=ENEMY_WAIT
        timer=ENEMY_WAIT_MS

def _finish_round(hero):
    global state,timer,skip_ready
    dmg = status.tick(hero)
    if dmg:
        _popup(str(dmg), 12, 25)
        if hero["HP"] <= 0:
            state = HERO_DEATH
            timer = POP_MS
            skip_ready = False
            return
    _start_round(hero)

def iniciar_batalha(hero):
    global state,timer,last_ms,hud,hud_y,sel,popup_t,gold_drop,victory_applied
    global skip_ready,level_pending,level_l1,level_l2,sword_t,ehp
    status.init(hero)
    ehp=ehpmax; state=WAIT; timer=0; last_ms=0; hud=False; hud_y=9; sel=0
    popup_t=0; gold_drop=_gold(golddrop); victory_applied=False
    skip_ready=False; level_pending=False; level_l1=""; level_l2=""; sword_t=-1
    _start_round(hero)

def _popup(txt,x,y,dur=POP_MS):
    global popup_txt,popup_x,popup_y,popup_y_fp,popup_t
    popup_txt=txt; popup_x=x; popup_y=y; popup_y_fp=y*100; popup_t=dur

def _start_death(sfx):
    global state,timer,popup_t,sword_t,hud,hud_y
    state=DEATH; timer=DEATH_MS; sword_t=-1; hud=False; hud_y=9
    sfx(92,180)

def _heal_amount(hero,it):
    return it.get("heal", max(1,(hero["HP_MAX"]*it.get("heal_percent",0)+99)//100))

def _draw_frame(bg, now, dt, terminal):
    global sword_t
    thumby.display.fill(0)
    if bg is not None: thumby.display.blit(bg,0,0,72,40,-1,0,0)
    bob=1 if ((now//180)&3)==1 else (-1 if ((now//180)&3)==3 else 0)
    lunge=0
    if state==ENEMY:
        e=ENEMY_MS-timer
        if e<0: e=0
        if e>ENEMY_MS: e=ENEMY_MS
        h=ENEMY_MS//2
        lunge=(e*10)//h if e<h else ((ENEMY_MS-e)*10)//h
    ix=16; iy=bob+lunge
    if (not terminal and ehp>0) or (state==DEATH and ((timer//70)&1)):
        if bm_enemy is not None and bm_enemy_mask is not None:
            thumby.display.blit(bm_enemy_mask,ix,iy,40,40,0,0,0)
            thumby.display.blit(bm_enemy,ix,iy,40,40,1,0,0)
        else:
            thumby.display.drawRectangle(20,4,32,28,1)
    if not terminal and state!=FLEE and sword_t>=0 and bm_sword is not None and bm_sword_mask is not None:
        sx=(sword_t*40)//HERO_MS
        sy=20-(72*sword_t*(HERO_MS-sword_t))//(HERO_MS*HERO_MS)
        thumby.display.blit(bm_sword_mask,sx,sy,40,40,0,0,0)
        thumby.display.blit(bm_sword,sx,sy,40,40,1,0,0)
        sword_t+=dt
        if sword_t>HERO_MS: sword_t=-1
    return ix,iy

def _draw_num2(v, x, y):
    s = str(v)
    if len(s) < 2:
        x += 6
    thumby.display.drawText(s, x, y, 1)

def _draw_hud(hero, now):
    global sel
    item=None; qty=0; heal_icon=icon_potion
    for it in hero["Inventory"]:
        if it.get("qtd",0)>0 and ("heal" in it or "heal_percent" in it or "mp_heal" in it):
            item=it; qty=it.get("qtd",0)
            if it.get("icon_key","")=="herb": heal_icon=icon_herb
            break
    item_count=1 if item else 0
    magic_count=len(hero["Magias"])
    action_count=item_count+magic_count+1
    if sel>=action_count: sel=action_count-1
    if sel<0: sel=0
    if hud or hud_y<9:
        fonte_normal()
        blink=((now//180)&1)==0
        if hud and hud_y==0:
            thumby.display.drawFilledRectangle(0,0,72,9,0)
            thumby.display.drawText(enemy_name,enemy_name_x,1,1)
        y=31+hud_y
        thumby.display.drawFilledRectangle(0,y,72,9,0)
        desenhar_icone(icon_hp,1,y+1); _draw_num2(hero["HP"],10,y+1)
        desenhar_icone(icon_mp,24,y+1); _draw_num2(hero["MP"],33,y+1)
        pick=sel%action_count
        if pick<item_count:
            if blink: desenhar_icone(heal_icon,47,y+1)
            _draw_num2(qty,56,y+1)
        elif pick<item_count+magic_count:
            m=hero["Magias"][pick-item_count]
            if blink: desenhar_icone(icon_strike if m.get("icon_key","")=="strike" else icon_magia,47,y+1)
            _draw_num2(m.get("custo",0),56,y+1)
        elif blink:
            thumby.display.blit(icon_flee_txt,52,y+2,15,5,-1,0,0)
    return item,item_count,magic_count,action_count

def _apply_level(hero):
    global level_pending,level_l1,level_l2
    level_pending=False; level_l1=""; level_l2=""
    hp=mp=atk=defs=0; sp1=""; sp2=""
    while hero["XP_MAX"]>0 and hero["LVL"]<MAX_LEVEL and hero["XP"]>=hero["XP_MAX"]:
        old=hero["LVL"]-1
        hero["XP"]-=hero["XP_MAX"]; hero["LVL"]+=1
        new=hero["LVL"]-1
        dh=LEVEL_HP[new]-LEVEL_HP[old]; dm=LEVEL_MP[new]-LEVEL_MP[old]
        da=LEVEL_ATK[new]-LEVEL_ATK[old]; dd=LEVEL_DEF[new]-LEVEL_DEF[old]
        hero["HP_MAX"]+=dh; hero["MP_MAX"]+=dm; hero["ATK"]+=da; hero["DEF"]+=dd
        hp+=dh; mp+=dm; atk+=da; defs+=dd
        s=_learn(hero)
        if s and not sp1: sp1=s
        elif s: sp2=s
        hero["XP_MAX"]=XP_NEXT[new]
    if hero["LVL"]>=MAX_LEVEL: hero["XP"]=0
    gains=(("+%d HP"%hp) if hp else "", ("+%d MP"%mp) if mp else "", ("+%d ATK"%atk) if atk else "", ("+%d DEF"%defs) if defs else "", sp1, sp2)
    for g in gains:
        if g and not level_l1: level_l1=g
        elif g and not level_l2: level_l2=g
    if level_l1:
        hero["HP"]=hero["HP_MAX"]; hero["MP"]=hero["MP_MAX"]; level_pending=True

def update(now, hero, bg, sfx, nav, music, mus_vic, mus_def):
    global state,timer,hud,hud_y,sel,popup_t,popup_y,popup_y_fp
    global ehp,hero_done,enemy_done,victory_applied,skip_ready,sword_t
    global emp
    dt=_dt(now)
    terminal = state==DEATH or state==VICTORY or state==LEVELUP or state==DEFEAT
    ix,iy=_draw_frame(bg,now,dt,terminal)
    item,item_count,magic_count,action_count=_draw_hud(hero,now)
    if dt<=0:
        return None
    next_state=None

    if state==WAIT:
        if thumby.buttonL.justPressed() or thumby.buttonB.justPressed():
            hud=not hud; sfx(400,50)
        step=(dt*90+999)//1000
        if step<1: step=1
        if hud and hud_y>0:
            hud_y-=step
            if hud_y<0: hud_y=0
        elif (not hud) and hud_y<9:
            hud_y+=step
            if hud_y>9: hud_y=9
        if hud and hud_y==0:
            if thumby.buttonD.justPressed(): sel=(sel+1)%action_count; nav()
            if thumby.buttonU.justPressed(): sel=(sel-1)%action_count; nav()
        if thumby.buttonA.justPressed():
            if not hud:
                _load_sword(); sword_t=0 if bm_sword is not None else -1
                state=HERO; timer=HERO_MS; sfx(600,100); hud_y=9
            elif hud_y==0:
                pick=sel%action_count
                if pick<item_count and item:
                    if hero["HP"]>=hero["HP_MAX"]:
                        _popup("FULL",12,25,520); sfx(120,80)
                    else:
                        heal=min(hero["HP_MAX"]-hero["HP"],_heal_amount(hero,item))
                        hero["HP"]+=heal; item["qtd"]-=1
                        if item["qtd"]<=0: hero["Inventory"].remove(item)
                        _popup("+"+str(heal),12,25); sfx(600,100)
                        _end_hero_turn(hero)
                    hud=False; hud_y=9
                elif pick<item_count+magic_count:
                    m=hero["Magias"][pick-item_count]; cost=m.get("custo",0)
                    if hero["MP"]<cost:
                        sfx(120,80)
                    else:
                        hero["MP"]-=cost
                        dmg,txt=_atk(hero["ATK"]+m.get("atk_bonus",0),edef,hero["LVL"],elvl)
                        ehp-=dmg; _popup(txt,ix+20,iy+10); sfx(800,150)
                        if ehp<=0: _start_death(sfx)
                        else: _end_hero_turn(hero)
                    hud=False; hud_y=9
                else:
                    chance=0.75 if hero["LVL"]>elvl else (0.5 if hero["LVL"]<elvl else 0.6)
                    if random.random()<chance: state=FLEE; timer=FLEE_MS; popup_t=0; sfx(300,200)
                    else: _end_hero_turn(hero); sfx(200,100)
                    hud=False; hud_y=9; sel=0
    elif state==HERO:
        timer-=dt
        if timer<=0:
            sword_t=-1
            dmg,txt=_atk(hero["ATK"],edef,hero["LVL"],elvl)
            ehp-=dmg; _popup(txt,ix+20,iy+10); sfx(200,150)
            if ehp<=0: _start_death(sfx)
            else: _end_hero_turn(hero)
    elif state==ENEMY_WAIT:
        timer-=dt
        if timer<=0: state=ENEMY; timer=ENEMY_MS
    elif state==ENEMY:
        timer-=dt
        if timer<=0:
            use_poison = eability == ABILITY_WEAK_POISON and emp >= 1 and random.random() < 0.5
            atk = eatk - 2 if use_poison else eatk
            if atk < 0:
                atk = 0
            if use_poison:
                emp -= 1
            dmg,txt=_atk(atk,hero["DEF"],elvl,hero["LVL"])
            hero["HP"]-=dmg
            if hero["HP"]<0: hero["HP"]=0
            if use_poison and dmg>0:
                status.weak_poison(hero)
            _popup(txt,12,25); sfx(150,200)
            if hero["HP"]<=0:
                state=HERO_DEATH; timer=POP_MS; skip_ready=False
            else:
                enemy_done=True
                if hero_done: _finish_round(hero)
                else: state=WAIT
    elif state==HERO_DEATH:
        timer-=dt
        if timer<=0:
            state=DEFEAT; timer=0; skip_ready=False; popup_t=0; music(mus_def,160,False)
    elif state==DEATH:
        timer-=dt
        if timer<=0:
            state=VICTORY; timer=VICT_MS; skip_ready=False; music(mus_vic,160,False)
    elif state==VICTORY:
        if not victory_applied:
            hero["XP"]+=expdrop; hero["Gold"]+=gold_drop; _apply_level(hero); victory_applied=True
        txt8c("VICTORY",4); txt8c(str(expdrop)+" XP",16); txt8c(str(gold_drop)+" BITS",28); fonte_normal()
        if not skip_ready and (not thumby.buttonA.pressed()) and (not thumby.buttonB.pressed()):
            skip_ready=True
        elif skip_ready and (thumby.buttonA.justPressed() or thumby.buttonB.justPressed()):
            timer=0
        timer-=dt
        if timer<=0:
            if level_pending: state=LEVELUP; timer=LV_MS; skip_ready=False
            else: next_state="TRANSICAO_OUT"
    elif state==LEVELUP:
        txt8c("LEVEL UP!",4); txt8c(level_l1,16); txt8c(level_l2,28); fonte_normal()
        if not skip_ready and (not thumby.buttonA.pressed()) and (not thumby.buttonB.pressed()):
            skip_ready=True
        elif skip_ready and (thumby.buttonA.justPressed() or thumby.buttonB.justPressed()):
            timer=0
        timer-=dt
        if timer<=0: next_state="TRANSICAO_OUT"
    elif state==DEFEAT:
        txt8c("GAME OVER",16); fonte_normal()
        if not skip_ready and (not thumby.buttonA.pressed()) and (not thumby.buttonB.pressed()):
            skip_ready=True
        elif skip_ready and (thumby.buttonA.justPressed() or thumby.buttonB.justPressed()):
            next_state="TITLE"
    elif state==FLEE:
        timer-=dt
        if timer<=0:
            next_state="BATTLE_FLEE_OUT"

    if popup_t>0 and (not terminal or state==DEATH):
        desenhar_texto_contornado_8x8(popup_txt,popup_x,popup_y)
        popup_y_fp-=dt*3; popup_y=popup_y_fp//100; popup_t-=dt
    return next_state
