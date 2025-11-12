import subprocess
import sys

import flet as ft
import minecraft_launcher_lib as mc
from users import save_user

mc_dir = mc.utils.get_minecraft_directory()


def close_popup(dialog, page):
    dialog.open = False
    page.update()


def change_dialog_open(input_field, user_data, dialog, page):
    input_field.value = user_data["username"] or ""
    dialog.open = True
    page.update()


def save_new_name(e, input_field, name_ref, user_data, dialog, page):
    new_name = input_field.value.strip()
    if not new_name:
        return

    user_data["username"] = new_name

    save_user(
        username=user_data.get("username"),
        uuid_val=user_data.get("uuid"),
        night_mode=user_data.get("night_mode", False),
        last_instance=user_data.get("last_instance")
    )

    if name_ref.current:
        name_ref.current.value = f"Nombre: {new_name}"

    dialog.open = False
    page.update()


def change_name_dialog(page, version, ram):
    input_field = ft.TextField(label="Ingresa tu nombre de usuario", autofocus=True)
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nombre de usuario"),
        content=input_field,
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_popup(dialog, page)),
            ft.TextButton("Iniciar",
                          on_click=lambda e: start_game(version, ram, save_user(input_field.value), page)),
        ]
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def start_game(version_id, ram, user_data, page):
    if not version_id:
        page.dialog = create_alert("Selecciona una versión para jugar.", page)
        page.dialog.open = True
        page.update()
        return

    try:
        ram_gb = float(ram)
    except ValueError:
        ram_gb = 4.0

    ram_mb = int(ram_gb * 1024)

    settings = {
        "username": user_data["username"],
        "uuid": user_data["uuid"],
        "token": "token",
        "jvmArguments": [f"-Xmx{ram_mb}M"],
    }

    command = mc.command.get_minecraft_command(version_id, mc_dir, settings)

    if sys.platform == "win32":
        subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:
        subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    page.go("/")


def create_alert(message, page):
    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Atención"),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Aceptar", on_click=lambda e: close_popup(page.dialog, page))
        ]
    )


def view_message(page, text, return_route="/", button_text="Volver"):
    return ft.View(
        route="/message",
        controls=[ft.Container(
            content=ft.Column(
                [ft.Text(text, size=20), ft.ElevatedButton(button_text, on_click=lambda e: page.go(return_route))],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.alignment.center,
            expand=True
        )]
    )


def view_loading(message="Instalando versión..."):
    return ft.View(
        route="/cargando",
        controls=[ft.Container(
            content=ft.Column(
                [ft.Text(message, size=20), ft.ProgressRing()],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.alignment.center,
            expand=True
        )]
    )
