import os
import signal
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import about

console = Console()
processes = []

def obtener_informacion_sistema():
    if os.path.exists("/etc/lsb-release"):
        with open("/etc/lsb-release") as f:
            lines = f.readlines()
        info = {}
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                info[key] = value.strip('"')
        return info.get("DISTRIB_DESCRIPTION", "Desconocido"), info.get("DISTRIB_CODENAME", "Desconocido")
    else:
        return "Desconocido", "Desconocido"

def mostrar_informacion():
    nombre_app = "Yel-Updater"
    version = "1.0 v060225"
    sistema, version_sistema = obtener_informacion_sistema()
    
    informacion = f"""
    Nombre de la app: [bold cyan]{nombre_app}[/bold cyan]
    Versión: [bold cyan]{version}[/bold cyan]
    Sistema: [bold cyan]{sistema}[/bold cyan]
    Versión del sistema: [bold cyan]{version_sistema}[/bold cyan]
    """
    console.print(informacion)

def mostrar_menu():
    tabla = Table(title="[bold]Menú de opciones[/bold]")
    tabla.add_column("Opción", style="cyan", no_wrap=True)
    tabla.add_column("Descripción", style="magenta")

    tabla.add_row("1", "Actualizar repositorios")
    tabla.add_row("2", "Actualizar paquetes")
    tabla.add_row("3", "Listar paquetes actualizables")
    tabla.add_row("4", "Autolimpieza")
    tabla.add_row("5", "Limpieza de paquetes")
    tabla.add_row("6", "Reparar dependencias")
    tabla.add_row("7", "Buscar y descargar kernel")
    tabla.add_row("8", "Buscar y borrar kernel")
    tabla.add_row("9", "Acerca del programa...")
    tabla.add_row("10", "Salir")

    console.print(tabla)

def enviar_notificacion(mensaje):
    subprocess.run(['notify-send', 'Yel-Updater', mensaje])

def ejecutar_comando(comando):
    proceso = subprocess.Popen(f"pkexec {comando}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes.append(proceso)
    stdout, stderr = proceso.communicate()
    processes.remove(proceso)
    if proceso.returncode != 0:
        console.print(f"[bold red]El comando falló:[/bold red] {comando}\n{stderr.decode().strip()}")
        enviar_notificacion("El comando falló")
    else:
        return stdout.decode()

def ejecutar_comando_con_progreso(comando, descripcion):
    with Progress(SpinnerColumn(), BarColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(f"[green]{descripcion}...", total=None)
        proceso = subprocess.Popen(f"pkexec {comando}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append(proceso)
        stdout, stderr = proceso.communicate()
        processes.remove(proceso)
        progress.update(task, completed=100)
        if proceso.returncode != 0:
            console.print(f"[bold red]El comando falló:[/bold red] {comando}\n{stderr.decode().strip()}")
            enviar_notificacion(f"El comando falló: {descripcion}")
        else:
            enviar_notificacion(f"{descripcion} completado")
            return stdout.decode()

def actualizar():
    console.print("[bold green]Ejecutando apt-fast update...[/bold green]")
    ejecutar_comando_con_progreso("apt-fast update", "Actualización de repositorios")

def actualizar_paquetes():
    console.print("[bold green]Ejecutando apt-fast upgrade...[/bold green]")
    ejecutar_comando_con_progreso("apt-fast upgrade -y", "Actualización de paquetes")

def listar_actualizables():
    console.print("[bold green]Listando paquetes actualizables...[/bold green]")
    salida = ejecutar_comando("apt-fast list --upgradable")
    if salida:
        paquetes = salida.strip().split("\n")
        cantidad = len(paquetes)
        console.print(salida)
        enviar_notificacion(f"Hay {cantidad} paquetes actualizables")
    else:
        console.print("[bold red]No hay paquetes actualizables.[/bold red]")
        enviar_notificacion("No hay paquetes actualizables por ahora")

def autolimpieza():
    console.print("[bold green]Ejecutando apt-fast autoclean...[/bold green]")
    ejecutar_comando_con_progreso("apt-fast autoclean", "Autolimpieza")

def autoremocion():
    console.print("[bold green]Ejecutando apt-fast autoremove...[/bold green]")
    ejecutar_comando_con_progreso("apt-fast autoremove -y", "Limpieza de paquetes")

def reparar_dependencias():
    console.print("[bold green]Reparando dependencias...[/bold green]")
    ejecutar_comando_con_progreso("apt-get install -f", "Reparación de dependencias")

def buscar_kernels():
    console.print("[bold green]Buscando kernels disponibles...[/bold green]")
    kernels = subprocess.check_output("apt-cache search linux-image", shell=True).decode().splitlines()
    # Filtrar solo los kernels de CuerdOS
    kernels = [k.split(' - ')[0] for k in kernels if 'cuerdos-linux-image' in k]
    return kernels

def seleccionar_kernel(kernels, accion):
    if not kernels:
        console.print(f"[bold red]No se encontraron kernels para {accion}.[/bold red]")
        return None
    console.print(f"[bold green]Seleccione el kernel a {accion}:[/bold green]")
    for idx, kernel in enumerate(kernels, start=1):
        console.print(f"{idx}. {kernel}")
    seleccion = Prompt.ask("Ingrese el número del kernel", choices=[str(i) for i in range(1, len(kernels)+1)])
    return kernels[int(seleccion)-1]

def descargar_kernel():
    kernels = buscar_kernels()
    kernel = seleccionar_kernel(kernels, "descargar")
    if kernel:
        console.print(f"[bold green]Descargando kernel {kernel}...[/bold green]")
        ejecutar_comando_con_progreso(f"apt-fast install {kernel}", f"Descarga del kernel {kernel}")

def borrar_kernel():
    console.print("[bold green]Listando kernels instalados...[/bold green]")
    kernels = subprocess.check_output("dpkg --list | grep linux-image", shell=True).decode().splitlines()
    # Filtrar solo los kernels de CuerdOS
    kernels = [k.split()[1] for k in kernels if 'cuerdos-linux-image' in k]
    kernel = seleccionar_kernel(kernels, "borrar")
    if kernel:
        console.print(f"[bold green]Borrando kernel {kernel}...[/bold green]")
        ejecutar_comando_con_progreso(f"apt-fast remove --purge {kernel}", f"Borrado del kernel {kernel}")

def mostrar_acerca_de():
    about.show_about_dialog()

def manejar_opcion(eleccion):
    opciones = {
        '1': actualizar,
        '2': actualizar_paquetes,
        '3': listar_actualizables,
        '4': autolimpieza,
        '5': autoremocion,
        '6': reparar_dependencias,
        '7': descargar_kernel,
        '8': borrar_kernel,
        '9': mostrar_acerca_de,
        '10': salir
    }
    accion = opciones.get(eleccion, lambda: console.print("[bold red]Opción no válida[/bold red]"))
    accion()
    if eleccion != '10':
        Prompt.ask("\nProceso completado. Presiona Enter para continuar...")
        console.clear()
        mostrar_menu()

def salir():
    console.print("[bold yellow]Saliendo...[/bold yellow]")
    for proceso in processes:
        proceso.terminate()
    exit()

def main():
    mostrar_informacion()
    mostrar_menu()
    while True:
        eleccion = Prompt.ask("Ingrese su elección", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], default="10")
        manejar_opcion(eleccion)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        salir()