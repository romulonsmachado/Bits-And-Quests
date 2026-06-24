import thumby, time
import items as _items
from ui import (
    fonte_normal, fonte_grande, largura_texto_5x7, largura_texto_8x8,
    desenhar_linha_centrada_8x8, desenhar_texto_selecionado_8x8,
    desenhar_texto_scroll, desenhar_icone, texto_scroll_offset_por_largura,
    desenhar_texto_janela_com_shift)

MARKET_STOCK=(_items.ITEM_HERB,_items.ITEM_PICKAXE)
BLACKSMITH_STOCK=(
    _items.ITEM_SHORT_SWORD,
    _items.ITEM_SWORD,
    _items.ITEM_LEATHER_ARMOR,
    _items.ITEM_CHAINMAIL,
    _items.ITEM_SHIELD,
)

DONE=1
ACTIVE=0

kind=0
mode=0
shop_sel=0
list_sel=0
list_scroll=0
confirm_sel=0
confirm_qty=1
msg=""
mu=0

def enter(k):
    global kind,mode,shop_sel,list_sel,list_scroll,confirm_sel,confirm_qty,msg,mu
    kind=k
    mode=0
    shop_sel=0
    list_sel=0
    list_scroll=0
    confirm_sel=0
    confirm_qty=1
    msg=""
    mu=0

def _is_equip_key(k):
    return k=="weapon" or k=="armor" or k=="shield"

def _stock():
    return BLACKSMITH_STOCK if kind else MARKET_STOCK

def _buy_stock(hero):
    if kind:
        return BLACKSMITH_STOCK
    if _has_item_key(hero, "pickaxe"):
        return (_items.ITEM_HERB,)
    return MARKET_STOCK

def _price(name):
    return _items.price_by_name(name)

def _sell_price(it):
    p=it.get("price",_price(it.get("nome","")))
    p=p//10
    return p if p>0 else 1

def _icon_for(k,icons):
    if k=="herb": return icons[1]
    if k=="weapon": return icons[2]
    if k=="armor": return icons[3]
    if k=="shield": return icons[4]
    if k=="potion": return icons[5]
    if k=="stone_tablet": return icons[6]
    if k=="magia": return icons[7]
    if k=="strike": return icons[8]
    if k=="pickaxe": return icons[2]
    return icons[5]

def _has_item_key(hero,key):
    for it in hero["Inventory"]:
        if it.get("icon_key","")==key:
            return True
    return False

def _is_sellable(it):
    if not it.get("sellable", True):
        return False
    if it.get("category", "") == "key":
        return False
    return it.get("icon_key", "") != "stone_tablet"

def _sell_match(it):
    if not _is_sellable(it):
        return False
    eq=_is_equip_key(it.get("icon_key",""))
    return eq if kind else not eq

def _sell_count(hero):
    c=0
    for it in hero["Inventory"]:
        if _sell_match(it):
            c+=1
    return c

def _sell_item(hero,idx):
    c=0
    for it in hero["Inventory"]:
        if _sell_match(it):
            if c==idx:
                return it
            c+=1
    return None

def _qty(it):
    q=it.get("qtd",1)
    if q<1: q=1
    return q

def _clamp_list(total):
    global list_sel,list_scroll
    if total<=0:
        list_sel=0; list_scroll=0
        return
    if list_sel>=total: list_sel=total-1
    if list_sel<0: list_sel=0
    if list_sel<list_scroll: list_scroll=list_sel
    if list_sel>=list_scroll+3: list_scroll=list_sel-2

def _move_list(total,step,nav):
    global list_sel
    if total<=0:
        return
    list_sel=(list_sel+step)%total
    _clamp_list(total)
    nav()

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

def _draw_scroll_full(text,x,y,max_px):
    if largura_texto_5x7(text)<=max_px:
        thumby.display.drawText(text,x,y,1)
        return
    shift=texto_scroll_offset_por_largura(largura_texto_5x7(text)+12,max_px)
    desenhar_texto_janela_com_shift(text,x,y,max_px,shift,1)

