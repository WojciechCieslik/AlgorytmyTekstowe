import os

os.environ["ARROW_LOG_LEVEL"] = "FATAL"
os.environ["GLOG_minloglevel"] = "2"

import customtkinter as ctk
import sys
import threading
import traceback
import webbrowser

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.recipe_logic import process_ingredients, init_ai_models


def _preload_models():
    print("Ładowanie modelu embeddingowego i bazy wektorowej...")
    init_ai_models(status_callback=print)
    print("Gotowe.")


class RecipeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Asystent Kulinarny")
        self.geometry("760x820")

        self.configure(padx=20, pady=20)

        self.label_title = ctk.CTkLabel(
            self, text="AI Asystent Kulinarny",
            font=ctk.CTkFont(size=28, weight="bold"), text_color="#FF4B4B"
        )
        self.label_title.pack(pady=(10, 5))

        self.label_subtitle = ctk.CTkLabel(
            self,
            text="Wpisz co masz w lodówce — możesz pisać naturalnie, np. „mam kurczaka, ryż i cebulę, ale nie mam masła”.",
            text_color="gray", font=ctk.CTkFont(size=14)
        )
        self.label_subtitle.pack(pady=(0, 30))

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="np. kurczak, ryż, cebula, śmietana... albo: mam jajka i mąkę, brak cukru",
            width=500, height=45, font=ctk.CTkFont(size=15)
        )
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda _event: self.on_search_click())

        self.button = ctk.CTkButton(
            self, text="Co z tego ugotuję?", command=self.on_search_click,
            width=200, height=45, font=ctk.CTkFont(size=15, weight="bold")
        )
        self.button.pack(pady=20)

        self.status_var = ctk.StringVar(value="Gotowy do pracy!")
        self.label_status = ctk.CTkLabel(
            self, textvariable=self.status_var,
            font=ctk.CTkFont(size=13, slant="italic"), text_color="#e6b800"
        )
        self.label_status.pack(pady=5)

        self.progressbar = ctk.CTkProgressBar(self, mode="indeterminate", width=400)

        # Uproszczony layout: wyniki u góry, log (tekst) na dole.
        # Unikamy chowania/pokazywania widgetów, bo w CustomTkinter na Windows
        # potrafi to prowadzić do błędów skalowania (dzielenie przez zero).
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=0)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.results_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            width=700,
        )
        self.results_frame.grid(row=0, column=0, sticky="nsew")
        self._enable_results_scroll()

        self.log_textbox = ctk.CTkTextbox(
            self.content_frame,
            height=180,
            font=ctk.CTkFont(size=13),
            wrap="word",
            fg_color="#2b2b2b",
        )
        self.log_textbox.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self._setup_readonly_textbox(self.log_textbox)

    def _setup_readonly_textbox(self, textbox: ctk.CTkTextbox):
        text_widget = getattr(textbox, "_textbox", textbox)
        text_widget.bind("<Key>", lambda _event: "break")

    def _enable_results_scroll(self):
        # W Windows scroll często działa tylko, gdy ręcznie podepniemy MouseWheel.
        def _on_mousewheel(event):
            canvas = getattr(self.results_frame, "_parent_canvas", None)
            if canvas is None:
                return

            try:
                over_widget = self.winfo_containing(event.x_root, event.y_root)
            except Exception:
                over_widget = None

            # Scrolluj tylko wtedy, gdy kursor jest nad wynikami (żeby nie przechwycić scrolla z innych elementów).
            if over_widget is None or not str(over_widget).startswith(str(self.results_frame)):
                return

            delta = 0
            if getattr(event, "delta", 0):
                # Windows: delta = ±120
                delta = int(-1 * (event.delta / 120))
            elif getattr(event, "num", None) == 4:
                delta = -1
            elif getattr(event, "num", None) == 5:
                delta = 1

            if delta:
                canvas.yview_scroll(delta, "units")

        # add="+" żeby nie nadpisać istniejących bindów CTk
        self.bind_all("<MouseWheel>", _on_mousewheel, add="+")
        self.bind_all("<Button-4>", _on_mousewheel, add="+")
        self.bind_all("<Button-5>", _on_mousewheel, add="+")

    @staticmethod
    def _collect_dishes(response: dict) -> list[dict]:
        dishes = response.get("dishes") or []
        if dishes:
            return [dish for dish in dishes if isinstance(dish, dict)]
        if response.get("dish_name"):
            return [{
                "dish_name": response.get("dish_name", "Nieznane danie"),
                "dish_link": response.get("dish_link", ""),
                "missing_ingredients": response.get("missing_ingredients", []),
            }]
        return []

    @staticmethod
    def _open_link(url: str):
        url = (url or "").strip()
        if not url or url == "#":
            return
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url.lstrip('/')}"
        webbrowser.open(url)

    def _clear_results_frame(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def update_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    def append_output_thread_safe(self, text):
        def _append():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", text + "\n")
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")
        self.after(0, _append)

    def on_search_click(self):
        ingredients = self.entry.get()
        if not ingredients.strip():
            self.status_var.set("Proszę wpisać jakieś składniki!")
            return

        self.button.configure(state="disabled")
        self._clear_results_frame()

        self.progressbar.pack(pady=5)
        self.progressbar.start()

        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

        threading.Thread(target=self.bg_search, args=(ingredients,), daemon=True).start()

    def bg_search(self, ingredients_text):
        try:
            response = process_ingredients(
                ingredients_text,
                status_callback=self.update_status,
                output_callback=self.append_output_thread_safe
            )
            self.after(0, self.on_search_done, response)
        except Exception as e:
            self.after(0, self.on_search_error, str(e))

    def _add_dish_result(self, idx: int, dish: dict):
        d_name = dish.get("dish_name", "Nieznane danie")
        d_link = dish.get("dish_link", "")
        d_missing = dish.get("missing_ingredients", [])

        if isinstance(d_missing, list):
            d_missing_str = ", ".join(d_missing)
        else:
            d_missing_str = str(d_missing)

        card = ctk.CTkFrame(self.results_frame)
        card.pack(fill="x", pady=4)

        ctk.CTkLabel(
            card, text=f"{idx}. {d_name}",
            font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        ).pack(fill="x", padx=10, pady=(8, 2))

        if d_missing_str:
            ctk.CTkLabel(
                card, text=f"Brakuje: {d_missing_str}",
                text_color="#ff8080", anchor="w"
            ).pack(fill="x", padx=10, pady=(0, 2))
        else:
            ctk.CTkLabel(
                card, text="Masz wszystkie składniki.",
                text_color="#80ff80", anchor="w"
            ).pack(fill="x", padx=10, pady=(0, 2))

        if d_link:
            ctk.CTkButton(
                card,
                text="Otwórz przepis w przeglądarce",
                command=lambda url=d_link: self._open_link(url),
                width=220,
                height=32,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
            ).pack(anchor="w", padx=10, pady=(2, 8))
        else:
            ctk.CTkLabel(
                card, text="Brak linku do przepisu",
                text_color="gray", anchor="w"
            ).pack(fill="x", padx=10, pady=(2, 8))

    def on_search_done(self, response):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.button.configure(state="normal")
        self._clear_results_frame()

        dishes = self._collect_dishes(response)

        if response.get("found") and dishes:
            info = response.get("info", "")

            if info:
                ctk.CTkLabel(
                    self.results_frame,
                    text=info,
                    wraplength=640,
                    justify="left",
                    font=ctk.CTkFont(size=14),
                    anchor="w",
                ).pack(fill="x", pady=(0, 12))

            for idx, dish in enumerate(dishes, 1):
                self._add_dish_result(idx, dish)

            self.status_var.set("Znaleziono przepis. Smacznego!")
        else:
            self.status_var.set("Niestety nie znalazłem niczego pasującego.")
            info = response.get("info", "")
            if info:
                ctk.CTkLabel(
                    self.results_frame,
                    text=info,
                    wraplength=640,
                    justify="left",
                    font=ctk.CTkFont(size=14),
                    anchor="w",
                ).pack(fill="x", pady=8)

    def on_search_error(self, error_msg):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.button.configure(state="normal")
        self._clear_results_frame()
        self.status_var.set("Wystąpił nieoczekiwany błąd!")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"\nSzczegóły błędu:\n{error_msg}")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    # Wymuszenie sensownego skalowania (CustomTkinter potrafi na Windows zwrócić 0.0).
    ctk.set_window_scaling(1.0)
    ctk.set_widget_scaling(1.0)

    try:
        _preload_models()
    except Exception:
        print(traceback.format_exc())
        raise SystemExit(1)

    app = RecipeApp()
    app.mainloop()
