from textual.app import App, ComposeResult
from textual_plot import HiResMode, PlotWidget
from textual.widgets import Static


class PlotBackgroundApp(App[None]):
    CSS = """
        #plot {
            height: 1fr;
            margin: 1 2;
            background: black;
        }

        Static {
            height: 1fr;
            content-align: center middle;
        }
    """

    def compose(self) -> ComposeResult:
        yield PlotWidget(id="plot")
        yield Static("Placeholder showing theme colors")

    def on_mount(self) -> None:
        self.theme = "textual-light"
        plot = self.query_one(PlotWidget)
        plot.plot(
            x=[0, 1, 2, 3, 4, 5], y=[0, 1, 4, 9, 16, 25], hires_mode=HiResMode.QUADRANT
        )


PlotBackgroundApp().run()