import requests, time
from PIL import Image
from typing import Tuple

amogus = [
           (1,0), (2,0), (3,0),
    (0,1), (1,1),
    (0,2), (1,2), (2,2), (3,2),
    (0,3), (1,3), (2,3), (3,3),
           (1,4),        (3,4)
]


def draw_pixel(x: int, y: int, color: str):
    color = color[-2:] + color[2:4] + color[:2]
    requests.post("https://spottedlo8.pl/api/place/pixel", json={
        "x": x,
        "y": y,
        "color": int(color,base=16)
    })
    print(f'[{time.strftime("%H:%M:%S")}] drawn ({x},{y})')
    time.sleep(5)


def draw_amogus(coords: Tuple[int, int], color: str):
    x,y=coords
    for offx, offy in amogus:
        draw_pixel(x+offx,y+offy,color)
    draw_pixel(x + 2,y + 1,"4285f4")
    draw_pixel(x + 3,y + 1,"4285f4")


def amogus_line(i: int,y: int):
    colt = ["2dd354", "fcd015", "f7931e", "ef4037", "b442cc", "1a1a1a"]
    col = 0
    while i < 197:
        draw_amogus((i, y), colt[col % len(colt)])
        col += 1
        i += 4


def img2pixels(filename: str):
    im = Image.open(filename, 'r')
    i = iter(im.getdata())
    w,h = im.size
    for y in range(h):
        for x in range(w):
            r,g,b = next(i)[:3]
            yield x,y,hex(r)[2:]+hex(g)[2:]+hex(b)[2:]


def draw_image(filename: str, coords: Tuple[int, int]):
    x,y = coords
    for offx,offy,color in img2pixels(filename):
        draw_pixel(x+offx,y+offy,color)

if __name__ == '__main__':
    draw_image('boty.png',(0,150))


