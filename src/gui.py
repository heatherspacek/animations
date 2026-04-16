import dearpygui.dearpygui as dpg


PLAYING = False


def vis_window_setup():
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
        with dpg.drawlist(200, 200) as dlist:
            dpg.draw_rectangle(pmin=[15, 15], pmax=[185, 185])
        dpg.add_slider_int(min_value=0, max_value=75, width=200, tag="slider")
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
            dpg.set_value("slider", dpg.get_value("slider")+1)

        dpg.render_dearpygui_frame()
    dpg.destroy_context()


def process_data():
    ...


def toggle_play():
    global PLAYING
    PLAYING = not PLAYING


if __name__ == "__main__":

    

    vis_window_setup()
