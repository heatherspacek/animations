import tkinter as tk
import itertools

if __name__ == "__main__":

    with open("verts.crds") as f:
        coords_raw = f.read().splitlines()
    from itertools import groupby

    sep = "==="
    frames = [list(g) for k, g in groupby(coords_raw, lambda x: x == sep) if not k]

    root = tk.Tk()
    root.title("Basic Canvas Drawing")

    canvas = tk.Canvas(root, width=600, height=800, bg="white")
    canvas.pack()

    i = 0

    def update_canvas(i):
        canvas.delete("all")
        draw_i = len(frames)-1 if i >= len(frames)-1 else i
        this_frame = frames[draw_i]

        for v1, v2, v3 in itertools.batched(this_frame, 3):
            (x1, y1, z1) = [float(b) for b in v1.split(",")]
            (x2, y2, z2) = [float(b) for b in v2.split(",")]
            (x3, y3, z3) = [float(b) for b in v3.split(",")]
            # projected_1_x = 50 + 1500*(x1/(z1+100))
            # projected_1_y = 50 + 1500*(y1/(z1+100))
            # projected_2_x = 50 + 1500*(x2/(z2+100))
            # projected_2_y = 50 + 1500*(y2/(z2+100))
            # projected_3_x = 50 + 1500*(x3/(z3+100))
            # projected_3_y = 50 + 1500*(y3/(z3+100))

            # canvas.create_line(projected_1_x, projected_1_y, projected_2_x, projected_2_y)
            # canvas.create_line(projected_2_x, projected_2_y, projected_3_x, projected_3_y)
            # canvas.create_line(projected_3_x, projected_3_y, projected_1_x, projected_1_y)
            eps = 0.02
            scale = 40
            x_offset = 5
            canvas.create_oval(scale*(x_offset + x1-eps),
                               scale*(z1-eps),
                               scale*(x_offset + x1+eps),
                               scale*(z1+eps)
                               )
            canvas.create_oval(scale*(x_offset + x2-eps),
                               scale*(z2-eps),
                               scale*(x_offset + x2+eps),
                               scale*(z2+eps)
                               )
            canvas.create_oval(scale*(x_offset + x3-eps),
                               scale*(z3-eps),
                               scale*(x_offset + x3+eps),
                               scale*(z3+eps)
                               )
        # breakpoint()
        i += 1
        print(i)
        # canvas.after(100, update_canvas, i)
    canvas.after(100, update_canvas, i)

    root.mainloop()
