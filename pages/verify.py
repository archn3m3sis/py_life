import reflex as rx
from auth_state import AuthState


def verify_page(token: str) -> rx.Component:
    AuthState.verify(token)   # triggered on mount
    return rx.center(
        rx.spinner(),  # simple loading indicator
        class_name="h-screen"
    )
