
# Python imports
import math
import logging
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb

# External imports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# Local imports
import ice_extractor as ie

logger = logging.getLogger(__name__)


class IceGUI():
    def __init__(self):
        root = tk.Tk()
        root.title("Ice Data Extractor")
        root.minsize(800, 600)

        menubar = tk.Menu()
        file_menu = tk.Menu(menubar, tearoff=False)

        file_menu.add_command(
            label="Load data...",
            accelerator="Ctrl+O",
            command=self.load_data
        )

        file_menu.add_command(
            label="Save data...",
            accelerator="Ctrl+S",
            command=self.save_data
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit...",
            accelerator="Ctrl+Q",
            command=self.exit_app
        )

        menubar.add_cascade(menu=file_menu, label="File")
        root.config(menu=menubar)

        root.bind_all("<Control-o>", self.load_data)
        root.bind_all("<Control-s>", self.save_data)
        root.bind_all("<Control-q>", self.exit_app)

        left_frame = tk.Frame(root, bd=3, relief=tk.GROOVE)
        left_frame.pack(side=tk.LEFT, anchor=tk.N, fill=tk.Y)

        lf1 = tk.Frame(left_frame)
        lf1.pack(side=tk.TOP, anchor=tk.E)
        tk.Label(lf1, text="Step [m]: ").pack(side=tk.LEFT, padx=5, pady=5)
        step_input = tk.Entry(lf1)
        step_input.insert(0, "500.0")
        step_input.pack(side=tk.LEFT, padx=5, pady=5)

        lf2 = tk.Frame(left_frame)
        lf2.pack(side=tk.TOP, anchor=tk.E)
        tk.Label(lf2, text="Angle [°]: ").pack(side=tk.LEFT, padx=5, pady=5)
        angle_input = tk.Entry(lf2)
        angle_input.bind("<Return>", self.change_arrow_text)
        angle_input.bind("<FocusOut>", self.change_arrow_text)
        angle_input.insert(0, "0.0")
        angle_input.pack(side=tk.LEFT, padx=5, pady=5)

        min_rough_label = tk.Label(left_frame, text="Min. roughness: ###")
        min_rough_label.pack(side=tk.TOP, padx=5, pady=5)
        max_rough_label = tk.Label(left_frame, text="Max. roughness: ###")
        max_rough_label.pack(side=tk.TOP, padx=5, pady=5)

        arrow_canvas = tk.Canvas(left_frame, width=100, height=100, bg="black")
        arrow_canvas.create_oval(0, 0, 100, 100, fill="white")
        angle_arrow = arrow_canvas.create_line(0, 50, 100, 50, arrow=tk.LAST,
            width=10, fill="blue", arrowshape=(20, 20, 10))
        arrow_canvas.bind("<B1-Motion>", self.change_arrow_mouse)
        arrow_canvas.bind("<Button-1>", self.change_arrow_mouse)
        arrow_canvas.pack(side=tk.TOP, padx=5, pady=5)

        extract_button = tk.Button(left_frame, text="Extract", command=self.extract_data)
        extract_button.pack(side=tk.TOP, padx=5, pady=5)

        status_label = tk.Label(left_frame, text="Ready.")
        status_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=5, pady=5)

        right_frame = tk.Frame(root, bd=3, relief=tk.GROOVE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        plot_frame = tk.Frame(right_frame)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        plot_figure = Figure(figsize=(5, 4), dpi=100)
        plot_canvas = FigureCanvasTkAgg(plot_figure, master=plot_frame)
        plot_canvas.draw()
        plot_toolbar = NavigationToolbar2Tk(plot_canvas, plot_frame, pack_toolbar=False)
        plot_toolbar.update()
        plot_toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.root = root
        self.step_input = step_input
        self.angle_input = angle_input
        self.arrow_canvas = arrow_canvas
        self.status_label = status_label
        self.angle_arrow = angle_arrow
        self.angle: float = 0.0

        self.plot_figure = plot_figure
        self.plot_canvas = plot_canvas

        self.min_rough_label = min_rough_label
        self.max_rough_label = max_rough_label

        self.extractor = ie.IceExtractor(root, status_label)

        self.data_modified: bool = False

    def run(self):
        self.root.mainloop()

    def change_arrow_mouse(self, event):
        r: float = 50.0
        x: float = event.x - r
        y: float = event.y - r
        length: float = math.hypot(x, y)
        angle: float = math.asin(y/length)
        angle_d: float = math.degrees(angle)

        if x < 0.0:
            angle_d = 180.0 - angle_d
        else:
            if angle_d < 0.0:
                angle_d = 360.0 + angle_d

        self.angle = angle_d
        self.angle_input.delete(0, tk.END)
        self.angle_input.insert(0, f"{self.angle}")
        self.change_arrow()

    def change_arrow_text(self, event=None):
        angle_t: str = self.angle_input.get()

        try:
            angle_d: float = float(angle_t)

            if (angle_d < 0.0) or (angle_d > 360.0):
                mb.showerror("Angle value error", f"The angle must be between 0.0 and 360.0, current value: {angle_t}")
            else:
                self.angle = angle_d
                self.change_arrow()

        except ValueError:
            mb.showerror("Angle value error", f"This is not a valid floating point number: {angle_t}")

    def change_arrow(self):
        r: float = 50.0
        angle: float = math.radians(self.angle)
        x: float = math.cos(angle)
        y: float = math.sin(angle)

        x1: float = r * (1.0 - x)
        y1: float = r * (1.0 - y)
        x2: float = r * (1.0 + x)
        y2: float = r * (1.0 + y)

        self.arrow_canvas.coords(self.angle_arrow, x1, y1, x2, y2)

    def check_empty_data(self) -> bool:
        if self.extractor.is_empty():
            mb.showerror("No data", "No data has been loaded. Please load a datafile first!")
            return False
        else:
            return True

    def extract_data(self):
        if self.check_empty_data():
            step_t = self.step_input.get()

            try:
                step_f: float = float(step_t)
                self.extractor.step = step_f
                self.extractor.angle = self.angle
                self.extractor.extract_points()
                self.plot_data()
                self.data_modified = True
                self.min_rough_label.config(text=f"Min. roughness: {self.extractor.min_rough:.2f}")
                self.max_rough_label.config(text=f"Max. roughness: {self.extractor.max_rough:.2f}")
                self.status_label.config(text="Ready.")
            except ValueError:
                mb.showerror("Step value error", f"This is not a valid floating point number: {step_t}")

    def ask_confirm(self) -> bool:
        if self.data_modified:
            res: bool = mb.askyesno("Confirm", "The data is not saved. Do you want to continue (changes will be lost) ?")
            return res
        else:
            return True

    def load_data(self, event=None):
        if self.ask_confirm():
            filename: str = fd.askopenfilename()
            if filename:
                try:
                    self.extractor.read_file(filename)
                    self.plot_data()
                    self.angle = self.extractor.angle
                    self.angle_input.delete(0, tk.END)
                    self.angle_input.insert(0, f"{self.angle:.2f}")
                    self.change_arrow()
                    self.data_modified = True
                    self.min_rough_label.config(text=f"Min. roughness: {self.extractor.min_rough:.2f}")
                    self.max_rough_label.config(text=f"Max. roughness: {self.extractor.max_rough:.2f}")
                    self.status_label.config(text="Ready.")
                except Exception as err:
                    mb.showerror("IO Error", f"An error occured while reading the file: '{err}'")


    def save_data(self, event=None):
        filename: str = fd.asksaveasfilename()
        if self.check_empty_data() and filename:
            self.extractor.save_roughness(filename)
            self.data_modified = False
            mb.showinfo("Data saved", f"All roughness points have been saved to: '{filename}'")

    def exit_app(self, event=None):
        if self.ask_confirm():
            self.root.destroy()

    def plot_data(self):
        self.plot_figure.clear()
        top_ax = self.plot_figure.add_subplot(2, 1, 1)
        bottom_ax = self.plot_figure.add_subplot(2, 1, 2, sharex=top_ax, sharey=top_ax)
        self.plot_figure.suptitle("Heatmaps of measured points")

        color_map = top_ax.tricontourf(
            self.extractor.original_points_x,
            self.extractor.original_points_y,
            self.extractor.original_points_z,
            cmap="winter")

        # Plot start and end points:
        for (x, y, _) in self.extractor.start_points:
            top_ax.plot(x, y, "yo")

        for (x, y, _) in self.extractor.end_points:
            top_ax.plot(x, y, "go")

        # Plot min / max roughness points:
        top_ax.plot(self.extractor.min_x, self.extractor.min_y, "rv", mec="k")
        top_ax.plot(self.extractor.max_x, self.extractor.max_y, "r^", mec="k")


        self.plot_figure.colorbar(color_map, ax=top_ax)
        top_ax.tick_params(axis="x", labelrotation=45)

        rough_x = []
        rough_y = []
        rough_z = []

        for (_, x, y, z) in self.extractor.row_roughness:
            rough_x.append(x)
            rough_y.append(y)
            rough_z.append(z)

        color_map = bottom_ax.tricontourf(
            rough_x,
            rough_y,
            rough_z,
            cmap="cool")

        self.plot_figure.colorbar(color_map, ax=bottom_ax)
        bottom_ax.tick_params(axis="x", labelrotation=45)

        self.plot_canvas.draw()

