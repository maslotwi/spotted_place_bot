import requests, time, sys
from PIL import Image
from typing import Tuple, List, Callable
from rich.progress import Progress, BarColumn, TimeElapsedColumn
from os import path
from queue import Queue

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
    -s              launch the server
    -c              launch the client
""")


def draw_pixel(x: int, y: int, color: str, progress=None, task=None):
    color = color[-2:] + color[2:4] + color[:2]
    requests.post("https://spottedlo8.pl/api/place/pixel", json={
        "x": x,
        "y": y,
        "color": int(color, base=16)
    })
    if progress is not None:
        progress.update(task, advance=1)
    #print(f'[{time.strftime("%H:%M:%S")}] drawn ({x},{y})')
    time.sleep(5)


def draw_amogus(coords: Tuple[int, int], color: str, canvas: Callable, progress=None, task=None):
    if progress is not None:
        task_amogus = progress.add_task("Amogus...", total=len(amogus) + 2)
        x, y = coords
        for offx, offy in amogus:
            progress.update(task_amogus, advance=1)
            canvas(x + offx, y + offy, color, progress, task)
        progress.update(task_amogus, advance=1)
        canvas(x + 2, y + 1, "4285f4", progress, task)
        progress.update(task_amogus, advance=1)
        canvas(x + 3, y + 1, "4285f4", progress, task)
        progress.remove_task(task_amogus)
    else:
        x, y = coords
        for offx, offy in amogus:
            canvas(x + offx, y + offy, color, progress, task)
        canvas(x + 2, y + 1, "4285f4", progress, task)
        canvas(x + 3, y + 1, "4285f4", progress, task)


def read_colors():
    with open('colors.txt', 'r') as f:
        return [i.strip().strip('#\'",.') for i in f.readlines()]


def amogus_line(x: int, y: int, end: int, colt: List[str], canvas: Callable, vertical: bool = False):
    global Total_pixels, Drawn_pixels
    col = 0
    if canvas == draw_pixel:
        with Progress() as progress:
            if vertical:
                total = (end - y) // 5 * (len(amogus) + 2)
            else:
                total = (end - x) // 4 * (len(amogus) + 2)
            main_task = progress.add_task("Progress...", total=total)
            while (x + 3 < end and not vertical) or (y + 4 <= end and vertical):
                draw_amogus((x, y), colt[col % len(colt)], canvas, progress, main_task)
                col += 1
                if vertical:
                    y += 5
                else:
                    x += 4
    else:
        if vertical:
            total = (end - y) // 5 * (len(amogus) + 2)
        else:
            total = (end - x) // 4 * (len(amogus) + 2)
        Total_pixels = total
        while (x + 3 < end and not vertical) or (y + 4 <= end and vertical):
            draw_amogus((x, y), colt[col % len(colt)], canvas)
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
    return w * h


def draw_image(filename: str, coords: Tuple[int, int], canvas: Callable):
    global Total_pixels, Drawn_pixels
    x, y = coords
    if canvas == add_task:
        Total_pixels = img_size(filename)
        for offx, offy, color in img2pixels(filename):
            canvas(x + offx, y + offy, color)
        return
    with Progress() as progress:
        task = progress.add_task("Progress...", total=img_size(filename))
        for offx, offy, color in img2pixels(filename):
            canvas(x + offx, y + offy, color, progress, task)


def add_task(x: int, y: int, color: str, progress=None, task=None):
    global Drawn_pixels
    Task_queue.put({
        "x": x,
        "y": y,
        "color": color,
        "progress": Drawn_pixels / Total_pixels,
        "status": "drawing"
    })
    Drawn_pixels += 1
    if progress is not None:
        progress.update(task, advance=1)
    # print(f'[{time.strftime("%H:%M:%S")}] drawn ({x},{y})')

def get_refiller(fun,*args,**kwargs):
    def refiller():
        fun(*args,**kwargs)
    return refiller


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
                        case "s":
                            action = "s"
                            await_arg = True
                        case "c":
                            action = "c"
                            await_arg = True
            else:
                if len(coords) < 2:
                    coords += (int(i),)
                else:
                    eprint("Coordinates should be an X Y pair")
                    usage()
                    exit(1)
    if len(coords) < 2 and action not in "sc":
        eprint("Coordinates should be an X Y pair")
        usage()
        exit(1)
    match action:
        case None:
            eprint("Invalid action")
            usage()
            exit(1)
        case "a":
            amogus_line(*coords, arg, read_colors(), draw_pixel, vert)
        case "i":
            draw_image(arg, coords, draw_pixel)
        case "c":
            with Progress(Progress.get_default_columns()[0],
                          BarColumn(),
                          Progress.get_default_columns()[2],
                          TimeElapsedColumn()) as progress:
                px = 0
                t1 = progress.add_task("You contributed 0 pixels, total progress:", total=1)
                while True:
                    data = requests.get(path.join(arg, "task")).json()
                    if data['status'] == "drawing":
                        progress.update(t1,
                                        completed=data['progress'],
                                        description=f"You contributed {px} pixel{'s' if px != 1 else ''}, total progress:")
                        draw_pixel(data['x'], data['y'], data['color'])
                        px += 1
                    else:
                        time.sleep(5)
        case "s":
            from flask import Flask, redirect,request, abort

            app = Flask(__name__)


            @app.route("/")
            def main_page():
                return redirect("/static/index.html")


            @app.route("/task")
            def get_task():
                if not Task_queue.empty():
                    return Task_queue.get()
                if Loop:
                    refill()
                    if not Task_queue.empty():
                        return Task_queue.get()
                return {"status": "idle"}

            @app.route('/request', methods=['POST'])
            def set_task():
                if request.form["passwd"] != arg:
                    abort(401)
                    return "<h1>401 UNAUTHORIZED</h1>"
                global refill
                vert = False
                global Loop
                if "loop" in request.form:
                    Loop = True
                else:
                    Loop = False
                if "vert" in request.form:
                    vert = True
                if request.form["mode"] == "amogus":
                    refill = get_refiller(amogus_line,int(request.form["x"]), int(request.form["y"]), int(request.form["arg"]), clrs, add_task,vert)
                else:
                    refill = get_refiller(draw_image,request.form["arg"], (int(request.form["x"]), int(request.form["y"])), add_task)
                refill()
                return redirect("/static/index.html")

            clrs = read_colors()
            Task_queue = Queue()
            Total_pixels = 0
            Drawn_pixels = 0
            Loop = False
            refill = lambda: Task_queue.put({"status":"idle"})
            app.run()