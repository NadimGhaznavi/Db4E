from textual.theme import Theme

db4e_theme = Theme(
    name="db4e",
    primary="#4d74a5",
    secondary="#81A1C1",
    accent="#d89339",
    foreground="#7b604b",
    background="#3a2406",
    success="#25962f",
    warning="#e05a02",
    error="#ae0e0c",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)