"""
"""

from datetime import datetime
from tkinter import Tk, ttk, VERTICAL, END
from time import sleep
from ttkthemes import ThemedTk
import os
from tkinter.font import Font
from reportlab.pdfgen import canvas

localtime = datetime.now().strftime("%A %d %B %Y %H-%M-%S")


class ScientCalc:
    def __init__(self):
        # Strategic order (scientific calculus + negative number)
        self.operands = ["*", "/", "+", "-"]

    def compute_string(self, calculator_str: str):
        if calculator_str:
            res, error = self._compute(part1=calculator_str)
            res = round(res, 2)
            if res == int(res):
                res = int(res)
            return (res, error)
        return (0, False)

    def _compute(self, operand: str = "+", part1: str = "0", part2: str = "0") -> float:
        """Recursive function trying to divide operations and compute (Tree style)"""
        # TODO bug 0-+6
        error = False
        try:
            res1 = float(part1)
        except ValueError:
            for o in self.operands:
                split_str = part1.rsplit(o, 1)
                if len(split_str) > 1:
                    res1, err = self._compute(o, split_str[0], split_str[1])
                    error |= err
                    break
        try:
            res2 = float(part2)
        except ValueError:
            for o in self.operands:
                split_str = part2.rsplit(o, 1)
                if len(split_str) > 1:
                    res2, err = self._compute(o, split_str[0], split_str[1])
                    error |= err
                    break

        operand_dict = {"+": self._add, "-": self._sub, "*": self._mul, "/": self._div}
        try:
            return (operand_dict[operand](res1, res2), error)
        except (UnboundLocalError, ZeroDivisionError):
            error |= True
            return (0, error)

    def _add(self, f1: float, f2: float) -> float:
        """Simple adder"""
        return f1 + f2

    def _sub(self, f1: float, f2: float) -> float:
        """Simple substracter"""
        return f1 - f2

    def _mul(self, f1: float, f2: float) -> float:
        """Simple product"""
        return f1 * f2

    def _div(self, f1: float, f2: float) -> float:
        """Simple div.."""
        return f1 / f2


