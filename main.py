import requests, time, sys
from PIL import Image
from typing import Tuple
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


def amogus_line(x: int, y: int, end: int):
    colt = ["2dd354", "fcd015", "f7931e", "ef4037", "b442cc", "1a1a1a"]
    col = 0
    with Progress() as progress:
        main_task = progress.add_task("Progress...", total=(end-x)//4*(len(amogus)+2))
        while x + 3 < end:
            draw_amogus((x, y), colt[col % len(colt)], progress, main_task)
            col += 1
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
    if len(sys.argv) == 1:
        eprint("Too few arguments")
        usage()
        exit(1)
    if sys.argv[1] in ("-h", "--help"):
        usage()
        exit()
    if len(sys.argv) < 5:
        eprint("Too few arguments")
        usage()
        exit(1)
    if len(sys.argv) > 5:
        eprint("Too many arguments")
        usage()
        exit(1)
    if sys.argv[1] == "-a":
        amogus_line(int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[2]))
    if sys.argv[1] == "-i":
        draw_image(sys.argv[2], (int(sys.argv[3]), int(sys.argv[4])))
    #draw_image('boty.png', (0, 150))
