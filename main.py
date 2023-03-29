import requests, time, sys
from PIL import Image
from typing import Tuple, List
from rich.progress import Progress

amogus = [
           (1,0), (2,0), (3,0),
    (0,1), (1,1),
    (0,2), (1,2), (2,2), (3,2),
    (0,3), (1,3), (2,3), (3,3),
           (1,4),        (3,4)
]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def usage():
    print(
        """Usage: placebot [OPTIONS] [COORDINATES]
    -i <FILE>       place image from file
    -a <END X>      place amogus line
    -v              place vertically 
    -h --help       display this help and exit
""")


def draw_pixel(x: int, y: int, color: str, progress, task):
    color = color[-2:] + color[2:4] + color[:2]
    requests.post("https://spottedlo8.pl/api/place/pixel", json={
        "x": x,
        "y": y,
        "color": int(color, base=16)
    })
    progress.update(task, advance=1)
    #print(f'[{time.strftime("%H:%M:%S")}] drawn ({x},{y})')
    time.sleep(5)


def draw_amogus(coords: Tuple[int, int], color: str, progress, task):
    task_amogus = progress.add_task("Amogus...", total=len(amogus)+2)
    x, y = coords
    for offx, offy in amogus:
        progress.update(task_amogus, advance=1)
        draw_pixel(x + offx, y + offy, color, progress, task)
    progress.update(task_amogus, advance=1)
    draw_pixel(x + 2, y + 1, "4285f4", progress, task)
    progress.update(task_amogus, advance=1)
    draw_pixel(x + 3, y + 1, "4285f4", progress, task)
    progress.remove_task(task_amogus)


def read_colors():
    with open('colors.txt','r') as f:
        return [i.strip().strip('#\'",.') for i in f.readlines()]


def amogus_line(x: int, y: int, end: int, colt: List[str], vertical: bool = False):
    col = 0
    with Progress() as progress:
        if vertical:
            total = (end-y)//5*(len(amogus)+2)
        else:
            total = (end-x)//4*(len(amogus)+2)
        main_task = progress.add_task("Progress...", total=total)
        while (x + 3 < end and not vertical) or (y+4 <= end and vertical):
            draw_amogus((x, y), colt[col % len(colt)], progress, main_task)
            col += 1
            if vertical:
                y += 5
            else:
                x += 4


def img2pixels(filename: str):
    im = Image.open(filename, 'r')
    i = iter(im.getdata())
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b = next(i)[:3]
            yield x, y, hex(r)[2:] + hex(g)[2:] + hex(b)[2:]


def img_size(filename: str):
    im = Image.open(filename, 'r')
    w, h = im.size
    return w*h


def draw_image(filename: str, coords: Tuple[int, int]):
    x, y = coords
    with Progress() as progress:
        task=progress.add_task("Progress...", total=img_size(filename))
        for offx, offy, color in img2pixels(filename):
            draw_pixel(x + offx, y + offy, color, progress, task)


if __name__ == '__main__':
    vert = False
    coords = ()
    arg = None
    await_arg = False
    action = None
    if len(sys.argv) == 1:
        eprint("Too few arguments")
        usage()
        exit(1)
    if sys.argv[1] in ("-h", "--help"):
        usage()
        exit()
    for i in sys.argv[1:]:
        if await_arg:
            if action == 'a':
                arg = int(i)
            else:
                arg = i
            await_arg = False
        else:
            if i.startswith('-'):
                for j in i:
                    match j:
                        case "v":
                            vert = True
                        case "a":
                            await_arg = True
                            action = "a"
                        case "i":
                            await_arg = True
                            action = "i"
            else:
                if len(coords) < 2:
                    coords += (int(i),)
                else:
                    eprint("Coordinates should be an X Y pair")
                    usage()
                    exit(1)
    if len(coords) < 2:
        eprint("Coordinates should be an X Y pair")
        usage()
        exit(1)
    match action:
        case "a":
            amogus_line(*coords, arg, read_colors(), vert)
        case "i":
            draw_image(arg, coords)
        case None:
            eprint("Invalid action")
            usage()
            exit(1)

