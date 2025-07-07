import reflex as rx
from ..auth import AuthState


def login_page() -> rx.Component:
    return rx.center(
        rx.card(
            rx.heading("Sign in", class_name="text-2xl mb-4"),
            rx.input(
                placeholder="Email address",
                value=AuthState.email,
                on_change=AuthState.set_email,
                class_name="input input-bordered w-full mb-4"
            ),
            rx.button("Send magic link", on_click=AuthState.send_link,
                      class_name="btn btn-primary w-full"),
            rx.alert(AuthState.message, rx.color("success"), is_open=AuthState.message != ""),
            rx.alert(AuthState.error, rx.color("error"),  is_open=AuthState.error != ""),
        ),
        class_name="h-screen"
    )
