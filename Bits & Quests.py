import gc, sys

GAME_DIR = "/Games/Bits & Quests"
if GAME_DIR not in sys.path:
    sys.path.append(GAME_DIR)

import title

titulo_result = title.run(GAME_DIR)
try:
    sys.bq_title_result = titulo_result
except:
    pass
if "title" in sys.modules:
    del sys.modules["title"]
del title
gc.collect()

try:
    execfile(GAME_DIR + "/game.py")
except NameError:
    import game
