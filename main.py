import flet as ft
import minecraft_launcher_lib as mc
import os
import views

mc_dir = mc.utils.get_minecraft_directory()
user_file = os.path.join(mc_dir, "user.json")

def main(page: ft.Page):
    page.title = "Minecraft Launcher"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.update()

    routes = {
        "/": lambda: views.view_initial(page),
        "/loaders": lambda: views.view_loaders(page),
        "/vanilla": lambda: views.view_vanilla(page),
        "/forge": lambda: views.view_forge(page),
        "/create_instance": lambda: views.view_create_instance(page),
        "/successful_installation": lambda: views.view_successful_installation,
        "/instances": lambda: views.view_instances(page),
        "/others": lambda: views.view_other_options(page),
        "/mods": lambda: views.view_mods(page),
        "/texture": lambda: views.view_textures(page),
        "/shaders": lambda: views.view_shaders(page)
    }

    def change_route(e):
        if e.route.startswith("/edit_instance/"):
            file = e.route.split("/edit_instance/")[1]
            view = lambda: views.view_edit_instance(page, file)
        else:
            view = routes.get(e.route)

        if view:
            if not page.views or page.views[-1].route != e.route:
                page.views.append(view())
                page.update()

    def return_back(e):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
        else:
            page.go("/")

    page.on_route_change = change_route
    page.on_view_pop = return_back
    page.go("/")


ft.app(target=main)
