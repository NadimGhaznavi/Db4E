from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual_plotext import PlotextPlot

class BarChartApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield PlotextPlot()
        yield Footer()

    def on_mount(self) -> None:
        plt = self.query_one(PlotextPlot).plt

        # Sample data for the bar chart
        categories = ["A", "B", "C", "D"]
        values = [10, 25, 15, 30]

        # Plotting the bar chart
        plt.bar(categories, values, color="blue")
        plt.title("Bar Chart Example")

if __name__ == "__main__":
    app = BarChartApp()
    app.run()