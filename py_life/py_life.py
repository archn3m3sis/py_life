"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
    )

app = rx.App()
app.add_page(index, route="/")