def _draw_shop_header(title,icons):
    fonte_normal()
    thumby.display.drawText(title,2,1,1)
    thumby.display.blit(icons[0],62,0,8,8,-1,0,0)

def _draw_shop_item_line(y,name,icon,price,icons,selected):
    price_txt=str(price)
    price_x=70-largura_texto_5x7(price_txt)
    if price_x<46: price_x=46
    desenhar_texto_scroll(name,13,y+1,price_x-14,1)
    thumby.display.drawFilledRectangle(3,y,9,8,0)
    thumby.display.drawFilledRectangle(price_x-1,y,73-price_x,8,0)
    if (not selected) or ((time.ticks_ms()//180)&1)==0:
        desenhar_icone(icon,3,y)
        thumby.display.drawText(price_txt,price_x,y+1,1)
    if selected:
        thumby.display.drawFilledRectangle(0,y,1,8,1)
        thumby.display.drawFilledRectangle(71,y,1,8,1)

def _shop_list(hero,icons,is_buy,nav):
    global mode,confirm_sel,confirm_qty,msg
    thumby.display.fill(0)
    _draw_shop_header("BUY" if is_buy else "SELL",icons)
    stock = _buy_stock(hero)
    total=len(stock) if is_buy else _sell_count(hero)
    _clamp_list(total)
    if total<=0:
        thumby.display.drawText("Empty",(72-largura_texto_5x7("Empty"))//2,20,1)
    else:
        for i in range(3):
            idx=list_scroll+i
            if idx>=total: break
            y=10+i*10
            if is_buy:
                item=_items.shop_tuple(stock[idx])
                _draw_shop_item_line(y,item[1],_icon_for(item[0],icons),item[2],icons,idx==list_sel)
            else:
                it=_sell_item(hero,idx)
                _draw_shop_item_line(y,it.get("nome",""),_icon_for(it.get("icon_key",""),icons),_sell_price(it),icons,idx==list_sel)
    if thumby.buttonD.justPressed(): _move_list(total,1,nav)
    elif thumby.buttonU.justPressed(): _move_list(total,-1,nav)
    if thumby.buttonB.justPressed():
        mode=0; nav()
    elif thumby.buttonA.justPressed() and total>0:
        confirm_sel=0; confirm_qty=1; msg=""
        mode=3 if is_buy else 4
        nav()

def _max_qty(hero,is_buy,item,price):
    if kind:
        return 1
    if is_buy and item == _items.ITEM_PICKAXE:
        return 1
    if is_buy:
        q=hero.get("Gold",0)//price
        if q<1: q=1
        return 99 if q>99 else q
    q=_qty(item)
    return 99 if q>99 else q

def _add_item(hero,item_id,qty):
    item=_items.shop_tuple(item_id)
    key,name,price=item
    if key=="pickaxe":
        if _has_item_key(hero,key):
            return
        hero["Inventory"].append(_items.make_key_item(key,name,1,price))
        return
    obj=_items.make_item(item_id,qty)
    _items.add_to_inventory(hero,obj)

def _remove_item(hero,it,qty):
    if it is None:
        return
    if it.get("qtd",1)>qty:
        it["qtd"]-=qty
        return
    if it in hero["Inventory"]:
        hero["Inventory"].remove(it)

def _confirm(now,hero,icons,is_buy,nav,sfx):
    global mode,confirm_sel,confirm_qty,msg,mu
    if is_buy:
        stock = _buy_stock(hero)
        total_items=len(stock)
        _clamp_list(total_items)
        item_id=stock[list_sel] if total_items>0 else _items.ITEM_HERB
        item=_items.shop_tuple(item_id)
        price=item[2]
        key=item[0]
        name=item[1]
    else:
        total_items=_sell_count(hero)
        _clamp_list(total_items)
        it=_sell_item(hero,list_sel)
        if it is None:
            mode=2; return
        price=_sell_price(it)
        key=it.get("icon_key","")
        name=it.get("nome","")
        item=it
        item_id=0
    maxq=_max_qty(hero,is_buy,item_id if is_buy else item,price)
    if confirm_qty>maxq: confirm_qty=maxq
    total=price*confirm_qty
    thumby.display.fill(0)
    desenhar_icone(_icon_for(key,icons),3,2)
    _draw_scroll_full(name,13,3,50)
    if msg and time.ticks_diff(mu,now)>0:
        desenhar_linha_centrada_8x8(msg,15,1)
    else:
        price_txt=str(total)
        qty_txt=str(confirm_qty)
        price_w=largura_texto_5x7(price_txt)
        qty_w=largura_texto_5x7(qty_txt)
        gap=14
        row_w=8+1+price_w+gap+qty_w
        x=(72-row_w)//2
        if x<0: x=0
        _draw_price(icons,total,x,16)
        if maxq<=1 or ((now//180)&1)==0:
            thumby.display.drawText(qty_txt,x+9+price_w+gap,17,1)
    _choice("BUY" if is_buy else "SELL","NO",confirm_sel,30)
    if maxq>1:
        if thumby.buttonU.justPressed():
            confirm_qty+=1
            if confirm_qty>maxq: confirm_qty=maxq
            nav()
        elif thumby.buttonD.justPressed():
            confirm_qty-=1
            if confirm_qty<1: confirm_qty=1
            nav()
    if thumby.buttonL.justPressed() or thumby.buttonR.justPressed():
        confirm_sel=1-confirm_sel; nav()
    if thumby.buttonB.justPressed():
        mode=1 if is_buy else 2; nav()
    elif thumby.buttonA.justPressed():
        if confirm_sel:
            mode=1 if is_buy else 2; nav()
        elif is_buy:
            if key=="pickaxe" and _has_item_key(hero,key):
                msg="OWNED"; mu=time.ticks_add(now,900); sfx(120,120)
                return
            if hero.get("Gold",0)>=total:
                hero["Gold"]-=total
                _add_item(hero,item_id,confirm_qty)
                mode=1; sfx(700,120)
            else:
                msg="NO BITS"; mu=time.ticks_add(now,900); sfx(120,120)
        else:
            hero["Gold"]=hero.get("Gold",0)+total
            _remove_item(hero,item,confirm_qty)
            _clamp_list(_sell_count(hero))
            mode=2; sfx(700,120)

def update(now,hero,icons,nav,sfx):
    global mode,shop_sel,list_sel,list_scroll,confirm_qty,msg
    if mode==0:
        thumby.display.fill(0)
        if shop_sel==0:
            desenhar_texto_selecionado_8x8("BUY",(72-largura_texto_8x8("BUY"))//2,10)
            desenhar_linha_centrada_8x8("SELL",24,1)
        else:
            desenhar_linha_centrada_8x8("BUY",10,1)
            desenhar_texto_selecionado_8x8("SELL",(72-largura_texto_8x8("SELL"))//2,24)
        if thumby.buttonU.justPressed() or thumby.buttonD.justPressed():
            shop_sel=1-shop_sel; nav()
        if thumby.buttonB.justPressed():
            nav(); return DONE
        if thumby.buttonA.justPressed():
            list_sel=0; list_scroll=0; confirm_qty=1; msg=""
            mode=1 if shop_sel==0 else 2
            nav()
        return ACTIVE
    if mode==1:
        _shop_list(hero,icons,True,nav)
    elif mode==2:
        _shop_list(hero,icons,False,nav)
    elif mode==3:
        _confirm(now,hero,icons,True,nav,sfx)
    else:
        _confirm(now,hero,icons,False,nav,sfx)
    return ACTIVE
