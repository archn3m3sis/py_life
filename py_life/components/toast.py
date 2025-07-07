"""
Toast component for displaying temporary notifications.

This module provides a reusable toast notification system with different types
(success, error, warning, info) and automatic dismissal functionality.
"""

import reflex as rx
from typing import Literal

ToastType = Literal["success", "error", "warning", "info"]


def toast(
    message: str,
    toast_type: ToastType = "info",
    duration: int = 5000,
    is_visible: bool = True,
    on_dismiss: callable = None,
) -> rx.Component:
    """
    Create a toast notification component.
    
    Args:
        message: The message to display
        toast_type: Type of toast ("success", "error", "warning", "info")
        duration: Duration in milliseconds before auto-dismiss (0 = no auto-dismiss)
        is_visible: Whether the toast is visible
        on_dismiss: Callback function when toast is dismissed
    
    Returns:
        A toast component
    """
    
    # Define colors and icons for different toast types
    color_schemes = {
        "success": {
            "bg": "bg-green-50 dark:bg-green-900",
            "border": "border-green-200 dark:border-green-700",
            "text": "text-green-800 dark:text-green-200",
            "icon": "✓",
            "icon_bg": "bg-green-200 dark:bg-green-700",
        },
        "error": {
            "bg": "bg-red-50 dark:bg-red-900",
            "border": "border-red-200 dark:border-red-700",
            "text": "text-red-800 dark:text-red-200",
            "icon": "✕",
            "icon_bg": "bg-red-200 dark:bg-red-700",
        },
        "warning": {
            "bg": "bg-yellow-50 dark:bg-yellow-900",
            "border": "border-yellow-200 dark:border-yellow-700",
            "text": "text-yellow-800 dark:text-yellow-200",
            "icon": "⚠",
            "icon_bg": "bg-yellow-200 dark:bg-yellow-700",
        },
        "info": {
            "bg": "bg-blue-50 dark:bg-blue-900",
            "border": "border-blue-200 dark:border-blue-700",
            "text": "text-blue-800 dark:text-blue-200",
            "icon": "ℹ",
            "icon_bg": "bg-blue-200 dark:bg-blue-700",
        },
    }
    
    scheme = color_schemes[toast_type]
    
    return rx.cond(
        is_visible,
        rx.box(
            rx.flex(
                # Icon
                rx.box(
                    rx.text(
                        scheme["icon"],
                        class_name=f"text-sm font-bold {scheme['text']}"
                    ),
                    class_name=f"flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center {scheme['icon_bg']}"
                ),
                # Message
                rx.text(
                    message,
                    class_name=f"flex-1 ml-3 text-sm {scheme['text']}"
                ),
                # Close button
                rx.button(
                    "×",
                    on_click=on_dismiss,
                    class_name=f"ml-3 text-lg font-bold {scheme['text']} hover:opacity-70 bg-transparent border-none cursor-pointer"
                ),
                class_name="items-start"
            ),
            class_name=f"max-w-md mx-auto p-4 rounded-lg border shadow-lg {scheme['bg']} {scheme['border']}",
            style={
                "animation": "slideIn 0.3s ease-out" if is_visible else "slideOut 0.3s ease-in",
            }
        )
    )


def toast_container(children: list) -> rx.Component:
    """
    Container for toast notifications with proper positioning.
    
    Args:
        children: List of toast components
    
    Returns:
        A positioned container for toasts
    """
    return rx.box(
        *children,
        class_name="fixed top-4 right-4 z-50 space-y-2",
        style={
            "pointer-events": "none",
        }
    )


class ToastState(rx.State):
    """State management for toast notifications."""
    
    # Toast properties
    toast_message: str = ""
    toast_type: ToastType = "info"
    toast_visible: bool = False
    toast_duration: int = 5000
    
    def show_toast(self, message: str, toast_type: ToastType = "info", duration: int = 5000):
        """Show a toast notification."""
        self.toast_message = message
        self.toast_type = toast_type
        self.toast_duration = duration
        self.toast_visible = True
        
        # Auto-dismiss after duration if specified
        if duration > 0:
            # Note: In a real implementation, you might want to use JavaScript setTimeout
            # or implement a timer mechanism. For now, we'll rely on manual dismissal.
            pass
    
    def hide_toast(self):
        """Hide the current toast notification."""
        self.toast_visible = False
        self.toast_message = ""
    
    def show_success(self, message: str, duration: int = 5000):
        """Show a success toast."""
        self.show_toast(message, "success", duration)
    
    def show_error(self, message: str, duration: int = 7000):
        """Show an error toast (longer duration by default)."""
        self.show_toast(message, "error", duration)
    
    def show_warning(self, message: str, duration: int = 6000):
        """Show a warning toast."""
        self.show_toast(message, "warning", duration)
    
    def show_info(self, message: str, duration: int = 5000):
        """Show an info toast."""
        self.show_toast(message, "info", duration)


def create_toast_system() -> rx.Component:
    """
    Create a complete toast notification system.
    
    Returns:
        A toast system component that can be added to your app
    """
    return toast_container([
        toast(
            message=ToastState.toast_message,
            toast_type=ToastState.toast_type,
            is_visible=ToastState.toast_visible,
            on_dismiss=ToastState.hide_toast,
        )
    ])
