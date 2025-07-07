import reflex as rx

config = rx.Config(
    app_name="py_life",
    db_url="sqlite:///py_life/database/data/pylife.db",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
