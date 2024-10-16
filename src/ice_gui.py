
# Python std lib
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb

# Local imports
import ice_extractor as ie
import ice_plotter as ip


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

        file_menu.add_command(
            label="Save plot...",
            command=self.save_plot
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

        left_frame = tk.Frame(root, bg="red", bd=3, relief=tk.GROOVE)
        left_frame.pack(side=tk.LEFT, anchor=tk.N)

        lf1 = tk.Frame(left_frame)
        lf1.pack(side=tk.TOP, anchor=tk.E)
        tk.Label(lf1, text="Step: ").pack(side=tk.LEFT, padx=5, pady=5)
        step_input = tk.Entry(lf1)
        step_input.pack(side=tk.LEFT, padx=5, pady=5)

        lf2 = tk.Frame(left_frame)
        lf2.pack(side=tk.TOP, anchor=tk.E)
        tk.Label(lf2, text="Angle: ").pack(side=tk.LEFT, padx=5, pady=5)
        angle_input = tk.Entry(lf2)
        angle_input.pack(side=tk.LEFT, padx=5, pady=5)

        extract_button = tk.Button(left_frame, text="Extract", command=self.extract_data)
        extract_button.pack(side=tk.TOP, padx=5, pady=5)

        right_frame = tk.Frame(root, bg="yellow", bd=3, relief=tk.GROOVE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        top_plot_frame = tk.Frame(right_frame, bg="green")
        top_plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        bottom_plot_frame = tk.Frame(right_frame, bg="blue")
        bottom_plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.root = root
        self.step_input = step_input
        self.angle_input = angle_input

        self.extractor = ie.IceExtractor()
        self.plotter = ip.IcePlotter()

        self.data_modified: bool = False

    def run(self):
        self.root.mainloop()

    def extract_data(self):
        pass

    def ask_confirm(self) -> bool:
        if self.data_modified:
            res: bool = mb.askyesno("Confirm", "The data is not saved. Do you want to continue ?")
            return res
        else:
            return True

    def load_data(self, event=None):
        if self.ask_confirm():
            filename: str = fd.askopenfilename()
            if filename:
                self.extractor.read_file(filename)
                self.data_modified = True
                self.plotter.get_data_from_extractor(self.extractor)

    def save_data(self, event=None):
        filename: str = fd.asksaveasfilename()
        if filename:
            self.extractor.save_extracted_points(filename)
            self.data_modified = False

    def save_plot(self):
        filename: str = fd.asksaveasfilename()
        if filename:
            self.plotter.save_figure(filename)

    def exit_app(self, event=None):
        if self.ask_confirm():
            self.root.destroy()

