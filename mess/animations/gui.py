import tkinter as tk
from tkinter import filedialog

import dearpygui.dearpygui as dpg
from platformdirs import user_cache_path

from mess.animations.vis import lerp_2d
from mess.animations.data import (
    retrieve_character_data,
    retrieve_move_data,
    name_to_internal_id,
    decorate_action_names,
)

PLAYING = False
CACHE_PATH = user_cache_path(
    "mess.animations",
    "Heather Spacek",
    ensure_exists=True
)


def vis_window_setup(chars):
    dpg.create_context()

    with dpg.font_registry():
        dpg.add_font("res/NotoSans-Regular.ttf", size=16*2, tag="default_font")
    dpg.bind_font("default_font")
    dpg.set_global_font_scale(0.5)

    with dpg.window(tag="win", width=500, height=700):
        dpg.add_file_dialog(
            directory_selector=True, show=False, callback=lambda x: _,
            tag="file_dialog_id", cancel_callback=lambda x: _, width=700,
            height=400
        )
        dpg.add_button(
            label="Choose location of SSBM disk backup...",
            callback=select_iso
        )
        with dpg.group(horizontal=True):
            dpg.add_text("Backup file path: ")
            dpg.add_text("(None chosen)", tag="loaded_iso_path")
        dpg.add_combo(chars, tag="char_combo", callback=on_character_choice, width=-1)
        dpg.add_combo([], tag="anim_combo", callback=on_animation_choice, width=-1, height_mode=dpg.mvComboHeight_Large)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Play/Pause",
                callback=toggle_play,
                width=100
            )
            dpg.add_spacer(width=50)
            dpg.add_button(label=" - ", callback=frame_minus_button)
            dpg.add_slider_int(
                min_value=0,
                max_value=1,
                width=150,
                tag="slider",
                callback=on_slider_change
            )
            dpg.add_button(label=" + ", callback=frame_plus_button)

        with dpg.drawlist(500, 500, tag="dlist", user_data=()):
            dpg.draw_rectangle(pmin=[25, 25], pmax=[475, 475])

    # #######################################################
    dpg.create_viewport(title="mess.animations.gui", width=700, height=700)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("win", True)

    # Startup state-check.
    try:
        with open(CACHE_PATH / "last_seen_iso_path", 'r') as f:
            last_seen_iso_path = f.read()
    except FileNotFoundError:
        # no last-seen
        disable_all()
    else:
        dpg.set_value("loaded_iso_path", last_seen_iso_path)

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
    selection = dpg.get_value("char_combo")
    iso_path = dpg.get_value("loaded_iso_path")
    anims_list, hurts_list, _ = retrieve_character_data(
        iso_path,
        name_to_internal_id(selection)
    )
    filtered_anim_list = decorate_action_names(anims_list, hurts_list)

    dpg.configure_item("anim_combo", items=filtered_anim_list)


def on_animation_choice():
    char_selection = dpg.get_value("char_combo")
    anim_selection = dpg.get_value("anim_combo")
    iso_path = dpg.get_value("loaded_iso_path")
    anims_list, _, _ = retrieve_character_data(
        iso_path,
        name_to_internal_id(char_selection)
    )
    hurts, hits = retrieve_move_data(
        iso_path,
        name_to_internal_id(char_selection),
        anims_list.index(anim_selection)
    )

    dpg.set_item_user_data("dlist", (hurts, hits))
    dpg.configure_item("slider", max_value=len(hurts)-1)
    on_slider_change()


def on_slider_change():
    DRAW_SCALE = 15
    # Clear canvas
    dpg.delete_item("dlist", children_only=True)
    dpg.draw_rectangle(pmin=[25, 25], pmax=[475, 475], parent="dlist")
    # Draw the frameee
    frame_n = dpg.get_value("slider")

    hurt_list, hit_list = dpg.get_item_user_data("dlist")
    for bone_struct in hurt_list[frame_n]:
        x1, y1, z1 = bone_struct.pos_a
        x2, y2, z2 = bone_struct.pos_b
        scale = bone_struct.size
        # bones_floats = [float(b) for b in bone_str.split(",")]
        # (x1, y1, z1, x2, y2, z2, scale) = bones_floats
        dpg_draw_capsule(190+z1 * DRAW_SCALE,
                         335-y1 * DRAW_SCALE,
                         190+z2 * DRAW_SCALE,
                         335-y2 * DRAW_SCALE,
                         scale * DRAW_SCALE
                         )

    for hitbox_struct in hit_list:
        # hit_floats = [float(h) for h in hitbox_str.split(",")]
        if hitbox_struct.frame_i != frame_n:
            continue
        x1, y1, z1 = [a * DRAW_SCALE for a in hitbox_struct.pos]
        r1 = hitbox_struct.size * DRAW_SCALE
        dpg.draw_circle([190+z1, 335-y1], r1, color=[255, 0, 0], parent="dlist")


def frame_minus_button():
    wraparound = dpg.get_value("slider") - 1
    if wraparound < 0:
        wraparound = dpg.get_item_configuration("slider")["max_value"]
    dpg.set_value("slider", wraparound)
    on_slider_change()


def frame_plus_button():
    wraparound = dpg.get_value("slider") + 1
    _max = dpg.get_item_configuration("slider")["max_value"]
    if wraparound > _max:
        wraparound = 0
    dpg.set_value("slider", wraparound)
    on_slider_change()


def select_iso():
    # Hide a tkinter root window.
    # This lets us use an OS-native (-ish) folder selection dialog.
    # (On Windows this should look full native. There's a nice fallback
    # on non-Windows that's superior to the DPG one.)
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askopenfilename(
        title="Choose location of SSBM backup image",
        initialdir=".",
        filetypes=[("GameCube Disk Image Backup", "*.iso")]
    )
    if folder_selected is not None:
        try:
            _ = retrieve_character_data(folder_selected, 1)
        except Exception:
            dpg.set_value("loaded_iso_path", "** Issue reading the chosen file.")
            disable_all()
        else:
            with open(CACHE_PATH / "last_seen_iso_path", 'w') as f:
                f.write(folder_selected)
            dpg.set_value("loaded_iso_path", folder_selected)
            enable_all()


def enable_all():
    dpg.enable_item("slider")
    dpg.enable_item("char_combo")
    dpg.enable_item("anim_combo")


def disable_all():
    dpg.disable_item("slider")
    dpg.disable_item("char_combo")
    dpg.disable_item("anim_combo")


if __name__ == "__main__":

    # fmt: off
    chars = [
        "Fox", "Falco", "Marth", "Captain Falcon", "Sheik", "Peach",
        "Jigglypuff", "Popo", "Yoshi", "Pikachu", "Luigi", "Samus",
        "Donkey Kong", "Ganondorf", "Dr. Mario", "Link", "Mario",
        "Mr. Game and Watch", "Young Link", "Pichu", "Roy", "Mewtwo",
        "Zelda", "Ness", "Bowser", "Kirby",
    ]
    # fmt: on
    vis_window_setup(chars)
