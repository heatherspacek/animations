import tkinter as tk

def lerp_2d(p1, p2, t):
    x = p1[0] + (p2[0] - p1[0]) * t
    y = p1[1] + (p2[1] - p1[1]) * t
    return (x, y)


def draw_circle(y, z, r):
    a,b,c,d = y-r, z-r, y+r, z+r
    viewscale = 7
    a *= viewscale
    b *= viewscale
    c *= viewscale
    d *= viewscale
    canvas.create_oval(a,b,c,d)


def draw_capsule(y1, z1, y2, z2, size):
    for t in [a/9 for a in range(10)]:
        x, y = lerp_2d((y1, z1), (y2, z2), t)
        draw_circle(x, y, size)


if __name__ == "__main__":

    with open("da.crds") as f:
        coords_raw = f.read().splitlines()
    from itertools import groupby

    sep = "==="
    frames = [list(g) for k, g in groupby(coords_raw, lambda x: x == sep) if not k]

    root = tk.Tk()
    root.title("Basic Canvas Drawing")

    canvas = tk.Canvas(root, width=400, height=300, bg="white")
    canvas.pack()

    i = 0

    def update_canvas(i):
        canvas.delete("all")
        draw_i = len(frames)-1 if i >= len(frames)-1 else i
        bones = frames[draw_i]

        for bone_str in bones:
            bones_floats = [float(b) for b in bone_str.split(",")]
            (x1, y1, z1, x2, y2, z2, scale) = bones_floats
            draw_capsule(z1, 20-y1, z2, 20-y2, scale)

        i += 1
        print(i)
        canvas.after(100, update_canvas, i)
    canvas.after(100, update_canvas, i)

    root.mainloop()
