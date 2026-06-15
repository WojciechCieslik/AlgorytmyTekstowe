import torch
import customtkinter as ctk
import sys
import os
import threading
import webbrowser

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.recipe_logic import process_ingredients, init_ai_models, start_background_init

class RecipeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Asystent Kulinarny")
        self.geometry("700x750")
        
        self.configure(padx=20, pady=20)

        self.label_title = ctk.CTkLabel(self, text="🍳 AI Asystent Kulinarny", font=ctk.CTkFont(size=28, weight="bold"), text_color="#FF4B4B")
        self.label_title.pack(pady=(10, 5))

        self.label_subtitle = ctk.CTkLabel(self, text="Wpisz co masz w lodówce, a sztuczna inteligencja wymyśli co z tego ugotować.", text_color="gray", font=ctk.CTkFont(size=14))
        self.label_subtitle.pack(pady=(0, 30))

        self.entry = ctk.CTkEntry(self, placeholder_text="np. kurczak, ryż, cebula, śmietana...", width=500, height=45, font=ctk.CTkFont(size=15))
        self.entry.pack(pady=10)

        self.button = ctk.CTkButton(self, text="Co z tego ugotuję?", command=self.on_search_click, width=200, height=45, font=ctk.CTkFont(size=15, weight="bold"))
        self.button.pack(pady=20)
        self.button.configure(state="disabled")

        self.status_var = ctk.StringVar(value="Przygotowuję modele i wczytuję bazę. Proszę czekać...")
        self.label_status = ctk.CTkLabel(self, textvariable=self.status_var, font=ctk.CTkFont(size=13, slant="italic"), text_color="#e6b800")
        self.label_status.pack(pady=5)

        self.progressbar = ctk.CTkProgressBar(self, mode="indeterminate", width=400)
        self.progressbar.pack(pady=5)
        self.progressbar.start()

        self.output_textbox = ctk.CTkTextbox(self, width=600, height=300, font=ctk.CTkFont(size=14), wrap="word", state="disabled", fg_color="#2b2b2b")
        self.output_textbox.pack(pady=10, fill="both", expand=True)

        threading.Thread(target=self.bg_init, daemon=True).start()

    def update_status_thread_safe(self, msg):
        self.after(0, lambda: self.status_var.set(msg))

    def append_output_thread_safe(self, text):
        def _append():
            self.output_textbox.configure(state="normal")
            self.output_textbox.insert("end", text + "\n")
            self.output_textbox.configure(state="disabled")
            self.output_textbox.see("end")
        self.after(0, _append)

    def bg_init(self):
        try:
            init_ai_models(status_callback=self.update_status_thread_safe)
            self.after(0, self.on_init_done)
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Błąd inicjalizacji: {str(e)}"))
            self.after(0, self.progressbar.stop)
            self.after(0, self.progressbar.pack_forget)

    def on_init_done(self):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.button.configure(state="normal")
        self.status_var.set("Gotowy do pracy! (Modele zostały załadowane)")

    def on_search_click(self):
        ingredients = self.entry.get()
        if not ingredients.strip():
            self.status_var.set("Proszę wpisać jakieś składniki!")
            return

        self.button.configure(state="disabled")
        
        self.progressbar.pack(pady=5)
        self.progressbar.start()
        
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")

        threading.Thread(target=self.bg_search, args=(ingredients,), daemon=True).start()

    def bg_search(self, ingredients_text):
        ingredients_list = [x.strip() for x in ingredients_text.split(",") if x.strip()]
        try:
            response = process_ingredients(
                ingredients_list, 
                status_callback=self.update_status_thread_safe,
                output_callback=self.append_output_thread_safe
            )
            self.after(0, self.on_search_done, response)
        except Exception as e:
            self.after(0, self.on_search_error, str(e))

    def on_search_done(self, response):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.button.configure(state="normal")

        if response.get("found"):
            info = response.get("info", "")
            dishes = response.get("dishes", [])
            
            self.output_textbox.configure(state="normal")
            self.output_textbox.insert("end", f"\n====================================\n🍽️ OSTATECZNA DECYZJA (DANIA):\n\nℹ️ {info}\n\n")
            
            if isinstance(dishes, list) and len(dishes) > 0:
                for idx, dish in enumerate(dishes, 1):
                    d_name = dish.get("dish_name", "Nieznane danie")
                    d_link = dish.get("dish_link", "#")
                    d_missing = dish.get("missing_ingredients", [])
                    
                    if isinstance(d_missing, list):
                        d_missing_str = ", ".join(d_missing)
                    else:
                        d_missing_str = str(d_missing)
                    
                    self.output_textbox.insert("end", f"{idx}. {d_name}\n")
                    if d_missing_str:
                        self.output_textbox.insert("end", f"   ❌ Brakuje: {d_missing_str}\n")
                    else:
                        self.output_textbox.insert("end", f"   ✅ Masz wszystkie składniki!\n")
                    
                    self.output_textbox.insert("end", f"   🔗 Link: ")
                    
                    # Create a clickable tag
                    tag_name = f"link_{idx}"
                    self.output_textbox.insert("end", f"{d_link}\n\n", tag_name)
                    
                    try:
                        self.output_textbox.tag_config(tag_name, foreground="#4da6ff", underline=True)
                        self.output_textbox.tag_bind(tag_name, "<Button-1>", lambda e, url=d_link: webbrowser.open(url))
                        self.output_textbox.tag_bind(tag_name, "<Enter>", lambda e, tag=tag_name: self.output_textbox.configure(cursor="hand2"))
                        self.output_textbox.tag_bind(tag_name, "<Leave>", lambda e, tag=tag_name: self.output_textbox.configure(cursor="arrow"))
                    except Exception:
                        pass # Ignorujemy błędy przypisania tagów
                        
            elif isinstance(dishes, dict):
                d_name = dishes.get("dish_name", "Nieznane danie")
                d_link = dishes.get("dish_link", "#")
                self.output_textbox.insert("end", f"{d_name}\nLink: {d_link}\n")
            else:
                d_name = response.get("dish_name", "Nieznane danie")
                d_link = response.get("dish_link", "#")
                self.output_textbox.insert("end", f"{d_name}\nLink: {d_link}\n")
                
            self.output_textbox.insert("end", "====================================")
            
            self.status_var.set("Znaleziono przepis! Smacznego!")
            self.output_textbox.configure(state="disabled")
            self.output_textbox.see("end")
        else:
            self.status_var.set("Niestety nie znalazłem niczego pasującego.")
            self.output_textbox.configure(state="normal")
            self.output_textbox.insert("end", response.get("info", ""))
            self.output_textbox.configure(state="disabled")
            self.output_textbox.see("end")

    def on_search_error(self, error_msg):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.button.configure(state="normal")
        self.status_var.set("Wystąpił nieoczekiwany błąd!")
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", f"\nSzczegóły błędu:\n{error_msg}")
        self.output_textbox.configure(state="disabled")
        self.output_textbox.see("end")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = RecipeApp()
    app.mainloop()
