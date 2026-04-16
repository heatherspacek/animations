import tkinter as tk

def lerp_2d(p1, p2, t):
    x = p1[0] + (p2[0] - p1[0]) * t
    y = p1[1] + (p2[1] - p1[1]) * t
    return (x, y)


def draw_circle(y, z, r, color="black"):
    a, b, c, d = y-r, z-r, y+r, z+r

    def view_transform(x):
        viewscale = 7
        viewoffset = 50
        return (x*viewscale) + viewoffset
    a = view_transform(a)
    b = view_transform(b)
    c = view_transform(c)
    d = view_transform(d)
    canvas.create_oval(a, b, c, d, outline=color)


def draw_capsule(y1, z1, y2, z2, size):
    for t in [a/9 for a in range(10)]:
        x, y = lerp_2d((y1, z1), (y2, z2), t)
        draw_circle(x, y, size)


if __name__ == "__main__":
    from itertools import groupby

    with open("da2.crds") as f:
        coords_raw = f.read().splitlines()

    sep = "==="
    frames = [list(g) for k, g in groupby(coords_raw, lambda x: x == sep) if not k]

    with open("hit.crds") as f:
        hitbox_coords_raw = f.read().splitlines()

    hits = []
    frame_ctr = -1
    for hb_line in hitbox_coords_raw:
        if hb_line == sep:
            frame_ctr += 1
            hits.append([])
        else:
            hits[frame_ctr].append(hb_line)
    breakpoint()

    root = tk.Tk()
    root.title("Basic Canvas Drawing")

    canvas = tk.Canvas(root, width=400, height=300, bg="white")
    canvas.pack()

    i = 0

    def update_canvas(i):
        canvas.delete("all")
        draw_i = len(frames)-1 if i >= len(frames)-1 else i
        bones = frames[draw_i]
        hitboxes = hits[draw_i]

        for bone_str in bones:
            bones_floats = [float(b) for b in bone_str.split(",")]
            (x1, y1, z1, x2, y2, z2, scale) = bones_floats
            draw_capsule(z1, 15-y1, z2, 15-y2, scale)
        for hitbox_str in hitboxes:
            hit_floats = [float(h) for h in hitbox_str.split(",")]
            x1 = hit_floats[7]
            y1 = hit_floats[8]
            z1 = hit_floats[9]
            r1 = hit_floats[10]
            draw_circle(z1, 15-y1, r1, color="red")
        i += 1
        print(i)
        canvas.after(100, update_canvas, i)
    canvas.after(100, update_canvas, i)

    root.mainloop()
