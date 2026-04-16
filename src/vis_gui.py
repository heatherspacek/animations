import dearpygui.dearpygui as dpg


def vis_window_setup():
    dpg.create_context()

    def left_panel():
        dpg.add_combo(["fox", "marth", "falco"])
        dpg.add_combo(["56", "27"])

    def right_panel():
        with dpg.drawlist(200, 200) as dlist:
            dpg.draw_rectangle(pmin=[15, 15], pmax=[185, 185])
        dpg.add_slider_int(min_value=0, max_value=75)

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
        dpg.render_dearpygui_frame()
    dpg.destroy_context()


if __name__ == "__main__":
    vis_window_setup()
