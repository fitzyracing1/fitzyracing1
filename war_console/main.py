import tkinter as tk
import threading
import time
from engine import ProceduralEngine
from plyer import notification
import pystray
from PIL import Image

# === Splash Screen ===
class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#0b0f14")
        self.overrideredirect(True)  # No title bar
        self.geometry("600x200+400+250")  # Centered
        label = tk.Label(self, text="WIRELESS INTERCEPT ONLINE_", fg="#00ff66",
                         bg="#0b0f14", font=("Consolas", 20, "bold"))
        label.pack(expand=True)
        self.after(2000, self.destroy)  # Auto-close after 2s

# === Main Command Console ===
class CommandConsole(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide until splash is done
        self.title("War of the Worlds — Command Console")
        self.configure(bg="#0b0f14")
        self.geometry("800x500")

        self.engine = ProceduralEngine()

        # Status panel
        self.status_label = tk.Label(self, text="", fg="#00ff66", bg="#0b0f14", font=("Consolas", 12))
        self.status_label.pack(anchor="w", padx=10, pady=5)

        # Event log
        self.log_text = tk.Text(self, bg="#0b0f14", fg="#00ff66", font=("Consolas", 11), wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Choice buttons
        self.choice_frame = tk.Frame(self, bg="#0b0f14")
        self.choice_frame.pack(side="bottom", fill="x")

        # Start tray icon in separate thread
        threading.Thread(target=self.start_tray, daemon=True).start()

        # Show splash first
        splash = SplashScreen(self)
        self.after(2100, self.start_game)  # Delay game start until splash closes

    def start_game(self):
        self.deiconify()  # Show main window
        episodes = self.engine.list_episodes()
        if not episodes:
            self.log("No episodes found.")
            return
        ep_file = episodes[0]
        episode_data = self.engine.load_episode(ep_file)
        self.events = self.engine.prepare_events(episode_data)
        self.next_event()

    def next_event(self):
        if not self.events:
            self.end_game()
            return
        event = self.events.pop(0)
        self.current_event = event
        self.show_event(event)

    def show_event(self, event):
        self.log(f"\n--- {event['title']} ---\n{event['description']}")
        for widget in self.choice_frame.winfo_children():
            widget.destroy()
        available = self.engine.get_available_choices(event)
        for choice in available:
            btn = tk.Button(self.choice_frame, text=choice['text'], command=lambda c=choice: self.choose(c),
                            bg="#111", fg="#0f0", font=("Consolas", 10))
            btn.pack(side="left", padx=5, pady=5)

    def choose(self, choice):
        self.engine.apply_choice(choice)
        self.log(choice["flavor"])
        self.update_status()
        if not self.engine.state["alive"]:
            self.end_game()
        else:
            self.next_event()

    def update_status(self):
        s = self.engine.state
        self.status_label.config(text=f"Morale: {s['morale']}  Resources: {s['resources']}  Intel: {s['intel']}  Time: {s['time']}")
        if s['morale'] <= 2:
            self.send_notification("Critical Morale", "Your crew is losing hope!")
            self.tray_icon.icon = self.icon_red

    def log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def end_game(self):
        epilogue = self.engine.generate_epilogue()
        self.log("\n=== EPILOGUE ===\n" + epilogue)
        self.engine.update_profile(self.engine.state)
        if self.engine.state["ending"] == "victory":
            self.send_notification("Victory!", "The cylinder’s song died. Reinforcements are on the move.")
        else:
            self.send_notification("Defeat", "The black smoke rolled in...")

    def send_notification(self, title, message):
        notification.notify(title=title, message=message, timeout=5)

    def start_tray(self):
        self.icon_green = Image.open("assets/icon_green.ico")
        self.icon_red = Image.open("assets/icon_red.ico")
        self.tray_icon = pystray.Icon("WotW", self.icon_green, menu=pystray.Menu(
            pystray.MenuItem("Threat Snapshot", self.show_snapshot),
            pystray.MenuItem("Send Daily Report", self.send_report),
            pystray.MenuItem("Exit", self.exit_app)
        ))
        self.tray_icon.run()

    def show_snapshot(self):
        s = self.engine.state
        self.send_notification("Threat Snapshot", f"Morale: {s['morale']} | Resources: {s['resources']} | Intel: {s['intel']}")

    def send_report(self):
        self.send_notification("Daily Report", "Report sent to HQ.")

    def exit_app(self):
        self.tray_icon.stop()
        self.destroy()

if __name__ == "__main__":
    app = CommandConsole()
    app.mainloop()