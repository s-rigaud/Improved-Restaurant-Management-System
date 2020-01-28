"""
"""

import os
from datetime import datetime
from tkinter import Tk, Toplevel, Event, ttk, END
from ttkthemes import ThemedTk
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk


from scient_calc import ScientCalc
from helpers import concrete_inc_dec

localtime = datetime.now().strftime("%A %d %B %Y %H-%M-%S")


class UI(ThemedTk):
    """Main class for the whole interface"""

    def __init__(self):
        ThemedTk.__init__(self, theme="equilux")
        root = self
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

        self.bg_color = "#2f3640"
        self.ico_path = None
        self.logo_path = None
        self.order_entry = None
        self.entries = []
        self.article_entries = []
        self.price_entries = {}
        self._width = 1028
        self._height = 500

        self._init_ui(root)

    def _init_ui(self, root: ThemedTk):
        root.title("Restaurant Management")
        root.geometry(f"{self._width}x{self._height}")
        root.resizable(False, False)
        root.overrideredirect(1)
        root.configure(bg=self.bg_color)
        root.wm_attributes("-transparentcolor", "#eaeaea")
        curr_path = os.path.dirname(os.path.abspath(__file__))
        self.ico_path = os.path.join(curr_path, "ico.ico")
        self.logo_path = os.path.join(curr_path, "ananas.png")
        root.iconbitmap(self.ico_path)

        # https://stackoverflow.com/questions/4055267#answer-4055612
        self.bind("<ButtonPress-1>", self._start_moving)
        self.bind("<ButtonRelease-1>", self._stop_moving)
        self.bind("<B1-Motion>", self._on_motion)

        self.configure_style()

        notebk = ttk.Notebook(root)
        notebk.pack()
        common_frame = ttk.Frame(notebk, width=self._width, height=self._height)
        price_frame = ttk.Frame(notebk, width=self._width, height=self._height)
        notebk.add(common_frame, text="Billing")
        notebk.add(price_frame, text="Prices $")

        ########## FRAME 1
        ### COMMON LABELS
        title_frame = ttk.Frame(common_frame, width=self._width, height=100)
        title_frame.place(x=0, y=0)
        title = ttk.Label(
            title_frame, text="Restaurant Management", style="title.TLabel"
        )
        title.place(x=self._width / 2, y=25, anchor="center")
        self.time_label = ttk.Label(title_frame, text=localtime, style="time.TLabel")
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
            "EXIT": root.destroy,
        }
        for label, function in button_labels.items():
            control_button = ttk.Button(common_frame, text=label, command=function)
            control_button.place(x=100 + 200 * index, y=400)
            index += 1

        ### COMMON BEHAVIOUR
        self.clear_fields()
        self.update_time()

        ################# FRAME 2
        self.display_food_price_frame(price_frame)

    @property
    def bill(self):
        # TODO ADD cost + service charge (client doesn't have to know)
        return "\n".join(
            [
                f"{label} : {entry.get()}"
                for label, entry in self.price_entries.items()
                if label != "Discount %"
            ]
        )

    def configure_style(self):
        s = ttk.Style()
        s.theme_settings(
            "equilux",
            {
                "TButton": {
                    "configure": {"padding": 0},
                    "map": {
                        "foreground": [
                            ("active", "#0be881"),
                            ("!disabled", "#009432"),
                        ],
                        "background": [("active", "#000"), ("!disabled", "#009432"),],
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

    def display_food_frame(self, common_frame: ttk.Frame):
        temp_label = ttk.Label(common_frame, text="Order Num :")
        temp_label.place(x=100, y=100)
        self.order_entry = ttk.Entry(common_frame, justify="center")
        self.order_entry.place(x=230, y=100, width=60)
        self.order_entry.bind("<Key>", lambda e: "break")
        self.add_buttons(common_frame, self.order_entry, 230, 100, 60)
        self.entries.append(self.order_entry)

        article_frame = ttk.Frame(common_frame, width=300, height=200)
        article_frame.place(x=50, y=140)
        article_list = list(self.articles.keys())

        for index, item in enumerate(article_list):
            ttk.Label(article_frame, text=item).place(
                x=195, y=20 + index * 30, anchor="e"
            )
            temp_entry = ttk.Entry(common_frame, justify="center")
            temp_entry.place(x=275, y=150 + 30 * index, width=40)
            temp_entry.bind("<Key>", lambda e: "break")
            self.add_buttons(common_frame, temp_entry, 275, 150 + 30 * index, 40)
            self.article_entries.append((item, temp_entry))
            self.entries.append(temp_entry)

    def display_total_frame(self, common_frame: ttk.Frame):
        discount_p_label = ttk.Label(common_frame, text="Discount %")
        discount_p_label.place(x=380, y=97)
        discount_p_entry = ttk.Entry(common_frame, justify="center")
        discount_p_entry.place(x=510, y=100, width=100)
        discount_p_entry.bind("<Key>", lambda e: "break")
        self.entries.append(discount_p_entry)
        self.price_entries.update({"Discount %": discount_p_entry})
        self.add_buttons(common_frame, discount_p_entry, 510, 100, 100)

        prices_txt = [
            "Cost",
            "Service Charge",
            "Tax",
            "SubTotal",
            "Discount",
            "Total",
        ]
        total_frame = ttk.Frame(common_frame, width=340, height=200)
        total_frame.place(x=350, y=125)
        for index, price_txt in enumerate(prices_txt):
            total_label = ttk.Label(total_frame, text=price_txt)
            total_label.place(x=200, y=35 + 30 * index, anchor="e")
            price_entry = ttk.Entry(total_frame, justify="center")
            price_entry.place(x=210, y=23 + 30 * index, width=100)
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
            )
            operand_button.place(
                x=928, y=160 + 51 * index, width=button_width, height=button_height,
            )
        zero_button = ttk.Button(
            common_frame, text=0, command=lambda: self.add_to_entry(self.res_entry, 0)
        )
        zero_button.place(x=775, y=313, width=button_width, height=button_height)
        reset_button = ttk.Button(common_frame, text="C", command=self.erase_calc)
        reset_button.place(x=826, y=313, width=button_width, height=button_height)
        dot_button = ttk.Button(
            common_frame,
            text=".",
            command=lambda: self.add_to_entry(self.res_entry, "."),
        )
        dot_button.place(x=877, y=313, width=button_width, height=button_height)
        equal_button = ttk.Button(
            common_frame,
            text="=",
            command=lambda: self.compute_string(self.res_entry, self.res_entry.get()),
        )
        equal_button.place(
            x=775, y=364, width=button_width * 4 + 4, height=button_height
        )

    def display_food_price_frame(self, price_frame: ttk.Frame):
        index = 0
        articles = {"Food": "Price", **self.articles}
        for food, price in articles.items():
            food_label = ttk.Label(price_frame, text=f"{food} |", style="rfood.TLabel")
            food_label.place(x=500, y=50 + 50 * index, anchor="e")
            price_label = ttk.Label(
                price_frame,
                text=f"{price} {self.currency}",
                style="yfood.TLabel",
                anchor="w",
            )
            price_label.place(x=500, y=38 + 50 * index)
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
                entry.insert(END, f" {self.currency}")

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
        add_button.place(x=entry_x + width, y=entry_y, width=20, height=20)
        minus_button = ttk.Button(
            frame,
            text="-",
            command=lambda x=entry: self.decrement(x),
            style="small.TButton",
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
        c.drawCentredString(page_x / 2, page_y / 10, self.restaurant_name)
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


gui = UI()
gui.mainloop()
