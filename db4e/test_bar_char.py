from textual.app import App, ComposeResult

from textual_plot import PlotWidget, HiResMode

from 


class MinimalApp(App[None]):
    def compose(self) -> ComposeResult:
        yield PlotWidget()

    def on_mount(self) -> None:
        plot = self.query_one(PlotWidget)
        x_list = [ 0, 1, 2, 3, 4, 5, 6 ]
        y_list = [ 3, 7, 6, 9, 3, 0, 4 ]

        x_list = self.gen_x(x_list)
        y_list = self.gen_y(y_list)

        plot.plot(x=x_list, y=y_list, hires_mode=HiResMode.BRAILLE)

    def gen_x(self, x_list):
        new_list = []
        for x in x_list:
            new_list.extend([x + 0, x + 0.1, x + 0.101])
            new_list.extend([x + 0.898, x + 0.899, x + 0.9])
        return new_list

    def gen_y(self, y_list):
        new_list = []
        for y in y_list:
            new_list.extend([0, 0, y, y, 0, 0])
        return new_list


if __name__ == "__main__":
    app = MinimalApp()
    app.run()


MinimalApp().run()