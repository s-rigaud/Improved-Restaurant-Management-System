"""
"""

import os
from datetime import datetime
from tkinter import Event, ttk, END, SUNKEN
from ttkthemes import ThemedTk
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk


from scient_calc import ScientCalc
from helpers import concrete_inc_dec

localtime = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")


class UI(ThemedTk):
    """Main class for the whole interface"""

    # TODO adjust cursor everywhere (customize)
    # https://docstore.mik.ua/orelly/perl3/tk/ch23_02.htm
    # TODO Make notebook frame more visible
    # TODO Improve PDF
    # TODO Rethink design
    # TODO Find a way to use transparency (nice result)
    # TODO pylint & black all
    def __init__(self):
        ThemedTk.__init__(self, theme="equilux")
        self.articles = {
            "Fried Potato": 35,
            "Chicken Burger": 25,
            "Big King": 20,
            "Chicken Royal": 40,
            "Veg Salad": 55,
        }
        self.operands = ["*", "/", "+", "-"]
        self.currency = "$"
        self.restaurant_name = "Le petit français"
        self.calc = ScientCalc()

        self.bg_color = "#252525"
        self.ico_path = None
        self.logo_path = None
        self.notebk = None
        self.order_entry = None
        self.discount_p_entry = None
        self.entries = []
        self.article_entries = []
        self.price_entries = {}
        self._width = 1028
        self._height = 500

        self._init_ui()

    def _init_ui(self):
        """Init the whole UI"""
        # TODO add icon for the window
        # https://stackoverflow.com/questions/31085533
        self.title("Restaurant Management")
        self.geometry(f"{self._width}x{self._height}+100+100")
        self.resizable(False, False)
        # self.iconify()
        # self.attributes('-alpha', 0.0)
        self.overrideredirect(1)
        self.configure(bg=self.bg_color)
        # self.wm_attributes("-transparentcolor", "#000")
        curr_path = os.path.dirname(os.path.abspath(__file__))
        self.ico_path = os.path.join(curr_path, "ico.ico")
        self.logo_path = os.path.join(curr_path, "ananas.png")
        self.iconbitmap(self.ico_path)

        self.configure_style()

        ####### TOP MENU
        self.notebk = ttk.Notebook(self)
        self.notebk.place(x=0, y=25)
        common_frame = ttk.Frame(self.notebk, width=self._width, height=self._height)
        price_frame = ttk.Frame(self.notebk, width=self._width, height=self._height)
        self.notebk.add(common_frame, text="Billing ۩ ")
        self.notebk.add(price_frame, text=f"Prices {self.currency} ")

        menu_bar = ttk.Label(self, style="menu.TLabel")
        menu_bar.place(x=0, y=0, width=self._width, height=25)
        title_menu = ttk.Label(
            menu_bar, text="Restaurant Management System", style="smalltitle.TLabel"
        )
        title_menu.place(x=self._width / 2, y=12, anchor="center")
        exit_button = ttk.Button(
            self, text="X", style="exit.TButton", cursor="pirate", command=self.destroy
        )
        exit_button.place(x=self._width - 25, y=0, width=25, height=25)

        # https://stackoverflow.com/questions/4055267#answer-4055612
        menu_bar.bind("<ButtonPress-1>", self._start_moving)
        menu_bar.bind("<ButtonRelease-1>", self._stop_moving)
        menu_bar.bind("<B1-Motion>", self._on_motion)
        title_menu.bind("<ButtonPress-1>", self._start_moving)
        title_menu.bind("<ButtonRelease-1>", self._stop_moving)
        title_menu.bind("<B1-Motion>", self._on_motion)
        ########## FRAME 1
        ### COMMON LABELS
        title = ttk.Label(
            common_frame, text="Restaurant Management®", style="title.TLabel"
        )
        title.place(x=self._width / 2, y=25, anchor="center")
        self.time_label = ttk.Label(
            common_frame, text=localtime, style="time.TLabel", cursor="clock"
        )
        self.time_label.place(x=self._width / 2, y=65, anchor="center")

        ### FOOD MENU
        self.display_food_frame(common_frame)
        ### PRICE
        self.display_total_frame(common_frame)
        ### CALCULATOR
        self.display_calculator_frame(common_frame)
        ### CONTROL BUTTONS
        index = 0
        button_labels = {
            "RESET": self.clear_fields,
            "SAVE": self.save_bill_to_pdf,
        }
        for label, function in button_labels.items():
            control_button = ttk.Button(
                common_frame, text=label, command=function, cursor="hand2"
            )
            control_button.place(x=100 + 200 * index, y=400, width=130, height=30)
            index += 1

        ################# FRAME 2
        self.display_food_price_frame(price_frame)

        ### COMMON BEHAVIOUR
        self.clear_fields()
        self.update_time()

    @property
    def bill(self):
        # TODO ADD cost + service charge (client doesn't have to know)
        return "\n".join(
            [f"{label} : {entry.get()}" for label, entry in self.price_entries.items()]
        )

    def configure_style(self):
        s = ttk.Style()
        s.theme_settings(
            "equilux",
            {
                "TButton": {
                    "configure": {"padding": -5},
                    "map": {
                        "foreground": [
                            ("active", "#e84118"),
                            ("!disabled", "#e1b12c"),
                        ],
                        "background": [
                            ("active", "#e84118"),
                            ("!disabled", "#e1b12c"),
                        ],
                    },
                },
                "TFrame": {"configure": {"background": self.bg_color},},
                "TLabel": {"configure": {"background": self.bg_color},},
                "TEntry": {"configure": {"background": self.bg_color},},
            },
        )
        s.configure(".", font="{U.S. 101} 15 bold", foreground="white")
        s.configure("title.TLabel", font="{U.S. 101} 30 bold", foreground="#e1b12c")
        s.configure("smalltitle.TLabel", font="{U.S. 101} 10", background="#3C3C3C")
        s.configure("time.TLabel", foreground="#e84118")
        s.configure("res.TEntry", background="#000")
        s.configure("rfood.TLabel", foreground="#e1b12c")
        s.configure("yfood.TLabel", foreground="#e84118")
        s.configure("menu.TLabel", foreground="#CCCCCC", background="#3C3C3C")
        s.configure("exit.TButton", foreground="#CCCCCC")
        s.map(
            "exit.TButton",
            foreground=[("active", "#CCCCCC"), ("!disabled", "#CCCCCC"),],
            background=[("active", "#ff0000"), ("!disabled", "#3C3C3C"),],
        )

    def display_food_frame(self, common_frame: ttk.Frame):
        temp_label = ttk.Label(common_frame, text="Order Num :")
        temp_label.place(x=100, y=100)
        self.order_entry = ttk.Entry(common_frame, justify="center")
        self.order_entry.place(x=230, y=100, width=60)
        self.order_entry.bind("<Key>", lambda e: "break")
        self.add_buttons(common_frame, self.order_entry, 230, 100, 60)
        self.entries.append(self.order_entry)

        for index, item in enumerate(self.articles.keys()):
            ttk.Label(common_frame, text=item).place(
                x=250, y=160 + index * 30, anchor="e"
            )
            temp_entry = ttk.Entry(common_frame, justify="center")
            temp_entry.place(x=275, y=150 + 30 * index, width=40)
            temp_entry.bind("<Key>", lambda e: "break")
            self.add_buttons(common_frame, temp_entry, 275, 150 + 30 * index, 40)
            self.article_entries.append((item, temp_entry))
            self.entries.append(temp_entry)

    def display_total_frame(self, common_frame: ttk.Frame):
        self.discount_p_entry = ttk.Label(common_frame, text="Discount %")
        self.discount_p_entry.place(x=380, y=97)
        self.discount_p_entry = ttk.Entry(common_frame, justify="center")
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
            price_entry = ttk.Entry(common_frame, justify="center")
            price_entry.place(x=535, y=150 + 30 * index, width=100)
            price_entry.bind("<Key>", lambda e: "break")
            self.entries.append(price_entry)
            self.price_entries.update({price_txt: price_entry})

    def display_calculator_frame(self, common_frame):
        self.res_entry = ttk.Entry(common_frame, style="res.TEntry", justify="center")
        self.res_entry.place(x=775, y=100, width=204, height=50)
        self.res_entry.bind("<Key>", lambda e: "break")
        self.entries.append(self.res_entry)
        button_width = 50
        button_height = 50
        for i in range(9):
            line = int(i / 3)
            column = int(i % 3)
            # x=i+1 to avoid reference to final value of i
            temp_button = ttk.Button(
                common_frame,
                text=i + 1,
                command=lambda x=i + 1: self.add_to_entry(self.res_entry, x),
                cursor="hand2",
            )
            temp_button.place(
                x=775 + 51 * column,
                y=160 + 51 * line,
                width=button_width,
                height=button_height,
            )

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
            common_frame, text="C", command=self.erase_calc, cursor="hand2"
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

    def display_food_price_frame(self, price_frame: ttk.Frame):
        index = 0
        articles = {"Food": "Price", **self.articles}
        for food, price in articles.items():
            food_label = ttk.Label(price_frame, text=food, style="rfood.TLabel")
            food_label.place(x=350, y=50 + 50 * index, anchor="w")
            price_label = ttk.Label(
                price_frame, text=f"{price} {self.currency}", style="yfood.TLabel"
            )
            price_label.place(x=600, y=50 + 50 * index, anchor="e")
            index += 1
        img = Image.open(self.logo_path).rotate(45, expand=True)
        tk_img = ImageTk.PhotoImage(img)
        logo = ttk.Label(price_frame, image=tk_img)
        logo.image = tk_img
        logo.place(x=self._width, y=self._height, width=300, height=500, anchor="se")

    def _start_moving(self, event: Event):
        self.x = event.x
        self.y = event.y

    def _stop_moving(self, event: Event):
        self.x = None
        self.y = None

    def _on_motion(self, event: Event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def clear_fields(self):
        """Reset all the entries with 0"""
        for entry in self.entries:
            entry.delete(0, END)
            if entry == self.res_entry:
                continue
            entry.insert(0, 0)
            if entry in self.price_entries.values():
                entry.insert(END, f".00 {self.currency}")
            elif entry == self.discount_p_entry:
                entry.insert(END, " %")

    def erase_calc(self):
        """Reset the display ofthe calculator"""
        self.res_entry.delete(len(self.res_entry.get()) - 1, END)

    def reset_calc_display(self):
        """Reset the display ofthe calculator"""
        self.res_entry.delete(0, END)

    def add_to_entry(self, entry, value):
        """Common method used to add operands to the calculator display"""
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
        self.res_entry.after(2000, self.reset_calc_display)

    def update_time(self):
        self.time_label.configure(text=datetime.now().strftime("%A, %d %B %Y %H:%M:%S"))
        self.time_label.after(1000, self.update_time)

    def calc_total(self):
        """Calculate the bill price"""
        price = 0
        for article, entry in self.article_entries:
            price += int(entry.get()) * self.articles[article]
        self.display_total(price)

    def display_total(self, price: float):
        """Display the bill prices"""
        discount_p = int(self.discount_p_entry.get().split()[0])
        for entry in [*self.price_entries.values(), self.discount_p_entry]:
            entry.delete(0, END)
        service = price * 0.1
        tax = price * 0.2
        sub_total = price + service + tax
        total = sub_total * (1 - discount_p / 100)
        discount = round(sub_total - total, 2)
        self.discount_p_entry.insert(0, f"{discount_p} %")
        self.price_entries["Cost"].insert(0, f"{price:.02f} {self.currency}")
        self.price_entries["Service Charge"].insert(
            0, f"{service:.02f} {self.currency}"
        )
        self.price_entries["Tax"].insert(0, f"{tax:.02f} {self.currency}")
        self.price_entries["SubTotal"].insert(0, f"{sub_total:.02f} {self.currency}")
        self.price_entries["Discount"].insert(0, f"{discount:.02f} {self.currency}")
        self.price_entries["Total"].insert(0, f"{total:.02f} {self.currency}")

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
            command=lambda x=entry: self.increment(x),
            style="small.TButton",
            cursor="hand2",
        )
        add_button.place(x=entry_x + width, y=entry_y, width=20, height=20)
        minus_button = ttk.Button(
            frame,
            text="-",
            command=lambda x=entry: self.decrement(x),
            style="small.TButton",
            cursor="hand2",
        )
        minus_button.place(x=entry_x - 20, y=entry_y, width=20, height=20)

    def increment(self, entry: ttk.Entry):
        """Increment the value of the entry by 1"""
        concrete_inc_dec(entry, "+")
        self.calc_total()

    def decrement(self, entry: ttk.Entry):
        """Decrement the value of the entry by 1"""
        concrete_inc_dec(entry, "-")
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
        self.create_png_picture(self.logo_path, pdf_img_path)

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

    def create_png_picture(self, curr_path: str, final_path=None):
        """Create a minify version of the logo to print on the pdf file"""
        final_path = final_path or curr_path
        img = Image.open(curr_path)
        img = img.resize((100, 100), Image.ANTIALIAS).transpose(Image.FLIP_TOP_BOTTOM)
        img.save(final_path)


if __name__ == "__main__":
    gui = UI()
    gui.mainloop()
