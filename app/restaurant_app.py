""" User Interface responsible for all this app
"""

import os
from datetime import datetime
from tkinter import Event, ttk, END
from ttkthemes import ThemedTk
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk


from scient_calc import ScientCalc
from tooltip import ToolTip


class RestaurantSystemUI(ThemedTk):
    """Main class for the whole interface"""

    # TODO Find a way to use transparency (nice result)
    # self.wm_attributes("-transparentcolor", "#000")
    # TODO Add database
    # TODO resize down

    def __init__(self, *args, **kwargs):
        ThemedTk.__init__(self, theme="equilux")
        restaurant_name = kwargs.get("restaurant_name")
        rest_img = kwargs.get("restaurant_image")

        self.articles = {
            "Fried Potatoes": 4,
            "Chicken Burger": 8,
            "Waffles": 3.5,
            "Chicken Royal Salad": 10,
            "Veggie Salad": 9,
        }
        self.operands = ["+", "-", "*", "/"]
        self.currency = "$"
        self.restaurant_name = restaurant_name or "Le petit français"
        self.calc = ScientCalc()

        self.bg_color = "#252525"
        self.fullscreen = False
        self.logo_path = None
        self.food_img = None

        self.entries = []
        self.calc_buttons = []
        self.operand_buttons = []
        self.low_calc_buttons = []
        self.control_buttons = []

        # Trying to minimize class attributes
        self.rand_widget_dict = {}
        # {text : (label, entry)
        self.food_widgets = {}
        self.total_widgets = {}
        self.article_widgets = {}
        # {entry: (button +, button -)}
        self.entry_buttons = {}
        self.x = 0
        self.y = 0
        self._width = 1028
        self._height = 500

        self._init_ui(rest_img)

    def _init_ui(self, rest_img: str):
        """Init the whole User Interface"""
        self.title("Restaurant Management System")
        self.geometry(f"{self._width}x{self._height}+100+100")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.98)
        self.configure(bg=self.bg_color)
        self._configure_style()

        curr_path = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(curr_path, "pen.ico")
        rest_img = rest_img or "ananas.png"
        self.logo_path = os.path.join(curr_path, rest_img)
        self.iconbitmap(ico_path)

        ####### TOP MENU
        notebk = ttk.Notebook(self)
        notebk.place(x=0, y=25)
        self.common_frame = ttk.Frame(notebk, width=self._width, height=self._height)
        self.price_frame = ttk.Frame(notebk, width=self._width, height=self._height)
        notebk.add(self.common_frame, text="Billing ۩ ")
        notebk.add(self.price_frame, text=f"Prices {self.currency} ")
        self.menu_bar = ttk.Frame(self, style="menu.TLabel")
        self.title_menu = ttk.Label(
            self.menu_bar,
            text=f"{self.restaurant_name} - Improved Restaurant Management System",
            style="smalltitle.TLabel",
        )
        self.minimize_button = ttk.Button(
            self.menu_bar, text="_", style="exit.TButton", command=self._minimize
        )
        self.fullscreen_button = ttk.Button(
            self.menu_bar,
            text="□",
            style="exit.TButton",
            command=self._switch_fullscreen,
        )
        self.exit_button = ttk.Button(
            self.menu_bar, text="X", style="exit.TButton", command=self.destroy
        )

        # https://stackoverflow.com/questions/4055267#answer-4055612
        self.menu_bar.bind("<ButtonPress-1>", self._start_moving)
        self.menu_bar.bind("<ButtonRelease-1>", self._stop_moving)
        self.menu_bar.bind("<B1-Motion>", self._on_motion)
        self.menu_bar.bind("<Double-Button-1>", lambda x: self._switch_fullscreen())
        self.title_menu.bind("<ButtonPress-1>", self._start_moving)
        self.title_menu.bind("<ButtonRelease-1>", self._stop_moving)
        self.title_menu.bind("<B1-Motion>", self._on_motion)
        self.title_menu.bind("<Double-Button-1>", lambda x: self._switch_fullscreen())
        notebk.bind("<Map>", self._frame_mapped)

        self.title_label = ttk.Label(
            self.common_frame, text="Restaurant Management®", style="title.TLabel"
        )
        localtime = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
        self.time_label = ttk.Label(
            self.common_frame, text=localtime, style="time.TLabel", cursor="clock"
        )

        self._display_food_part(self.common_frame)
        self._display_total_part(self.common_frame)
        self._display_calculator_part(self.common_frame)
        self._display_control_button_part(self.common_frame)

        ################# FRAME 2
        self._display_price_frame(self.price_frame)

        self.clear_fields()
        self._update_time()
        self.place_widgets()

    @property
    def bill(self):
        """Resturn the customer bill which will be display on the PDF file"""
        return "\n".join(
            [
                f"{text} : {price_tuple[1].get()}"
                for text, price_tuple in self.total_widgets.items()
            ]
        )

    def _configure_style(self):
        """Configure all the styles used by the widgets equilux is the default theme used.
        It comes from the ttkthemes library and some default mapping attributes are redifined"""
        style = ttk.Style()
        style.theme_settings(
            "equilux",
            {
                "TButton": {
                    "configure": {"padding": -5, "focuscolor": "#464646"},
                    "map": {
                        "foreground": [
                            ("active", "#E1B12C"),
                            ("!disabled", "#E1B12C"),
                        ],
                        "background": [
                            ("active", "#E1B12C"),
                            ("!disabled", self.bg_color),
                        ],
                    },
                },
                "TNotebook": {"configure": {"tabmargins": [0, 0, 0, 0]}},
                "TNotebook.Tab": {
                    "configure": {"padding": [25, 5], "focuscolor": "#464646"},
                    "map": {"expand": [("selected", [5, 1, 5, 3])],},
                },
                "TFrame": {"configure": {"background": self.bg_color},},
                "TLabel": {"configure": {"background": self.bg_color},},
                "TEntry": {"configure": {"background": self.bg_color}},
            },
        )
        style.configure(".", font="{U.S. 101} 15 bold", foreground="#fff")
        style.configure("title.TLabel", font="{U.S. 101} 30 bold", foreground="#E1B12C")
        style.configure("smalltitle.TLabel", font="{U.S. 101} 10", background="#3C3C3C")
        style.configure("time.TLabel", foreground="#E84118")
        style.configure("res.TEntry", background="#000")
        style.configure("rfood.TLabel", foreground="#E1B12C")
        style.configure("yfood.TLabel", foreground="#E84118")
        style.configure("menu.TLabel", foreground="#CCCCCC", background="#3C3C3C")
        style.configure("exit.TButton", font="{U.S. 101} 10", foreground="#CCCCCC")
        style.map(
            "exit.TButton",
            foreground=[("active", "#CCCCCC"), ("!disabled", "#CCCCCC"),],
            background=[("active", "#ff0000"), ("!disabled", "#3C3C3C"),],
        )

    def _display_food_part(self, common_frame: ttk.Frame):
        """Display every food with corresponding buttons and entries"""
        self.rand_widget_dict["order_label"] = ttk.Label(
            common_frame, text="Order Num :"
        )
        self.rand_widget_dict["order_entry"] = ttk.Entry(
            common_frame, justify="center", cursor="arrow"
        )
        self.rand_widget_dict["order_entry"].bind("<Key>", lambda e: "break")
        self.add_buttons(self.rand_widget_dict["order_entry"])
        self.entries.append(self.rand_widget_dict["order_entry"])

        for item in self.articles:
            article_label = ttk.Label(common_frame, text=item)
            article_entry = ttk.Entry(common_frame, justify="center", cursor="arrow")
            article_entry.bind("<Key>", lambda e: "break")
            self.add_buttons(article_entry)
            self.food_widgets.update({item: (article_label, article_entry)})
            self.entries.append(article_entry)

    def _display_total_part(self, common_frame: ttk.Frame):
        """Display all the total price entries"""
        self.rand_widget_dict["discount_p_label"] = ttk.Label(
            common_frame, text="Discount %"
        )
        self.rand_widget_dict["discount_p_entry"] = ttk.Entry(
            common_frame, justify="center", cursor="arrow"
        )
        self.rand_widget_dict["discount_p_entry"].bind("<Key>", lambda e: "break")
        self.entries.append(self.rand_widget_dict["discount_p_entry"])
        self.add_buttons(self.rand_widget_dict["discount_p_entry"])

        prices_txt = [
            "Cost",
            "Service Charge",
            "Tax",
            "SubTotal",
            "Discount",
            "Total",
        ]
        for price_txt in prices_txt:
            total_label = ttk.Label(common_frame, text=price_txt)
            price_entry = ttk.Entry(common_frame, justify="center", cursor="arrow")
            price_entry.bind("<Key>", lambda e: "break")
            self.entries.append(price_entry)
            self.total_widgets.update({price_txt: (total_label, price_entry)})

    def _display_calculator_part(self, common_frame):
        """Display the calculator"""
        res_entry = ttk.Entry(
            common_frame, style="res.TEntry", justify="center", cursor="arrow"
        )
        res_entry.bind("<Key>", lambda e: "break")
        self.rand_widget_dict["res_entry"] = res_entry
        self.entries.append(res_entry)
        for i in range(1, 10):
            # x=i+1 to avoid reference to final value of i
            calc_button = ttk.Button(
                common_frame,
                text=i,
                command=lambda x=i: self.add_to_calc_entry(x),
                cursor="hand2",
            )
            self.calc_buttons.append(calc_button)

        for operand in self.operands:
            operand_button = ttk.Button(
                common_frame,
                text=operand,
                command=lambda x=operand: self.add_to_calc_entry(x),
                cursor="hand2",
            )
            self.operand_buttons.append(operand_button)
        zero_button = ttk.Button(
            common_frame,
            text=0,
            command=lambda: self.add_to_calc_entry(0),
            cursor="hand2",
        )
        self.low_calc_buttons.append(zero_button)
        reset_button = ttk.Button(
            common_frame, text="C", command=self._erase_calc, cursor="hand2"
        )
        self.low_calc_buttons.append(reset_button)
        dot_button = ttk.Button(
            common_frame,
            text=".",
            command=lambda: self.add_to_calc_entry("."),
            cursor="hand2",
        )
        self.low_calc_buttons.append(dot_button)
        self.rand_widget_dict["equal_button"] = ttk.Button(
            common_frame,
            text="=",
            command=lambda: self.compute_string(
                self.rand_widget_dict["res_entry"].get()
            ),
            cursor="hand2",
        )

    def _display_control_button_part(self, common_frame: ttk.Frame):
        """Display RESt and SAVE buttons"""
        button_functions = {
            "RESET": self.clear_fields,
            "SAVE": self.save_bill_to_pdf,
        }
        for button_txt in button_functions:
            control_button = ttk.Button(
                common_frame,
                text=button_txt,
                command=button_functions[button_txt],
                cursor="hand2",
            )
            self.control_buttons.append(control_button)
            if button_txt == "SAVE":
                ToolTip(control_button, text="Export the order to pdf")

    def _display_price_frame(self, price_frame: ttk.Frame):
        """Display the price of the food in the second notebook frame"""
        articles = {"Food": "Price", **self.articles}
        for food in articles:
            food_label = ttk.Label(price_frame, text=food, style="rfood.TLabel")
            price_label = ttk.Label(
                price_frame,
                text=f"{articles[food]} {self.currency}",
                style="yfood.TLabel",
            )
            self.article_widgets.update({food: (food_label, price_label)})
        img = Image.open(self.logo_path).rotate(45, expand=True)
        tk_img = ImageTk.PhotoImage(img)
        logo = ttk.Label(price_frame, image=tk_img)
        logo.image = tk_img
        self.food_img = logo

    def _start_moving(self, event: Event):
        """The window start being dragged"""
        self.x = event.x
        self.y = event.y
        self.attributes("-alpha", 0.85)

    def _stop_moving(self, event: Event):
        """Reset coords after being dragged"""
        self.x = None
        self.y = None
        self.attributes("-alpha", 0.98)

    def _on_motion(self, event: Event):
        """Usedto move the window when it is dragged"""
        if not (self.x is None or self.y is None):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")

    def clear_fields(self):
        """Reset all the entries with 0"""
        price_entries = [price_tuple[1] for price_tuple in self.total_widgets.values()]
        for entry in self.entries:
            entry["state"] = "normal"
            entry.delete(0, END)
            if entry != self.rand_widget_dict["res_entry"]:
                entry.insert(0, 0)
                if entry in price_entries:
                    entry.insert(END, f".00 {self.currency}")
                elif entry == self.rand_widget_dict["discount_p_entry"]:
                    entry.insert(END, " %")
                entry["state"] = "readonly"

    def _erase_calc(self):
        """Reset the display ofthe calculator"""
        self.rand_widget_dict["res_entry"].delete(
            len(self.rand_widget_dict["res_entry"].get()) - 1, END
        )

    def _reset_calc_display(self):
        """Reset the display ofthe calculator"""
        self.rand_widget_dict["res_entry"].delete(0, END)

    def add_to_calc_entry(self, value):
        """Common method used to add operands and numbers to the calculator display"""
        self.rand_widget_dict["res_entry"].insert(END, value)

    def compute_string(self, calculator_str: str):
        """Use ScientCalc to compute calc display string"""
        if calculator_str:
            res, error = self.calc.compute_string(calculator_str)
            self.rand_widget_dict["res_entry"].delete(0, END)
            if error:
                self.calc_input_error()
            else:
                self.rand_widget_dict["res_entry"].insert(END, res)

    def calc_input_error(self):
        """Display errors appearing in the calculator display"""
        self.rand_widget_dict["res_entry"].delete(0, END)
        self.rand_widget_dict["res_entry"].insert(0, "You enter a wrong formula")
        self.rand_widget_dict["res_entry"].after(2000, self._reset_calc_display)

    def _update_time(self):
        """Update the time label every second"""
        self.time_label.configure(text=datetime.now().strftime("%A, %d %B %Y %H:%M:%S"))
        self.time_label.after(1000, self._update_time)

    def calc_total(self):
        """Calculate the bill price"""
        price = 0
        for text, article_tuple in self.food_widgets.items():
            price += self.articles[text] * int(article_tuple[1].get())
        self._display_total(price)

    def _display_total(self, price: float):
        """Display the bill prices"""
        discount_p = int(self.rand_widget_dict["discount_p_entry"].get().split()[0])
        price_entries = [price_tuple[1] for price_tuple in self.total_widgets.values()]
        for entry in [*price_entries, self.rand_widget_dict["discount_p_entry"]]:
            entry["state"] = "normal"
            entry.delete(0, END)
        service = price * 0.1
        tax = price * 0.2
        sub_total = price + service + tax
        total = sub_total * (1 - discount_p / 100)
        discount = round(sub_total - total, 2)
        self.rand_widget_dict["discount_p_entry"].insert(0, f"{discount_p} %")
        self.total_widgets["Cost"][1].insert(0, f"{price:.02f} {self.currency}")
        self.total_widgets["Service Charge"][1].insert(
            0, f"{service:.02f} {self.currency}"
        )
        self.total_widgets["Tax"][1].insert(0, f"{tax:.02f} {self.currency}")
        self.total_widgets["SubTotal"][1].insert(0, f"{sub_total:.02f} {self.currency}")
        self.total_widgets["Discount"][1].insert(0, f"{discount:.02f} {self.currency}")
        self.total_widgets["Total"][1].insert(0, f"{total:.02f} {self.currency}")
        for entry in [*price_entries, self.rand_widget_dict["discount_p_entry"]]:
            entry["state"] = "readonly"

    def add_buttons(self, entry: ttk.Entry):
        """Add button to add or remove food from the bill"""
        self.update()
        parent = self.nametowidget(entry.winfo_parent())
        add_button = ttk.Button(
            parent,
            text="+",
            command=lambda x=entry: self._increment(x),
            style="small.TButton",
            cursor="hand2",
        )
        minus_button = ttk.Button(
            parent,
            text="-",
            command=lambda x=entry: self._decrement(x),
            style="small.TButton",
            cursor="hand2",
        )
        self.entry_buttons.update({entry: (add_button, minus_button)})

    @classmethod
    def concrete_inc_dec(cls, entry: ttk.Entry, operand: str):
        """Concrete function to add or substract the value from an input"""
        old_value = entry.get().split()[0]
        value = float(old_value)
        if operand == "+":
            value += 1
        else:
            value -= 1
            if value < 0:
                value = 0
        if value == int(value):
            value = int(value)

        entry["state"] = "normal"
        entry.delete(0, "end")
        entry.insert(0, value)
        entry["state"] = "readonly"

    def _increment(self, entry: ttk.Entry):
        """Increment the value of the entry by 1"""
        self.concrete_inc_dec(entry, "+")
        self.calc_total()

    def _decrement(self, entry: ttk.Entry):
        """Decrement the value of the entry by 1"""
        self.concrete_inc_dec(entry, "-")
        self.calc_total()

    def save_bill_to_pdf(self):
        """Export the bill infos into a specific file inside the bill folder"""
        order_id = self.rand_widget_dict["order_entry"].get()
        date = self.time_label["text"]

        curr_path = os.path.dirname(os.path.abspath(__file__))
        order_dir = os.path.join(curr_path, "orders")
        if not os.path.isdir(order_dir):
            os.makedirs(order_dir)
        pdf_path = os.path.join(order_dir, f"Order_{order_id}.pdf")
        pdf_img_path = os.path.join(curr_path, "logo_pdf.png")
        self._create_png_picture(self.logo_path, pdf_img_path)

        cvs = canvas.Canvas(pdf_path, pagesize=(300, 300), bottomup=0)
        cvs.setAuthor("Hylectrif")
        cvs.setFont("Helvetica", 12)
        cvs.setTitle(f"Bill for the order n°{order_id} 📝")
        page_x, page_y = cvs._pagesize

        cvs.drawImage(
            pdf_img_path, page_x - 100, page_y - 100, mask="auto",
        )
        cvs.drawImage(
            pdf_img_path, 0, page_y - 100, mask="auto",
        )
        cvs.drawCentredString(page_x / 2, page_y / 10, f"֍ {self.restaurant_name} ֎")
        cvs.drawCentredString(page_x / 2, page_y / 10 + 25, date)
        cvs.roundRect(page_x / 2 - 25, page_y - 50, 50, 40, 50, fill=1)

        for index, text in enumerate(self.bill.split("\n"), 1):
            cvs.drawCentredString(page_x / 2, page_y / 4 + index * 25, text)
        cvs.save()

    @classmethod
    def _create_png_picture(cls, curr_path: str, final_path):
        """Create a minify version of the logo to print on the pdf file"""
        if not os.path.isfile(final_path):
            img = Image.open(curr_path)
            img = img.resize((100, 100), Image.ANTIALIAS).transpose(
                Image.FLIP_TOP_BOTTOM
            )
            img.save(final_path)

    def _frame_mapped(self, event: Event):
        """Default mapping required for minimizing the window"""
        self.update_idletasks()
        self.overrideredirect(True)
        self.state("normal")

    def _minimize(self):
        """Minimize the window in the task bar"""
        self.update_idletasks()
        self.overrideredirect(False)
        self.state("iconic")

    def _switch_fullscreen(self):
        """Set the window to fulscreen or resize it"""
        if self.fullscreen:
            self.state("normal")
            self.fullscreen = False
        else:
            self.state("zoomed")
            self.fullscreen = True

        self._width, self._height = [
            int(x) for x in self.winfo_geometry().split("+")[0].split("x")
        ]
        self.place_widgets()

    def place_widgets(self):
        """Replace widgets following the size of the window"""
        width_ratio = self._width / 1028
        height_ratio = self._height / 500
        self.menu_bar.place(x=0, y=0, width=self._width, height=25)
        self.title_menu.place(x=self._width / 2, y=12, anchor="center")
        self.minimize_button.place(x=self._width - 75, y=0, width=25, height=25)
        self.fullscreen_button.place(x=self._width - 50, y=0, width=25, height=25)
        self.exit_button.place(x=self._width - 25, y=0, width=25, height=25)

        self.common_frame.config(width=self._width - 10, height=self._height - 10)
        self.title_label.place(x=self._width / 2, y=25 * height_ratio, anchor="center")
        self.time_label.place(x=self._width / 2, y=65 * height_ratio, anchor="center")

        self.rand_widget_dict["order_label"].place(
            x=100 * width_ratio, y=100 * height_ratio
        )
        self.rand_widget_dict["order_entry"].place(
            x=230 * width_ratio, y=100 * height_ratio, width=60
        )
        self.update()
        for index, article_tuple in enumerate(self.food_widgets.values()):
            article_tuple[0].place(
                x=250 * width_ratio, y=(160 + index * 30) * height_ratio, anchor="e",
            )
            article_tuple[1].place(
                x=275 * width_ratio, y=(150 + 30 * index) * height_ratio, width=40,
            )
        self.rand_widget_dict["discount_p_label"].place(
            x=380 * width_ratio, y=97 * height_ratio
        )
        self.rand_widget_dict["discount_p_entry"].place(
            x=510 * width_ratio, y=100 * height_ratio, width=100,
        )
        for index, price_tuple in enumerate(self.total_widgets.values()):
            price_tuple[0].place(
                x=525 * width_ratio, y=(160 + 30 * index) * height_ratio, anchor="e",
            )
            price_tuple[1].place(
                x=535 * width_ratio, y=(150 + 30 * index) * height_ratio, width=100,
            )

        self.rand_widget_dict["res_entry"].place(
            x=775 * width_ratio, y=100 * height_ratio, width=204, height=50,
        )
        for index, calc_button in enumerate(self.calc_buttons):
            line = int(index / 3)
            column = int(index % 3)
            calc_button.place(
                x=775 * width_ratio + 51 * column,
                y=160 * height_ratio + 51 * line,
                width=50,
                height=50,
            )
        for index, calc_button in enumerate(self.low_calc_buttons):
            calc_button.place(
                x=775 * width_ratio + 51 * index,
                y=160 * height_ratio + 51 * 3,
                width=50,
                height=50,
            )
        x_operand = 928 / 1.055 if self.fullscreen else 928
        for index, operand_button in enumerate(self.operand_buttons):
            operand_button.place(
                x=x_operand * width_ratio,
                y=160 * height_ratio + 51 * index,
                width=50,
                height=50,
            )
        y_equal = 364 / 1.25 if self.fullscreen else 364
        self.rand_widget_dict["equal_button"].place(
            x=775 * width_ratio, y=y_equal * height_ratio, width=204, height=50,
        )

        self.update()
        for entry, buttons in self.entry_buttons.items():
            entry_width = entry.winfo_width()
            entry_x = entry.winfo_x()
            entry_y = entry.winfo_y()
            buttons[0].place(
                x=entry_x + entry_width, y=entry_y, width=20, height=20,
            )
            buttons[1].place(
                x=entry_x - 20, y=entry_y, width=20, height=20,
            )
        self.update()
        for index, control_button in enumerate(self.control_buttons):
            control_button.place(
                x=(100 + 200 * index) * width_ratio,
                y=380 * height_ratio,
                width=130,
                height=30,
            )

        self.price_frame.config(width=self._width, height=self._height)
        for index, labels in enumerate(self.article_widgets.values()):
            labels[0].place(
                x=350 * width_ratio, y=(50 + 50 * index) * height_ratio, anchor="w",
            )
            labels[1].place(
                x=600 * width_ratio, y=(50 + 50 * index) * height_ratio, anchor="e",
            )
        self.food_img.place(
            x=self._width, y=self._height, width=300, height=500, anchor="se",
        )
        self.update()


if __name__ == "__main__":
    gui = RestaurantSystemUI()
    gui.mainloop()
