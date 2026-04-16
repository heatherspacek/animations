import dearpygui.dearpygui as dpg

from vis import hitboxes_from_file, hurtboxes_from_file, lerp_2d

PLAYING = False


def vis_window_setup(hit, hurt):  # debug signature
    dpg.create_context()

    def left_panel():
        dpg.add_file_dialog(
            directory_selector=True, show=False, callback=lambda x: _,
            tag="file_dialog_id", cancel_callback=lambda x: _, width=700,
            height=400
        )
        dpg.add_button(
            label="Location of SSBM disc backup...",
            callback=lambda: dpg.show_item("file_dialog_id")
        )
        dpg.add_text("Backup location: (None chosen)")
        dpg.add_combo(["fox", "marth", "falco"])
        dpg.add_combo(["56", "27"])
        dpg.add_button(label="Retrieve", callback=process_data)

    def right_panel():
        with dpg.drawlist(200, 200, tag="dlist", user_data=(hit, hurt)):
            dpg.draw_rectangle(pmin=[15, 15], pmax=[185, 185])
        dpg.add_slider_int(min_value=0, max_value=len(hurt)-1, width=200, tag="slider",
                           callback=on_slider_change)
        dpg.add_button(
            label="Play animation",
            callback=toggle_play
        )

    with dpg.window(tag="win", width=700, height=700):
        with dpg.group(horizontal=True) as _:
            with dpg.group():
                left_panel()
            with dpg.group():
                right_panel()

    # #######################################################
    dpg.create_viewport(title="Tool1", width=700, height=700)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("win", True)

    while dpg.is_dearpygui_running():
        if PLAYING:
            dpg.set_value("slider", (dpg.get_value("slider")+1) % (len(hurt)-1))
            on_slider_change()
        dpg.render_dearpygui_frame()
    dpg.destroy_context()


def process_data():
    ...


def toggle_play():
    global PLAYING
    PLAYING = not PLAYING


def dpg_draw_capsule(y1, z1, y2, z2, size):
    for t in [a/9 for a in range(10)]:
        x, y = lerp_2d((y1, z1), (y2, z2), t)
        dpg.draw_circle([x, y], size, parent="dlist")


def on_slider_change():
    DRAW_SCALE = 4.5
    # Clear canvas
    dpg.delete_item("dlist", children_only=True)
    # Draw the frameee
    frame_n = dpg.get_value("slider")
    (hit, hurt) = dpg.get_item_user_data("dlist")
    bones = hurt[frame_n]
    hitboxes = hit[frame_n]

    for bone_str in bones:
        bones_floats = [float(b) for b in bone_str.split(",")]
        (x1, y1, z1, x2, y2, z2, scale) = bones_floats
        dpg_draw_capsule(90+z1 * DRAW_SCALE,
                         135-y1 * DRAW_SCALE,
                         90+z2 * DRAW_SCALE,
                         135-y2 * DRAW_SCALE,
                         scale * DRAW_SCALE
                         )
    for hitbox_str in hitboxes:
        hit_floats = [float(h) for h in hitbox_str.split(",")]
        x1 = hit_floats[7] * DRAW_SCALE
        y1 = hit_floats[8] * DRAW_SCALE
        z1 = hit_floats[9] * DRAW_SCALE
        r1 = hit_floats[10] * DRAW_SCALE
        dpg.draw_circle([90+z1, 135-y1], r1, color=[255, 0, 0], parent="dlist")


if __name__ == "__main__":
    hit = hitboxes_from_file("output_hitboxes.crd")
    hurt = hurtboxes_from_file("output_hurtboxes.crd")
    vis_window_setup(hit, hurt)
