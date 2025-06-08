from rich.console import Console
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import Box, Frame, Label, RadioList, Button
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window

console = Console()

class WalkdataCLI:
    def __init__(self):
        self.console = console
        self.style = Style.from_dict({
            "frame": "bg:#1e1e1e #ffffff",
            "label": "#ffffff",
            "radiolist focused": "bg:#005f5f",
            "button": "#ffffff",
            "button.focused": "bg:#4444ff #ffffff"
        })

        self.menu_options = [
            ("View Walkable Cities", "view"),
            ("Add a New City", "add"),
            ("Load Sample Data", "load"),
            ("Exit", "exit")
        ]

        self.radio_list = RadioList(self.menu_options)
        self.message_control = FormattedTextControl(text="Use ↑ ↓ to navigate, Enter to select, q to quit.")
        self.message_window = Window(content=self.message_control, height=1)

        self.body = HSplit([
            Label(text="Welcome to Walkdata CLI — Choose an action:", style="bold"),
            self.radio_list,
            self.message_window,
        ])

        self.kb = KeyBindings()

        @self.kb.add("enter")
        def _(event):
            choice = self.radio_list.current_value
            if choice == "view":
                self._show_view_screen()
            elif choice == "add":
                self._show_add_screen()
            elif choice == "load":
                self._show_load_screen()
            elif choice == "exit":
                event.app.exit()

        @self.kb.add("q")
        def _(event):
            event.app.exit()

        # Set initial layout and application
        self.app = Application(
            layout=Layout(Box(Frame(self.body), padding=2)),
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=True,
            style=self.style
        )

        # 👇 FIX: Ensure the radio list is focused on app start (needed for macOS)
        self.app.layout.focus(self.radio_list)

    def _set_body(self, new_body):
        self.app.layout.container = Box(Frame(new_body), padding=2)
        self.app.invalidate()

    def _show_message(self, message, color="white"):
        self.message_control.text = f"[{color}]{message}[/{color}]"
        self.app.invalidate()

    def _show_view_screen(self):
        new_body = HSplit([
            Label(text="📍 View Walkable Cities - Coming Soon!", style="bold"),
            Button(text="Back to Main Menu", handler=lambda: self._set_body(self.body)),
        ])
        self._set_body(new_body)

    def _show_add_screen(self):
        new_body = HSplit([
            Label(text="➕ Add a New City - Pretend there's a form here", style="bold"),
            Button(text="Back to Main Menu", handler=lambda: self._set_body(self.body)),
        ])
        self._set_body(new_body)

    def _show_load_screen(self):
        new_body = HSplit([
            Label(text="📦 Loading Sample Data... Done!", style="bold"),
            Button(text="Back to Main Menu", handler=lambda: self._set_body(self.body)),
        ])
        self._set_body(new_body)

    def run(self):
        self.app.run()


if __name__ == "__main__":
    WalkdataCLI().run()

