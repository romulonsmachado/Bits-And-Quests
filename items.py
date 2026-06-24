ITEM_HERB = 1
ITEM_SHORT_SWORD = 2
ITEM_SWORD = 3
ITEM_LEATHER_ARMOR = 4
ITEM_CHAINMAIL = 5
ITEM_SHIELD = 6
ITEM_PICKAXE = 7
ITEM_LEATHER_CLOTHES = 8
ITEM_STONE_TABLET = 9

# id, icon_key, name, price, flags
ITEMS = (
    None,
    (ITEM_HERB, "herb", "Healing Herb", 10, 1),
    (ITEM_SHORT_SWORD, "weapon", "Short Sword", 10, 2),
    (ITEM_SWORD, "weapon", "Sword", 30, 2),
    (ITEM_LEATHER_ARMOR, "armor", "Leather Armor", 12, 2),
    (ITEM_CHAINMAIL, "armor", "Chainmail", 50, 2),
    (ITEM_SHIELD, "shield", "Shield", 40, 2),
    (ITEM_PICKAXE, "pickaxe", "Pickaxe", 8, 4),
    (ITEM_LEATHER_CLOTHES, "armor", "Leather Clothes", 10, 2),
    (ITEM_STONE_TABLET, "stone_tablet", "Stone Tablet", 0, 4),
)
FLAG_HEAL = 1
FLAG_EQUIP = 2
FLAG_KEY = 4

def item_def(item_id):
    if 0 < item_id < len(ITEMS):
        return ITEMS[item_id]
    return None

def item_id_by_name(name):
    for it in ITEMS:
        if it and it[2] == name:
            return it[0]
    return 0

def item_id_by_key_name(icon_key, name):
    for it in ITEMS:
        if it and it[1] == icon_key and it[2] == name:
            return it[0]
    return item_id_by_name(name)

def shop_tuple(item_id):
    it = item_def(item_id)
    if not it:
        return ("herb", "Healing Herb", 1)
    return (it[1], it[2], it[3])

def price_by_name(name):
    it = item_def(item_id_by_name(name))
    return it[3] if it else 1

def make_item(item_id, qty=1):
    it = item_def(item_id)
    if not it:
        return {"id": 0, "icon_key": "herb", "nome": "Unknown", "qtd": qty, "price": 1}
    obj = {"id": item_id, "icon_key": it[1], "nome": it[2], "qtd": qty}
    if it[3]:
        obj["price"] = it[3]
    if it[4] & FLAG_HEAL:
        obj["heal_percent"] = 50
    if it[4] & FLAG_KEY:
        obj["category"] = "key"
        obj["sellable"] = False
    return obj

def is_equip_key(key):
    return key == "weapon" or key == "armor" or key == "shield"

def slot_for_key(key):
    if key == "weapon":
        return "Weapon"
    if key == "armor":
        return "Armor"
    if key == "shield":
        return "Shield"
    return ""

def calc_heal_hp(hero, obj):
    return obj.get("heal", max(1, (hero["HP_MAX"] * obj.get("heal_percent", 0) + 99) // 100))

def calc_heal_mp(hero, obj):
    return obj.get("mp_heal", max(1, (hero["MP_MAX"] * obj.get("mp_heal_percent", 0) + 99) // 100))

def has_heal_hp(obj):
    return "heal" in obj or "heal_percent" in obj

def has_heal_mp(obj):
    return "mp_heal" in obj or "mp_heal_percent" in obj

def heal_blocked(hero, obj):
    check = False
    can_restore = False
    if has_heal_hp(obj):
        check = True
        if hero["HP"] < hero["HP_MAX"]:
            can_restore = True
    if has_heal_mp(obj):
        check = True
        if hero["MP"] < hero["MP_MAX"]:
            can_restore = True
    return check and not can_restore

def bonus_atk(slot, name):
    if slot == "Weapon":
        if name == "Short Sword":
            return 1
        if name == "Sword":
            return 2
    return 0

def bonus_def(slot, name):
    if slot == "Armor" and name == "Leather Clothes":
        return 1
    if slot == "Armor" and name == "Leather Armor":
        return 2
    if slot == "Armor" and name == "Chainmail":
        return 3
    return 1 if slot == "Shield" and name == "Shield" else 0

def recalc_atk(hero, level_atk, max_level):
    lvl = hero.get("LVL", 1)
    if lvl < 1:
        lvl = 1
    if lvl > max_level:
        lvl = max_level
    hero["ATK"] = level_atk[lvl - 1] + bonus_atk("Weapon", hero.get("Weapon", "None"))

def desequip_slot(hero, slot):
    name = hero[slot]
    if name == "None":
        return False
    icon_key = hero.get(slot + "_icon", slot.lower())
    hero["ATK"] -= bonus_atk(slot, name)
    hero["DEF"] -= bonus_def(slot, name)
    hero["Inventory"].append({"id": item_id_by_key_name(icon_key, name), "icon_key": icon_key, "nome": name})
    hero[slot] = "None"
    hero[slot + "_icon"] = ""
    return True

def equip_item_slot(hero, slot, ref):
    if hero[slot] != "None":
        desequip_slot(hero, slot)
    hero[slot] = ref["nome"]
    hero[slot + "_icon"] = ref.get("icon_key", slot.lower())
    hero["ATK"] += bonus_atk(slot, ref["nome"])
    hero["DEF"] += bonus_def(slot, ref["nome"])
    if ref in hero["Inventory"]:
        if ref.get("qtd", 1) > 1:
            ref["qtd"] -= 1
        else:
            hero["Inventory"].remove(ref)

def equipped_icon_key(hero, slot):
    return hero.get(slot + "_icon", "")

def equip_effect(slot_key, name):
    slot = slot_for_key(slot_key)
    atk = bonus_atk(slot, name) if slot else 0
    defs = bonus_def(slot, name) if slot else 0
    if atk and defs:
        return "+" + str(atk) + " ATK +" + str(defs) + " DEF"
    if atk:
        return "+" + str(atk) + " ATK"
    if defs:
        return "+" + str(defs) + " DEF"
    return "No effect"

def add_to_inventory(hero, item):
    slot_key = item.get("icon_key", "")
    slot = slot_for_key(slot_key)
    if slot and hero[slot] == "None":
        equip_item_slot(hero, slot, item)
        return True
    for it in hero["Inventory"]:
        if (item.get("id", 0) and it.get("id", 0) == item.get("id", 0)) or it.get("nome") == item["nome"]:
            it["qtd"] = it.get("qtd", 0) + item.get("qtd", 1)
            if "price" in item:
                it["price"] = item["price"]
            return False
    hero["Inventory"].append(item)
    return False

def make_key_item(icon_key, name, qty=1, price=0):
    obj = {"id": item_id_by_key_name(icon_key, name), "icon_key": icon_key, "nome": name, "qtd": qty, "category": "key", "sellable": False}
    if price:
        obj["price"] = price
    return obj

def has_item_name(hero, name):
    for it in hero["Inventory"]:
        if it.get("nome", "") == name:
            return True
    return False
