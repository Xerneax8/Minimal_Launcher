import asyncio
import json
import os
import shutil
import sys
import flet as ft
import minecraft_launcher_lib as mc
import users
from utils import create_alert, start_game, change_dialog_open, close_popup, save_new_name, view_message, view_loading

mc_dir = mc.utils.get_minecraft_directory()
user_file = os.path.join(mc_dir, "user.json")


def view_initial(page):
    user = users.load_user()
    last_instance_name = user.get("last_instance")
    last_instance_route = (
        os.path.join(mc_dir, "instances", last_instance_name)
        if last_instance_name else None
    )
    last_valid_instance = (
            last_instance_name is not None and os.path.isfile(last_instance_route)
    )
    night_mode_initial = user.get("night_mode", False)
    page.theme_mode = ft.ThemeMode.DARK if night_mode_initial else ft.ThemeMode.LIGHT

    def toggle_theme(e):
        new_night_mode = not (page.theme_mode == ft.ThemeMode.DARK)
        page.theme_mode = (
            ft.ThemeMode.DARK if new_night_mode else ft.ThemeMode.LIGHT
        )
        night_mode_button.icon = (
            ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE
        )

        users.save_user(
            username=user.get("username"),
            uuid_val=user.get("uuid"),
            night_mode=page.theme_mode == ft.ThemeMode.DARK,
            last_instance=user.get("last_instance"),
        )

        page.update()

    night_mode_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if night_mode_initial else ft.Icons.DARK_MODE,
        tooltip="Cambiar a modo claro/oscuro",
        on_click=toggle_theme,
    )

    last_instance_text = ft.Text(
        f"Última instancia: {last_instance_name.replace('.json', '')}" if last_instance_name else "",
        size=16,
        italic=True,
        visible=last_valid_instance
    )

    starting_game_message = ft.Text(
        "Iniciando el juego...",
        size=14,
        color=ft.Colors.GREEN,
        visible=False
    )

    def play_last_instance(e):
        if not last_valid_instance:
            page.dialog = create_alert("La última instancia guardada no existe.", page)
            page.dialog.open = True
            page.update()
            return

        starting_game_message.visible = True  # Mostrar el mensaje
        page.update()

        try:
            with open(last_instance_route, "r") as f:
                data = json.load(f)
            start_game(data["version"], data["ram"], user, page)
        except Exception as ex:
            print(ex)
            page.dialog = create_alert(f"No se pudo iniciar la instancia: {ex}", page)
            page.dialog.open = True
            starting_game_message.visible = False  # Ocultar mensaje si falla
            page.update()

    last_instance_button = ft.ElevatedButton(
        "Jugar última instancia",
        on_click=play_last_instance,
        icon=ft.Icons.PLAY_ARROW,
        visible=last_valid_instance
    )

    name_ref = ft.Ref[ft.Text]()
    change_input = ft.TextField(label="Nuevo nombre", autofocus=True)
    change_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cambiar nombre de user"),
        content=change_input,
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_popup(change_dialog, page)),
            ft.TextButton(
                "Guardar",
                on_click=lambda e: save_new_name(
                    e, change_input, name_ref, user, change_dialog, page
                )
            ),
        ],
    )
    page.overlay.append(change_dialog)

    def obtain_resource_route(file_name):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, file_name)
        return os.path.join(os.path.abspath("."), file_name)

    logo_route = obtain_resource_route("logo.png")
    logo_image = ft.Container(
        content=ft.Image(
            src=logo_route,
            width=100,
            height=100,
        ),
        alignment=ft.alignment.bottom_right,
        margin=10,
    )

    return ft.View(
        route="/",
        controls=[
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                value=f"Nombre: {user.get('username') or 'No definido'}",
                                                ref=name_ref
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT,
                                                tooltip="Cambiar nombre de user",
                                                on_click=lambda e: change_dialog_open(change_input, user,
                                                                                      change_dialog, page)
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.END
                                    ),
                                    ft.Row(
                                        controls=[night_mode_button],
                                        alignment=ft.MainAxisAlignment.END
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                expand=True
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    ),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("¿Qué quieres hacer hoy?", size=30),
                                    ft.Row(
                                        controls=[
                                            ft.ElevatedButton("Instalar", on_click=lambda e: page.go("/loaders")),
                                            ft.ElevatedButton("Crear instancia",
                                                              on_click=lambda e: page.go("/create_instance")),
                                            ft.ElevatedButton("Instancias", on_click=lambda e: page.go("/instances")),
                                            ft.ElevatedButton("Otros", on_click=lambda e: page.go("/others"))
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    ft.Container(height=30),
                                    last_instance_text,
                                    last_instance_button,
                                    starting_game_message
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                    )
                ],
                expand=True,
                spacing=20,
            ),
            logo_image
        ],
    )


