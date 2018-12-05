from wallpaper_tools import *

import yaml
import io
import pickle

def number(list_of_things, start_ind=1):
    return [f"{start_ind+i}. {item_in_list}" for i, item_in_list in enumerate(list_of_things)]


def setup():
    boxwidth = 1400
    boxheight = 800
    origin_x = 3000
    origin_y = 250
    margin = 50

    drive = "c:\\"
    folder = "Users\\xzack\\Projects\\zl\\wallpapers"
    image = "joanna-kosinska-289519-unsplash.jpg"
    image_path = os.path.join(drive, folder, image)
    img = Image.open(image_path)


    topleft = Textbox(x=origin_x, y=origin_y,
                      w=boxwidth, h=boxheight,
                      fontsize=72)
    topright = Textbox(x=origin_x+boxwidth+margin, y=origin_y,
                       w=boxwidth, h=boxheight,
                       fontsize=72)
    bottomleft = Textbox(x=origin_x, y=origin_y+boxheight+margin,
                       w=boxwidth, h=boxheight,
                       fontsize=72)
    bottomright = Textbox(x=origin_x+boxwidth+margin, y=origin_y+boxheight+margin,
                       w=boxwidth, h=boxheight,
                       fontsize=72)


    drive="c:\\"
    folder="Users\\xzack\\Projects\\zl"
    fontfile = "Inconsolata.otf"
    fontsize = 72
    fontpath = os.path.join(drive, folder, fontfile)
    font = ImageFont.truetype(fontpath, fontsize)

    img = topleft.draw(img, text="", font=font,
                      toptext="urgent", lefttext="critical", bg=True)
    img = topright.draw(img, text="", font=font, toptext="not urgent", bg=True)
    img = bottomleft.draw(img, text="", font=font, lefttext="not critical", bg=True)
    img = bottomright.draw_bg(img)

    import pickle
    drive = "c:\\"
    folder = "Users\\xzack\\Projects\\zl"
    pickled = { "img": img,
        "textboxes": (topleft, topright, bottomleft, bottomright) }
    pickle.dump( pickled, open( os.path.join(drive, folder, "save.p"), "wb" ) )


def update():

    drive="c:\\"
    folder="Users\\xzack\\Projects\\zl"
    fontfile = "Inconsolata.otf"
    fontsize = 72
    fontpath = os.path.join(drive, folder, fontfile)
    font = ImageFont.truetype(fontpath, fontsize)

    pickled = pickle.load( open(os.path.join(drive, folder, "save.p" ),"rb") )
    img = pickled["img"]
    topleft, topright, bottomleft, bottomright = pickled["textboxes"]


    with open("data.yaml", 'r') as stream:
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

    img.save('sample-out.jpg')
    set_background('sample-out.jpg')

def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

def complete(completed_number):
    with open("data.yaml", 'r') as stream:
        current = yaml.load(stream)

    categories = ["urgent + critical", "not urgent + critical",
        "urgent + not critical", "not urgent + not critical"]
    inds = flatten([ list(range(len(current[cat]))) for cat in categories])
    cats = flatten([ [cat] * len(current[cat]) for cat in categories ])

    i = completed_number - 1
    del current[cats[i]][inds[i]]

    with io.open('data.yaml', 'w', encoding='utf8') as outfile:
        yaml.dump(current, outfile, default_flow_style=False, allow_unicode=True)

# handle console input
import sys

if len(sys.argv) > 1:
    if sys.argv[1] == "update":
        update()
    elif sys.argv[1] == "setup":
        setup()
    elif sys.argv[1] == "add":
        with open("data.yaml", 'r') as stream:
            current = yaml.load(stream)

        if len(sys.argv) > 2:
            category1, category2 = "not urgent", "not critical"
            if len(sys.argv) > 3:
                if 'u' in sys.argv[3]:
                    category1 = "urgent"
                if 'c' in sys.argv[3]:
                    category2 = "critical"
            current[category1 + " + " + category2] += [sys.argv[2]]

        with io.open('data.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(current, outfile, default_flow_style=False, allow_unicode=True)
    elif sys.argv[1] == "complete":
        if len(sys.argv) > 2:
            complete(int(sys.argv[2]))
        else:
            print("Must select a task to complete.")
    else:
        print("Command not recognized.")