class UI:
    """Main class for the whole interface"""

    def __init__(self, root: ThemedTk):
        self.root = root
        self.articles = {
            "Fried Potato": 35,
            "Chicken Burger": 25,
            "Big King": 20,
            "Chicken Royal": 40,
            "Veg Salad": 55,
        }
        self.entries = []
        self.article_entries = []
        self.price_entries = {}
        self.operands = ["*", "/", "+", "-"]
        self.currency = "$"
        self.bg_color = "#2f3640"
        self.restaurant_name = "Le petit français"
        self.order_entry = None
        self.calc = ScientCalc()

        root.title("Restaurant Management")
        root.geometry("1028x500")
        root.configure(bg=self.bg_color)
        curr_path = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(curr_path, "./ico.ico")
        root.iconbitmap(ico_path)

        print(ttk.Style().theme_use())
        s = ttk.Style()
        s.theme_settings(
            "equilux",
            {
                "TButton": {
                    "configure": {"padding": 0},
                    "map": {
                        "foreground": [
                            ("active", "green2"),
                            ("!disabled", "green4"),
                            ("focus", "#4cd137"),
                        ],
                        "background": [
                            ("active", "green2"),
                            ("!disabled", "green4"),
                            ("focus", "#4cd137"),
                        ],
                    },
                },
            },
        )

        s.configure(
            ".", background=self.bg_color, font="{U.S. 101} 15 bold", foreground="white"
        )
        s.configure("title.TLabel", font="{U.S. 101} 30 bold", foreground="#e1b12c")
        s.configure("time.TLabel", font="{U.S. 101} 15 bold", foreground="#e84118")
        s.configure("res.TEntry", background="#000")
        s.configure("rfood.TLabel", font="{U.S. 101} 15 bold", foreground="#e1b12c")
        s.configure("yfood.TLabel", font="{U.S. 101} 15 bold", foreground="#e84118")

        notebk = ttk.Notebook(root)
        notebk.pack()
        common_frame = ttk.Frame(notebk, width=1028, height=500)
        price_frame = ttk.Frame(notebk, width=1028, height=500)
        notebk.add(common_frame, text="Billing")
        notebk.add(price_frame, text="Prices $")

        ########## FRAME 1

        ### COMMON LABELS
        title = ttk.Label(
            common_frame, text="Restaurant Management", style="title.TLabel"
        )
        title.place(relx=0.268, rely=0.02, height=51, width=507)
        self.time_label = ttk.Label(common_frame, text=localtime, style="time.TLabel")
        self.time_label.place(relx=0.34, rely=0.12)

        ### FOOD MENU
        temp_label = ttk.Label(common_frame, text="Order Num :")
        temp_label.place(relx=0.03, rely=0.2)
        self.order_entry = ttk.Entry(common_frame, justify="center")
        self.order_entry.place(relx=0.17, rely=0.2, width=60)
        self.order_entry.bind("<Key>", lambda e: "break")
        self.add_buttons(common_frame, self.order_entry, 0.17, 0.2, 60)
        self.entries.append(self.order_entry)

        article_frame = ttk.Frame(common_frame, width=300, height=200)
        article_frame.place(relx=0.045, rely=0.17 + 0.07 * 2)
        article_list = list(self.articles.keys())

        for index, item in enumerate(article_list):
            ttk.Label(article_frame, text=item).place(
                x=195, y=20 + index * 30, anchor="e"
            )
            temp_entry = ttk.Entry(common_frame, justify="center")
            temp_entry.place(relx=0.26, rely=0.33 + 0.065 * index, width=40)
            temp_entry.bind("<Key>", lambda e: "break")
            self.add_buttons(common_frame, temp_entry, 0.26, 0.33 + 0.065 * index, 40)
            self.article_entries.append((item, temp_entry))
            self.entries.append(temp_entry)

        ### PRICE
        prices = [
            "Discount %",
            "Cost",
            "Service Charge",
            "Tax",
            "SubTotal",
            "Discount",
            "Total",
        ]
        for index, price_txt in enumerate(prices):
            price_label = ttk.Label(common_frame, text=f"{price_txt} :")
            price_label.place(relx=0.4, rely=0.25 + 0.07 * index)
            price_entry = ttk.Entry(common_frame, justify="center")
            price_entry.place(relx=0.55, rely=0.25 + 0.07 * index, width=100)
            price_entry.bind("<Key>", lambda e: "break")
            self.entries.append(price_entry)
            self.price_entries.update({price_txt: price_entry})
            if price_txt == "Discount %":
                self.add_buttons(
                    common_frame, price_entry, 0.55, 0.25 + 0.07 * index, 100
                )

        ### CALCULATOR
        self.res_entry = ttk.Entry(common_frame, style="res.TEntry", justify="center")
        self.res_entry.place(relx=0.75, rely=0.15, width=204, height=50)
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
            )
            temp_button.place(
                relx=0.75 + 0.05 * column,
                rely=0.28 + 0.11 * line,
                width=button_width,
                height=button_height,
            )

        for index, operand in enumerate(self.operands):
            operand_button = ttk.Button(
                common_frame,
                text=operand,
                command=lambda x=operand: self.add_to_entry(self.res_entry, x),
            )
            operand_button.place(
                relx=0.9,
                rely=0.28 + 0.11 * index,
                width=button_width,
                height=button_height,
            )
        zero_button = ttk.Button(
            common_frame, text=0, command=lambda: self.add_to_entry(self.res_entry, 0)
        )
        zero_button.place(
            relx=0.75, rely=0.61, width=button_width, height=button_height
        )
        reset_button = ttk.Button(common_frame, text="C", command=self.erase_calc)
        reset_button.place(
            relx=0.80, rely=0.61, width=button_width, height=button_height
        )
        dot_button = ttk.Button(
            common_frame,
            text=".",
            command=lambda: self.add_to_entry(self.res_entry, "."),
        )
        dot_button.place(relx=0.85, rely=0.61, width=button_width, height=button_height)
        equal_button = ttk.Button(
            common_frame,
            text="=",
            command=lambda: self.compute_string(self.res_entry, self.res_entry.get()),
        )
        equal_button.place(
            relx=0.75, rely=0.72, width=button_width * 4 + 4, height=button_height
        )

        ### CONTROL BUTTONS
        index = 0
        button_labels = {
            "TOTAL": self.calc_total,
            "RESET": self.clear_fields,
            "SAVE": self.save_bill_to_pdf,
            "EXIT": root.destroy,
        }
        for label, function in button_labels.items():
            control_button = ttk.Button(common_frame, text=label, command=function)
            control_button.place(relx=0.1 + 0.23 * index, rely=0.85)
            index += 1

        ### COMMON BEHAVIOUR
        self.clear_fields()
        self.update_time()

        ################# FRAME 2
        index = 0
        articles = {"Food": "Price", **self.articles}
        for key, value in articles.items():
            key_label = ttk.Label(price_frame, text=key, style="rfood.TLabel")
            key_label.place(relx=0.3, rely=0.1 + 0.15 * index)
            value_label = ttk.Label(
                price_frame, text=value, style="yfood.TLabel", justify="center"
            )
            value_label.place(relx=0.7, rely=0.1 + 0.15 * index)
            index += 1

    @property
    def bill(self):
        return "\n".join(
            [f"{label} : {entry.get()}" for label, entry in self.price_entries.items()]
        )

    def clear_fields(self):
        """Reset all the entries with 0"""
        for entry in self.entries:
            entry.delete(0, END)
            entry.insert(0, 0)
        self.res_entry.delete(0, END)

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
        res, error = self.calc.compute_string(calculator_str)
        print(res, error)
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
        self.time_label.configure(text=datetime.now().strftime("%A %d %B %Y %H:%M:%S"))
        self.time_label.after(1000, self.update_time)

    def calc_total(self):
        """Calculate the bill price"""
        price = 0
        for article, entry in self.article_entries:
            price += int(entry.get()) * self.articles[article]
        self.display_total(price)

    def display_total(self, price: float):
        """Display the bill prices"""
        discount_p = int(self.price_entries["Discount %"].get().split()[0])
        for entry in self.price_entries.values():
            entry.delete(0, END)
        service = price * 0.1
        tax = price * 0.2
        sub_total = price + service + tax
        total = sub_total * (1 - discount_p / 100)
        discount = round(sub_total - total, 2)
        self.price_entries["Discount %"].insert(0, f"{discount_p} %")
        self.price_entries["Cost"].insert(0, f"{price:.02f} {self.currency}")
        self.price_entries["Service Charge"].insert(
            0, f"{service:.02f} {self.currency}"
        )
        self.price_entries["Tax"].insert(0, f"{tax:.02f} {self.currency}")
        self.price_entries["SubTotal"].insert(0, f"{sub_total:.02f} {self.currency}")
        self.price_entries["Discount"].insert(0, f"{discount} {self.currency}")
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
        )
        add_button.place(
            relx=entry_x + width / 1000 - 0.002, rely=entry_y, width=20, height=20
        )
        minus_button = ttk.Button(
            frame,
            text="-",
            command=lambda x=entry: self.decrement(x),
            style="small.TButton",
        )
        minus_button.place(relx=entry_x - 0.02, rely=entry_y, width=20, height=20)

    def concrete_inc_dec(self, entry: ttk.Entry, operand: str):
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
        entry.delete(0, END)
        entry.insert(0, value)

    def increment(self, entry: ttk.Entry):
        """Increment the value of the entry by 1"""
        self.concrete_inc_dec(entry, "+")

    def decrement(self, entry: ttk.Entry):
        """Decrement the value of the entry by 1"""
        self.concrete_inc_dec(entry, "-")

    def save_bill_to_pdf(self):
        order = self.order_entry.get()
        date = self.time_label["text"]
        curr_path = os.path.dirname(os.path.abspath(__file__))
        order_dir = os.path.join(curr_path, "orders")
        if not os.path.isdir(order_dir):
            os.makedirs(order_dir)
        pdf_path = os.path.join(order_dir, f"Order_{order}.pdf")

        c = canvas.Canvas(pdf_path, bottomup=0)
        c.drawString(10, 25, self.restaurant_name)
        c.drawString(10, 50, date)
        for index, text in enumerate(self.bill.split("\n"), 1):
            c.drawString(10, 50 + index * 25, text)
        c.save()


root = ThemedTk(theme="equilux")
gui = UI(root)
root.mainloop()
