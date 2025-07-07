import reflex as rx
import auth_utils


class AuthState(rx.State):
    email: str = ""
    message: str = ""
    error: str = ""

    async def send_link(self):
        try:
            link = await rx.run_in_thread(auth_utils.create_magic_link, self.email)
            await rx.run_in_thread(auth_utils.send_magic_link, self.email, link)
            self.message = "Magic link sent! Check your inbox."
        except Exception as e:
            error_message = str(e)
            if 'expired' in error_message or 'used' in error_message:
                error_message = "Link expired—request a new one."
            self.error = error_message

    async def verify(self, token: str):
        try:
            user = await rx.run_in_thread(auth_utils.verify_token, token)
            rx.session.set("user_id", str(user.id))
            self.message = "Login successful!"
            return rx.redirect("/")
        except Exception as e:
            error_message = str(e)
            if 'expired' in error_message or 'used' in error_message:
                error_message = "Link expired—request a new one."
            self.error = error_message
            return rx.redirect("/login")


def is_authenticated() -> bool:
    """Check if the current user is authenticated."""
    return rx.session.get("user_id") is not None


def logout():
    """Log out the current user by clearing the session."""
    rx.session.clear()
    return rx.redirect("/login")
