from rich.console import Console
import questionary

console = Console()

def main_menu():
    while True:
        choice = questionary.select(
            "Welcome to Walkdata CLI — Choose an action:",
            choices=[
                "View Walkable Cities",
                "Add a New City",
                "Load Sample Data",
                "Exit"
            ]
        ).ask()

        if choice == "View Walkable Cities":
            console.print("[bold cyan]Feature coming soon: View Walkable Cities[/bold cyan]")

        elif choice == "Add a New City":
            name = questionary.text("Enter city name:").ask()
            score = questionary.text("Enter walkability score:").ask()
            console.print(f"[green]Pretending to add {name} with score {score}...[/green]")

        elif choice == "Load Sample Data":
            console.print("[yellow]Pretending to load sample data...[/yellow]")

        elif choice == "Exit":
            console.print("[bold red]Goodbye![/bold red]")
            break

if __name__ == "__main__":
    main_menu()

