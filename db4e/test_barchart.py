
from textual.app import App, ComposeResult

from db4e.Widgets.BarChart import BarChart
from db4e.Modules.MiningETL import MiningETL
from db4e.Modules.MiningDb import MiningDb





class MinimalApp(App[None]):


    barchart = BarChart("Barchart", "barchart")

    def compose(self) -> ComposeResult:
        self.barchart


    def on_mount(self):
        barchart  = self.query_one("#barchart")
        db = MiningDb()
        mining_etl = MiningETL(db)
        
        data = mining_etl.get_block_found_events("Main")
        barchart.load_data(data["times"], data["values"])
        barchart.barchart_plot()


if __name__ == "__main__":
    app = MinimalApp()
    app.run()


MinimalApp().run()