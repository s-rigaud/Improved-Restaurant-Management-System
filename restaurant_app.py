""" User Interface responsible for all this app
"""

import os
from datetime import datetime
from tkinter import Event, ttk, END
from ttkthemes import ThemedTk
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk


from scient_calc import ScientCalc

localtime = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")


class UI(ThemedTk):
    """Main class for the whole interface"""

    # TODO Find a way to use transparency (nice result)
    # self.wm_attributes("-transparentcolor", "#000")
    # TODO Add tooltip
    # https://stackoverflow.com/questions/20399243
    # TODO SEE
    # http://effbot.org/tkinterbook/wm.htm
    # TODO AJUST FULLSCREEN STYLE
    # TODO COMPACT ATTRIBUTE WIDGETS IN DICT

    def __init__(self, restaurant_name: str = ""):
        ThemedTk.__init__(self, theme="equilux")
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
        self.logo_path = None
        self.notebk = None
        self.res_entry = None
        self.order_label = None
        self.order_entry = None
        self.discount_p_entry = None
        self.entries = []
        self.calc_buttons = []
        # {text : (label, entry)
        self.food_widgets = {}
        self.total_widgets = {}
        self.x = 0
        self.y = 0
        self._width = 1028
        self._height = 500

        self._init_ui()

    def _init_ui(self):
        """Init the whole User Interface"""
        # TODO add icon for the window
        # https://stackoverflow.com/questions/31085533
        self.title("Restaurant Management")
        self.geometry(f"{self._width}x{self._height}+100+100")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=self.bg_color)
        self._configure_style()

        curr_path = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(curr_path, "ico.ico")
        self.logo_path = os.path.join(curr_path, "ananas.png")
        self.iconbitmap(ico_path)

        ####### TOP MENU
        self.notebk = ttk.Notebook(self)
        self.notebk.place(x=0, y=25)
        self.common_frame = ttk.Frame(
            self.notebk, width=self._width, height=self._height
        )
        self.price_frame = ttk.Frame(
            self.notebk, width=self._width, height=self._height
        )
        self.notebk.add(self.common_frame, text="Billing ۩ ")
        self.notebk.add(self.price_frame, text=f"Prices {self.currency} ")
        self.menu_bar = ttk.Frame(self, style="menu.TLabel")
        self.menu_bar.place(x=0, y=0, width=self._width, height=25)
        self.title_menu = ttk.Label(
            self.menu_bar,
            text=f"{self.restaurant_name} - Improved Restaurant Management System",
            style="smalltitle.TLabel",
        )
        self.title_menu.place(x=self._width / 2, y=12, anchor="center")
        self.minimize_button = ttk.Button(
            self.menu_bar, text="_", style="exit.TButton", command=self._minimize
        )
        self.minimize_button.place(x=self._width - 75, y=0, width=25, height=25)
        self.fullscreen_button = ttk.Button(
            self.menu_bar, text="□", style="exit.TButton", command=self._fullscreen
        )
        self.fullscreen_button.place(x=self._width - 50, y=0, width=25, height=25)
        self.exit_button = ttk.Button(
            self.menu_bar, text="X", style="exit.TButton", command=self.destroy
        )
        self.exit_button.place(x=self._width - 25, y=0, width=25, height=25)

        # https://stackoverflow.com/questions/4055267#answer-4055612
        self.menu_bar.bind("<ButtonPress-1>", self._start_moving)
        self.menu_bar.bind("<ButtonRelease-1>", self._stop_moving)
        self.menu_bar.bind("<B1-Motion>", self._on_motion)
        self.menu_bar.bind("<Double-Button-1>", lambda x: self._fullscreen())
        self.title_menu.bind("<ButtonPress-1>", self._start_moving)
        self.title_menu.bind("<ButtonRelease-1>", self._stop_moving)
        self.title_menu.bind("<B1-Motion>", self._on_motion)
        self.title_menu.bind("<Double-Button-1>", lambda x: self._fullscreen())

        self.notebk.bind("<Map>", self._frame_mapped)
        ########## FRAME 1
        ### COMMON LABELS
        self.title = ttk.Label(
            self.common_frame, text="Restaurant Management®", style="title.TLabel"
        )
        self.title.place(x=self._width / 2, y=25, anchor="center")
        self.time_label = ttk.Label(
            self.common_frame, text=localtime, style="time.TLabel", cursor="clock"
        )
        self.time_label.place(x=self._width / 2, y=65, anchor="center")

        ### FOOD MENU
        self._display_food_frame(self.common_frame)
        ### PRICE
        self._display_total_frame(self.common_frame)
        ### CALCULATOR
        self._display_calculator_frame(self.common_frame)
        ### CONTROL BUTTONS
        index = 0
        button_labels = {
            "RESET": self.clear_fields,
            "SAVE": self.save_bill_to_pdf,
        }
        for label, function in button_labels.items():
            control_button = ttk.Button(
                self.common_frame, text=label, command=function, cursor="hand2"
            )
            control_button.place(x=100 + 200 * index, y=400, width=130, height=30)
            index += 1

        ################# FRAME 2
        self._display_price_frame(self.price_frame)

        ### COMMON BEHAVIOUR
        self.clear_fields()
        self._update_time()

    @property
    def bill(self):
        """Resturn the customer bill which will be display on the PDF file"""
        return "\n".join(
            [
                f"{text} : {price_tuple[1].get()}"
                for text, price_tuple in self.total_widgets.items()
            ]
        )

    @property
    def is_fullscreen(self):
        """Naively try to know if the window is in fulscreen mode"""
        return self._width != 1028 or self._height != 500

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
        print(style.element_options("TEntry.cursor"))

    def _display_food_frame(self, common_frame: ttk.Frame):
        """Display every food with corresponding buttons and entries"""
        self.order_label = ttk.Label(common_frame, text="Order Num :")
        self.order_label.place(x=100, y=100)
        self.order_entry = ttk.Entry(common_frame, justify="center", cursor="arrow")
        self.order_entry.place(x=230, y=100, width=60)
        self.order_entry.bind("<Key>", lambda e: "break")
        self.add_buttons(common_frame, self.order_entry, 230, 100, 60)
        self.entries.append(self.order_entry)

        for index, item in enumerate(self.articles.keys()):
            article_label = ttk.Label(common_frame, text=item)
            article_label.place(x=250, y=160 + index * 30, anchor="e")
            article_entry = ttk.Entry(common_frame, justify="center", cursor="arrow")
            article_entry.place(x=275, y=150 + 30 * index, width=40)
            article_entry.bind("<Key>", lambda e: "break")
            self.add_buttons(common_frame, article_entry, 275, 150 + 30 * index, 40)
            self.food_widgets.update({item: (article_label, article_entry)})
            self.entries.append(article_entry)

    def _display_total_frame(self, common_frame: ttk.Frame):
        """Display all the total price entries"""
        self.discount_p_entry = ttk.Label(common_frame, text="Discount %")
        self.discount_p_entry.place(x=380, y=97)
        self.discount_p_entry = ttk.Entry(
            common_frame, justify="center", cursor="arrow"
        )
        self.discount_p_entry.place(x=510, y=100, width=100)
        self.discount_p_entry.bind("<Key>", lambda e: "break")
        self.entries.append(self.discount_p_entry)
        self.add_buttons(common_frame, self.discount_p_entry, 510, 100, 100)

        prices_txt = [
            "Cost",
            "Service Charge",
            "Tax",
            "SubTotal",
            "Discount",
            "Total",
        ]
        for index, price_txt in enumerate(prices_txt):
            total_label = ttk.Label(common_frame, text=price_txt)
            total_label.place(x=525, y=160 + 30 * index, anchor="e")
            price_entry = ttk.Entry(common_frame, justify="center", cursor="arrow")
            price_entry.place(x=535, y=150 + 30 * index, width=100)
            price_entry.bind("<Key>", lambda e: "break")
            self.entries.append(price_entry)
            self.total_widgets.update({price_txt: (total_label, price_entry)})

    def _display_calculator_frame(self, common_frame):
        """Display the calculator"""
        self.res_entry = ttk.Entry(
            common_frame, style="res.TEntry", justify="center", cursor="arrow"
        )
        self.res_entry.place(x=775, y=100, width=204, height=50)
        self.res_entry.bind("<Key>", lambda e: "break")
        self.entries.append(self.res_entry)
        button_width = 50
        button_height = 50
        for i in range(9):
            line = int(i / 3)
            column = int(i % 3)
            # x=i+1 to avoid reference to final value of i
            calc_button = ttk.Button(
                common_frame,
                text=i + 1,
                command=lambda x=i + 1: self.add_to_entry(self.res_entry, x),
                cursor="hand2",
            )
            calc_button.place(
                x=775 + 51 * column,
                y=160 + 51 * line,
                width=button_width,
                height=button_height,
            )
            self.calc_buttons.append(calc_button)

        for index, operand in enumerate(self.operands):
            operand_button = ttk.Button(
                common_frame,
                text=operand,
                command=lambda x=operand: self.add_to_entry(self.res_entry, x),
                cursor="hand2",
            )
            operand_button.place(
                x=928, y=160 + 51 * index, width=button_width, height=button_height,
            )
        zero_button = ttk.Button(
            common_frame,
            text=0,
            command=lambda: self.add_to_entry(self.res_entry, 0),
            cursor="hand2",
        )
        zero_button.place(x=775, y=313, width=button_width, height=button_height)
        reset_button = ttk.Button(
            common_frame, text="C", command=self._erase_calc, cursor="hand2"
        )
        reset_button.place(x=826, y=313, width=button_width, height=button_height)
        dot_button = ttk.Button(
            common_frame,
            text=".",
            command=lambda: self.add_to_entry(self.res_entry, "."),
            cursor="hand2",
        )
        dot_button.place(x=877, y=313, width=button_width, height=button_height)
        equal_button = ttk.Button(
            common_frame,
            text="=",
            command=lambda: self.compute_string(self.res_entry, self.res_entry.get()),
            cursor="hand2",
        )
        equal_button.place(
            x=775, y=364, width=button_width * 4 + 4, height=button_height
        )

    def _display_price_frame(self, price_frame: ttk.Frame):
        """Display the price of the food in the second notebook frame"""
        articles = {"Food": "Price", **self.articles}
        for index, food in enumerate(articles.keys()):
            food_label = ttk.Label(price_frame, text=food, style="rfood.TLabel")
            food_label.place(x=350, y=50 + 50 * index, anchor="w")
            price_label = ttk.Label(
                price_frame,
                text=f"{articles[food]} {self.currency}",
                style="yfood.TLabel",
            )
            price_label.place(x=600, y=50 + 50 * index, anchor="e")
        img = Image.open(self.logo_path).rotate(45, expand=True)
        tk_img = ImageTk.PhotoImage(img)
        logo = ttk.Label(price_frame, image=tk_img)
        logo.image = tk_img
        logo.place(x=self._width, y=self._height, width=300, height=500, anchor="se")

    def _start_moving(self, event: Event):
        """The window start being dragged"""
        self.x = event.x
        self.y = event.y

    def _stop_moving(self, event: Event):
        """Reset coords after being dragged"""
        self.x = None
        self.y = None

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
            if entry != self.res_entry:
                entry.insert(0, 0)
                if entry in price_entries:
                    entry.insert(END, f".00 {self.currency}")
                elif entry == self.discount_p_entry:
                    entry.insert(END, " %")
                entry["state"] = "readonly"

    def _erase_calc(self):
        """Reset the display ofthe calculator"""
        self.res_entry.delete(len(self.res_entry.get()) - 1, END)

    def _reset_calc_display(self):
        """Reset the display ofthe calculator"""
        self.res_entry.delete(0, END)

    def add_to_entry(self, entry, value):
        """Common method used to add operands and numbers to the calculator display"""
        entry.insert(END, value)

    def compute_string(self, entry: ttk.Entry, calculator_str: str):
        """Use ScientCalc to compute calc display string"""
        res, error = self.calc.compute_string(calculator_str)
        entry.delete(0, END)
        if error:
            self.calc_input_error()
        else:
            entry.insert(END, res)

    def calc_input_error(self):
        """Display errors appearing in the calculator display"""
        self.res_entry.delete(0, END)
        self.res_entry.insert(0, "You enter a wrong formula")
        self.res_entry.after(2000, self._reset_calc_display)

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
        discount_p = int(self.discount_p_entry.get().split()[0])
        price_entries = [price_tuple[1] for price_tuple in self.total_widgets.values()]
        for entry in [*price_entries, self.discount_p_entry]:
            entry["state"] = "normal"
            entry.delete(0, END)
        service = price * 0.1
        tax = price * 0.2
        sub_total = price + service + tax
        total = sub_total * (1 - discount_p / 100)
        discount = round(sub_total - total, 2)
        self.discount_p_entry.insert(0, f"{discount_p} %")
        self.total_widgets["Cost"][1].insert(0, f"{price:.02f} {self.currency}")
        self.total_widgets["Service Charge"][1].insert(
            0, f"{service:.02f} {self.currency}"
        )
        self.total_widgets["Tax"][1].insert(0, f"{tax:.02f} {self.currency}")
        self.total_widgets["SubTotal"][1].insert(0, f"{sub_total:.02f} {self.currency}")
        self.total_widgets["Discount"][1].insert(0, f"{discount:.02f} {self.currency}")
        self.total_widgets["Total"][1].insert(0, f"{total:.02f} {self.currency}")
        for entry in [*price_entries, self.discount_p_entry]:
            entry["state"] = "readonly"

    def add_buttons(
        self,
        frame: ttk.Frame,
        entry: ttk.Entry,
        entry_x: float,
        entry_y: float,
        width: int,
    ):
        """Add button to add or remove food from the bill"""
        add_button = ttk.Button(
            frame,
            text="+",
            command=lambda x=entry: self._increment(x),
            style="small.TButton",
            cursor="hand2",
        )
        add_button.place(x=entry_x + width, y=entry_y, width=20, height=20)
        minus_button = ttk.Button(
            frame,
            text="-",
            command=lambda x=entry: self._decrement(x),
            style="small.TButton",
            cursor="hand2",
        )
        minus_button.place(x=entry_x - 20, y=entry_y, width=20, height=20)

    def concrete_inc_dec(self, entry, operand: str):
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
        order_id = self.order_entry.get()
        date = self.time_label["text"]

        curr_path = os.path.dirname(os.path.abspath(__file__))
        order_dir = os.path.join(curr_path, "orders")
        if not os.path.isdir(order_dir):
            os.makedirs(order_dir)
        pdf_path = os.path.join(order_dir, f"Order_{order_id}.pdf")
        pdf_img_path = os.path.join(curr_path, "logo_pdf.png")
        self._create_png_picture(self.logo_path, pdf_img_path)

        c = canvas.Canvas(pdf_path, pagesize=(300, 300), bottomup=0)
        c.setAuthor("Hylectrif")
        c.setFont("Helvetica", 12)
        c.setTitle(f"Bill for the order n°{order_id} 📝")
        page_x, page_y = c._pagesize

        c.drawImage(
            pdf_img_path, page_x - 100, page_y - 100, mask="auto",
        )
        c.drawImage(
            pdf_img_path, 0, page_y - 100, mask="auto",
        )
        c.drawCentredString(page_x / 2, page_y / 10, f"֍ {self.restaurant_name} ֎")
        c.drawCentredString(page_x / 2, page_y / 10 + 25, date)
        c.roundRect(page_x / 2 - 25, page_y - 50, 50, 40, 50, fill=1)

        for index, text in enumerate(self.bill.split("\n"), 1):
            c.drawCentredString(page_x / 2, page_y / 4 + index * 25, text)
        c.save()

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

    def _fullscreen(self):
        """Set the window to fulscreen or resize it"""
        if self.is_fullscreen:
            self.state("normal")
        else:
            self.state("zoomed")

        self._width, self._height = [
            int(x) for x in self.winfo_geometry().split("+")[0].split("x")
        ]
        self.replace_widgets(self.is_fullscreen)

    def replace_widgets(self, fullscreen):
        """Replace widgets following the size of the window"""
        width_ratio = self._width / 1028
        height_ratio = self._height / 500
        self.menu_bar.place(x=0, y=0, width=self._width, height=25)
        self.title_menu.place(x=self._width / 2, y=12, anchor="center")
        self.minimize_button.place(x=self._width - 75, y=0, width=25, height=25)
        self.fullscreen_button.place(x=self._width - 50, y=0, width=25, height=25)
        self.exit_button.place(x=self._width - 25, y=0, width=25, height=25)

        self.common_frame.config(width=self._width, height=self._height)
        self.title.place(x=self._width / 2, y=25 * height_ratio, anchor="center")
        self.time_label.place(x=self._width / 2, y=65 * height_ratio, anchor="center")

        self.order_label.place(x=100 * width_ratio, y=100 * height_ratio)
        self.order_entry.place(x=230 * width_ratio, y=100 * height_ratio)

        for index, article_tuple in enumerate(self.food_widgets.values()):
            article_tuple[0].place(
                x=250 * width_ratio, y=(160 + index * 30) * height_ratio, anchor="e"
            )
            article_tuple[1].place(
                x=275 * width_ratio, y=(150 + 30 * index) * height_ratio
            )
        self.discount_p_entry.place(x=380 * width_ratio, y=97 * height_ratio)
        for index, price_tuple in enumerate(self.total_widgets.values()):
            price_tuple[0].place(
                x=525 * width_ratio, y=(160 + 30 * index) * height_ratio, anchor="e"
            )
            price_tuple[1].place(
                x=535 * width_ratio, y=(150 + 30 * index) * height_ratio
            )

        self.res_entry.place(
            x=775 * width_ratio, y=100 * height_ratio, width=204, height=50
        )
        for index, calc_button in enumerate(self.calc_buttons):
            line = int(index / 3)
            column = int(index % 3)
            calc_button.place(
                x=775 * width_ratio + 51 * column, y=160 * height_ratio + 51 * line,
            )

        self.price_frame.config(width=self._width, height=self._height)

        self.update()
        if fullscreen:
            pass


if __name__ == "__main__":
    gui = UI()
    gui.mainloop()
