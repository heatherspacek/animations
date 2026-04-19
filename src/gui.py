import dearpygui.dearpygui as dpg

from animations import data_dump, HitBoxProcessed, HurtBoxProcessed
from vis import lerp_2d

PLAYING = False


def vis_window_setup(chars, anims, bighurt, bighit):  # debug signature
    dpg.create_context()

    def left_panel():
        dpg.add_spacer(tag="data_dummy", user_data=(bighurt, bighit))
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
        dpg.add_combo(chars, tag="char_combo", callback=on_character_choice, user_data=chars)
        dpg.add_combo([], tag="anim_combo", callback=on_animation_choice, user_data=anims)
        dpg.add_button(label="Retrieve", callback=None)

    def right_panel():
        with dpg.drawlist(250, 250, tag="dlist", user_data=()):
            dpg.draw_rectangle(pmin=[25, 25], pmax=[225, 225])
        dpg.add_slider_int(min_value=0, max_value=1, width=200, tag="slider",
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
            dpg.set_value(
                "slider",
                (dpg.get_value("slider")+1)
                % (dpg.get_item_configuration("slider")["max_value"])
            )
            on_slider_change()
        dpg.render_dearpygui_frame()
    dpg.destroy_context()


def toggle_play():
    global PLAYING
    PLAYING = not PLAYING


def dpg_draw_capsule(y1, z1, y2, z2, size):
    for t in [a/9 for a in range(10)]:
        x, y = lerp_2d((y1, z1), (y2, z2), t)
        dpg.draw_circle([x, y], size, parent="dlist")


def on_character_choice():
    anims = dpg.get_item_user_data("anim_combo")
    chars = dpg.get_item_user_data("char_combo")
    selection = dpg.get_value("char_combo")
    char_index = chars.index(selection)
    (bighurt, _) = dpg.get_item_user_data("data_dummy")
    filtered_anim_list = [
        a
        for a, lst in zip(anims[char_index], bighurt[char_index])
        if lst  # non-empty
    ]
    dpg.configure_item("anim_combo", items=filtered_anim_list)


def on_animation_choice():
    char_selection = dpg.get_value("char_combo")
    char_index = dpg.get_item_user_data("char_combo").index(char_selection)
    anim_selection = dpg.get_value("anim_combo")
    anim_index = dpg.get_item_user_data("anim_combo")[char_index].index(anim_selection)
    (bighurt, bighit) = dpg.get_item_user_data("data_dummy")
    hurt_list = bighurt[char_index][anim_index]
    hit_list = bighit[char_index][anim_index]
    dpg.set_item_user_data("dlist", (hurt_list, hit_list))
    dpg.configure_item("slider", max_value=len(hurt_list)-1)
    on_slider_change()


def on_slider_change():
    DRAW_SCALE = 4.5
    # Clear canvas
    dpg.delete_item("dlist", children_only=True)
    # Draw the frameee
    frame_n = dpg.get_value("slider")

    hurt_list, hit_list = dpg.get_item_user_data("dlist")
    for bone_struct in hurt_list[frame_n]:
        x1, y1, z1 = bone_struct.pos_a
        x2, y2, z2 = bone_struct.pos_b
        scale = bone_struct.size
        # bones_floats = [float(b) for b in bone_str.split(",")]
        # (x1, y1, z1, x2, y2, z2, scale) = bones_floats
        dpg_draw_capsule(90+z1 * DRAW_SCALE,
                         135-y1 * DRAW_SCALE,
                         90+z2 * DRAW_SCALE,
                         135-y2 * DRAW_SCALE,
                         scale * DRAW_SCALE
                         )

    for hitbox_struct in hit_list:
        # hit_floats = [float(h) for h in hitbox_str.split(",")]
        if hitbox_struct.frame_i != frame_n:
            continue
        x1, y1, z1 = [a * DRAW_SCALE for a in hitbox_struct.pos]
        r1 = hitbox_struct.size * DRAW_SCALE
        dpg.draw_circle([90+z1, 135-y1], r1, color=[255, 0, 0], parent="dlist")


if __name__ == "__main__":

    # Later, this will be a retrieve-from-db!
    (chars, anims, bighurt, bighit) = data_dump(
        "/home/heather/Documents/Disk Images/Super Smash Bros. Melee (v1.02).iso"
    )

    vis_window_setup(chars, anims, bighurt, bighit)
