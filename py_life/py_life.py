"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from pages.verify import verify_page
from pages.login import login_page
from auth_state import AuthState


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    # Protect the index page - redirect unauthenticated users to login
    if not AuthState.is_authenticated():
        return rx.redirect("/login")
    
    return rx.container(
        rx.color_mode.button(position="top-right"),
    )

app = rx.App()
app.add_page(index, route="/")
app.add_page(login_page, route="/login")
app.add_page(verify_page, route="/verify/[token]")
