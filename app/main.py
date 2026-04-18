import os
import threading
import customtkinter as ctk

from ping_module import start_ping_process, read_ping_output
from tracert_module import start_tracert_process, read_tracert_output
from file_module import save_text
from network_info_module import get_full_network_info

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class NetworkToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Network Tools App")
        self.geometry("950x780")

        self.last_result = ""
        self.last_saved_file = ""
        self.current_process = None
        self.stop_requested = False

        # ===== TÍTULO CAMPOS =====
        self.host_label = ctk.CTkLabel(self, text="Dominio o IP")
        self.host_label.pack(pady=(15, 5))

        self.host_entry = ctk.CTkEntry(self, width=350)
        self.host_entry.insert(0, "www.google.com")
        self.host_entry.pack()

        self.count_label = ctk.CTkLabel(self, text="Cantidad de pings")
        self.count_label.pack(pady=(10, 5))

        self.count_entry = ctk.CTkEntry(self, width=120)
        self.count_entry.insert(0, "10")
        self.count_entry.pack()

        self.size_label = ctk.CTkLabel(self, text="Tamaño del paquete")
        self.size_label.pack(pady=(10, 5))

        self.size_entry = ctk.CTkEntry(self, width=120)
        self.size_entry.insert(0, "32")
        self.size_entry.pack()

        # ===== BOTONES =====
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.pack(pady=15)

        self.ping_button = ctk.CTkButton(
            self.buttons_frame,
            text="Ejecutar Ping",
            command=self.execute_ping
        )
        self.ping_button.grid(row=0, column=0, padx=8, pady=8)

        self.tracert_button = ctk.CTkButton(
            self.buttons_frame,
            text="Ver Saltos",
            command=self.execute_tracert
        )
        self.tracert_button.grid(row=0, column=1, padx=8, pady=8)

        self.stop_button = ctk.CTkButton(
            self.buttons_frame,
            text="Detener todo",
            command=self.stop_all,
            fg_color="#b91c1c",
            hover_color="#991b1b"
        )
        self.stop_button.grid(row=0, column=2, padx=8, pady=8)

        self.net_info_button = ctk.CTkButton(
            self.buttons_frame,
            text="Info de Red",
            command=self.generate_network_info_file
            
        )
        self.net_info_button.grid(row=1, column=0, padx=8, pady=8)

        self.save_button = ctk.CTkButton(
            self,
            text="Guardar resultado en TXT",
            command=self.save_result
        )
        self.save_button.pack(pady=(8, 5))

        self.open_file_button = ctk.CTkButton(
            self,
            text="Abrir último archivo guardado",
            command=self.open_saved_file,
            state="disabled"
        )
        self.open_file_button.pack(pady=(0, 10))

        # ===== PROGRESO =====
        self.progress_label = ctk.CTkLabel(self, text="Progreso: 0%")
        self.progress_label.pack(pady=(5, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=500,
            progress_color="#22c55e",
            fg_color="#2b2b2b"
        )
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(0)

        # ===== SALIDA =====
        self.output_box = ctk.CTkTextbox(self, width=900, height=420)
        self.output_box.pack(padx=20, pady=15)

    # =========================
    # UTILIDADES
    # =========================
    def set_buttons_state(self, state: str):
        self.ping_button.configure(state=state)
        self.tracert_button.configure(state=state)
        self.net_info_button.configure(state=state)
        self.save_button.configure(state=state)
        self.open_file_button.configure(
            state="normal" if self.last_saved_file else "disabled"
        )

    def show_output(self, content: str):
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", content)

    def safe_int(self, value: str, default: int) -> int:
        try:
            return int(value)
        except ValueError:
            return default

    def run_in_thread(self, target_function):
        thread = threading.Thread(target=target_function, daemon=True)
        thread.start()

    def update_progress(self, current: int, total: int):
        if total <= 0:
            return

        percent = current / total
        self.after(0, lambda: self.progress_bar.set(percent))
        self.after(
            0,
            lambda: self.progress_label.configure(
                text=f"Progreso: {int(percent * 100)}%"
            )
        )

    def reset_progress(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Progreso: 0%")

    def set_indeterminate_progress(self, active: bool):
        if active:
            self.progress_label.configure(text="Procesando...")
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)
            self.progress_label.configure(text="Progreso: 0%")

    # =========================
    # DETENER TODO
    # =========================
    def stop_all(self):
        self.stop_requested = True

        if self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass

        self.set_indeterminate_progress(False)
        self.progress_bar.set(0)
        self.progress_label.configure(text="Proceso detenido")
        self.show_output("El proceso fue detenido por el usuario.")
        self.current_process = None
        self.set_buttons_state("normal")

    # =========================
    # PING
    # =========================
    def execute_ping(self):
        host = self.host_entry.get().strip()
        count = self.safe_int(self.count_entry.get().strip(), 4)
        size = self.safe_int(self.size_entry.get().strip(), 32)

        if not host:
            self.show_output("Debes escribir un dominio o IP.")
            return

        if count <= 0:
            self.show_output("La cantidad de pings debe ser mayor que 0.")
            return

        if size <= 0:
            self.show_output("El tamaño del paquete debe ser mayor que 0.")
            return

        self.stop_requested = False
        self.reset_progress()
        self.set_buttons_state("disabled")
        self.stop_button.configure(state="normal")
        self.show_output("Ejecutando ping... espera un momento.")

        def task():
            process = start_ping_process(host, count, size)
            self.current_process = process

            result = read_ping_output(
                process,
                count,
                progress_callback=self.update_progress,
                stop_callback=lambda: self.stop_requested
            )

            self.last_result = result
            self.current_process = None

            def finish():
                if not self.stop_requested:
                    self.progress_bar.set(1)
                    self.progress_label.configure(text="Progreso: 100%")
                    self.show_output(result)
                self.set_buttons_state("normal")

            self.after(0, finish)

        self.run_in_thread(task)

    # =========================
    # TRACERT
    # =========================
    def execute_tracert(self):
        host = self.host_entry.get().strip()

        if not host:
            self.show_output("Debes escribir un dominio o IP.")
            return

        self.stop_requested = False
        self.set_buttons_state("disabled")
        self.stop_button.configure(state="normal")
        self.set_indeterminate_progress(True)
        self.show_output("Ejecutando tracert... espera un momento.")

        def task():
            process = start_tracert_process(host)
            self.current_process = process

            result = read_tracert_output(
                process,
                stop_callback=lambda: self.stop_requested
            )

            self.last_result = result
            self.current_process = None

            def finish():
                if not self.stop_requested:
                    self.set_indeterminate_progress(False)
                    self.show_output(result)
                self.set_buttons_state("normal")

            self.after(0, finish)

        self.run_in_thread(task)

    # =========================
    # INFO COMPLETA DE RED
    # =========================
    def generate_network_info_file(self):
        self.stop_requested = False
        self.set_buttons_state("disabled")
        self.set_indeterminate_progress(True)
        self.show_output("Generando archivo con información completa de red...")

        def task():
            result = get_full_network_info()
            self.last_result = result

            path = save_text(result, "network_info")
            self.last_saved_file = path

            def finish():
                self.set_indeterminate_progress(False)
                self.open_file_button.configure(state="normal")
                self.show_output(f"Archivo generado en:\n{path}\n\n{result}")
                self.set_buttons_state("normal")

                try:
                    os.startfile(path)
                except Exception as e:
                    self.show_output(
                        f"Archivo generado en:\n{path}\n\n"
                        f"No se pudo abrir automáticamente.\nError: {e}"
                    )

            self.after(0, finish)

        self.run_in_thread(task)

    # =========================
    # GUARDAR RESULTADO
    # =========================
    def save_result(self):
        if not self.last_result.strip():
            self.show_output("No hay resultado para guardar.")
            return

        host = self.host_entry.get().strip().replace(".", "_")
        if not host:
            host = "network_result"

        path = save_text(self.last_result, f"ping_{host}")
        self.last_saved_file = path
        self.open_file_button.configure(state="normal")

        self.show_output(
            f"Archivo guardado en:\n{path}\n\nAbriendo archivo automáticamente..."
        )

        try:
            os.startfile(path)
        except Exception as e:
            self.show_output(
                f"Archivo guardado en:\n{path}\n\n"
                f"No se pudo abrir automáticamente.\nError: {e}"
            )

    # =========================
    # ABRIR ÚLTIMO ARCHIVO
    # =========================
    def open_saved_file(self):
        if not self.last_saved_file:
            self.show_output("Todavía no has guardado ningún archivo.")
            return

        if not os.path.exists(self.last_saved_file):
            self.show_output("El archivo guardado ya no existe en la ruta esperada.")
            return

        try:
            os.startfile(self.last_saved_file)
        except Exception as e:
            self.show_output(f"No se pudo abrir el archivo.\nError: {e}")


if __name__ == "__main__":
    app = NetworkToolsApp()
    app.mainloop()