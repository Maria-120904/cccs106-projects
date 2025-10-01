import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

def display_contacts(page, contacts_list_view, db_conn, search_term=""):
    """Fetches and displays all contacts in the ListView, optionally filtered."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)
    for contact in contacts:
        contact_id, name, phone, email = contact
        
        # Create a modern card for each contact
        contact_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header with name and menu
                    ft.Row([
                        ft.Text(
                            name, 
                            size=18, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_800
                        ),
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    text="Edit",
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)
                                ),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(
                                    text="Delete",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda _, cid=contact_id: delete_contact(page, cid, db_conn, contacts_list_view)
                                ),
                            ],
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(height=1),
                    
                    # Contact details with icons
                    ft.Row([
                        ft.Icon(ft.Icons.PHONE, color=ft.Colors.GREEN, size=20),
                        ft.Text(phone, size=14),
                    ], spacing=8),
                    
                    ft.Row([
                        ft.Icon(ft.Icons.EMAIL, color=ft.Colors.BLUE, size=20),
                        ft.Text(email, size=14),
                    ], spacing=8),
                    
                ], spacing=8),
                padding=15,
                width=380
            ),
            elevation=2,
            margin=ft.margin.symmetric(vertical=4)
        )
        
        contacts_list_view.controls.append(contact_card)
    page.update()

def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list, with input validation."""
    name_input, phone_input, email_input = inputs
    has_error = False

    # Name validation
    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        has_error = True
    else:
        name_input.error_text = None

    # Phone validation
    if not phone_input.value.strip():
        phone_input.error_text = "Phone cannot be empty"
        has_error = True
    elif not phone_input.value.isdigit():
        phone_input.error_text = "Phone must be numbers only"
        has_error = True
    else:
        phone_input.error_text = None

    # Email validation
    if not email_input.value.strip():
        email_input.error_text = "Email cannot be empty"
        has_error = True
    elif "@" not in email_input.value:
        email_input.error_text = "Email must contain '@'"
        has_error = True
    else:
        email_input.error_text = None

    page.update()

    if has_error:
        return

    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)
    for field in inputs:
        field.value = ""
    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view):
    """Shows a confirmation dialog before deleting a contact."""
    def confirm_delete(e):
        dialog.open = False
        page.update()
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn)

    def cancel_delete(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("No", on_click=cancel_delete),
            ft.TextButton("Yes", on_click=confirm_delete),
        ],
    )
    page.open(dialog)

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit an existing contact."""
    contact_id, name, phone, email = contact
    
    # Create input fields with current values
    edit_name = ft.TextField(label="Name", value=name, width=300)
    edit_phone = ft.TextField(label="Phone", value=phone, width=300)
    edit_email = ft.TextField(label="Email", value=email, width=300)
    
    def save_and_close(e):
        # Update the contact in database
        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)
    
    def cancel_edit(e):
        dialog.open = False
        page.update()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([
            edit_name,
            edit_phone,
            edit_email,
        ], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=cancel_edit),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    page.open(dialog)