def view_successful_installation():
    return ft.View(
        route="/successful_installation",
        controls=[ft.Container(
            content=ft.Column(
                [ft.Text("✅ Versión instalada correctamente", size=20),
                 ft.ElevatedButton("Volver al inicio", on_click=lambda e: e.page.go("/"))],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )]
    )


def view_loaders(page):
    return ft.View(
        route="/loaders",
        appbar=ft.AppBar(title=ft.Text("Loaders")),
        controls=[ft.Container(
            content=ft.Column(
                [ft.Text("Selecciona una versión:", size=20),
                 ft.Row([
                     ft.ElevatedButton("Vanilla", on_click=lambda e: page.go("/vanilla")),
                     ft.ElevatedButton("Forge", on_click=lambda e: page.go("/forge")),
                     ft.ElevatedButton("Fabric", on_click=lambda e: page.go("/fabric"))
                 ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )]
    )


def view_other_options(page):
    return ft.View(
        route="/others",
        appbar=ft.AppBar(title=ft.Text("Gestión de archivos")),
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Gestión de Mods, Packs de Texturas y Shaders", size=20),
                        ft.Row(
                            [
                                ft.ElevatedButton("Mods", on_click=lambda e: page.go("/mods")),
                                ft.ElevatedButton("Packs de Texturas", on_click=lambda e: page.go("/texture")),
                                ft.ElevatedButton("Shaders", on_click=lambda e: page.go("/shaders")),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )


# ---------------------- Vistas Dinámicas ----------------------

def view_vanilla(page):
    versions = [v["id"] for v in mc.utils.get_available_versions(mc_dir) if v["type"] == "release"]
    selected_version = ft.Ref[ft.Dropdown]()

    error_message = ft.Text(value="❗ Selecciona una versión antes de continuar.", color="red", visible=False)

    async def install(e):
        version_id = selected_version.current.value
        if not version_id:
            error_message.visible = True
            page.update()
            return

        error_message.visible = False
        page.views.append(view_loading())
        page.update()
        try:
            await asyncio.to_thread(mc.install.install_minecraft_version, version_id, mc_dir)
            page.go("/successful_installation")
        except Exception as ex:
            page.views.pop()
            page.views.append(view_message(page, f"❌ Error al instalar: {ex}", "/vanilla"))
            page.update()

    return ft.View(
        route="/vanilla",
        appbar=ft.AppBar(title=ft.Text("Instalador de Vanilla")),
        controls=[ft.Container(
            content=ft.Column(
                [ft.Dropdown(ref=selected_version, label="Versiones disponibles",
                             options=[ft.dropdown.Option(v) for v in versions], width=250),
                 ft.ElevatedButton("Instalar versión", on_click=install), error_message],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )]
    )


def view_forge(page):
    forge_versions = mc.forge.list_forge_versions()
    forge_version_per_mc_version = {}
    for full_version in forge_versions:
        if "-" in full_version:
            mc_ver, forge_ver = full_version.split("-", 1)
            forge_version_per_mc_version.setdefault(mc_ver, []).append(forge_ver)

    selected_mc = ft.Ref[ft.Dropdown]()
    selected_forge = ft.Ref[ft.Dropdown]()
    forge_dropdown = ft.Dropdown(ref=selected_forge, label="Versión de Forge", options=[], width=250)

    error_message = ft.Text(value="❗ Selecciona ambas versiones antes de continuar.", color="red", visible=False)

    def forge_install(e):
        mc_ver = selected_mc.current.value
        forge_dropdown.options = [ft.dropdown.Option(v) for v in
                                  forge_version_per_mc_version.get(mc_ver, [])] if mc_ver else []
        forge_dropdown.value = None
        page.update()

    async def install(e):
        mc_ver = selected_mc.current.value
        forge_ver = selected_forge.current.value
        if not mc_ver or not forge_ver:
            error_message.visible = True
            page.update()
            return

        error_message.visible = False
        page.views.append(view_loading())
        page.update()
        try:
            await asyncio.to_thread(mc.forge.install_forge_version, f"{mc_ver}-{forge_ver}", mc_dir)
            page.go("/successful_installation")
        except Exception as ex:
            page.views.pop()
            page.views.append(view_message(page, f"❌ Error al instalar: {ex}", "/forge"))
            page.update()

    return ft.View(
        route="/forge",
        appbar=ft.AppBar(title=ft.Text("Instalador de Forge")),
        controls=[ft.Container(
            content=ft.Column(
                [ft.Row([
                    ft.Dropdown(ref=selected_mc, label="Versión de Minecraft",
                                options=[ft.dropdown.Option(v) for v in
                                         sorted(forge_version_per_mc_version, reverse=True)],
                                on_change=forge_install, width=250),
                    forge_dropdown], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                    ft.ElevatedButton("Instalar versión", on_click=install), error_message],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )]
    )


def view_fabric(page):
    # Get all Fabric-compatible Minecraft versions
    fabric_versions = mc.fabric.get_stable_minecraft_versions()
    fabric_version_per_mc_version = {}

    # Group loader versions by Minecraft version
    for v in fabric_versions:
        mc_ver = v
        loaders = [loader["version"] for loader in mc.fabric.get_all_loader_versions()]
        fabric_version_per_mc_version[mc_ver] = loaders

    selected_mc = ft.Ref[ft.Dropdown]()
    selected_loader = ft.Ref[ft.Dropdown]()
    loader_dropdown = ft.Dropdown(ref=selected_loader, label="Versión de Fabric Loader", options=[], width=250)

    error_message = ft.Text(value="❗ Selecciona ambas versiones antes de continuar.", color="red", visible=False)

    # When a Minecraft version is selected, update available loader versions
    def fabric_install(e):
        mc_ver = selected_mc.current.value
        loader_dropdown.options = [
            ft.dropdown.Option(v) for v in fabric_version_per_mc_version.get(mc_ver, [])
        ] if mc_ver else []
        loader_dropdown.value = None
        page.update()

    # Async installation
    async def install(e):
        mc_ver = selected_mc.current.value
        loader_ver = selected_loader.current.value
        if not mc_ver or not loader_ver:
            error_message.visible = True
            page.update()
            return

        error_message.visible = False
        page.views.append(view_loading())
        page.update()

        try:
            await asyncio.to_thread(
                mc.fabric.install_fabric, mc_ver, mc_dir, loader_ver
            )
            page.go("/successful_installation")
        except Exception as ex:
            page.views.pop()
            page.views.append(view_message(page, f"❌ Error al instalar: {ex}", "/fabric"))
            page.update()

    # Build the Fabric installer page
    return ft.View(
        route="/fabric",
        appbar=ft.AppBar(title=ft.Text("Instalador de Fabric")),
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Dropdown(
                                ref=selected_mc,
                                label="Versión de Minecraft",
                                options=[ft.dropdown.Option(v) for v in
                                         sorted(fabric_version_per_mc_version.keys(), reverse=True)],
                                on_change=fabric_install,
                                width=250
                            ),
                            loader_dropdown
                        ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20),
                        ft.ElevatedButton("Instalar versión", on_click=install),
                        error_message
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )


def view_create_instance(page):
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {"username": None, "uuid": None, "night_mode": False, "last_instance": None}

    name_ref = ft.Ref[ft.Text]()
    name_input = ft.TextField(label="Nuevo nombre", autofocus=True)

    change_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cambiar nombre de usuario"),
        content=name_input,
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_popup(change_dialog, page)),
            ft.TextButton("Guardar", on_click=lambda e: save_new_name(
                e, name_input, name_ref, user_data, change_dialog, page)),
        ]
    )

    page.overlay.append(change_dialog)

    versions = [v["id"] for v in mc.utils.get_installed_versions(mc_dir)]
    if not versions:
        return view_message(page, "❗ No hay versiones instaladas.", "/")

    dropdown = ft.Dropdown(label="Versiones instaladas", options=[ft.dropdown.Option(v) for v in versions], width=250)

    ram_values = [4 + 0.5 * i for i in range(9)]
    ram_options = [ft.dropdown.Option(str(ram)) for ram in ram_values]
    ram_dropdown = ft.Dropdown(label="Asignar RAM (GB)", options=ram_options, value="4.0", width=150)

    instance_input = ft.TextField(label="Nombre de la instancia", width=250)

    save_successful_messsage = ft.Text("Instancia guardada correctamente ✅", size=16, visible=False)
    error_message = ft.Text(value="Debes completar todos los campos.", color="red", visible=False)

    def create_instance(e):
        instance_name = instance_input.value.strip()
        version = dropdown.value
        ram = ram_dropdown.value

        if not instance_name or not version:
            error_message.visible = True
            save_successful_messsage.visible = False
            page.update()
            return

        instancia_data = {
            "name": instance_name,
            "version": version,
            "ram": ram
        }

        instances_dir = os.path.join(mc_dir, "instances")
        os.makedirs(instances_dir, exist_ok=True)

        instance_file = os.path.join(instances_dir, f"{instance_name}.json")
        with open(instance_file, "w") as f:
            json.dump(instancia_data, f, indent=4)

        save_successful_messsage.visible = True
        page.update()

    return ft.View(
        route="/create_instance",
        appbar=ft.AppBar(title=ft.Text("Crear instancia")),
        controls=[ft.Container(
            content=ft.Column(
                [
                    instance_input,
                    dropdown,
                    ram_dropdown,
                    ft.ElevatedButton("Crear instancia", on_click=create_instance),
                    error_message,
                    save_successful_messsage
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )]
    )


def view_instances(page):
    instances_dir = os.path.join(mc_dir, "instances")
    os.makedirs(instances_dir, exist_ok=True)

    instances_files = [f for f in os.listdir(instances_dir) if f.endswith(".json")]
    instances = []

    if not instances_files:
        return view_message(page, "❗ No hay instancias creadas.", "/")

    for file in instances_files:
        ruta = os.path.join(instances_dir, file)
        try:
            with open(ruta, "r") as f:
                data = json.load(f)
                data["archive"] = file
                instances.append(data)
        except Exception as e:
            print(e)
            continue

    selected = ft.Ref[ft.RadioGroup]()

    error_message = ft.Text(value="❗ Selecciona una instancia para jugar.", color="red", visible=False)
    starting_game_message = ft.Text(value="Iniciando el juego...", color="green", visible=False)
    username_error_message = ft.Text(value="❗ Debes asignar un nombre de usuario antes de jugar.", color="red",
                                     visible=False)

    deleting_instance_confirmation_dialog = ft.AlertDialog(
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text("¿Estás seguro de que quieres eliminar esta instancia?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_dialog()),
            ft.TextButton("Eliminar", on_click=lambda e: delete_instance())
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        modal=True
    )

    file_to_delete = {"valor": None}

    def close_dialog():
        deleting_instance_confirmation_dialog.open = False
        page.update()

    def delete_instance():
        if file_to_delete["valor"]:
            try:
                os.remove(os.path.join(instances_dir, file_to_delete["valor"]))
            except Exception as ex:
                page.dialog = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text(f"No se pudo eliminar la instancia: {ex}"),
                    actions=[ft.TextButton("Cerrar", on_click=lambda e: page.dialog.clean())]
                )
                page.dialog.open = True
                page.update()
                return
            file_to_delete["valor"] = None
        deleting_instance_confirmation_dialog.open = False

        # Recarga solo la lista de instancias
        reloading_instance_list()

    radios = []
    for instance in instances:
        name = instance.get("name", "Without name")
        version = instance.get("version", "???")
        ram = instance.get("ram", "???")
        value = instance["archive"]

        def on_click_edit(e, file=value):
            page.go(f"/edit_instance/{file}")

        def on_click_delete(e, file=value):
            file_to_delete["valor"] = file
            deleting_instance_confirmation_dialog.open = True
            page.update()

        radio_with_buttons = ft.Row(
            [
                ft.Radio(value=value, label=f"{name} (MC {version}, RAM {ram} GB)"),
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=on_click_edit),
                ft.IconButton(icon=ft.Icons.REMOVE, tooltip="Eliminar", on_click=on_click_delete)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )

        radios.append(radio_with_buttons)

    instances_list_ref = ft.Ref[ft.Column]()
    radio_group = ft.RadioGroup(ref=selected, content=ft.Column(radios, spacing=10))
    instances_list_ref.current = radio_group.content

    def reloading_instance_list():
        files = [f for f in os.listdir(instances_dir) if f.endswith(".json")]
        instances.clear()

        for file in files:
            route = os.path.join(instances_dir, file)
            try:
                with open(route, "r") as f:
                    data = json.load(f)
                    data["archive"] = file
                    instances.append(data)
            except:
                continue

        radios.clear()
        for instance in instances:
            name = instance.get("name", "Without name")
            version = instance.get("version", "???")
            ram = instance.get("ram", "???")
            value = instance["archive"]

            def on_click_editar(e, archive=value):
                page.go(f"/edit_instance/{archive}")

            def on_click_eliminar(e, archive=value):
                file_to_delete["valor"] = archive
                deleting_instance_confirmation_dialog.open = True
                page.update()

            radio_with_buttons = ft.Row(
                [
                    ft.Radio(value=value, label=f"{name} (MC {version}, RAM {ram} GB)"),
                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=on_click_editar),
                    ft.IconButton(icon=ft.Icons.REMOVE, tooltip="Eliminar", on_click=on_click_eliminar)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
            radios.append(radio_with_buttons)

        # Actualiza el contenido del Column referenciado
        instances_list_ref.current.controls.clear()
        instances_list_ref.current.controls.extend(radios)
        page.update()

    def play_instance(e):
        user = users.load_user()
        if not user.get("username"):  # Verificamos si no hay nombre asignado
            username_error_message.visible = True
            error_message.visible = False
            starting_game_message.visible = False
            page.update()
            return

        username_error_message.visible = False

        if not selected.current or not selected.current.value:
            error_message.visible = True
            starting_game_message.visible = False
            page.update()
            return

        error_message.visible = False
        starting_game_message.visible = True
        page.update()

        instance_route = os.path.join(instances_dir, selected.current.value)
        try:
            with open(instance_route, "r") as f:
                instance_data = json.load(f)
        except Exception as ex:
            starting_game_message.visible = False
            page.dialog = create_alert(f"Error al cargar la instancia: {ex}", page)
            page.dialog.open = True
            page.update()
            return

        # Justo después de cargar datos de la instancia y antes de llamar a iniciar_juego
        user["last_instance"] = selected.current.value
        users.save_user(
            username=user.get("username"),
            uuid_val=user.get("uuid"),
            night_mode=user.get("night_mode"),
            last_instance=user["last_instance"]
        )

        start_game(instance_data["version"], instance_data["ram"], user, page)

    return ft.View(
        route="/instances",
        appbar=ft.AppBar(title=ft.Text("Instancias guardadas")),
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        radio_group,
                        ft.ElevatedButton("▶️ Jugar instancia", on_click=play_instance),
                        error_message,
                        username_error_message,
                        starting_game_message,
                    ],
                    spacing=15,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=20
            ),
            deleting_instance_confirmation_dialog
        ]
    )


def view_edit_instance(page, file_instance):
    instances_dir = os.path.join(mc_dir, "instances")
    instance_route = os.path.join(instances_dir, file_instance)

    try:
        with open(instance_route, "r") as f:
            instance_data = json.load(f)
    except Exception as ex:
        return view_message(page, f"Error al cargar la instancia: {ex}")

    original_name = instance_data.get("name", "")
    original_verion = instance_data.get("version", "")
    original_ram = str(instance_data.get("ram", "4.0"))

    versions = [v["id"] for v in mc.utils.get_installed_versions(mc_dir)]
    if not versions:
        return view_message(page, "❗ No hay versiones instaladas.", "/")

    input_name = ft.TextField(label="Nombre de la instancia", value=original_name, width=250)
    version_dropdown = ft.Dropdown(
        label="Versión instalada",
        options=[ft.dropdown.Option(v) for v in versions],
        value=original_verion,
        width=250
    )
    ram_values = [4 + 0.5 * i for i in range(9)]
    ram_dropdown = ft.Dropdown(
        label="Asignar RAM (GB)",
        options=[ft.dropdown.Option(str(ram)) for ram in ram_values],
        value=original_ram,
        width=150
    )

    update_message = ft.Text("Instancia actualizada ✅", visible=False, size=16)

    def save_changes(e):
        new_name = input_name.value.strip()
        new_version = version_dropdown.value
        new_ram = ram_dropdown.value

        if not new_name or not new_version or not new_ram:
            page.dialog = create_alert("Todos los campos son obligatorios.", page)
            page.dialog.open = True
            page.update()
            return

        new_data = {
            "name": new_name,
            "version": new_version,
            "ram": new_ram
        }

        try:
            with open(instance_route, "w") as f:
                json.dump(new_data, f, indent=4)
            update_message.visible = True
            page.update()
        except Exception as ex:
            page.dialog = create_alert(f"No se pudo guardar: {ex}", page)
            page.dialog.open = True
            page.update()

    return ft.View(
        route=f"/edit_instance/{file_instance}",
        appbar=ft.AppBar(title=ft.Text("Editar instancia")),
        controls=[
            ft.Container(
                content=ft.Column(
                    [input_name, version_dropdown, ram_dropdown,
                     ft.ElevatedButton("Guardar cambios", on_click=save_changes),
                     update_message],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=20
            )
        ]
    )


def view_files(page, folder_name, title_text, route_path):
    folder_path = os.path.join(mc_dir, folder_name)

    # File picker para agregar archivos
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=10,
        auto_scroll=False,
    )

    def delete_file(filename, row_control):
        try:
            os.remove(os.path.join(folder_path, filename))
            list_view.controls.remove(row_control)
            page.update()
        except Exception as e:
            print(f"Error al borrar archivo: {e}")

    def create_row(filename):
        row = ft.Row(
            controls=[
                ft.Text(filename, expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Eliminar",
                    on_click=lambda e: delete_file(filename, row)
                )
            ]
        )
        return row

    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        files = []
    except Exception as e:
        files = [f"Error al leer archivos: {str(e)}"]

    for f in files:
        list_view.controls.append(create_row(f))

    def on_file_selected(e):
        if e.files:
            for f in e.files:
                destination = os.path.join(folder_path, os.path.basename(f.path))
                try:
                    shutil.copy(f.path, destination)
                    list_view.controls.append(create_row(os.path.basename(f.path)))
                    page.update()
                except Exception as err:
                    print(f"Error al copiar archivo: {err}")

    file_picker.on_result = on_file_selected

    add_button = ft.IconButton(
        icon=ft.Icons.ADD,
        on_click=lambda e: file_picker.pick_files(allow_multiple=False),
        tooltip="Agregar"
    )

    return ft.View(
        route=route_path,
        appbar=ft.AppBar(title=ft.Text(title_text)),
        controls=[
            ft.Container(
                alignment=ft.alignment.center,
                expand=True,
                content=ft.Column(
                    controls=[
                        ft.Text(f"{title_text}:", size=20),
                        add_button,
                        ft.Container(
                            height=400,
                            width=400,
                            content=list_view
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                )
            )
        ]
    )


def view_mods(page):
    return view_files(page, "mods", "Lista de Mods", "/mods")


def view_textures(page):
    return view_files(page, "resourcepacks", "Lista de Packs de Texturas", "/textures")


def view_shaders(page):
    return view_files(page, "shaderpacks", "Lista de Shaders", "/shaders")
