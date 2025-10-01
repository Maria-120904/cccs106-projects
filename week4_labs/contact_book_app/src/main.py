import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 500
    page.window_height = 700
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT  # Default to light mode
    
    db_conn = init_db()
    
    # Theme toggle function
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_switch.label = "Light Mode"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_switch.label = "Dark Mode"
        page.update()
    
    # Theme toggle switch
    theme_switch = ft.ElevatedButton(
        "Dark Mode",
        icon=ft.Icons.DARK_MODE,
        on_click=toggle_theme,
        width=150
    )
    
    # Input fields with consistent width
    name_input = ft.TextField(label="Name", width=400)
    phone_input = ft.TextField(label="Phone", width=400)
    email_input = ft.TextField(label="Email", width=400)
    inputs = (name_input, phone_input, email_input)
    
    # Add contact button centered
    add_button = ft.ElevatedButton(
        "Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn),
        width=200
    )
    
    # Search field
    search_input = ft.TextField(
        label="Search contacts...",
        prefix_icon=ft.Icons.SEARCH,
        width=400,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, e.control.value)
    )
    
    # Contacts list view with fixed width
    contacts_list_view = ft.ListView(
        expand=1, 
        spacing=10, 
        auto_scroll=True,
        width=400
    )
    
    # Header with title and theme toggle
    header = ft.Row([
        ft.Text("Contact Book", size=24, weight=ft.FontWeight.BOLD),
        theme_switch
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400)
    
    # Main container with centered content
    main_content = ft.Column(
        [
            header,  # Header with theme toggle
            ft.Divider(height=20),
            name_input,
            phone_input,
            email_input,
            ft.Container(height=10),  # Spacing
            add_button,
            ft.Divider(height=20),
            ft.Text("Contacts", size=18, weight=ft.FontWeight.BOLD),
            search_input,
            ft.Container(
                content=contacts_list_view,
                width=400,
                height=300,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                padding=10
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    page.add(main_content)
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)