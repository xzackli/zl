from wallpaper_tools import *

import yaml
import io
import pickle
import sys
import os
import logging
from pathlib import Path


def number(list_of_things, start_ind=1):
    return [f"{start_ind+i}. {item_in_list}" for i, item_in_list in enumerate(list_of_things)]


abs_path = Path(__file__).resolve().parent
data_path = abs_path / "data" / "data.yaml"
log_path = abs_path / "data" / "log.txt"

home = Path.home()
config_path = home / ".config" / "zl.conf"
with open(str(config_path), 'r') as stream:
    config = yaml.load(stream)

save_path = abs_path / "data" / f"save_{config['machine']}.p"
image_path = abs_path / "data" / f"generated_{config['machine']}.jpg"


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler( str(log_path), mode='a')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    # logger.addHandler(screen_handler)
    return logger


logger = setup_custom_logger('zl')


def setup():
    boxwidth = config["boxwidth"]
    boxheight = config["boxheight"]
    origin_x = config["origin_x"]
    origin_y = config["origin_y"]
    margin = config["margin"]

    image = config["wallpaper"]
    image_path = abs_path / "wallpapers" / image
    img = Image.open(str(image_path))


    topleft = Textbox(x=origin_x, y=origin_y,
                      w=boxwidth, h=boxheight,
                      fontsize=config["fontsize"])
    topright = Textbox(x=origin_x+boxwidth+margin, y=origin_y,
                       w=boxwidth, h=boxheight,
                       fontsize=config["fontsize"])
    bottomleft = Textbox(x=origin_x, y=origin_y+boxheight+margin,
                       w=boxwidth, h=boxheight,
                       fontsize=config["fontsize"])
    bottomright = Textbox(x=origin_x+boxwidth+margin, y=origin_y+boxheight+margin,
                       w=boxwidth, h=boxheight,
                       fontsize=config["fontsize"])


    fontfile = "Inconsolata.otf"
    fontsize = config["titlesize"]
    fontpath = abs_path / fontfile
    font = ImageFont.truetype(str(fontpath), fontsize)

    img = topleft.draw(img, text="", font=font,
                      toptext="urgent", lefttext="critical", bg=True)
    img = topright.draw(img, text="", font=font, toptext="not urgent", bg=True)
    img = bottomleft.draw(img, text="", font=font, lefttext="not critical", bg=True)
    img = bottomright.draw_bg(img)

    import pickle
    pickled = { "img": img,
        "textboxes": (topleft, topright, bottomleft, bottomright) }
    pickle.dump( pickled, open( str(save_path), "wb" ) )


def update():

    fontfile = "Inconsolata.otf"
    fontsize = config["fontsize"]
    fontpath = abs_path / fontfile
    font = ImageFont.truetype(str(fontpath), fontsize)

    pickled = pickle.load( open(str(save_path),"rb") )
    img = pickled["img"]
    topleft, topright, bottomleft, bottomright = pickled["textboxes"]


    with open(str(data_path), 'r') as stream:
        current = yaml.load(stream)

    start_ind = 1

    inp_text = current["urgent + critical"]
    boxtext = "\n".join(number(inp_text, start_ind=start_ind))
    start_ind += len(inp_text)
    img = topleft.draw(img, text=boxtext, font=font)

    inp_text = current["not urgent + critical"]
    boxtext = "\n".join(number(inp_text, start_ind=start_ind))
    start_ind += len(inp_text)
    img = topright.draw(img, text=boxtext, font=font)

    inp_text = current["urgent + not critical"]
    boxtext = "\n".join(number(inp_text, start_ind=start_ind))
    start_ind += len(inp_text)
    img = bottomleft.draw(img, text=boxtext, font=font)

    inp_text = current["not urgent + not critical"]
    boxtext = "\n".join(number(inp_text, start_ind=start_ind))
    start_ind += len(inp_text)
    img = bottomright.draw(img, text=boxtext, font=font)

    img.save(str(image_path))

    if config['OS'] == 'LINUX':
        set_background_linux(image_path)
    else:
        set_background(image_path)


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

def get_cat_and_subind(current, num):
    categories = ["urgent + critical", "not urgent + critical",
        "urgent + not critical", "not urgent + not critical"]
    inds = flatten([ list(range(len(current[cat]))) for cat in categories])
    cats = flatten([ [cat] * len(current[cat]) for cat in categories ])

    i = num - 1
    return cats[i], inds[i]

def add(inp, inp_cat=""):

    with open(data_path, 'r') as stream:
        current = yaml.load(stream)

    current[get_category(inp_cat)] += [inp]

    with io.open(data_path, 'w', encoding='utf8') as outfile:
        yaml.dump(current, outfile, default_flow_style=False, allow_unicode=True)

    logger.info(f'added: {get_category(inp_cat)}, {inp}')

def complete(completed_number):

    with open(data_path, 'r') as stream:
        current = yaml.load(stream)

    cat, ind = get_cat_and_subind(current, completed_number)

    logger.info(f'completed: {cat}, {current[cat][ind]}')
    del current[cat][ind]

    with io.open(data_path, 'w', encoding='utf8') as outfile:
        yaml.dump(current, outfile, default_flow_style=False, allow_unicode=True)



def get_category(cat_str):
    category1, category2 = "not urgent", "not critical"
    if 'u' in cat_str:
        category1 = "urgent"
    if 'c' in cat_str:
        category2 = "critical"
    return category1 + " + " + category2


def move(task_number, new_category):

    with open(data_path, 'r') as stream:
        current = yaml.load(stream)

    cat, ind = get_cat_and_subind(current, task_number)
    copy_str = current[cat][ind][:]

    logger.info(f'moved: {copy_str}, {cat} -> {get_category(new_category)}')

    del current[cat][ind]
    current[get_category(new_category)] += [copy_str]

    with io.open(data_path, 'w', encoding='utf8') as outfile:
        yaml.dump(current, outfile, default_flow_style=False, allow_unicode=True)


def edit(task_number, new_text):

    with open(data_path, 'r') as stream:
        current = yaml.load(stream)

    cat, ind = get_cat_and_subind(current, task_number)
    logger.info(f'edited: {current[cat][ind]} -> {new_text}')
    current[cat][ind] = new_text

    with io.open(data_path, 'w', encoding='utf8') as outfile:
        yaml.dump(current, outfile, default_flow_style=False, allow_unicode=True)




# handle console input
import sys

if len(sys.argv) > 1:
    if sys.argv[1] == "update":
        # update()
        pass
    elif sys.argv[1] == "setup":
        setup()
    elif sys.argv[1] == "add":
        if len(sys.argv) > 3:
            add(sys.argv[2], sys.argv[3])
        elif len(sys.argv) > 2:
            add(sys.argv[2], "")
        else:
            print("bad input")
    elif sys.argv[1] == "complete":
        if len(sys.argv) > 2:
            complete(int(sys.argv[2]))
        else:
            print("Must select a task to complete.")
    elif sys.argv[1] == "move":
        if len(sys.argv) > 3:
            move(int(sys.argv[2]), sys.argv[3] )
        elif len(sys.argv) > 2:
            move(int(sys.argv[2]), "" )
        else:
            print("usage: zl move <task> <category>")
    elif sys.argv[1] == "edit":
        if len(sys.argv) == 4:
            edit(int(sys.argv[2]), sys.argv[3])
        else:
            print("usage: zl edit <task> <new text>")
    else:
        print("Command not recognized.")

update()
