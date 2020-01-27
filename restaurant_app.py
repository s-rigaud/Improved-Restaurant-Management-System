from datetime import datetime
from tkinter import Tk, Label, Button, Entry, END
from time import sleep

localtime = datetime.now().strftime("%A %d %B %Y %H-%M-%S")

class UI:
    """Main class for the whole interface"""
    def __init__(self, root: Tk):
        self.root = root
        self.articles = {"Fried Potato": 35,
                         "Chicken Burger": 25,
                         "Big King": 20,
                         "Chicken Royal": 40,
                         "Veg Salad": 55,}
        self.entries = []
        self.article_entries = []
        self.price_entries = {}
        self.operands = ['*', '/', '+', '-'][::-1]
        root.title("Restaurant Management")
        root.geometry("1028x500")
        root.configure(bg="#34495e")

        font10 = "{Courier New} 10 normal"
        font30 = "{U.S. 101} 30 bold"
        font11 = "Al-Aramco 11 bold"
        font13 = "{Segeo UI} 13 bold"

        ### COMMON LABELS
        title = Label(master=root, text="Restaurant Management", bg="#2c3e50", font=font30, fg="#95a5a6")
        title.place(relx=0.268, rely=0.02, height=51, width=507)
        self.time_label = Label(master=root, text=localtime, bg="#2c3e50", font=font13, fg="#95a5a6")
        self.time_label.place(relx=0.480, rely=0.12)

        ### FOOD MENU
        article_list = list(self.articles.keys())
        article_list[0:0] = ["Order Num"]
        for index, item in enumerate(article_list):
            temp_label = Label(master=root, text=f"{item} :", bg="#2c3e50", font=font11, fg="#95a5a6")
            temp_label.place(relx=0.054, rely=0.25 + 0.07*index)
            temp_entry = Entry(master=root, bg="#7f8c8d", font=font10)
            temp_entry.place(relx=0.2, rely=0.25 + 0.07*index)
            self.entries.append(temp_entry)
            self.add_buttons(temp_entry, 0.2, 0.25 + 0.07*index)
            if index > 0:
                self.article_entries.append((item, temp_entry))

        ### CALCULATOR
        self.res_entry = Entry(master=root, bg="#7f8c8d", font=font10)
        self.res_entry.place(relx=0.8, rely=0.15)
        self.entries.append(self.res_entry)
        button_width = 50
        button_height = 50
        for i in range(9):
            line = int(i/3)
            column = int(i%3)
            # x=i+1 to avoid reference to final value of i
            temp_button = Button(master=root, text=i+1, bg="#7f8c8d", font=font10, command=lambda x=i+1: self.add_to_entry(self.res_entry, x))
            temp_button.place(relx=0.8 + 0.05*column, rely=0.25 + 0.1*line, width=button_width, height=button_height)
        for index, operand in enumerate(self.operands):
            operand_button = Button(master=root, text=operand, bg="#7f8c8d", font=font10, command=lambda x=operand: self.add_to_entry(self.res_entry, x))
            operand_button.place(relx=0.95, rely=0.25 + 0.1*index, width=button_width, height=button_height)
        zero_button = Button(master=root, text=0, bg="#7f8c8d", font=font10, command=lambda: self.add_to_entry(self.res_entry, 0))
        zero_button.place(relx=0.8, rely=0.55, width=button_width, height=button_height)
        reset_button = Button(master=root, text='C', bg="#7f8c8d", font=font10, command=self.reset_calc)
        reset_button.place(relx=0.85, rely=0.55, width=button_width, height=button_height)
        dot_button = Button(master=root, text=".", bg="#7f8c8d", font=font10, command=lambda: self.add_to_entry(self.res_entry, '.'))
        dot_button.place(relx=0.9, rely=0.55, width=button_width, height=button_height)
        equal_button = Button(master=root, text="=", bg="#7f8c8d", font=font10, command=lambda: self.compute_string(self.res_entry, self.res_entry.get()))
        equal_button.place(relx=0.8, rely=0.65, width=button_width*4, height=button_height)

        ### PRICE
        prices = ["Cost", "Service Charge", "Tax", "SubTotal", "Total"]
        for index, price_label in enumerate(prices):
            price_label = Label(master=root, text=f"{price_label} :", bg="#2c3e50", font=font11, fg="#95a5a6")
            price_label.place(relx=0.4, rely=0.25 + 0.07*index)
        for index, price_label in enumerate(prices):
            price_entry = Entry(master=root, bg="#7f8c8d", font=font10)
            price_entry.place(relx=0.55, rely=0.25 + 0.07*index)
            self.entries.append(price_entry)
            self.price_entries.update({price_label: price_entry})

        ### CONTROL BUTTONS
        index = 0
        button_labels = {"PRICES": self.display_prices,
                         "TOTAL": self.calc_total,
                         "RESET": self.clear_fields,
                         "EXIT": root.destroy}
        for label, function in button_labels.items():
            control_button = Button(master=root, text=label, bg="#7f8c8d", font=font11, fg="#95a5a6", command=function)
            control_button.place(relx=0.2 + 0.1*index, rely=0.8)
            index += 1

        ### COMMON BEHAVIOUR
        self.clear_fields()
        self.update_time()

    def display_prices(self):
        """Small window displaying the price of each food in the menu"""
        price = Tk()
        price.geometry("250x250")
        price.title("Price list")
        price.configure(bg="#34495e")
        price.focus_force()
        index = 0
        articles = {"Food": "Price", **self.articles}
        for key, value in articles.items():
            key_label = Label(master=price, text=key, bg="#2c3e50", font="{Segeo UI} 13 bold", fg="#95a5a6")
            key_label.place(relx=0.1, rely=0.1 + 0.15*index)
            value_label = Label(master=price, text=value, bg="#2c3e50", font="{Segeo UI} 13 bold", fg="#95a5a6")
            value_label.place(relx=0.1+0.7, rely=0.1 + 0.15*index)
            index += 1

    def clear_fields(self):
        """Reset all the entries with 0"""
        for entry in self.entries:
            entry.delete(0, END)
            entry.insert(0, 0)
        self.res_entry.delete(0, END)

    def reset_calc(self):
        """Reset the display ofthe calculator"""
        self.res_entry.delete(len(self.res_entry.get())-1, END)

    def add_to_entry(self, entry, value):
        """Common method used to add operands to the calculator display"""
        entry.insert(END, value)

    def compute_string(self, entry: Entry, calculator_str: str):
        """Computing numbers appearing in the calculator display"""
        res = self.compute('+', calculator_str)
        if res is not None:
            if res == int(res):
                res = int(res)
            entry.delete(0, END)
            entry.insert(END, res)

    def compute(self, operand: str, part1: str = '0', part2: str = '0') -> float:
        """Recursive function trying to divide operations and compute (Tree style)"""
        #TODO is a little bit buggy  6/2/3 for example
        try:
            res1 = float(part1)
        except ValueError:
            for o in self.operands:
                split_str = part1.split(o, 1)
                if len(split_str) > 1:
                    res1 = self.compute(o, split_str[0], split_str[1])
                    break
        try:
            res2 = float(part2)
        except ValueError:
            for o in self.operands:
                split_str = part2.split(o, 1)
                if len(split_str) > 1:
                    res2 = self.compute(o, split_str[0], split_str[1])
                    break

        operand_dict = {'+': self._add,
                        '-': self._sub,
                        '*': self._mul,
                        '/': self._div}
        try:
            return operand_dict[operand](res1, res2)
        except UnboundLocalError:
            self.calc_input_error()
            return None

    def _add(self, f1: float, f2: float) -> float:
        return f1 + f2

    def _sub(self, f1: float, f2: float) -> float:
        return f1 - f2

    def _mul(self, f1: float, f2: float) -> float:
        return f1 * f2

    def _div(self, f1: float, f2: float) -> float:
        return f1 / f2

    def calc_input_error(self):
        """Display errors appearing in the calculator display"""
        self.res_entry.delete(0, END)
        self.res_entry.insert(0, "You enter a wrong formula")
        self.res_entry.after(2000, self.reset_calc)

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
        self.price_entries["Cost"].delete(0, END)
        self.price_entries["Cost"].insert(0, f"{price:.02f}")
        self.price_entries["Service Charge"].delete(0, END)
        self.price_entries["Service Charge"].insert(0, f"{price*0.1:.02f}")
        self.price_entries["Tax"].delete(0, END)
        self.price_entries["Tax"].insert(0, f"{price*0.2:.02f}")
        sub_total = float(self.price_entries["Cost"].get()) \
                    + float(self.price_entries["Service Charge"].get()) \
                    + float(self.price_entries["Tax"].get())
        self.price_entries["SubTotal"].delete(0, END)
        self.price_entries["SubTotal"].insert(0, f"{sub_total:.02f}")
        #TODO discount %
        total = sub_total
        self.price_entries["Total"].delete(0, END)
        self.price_entries["Total"].insert(0, f"{total:.02f}")

    def add_buttons(self, entry: Entry, entry_x: float, entry_y: float):
        """Add button to add or remove food from the bill"""
        add_button = Button(master=root, text='+', bg="#7f8c8d", font="{Courier New} 10 normal", command=lambda x=entry: self.increment(x))
        add_button.place(relx=entry_x-0.02, rely=entry_y, width=20, height=20)
        minus_button = Button(master=root, text='-', bg="#7f8c8d", font="{Courier New} 10 normal", command=lambda x=entry: self.decrement(x))
        minus_button.place(relx=entry_x+0.16, rely=entry_y, width=20, height=20)

    def increment(self, entry: Entry):
        """Increment the value of the entry by 1"""
        old_value = entry.get()
        try:
            value = float(old_value)
            if value == int(value):
                value = int(value)
        except ValueError:
            print(f"The value of the entry was not a float")
            value = -1
        else:
            entry.delete(0, END)
            entry.insert(0, value+1)

    def decrement(self, entry: Entry):
        """Decrement the value of the entry by 1"""
        old_value = entry.get()
        try:
            value = float(old_value)
            if value == int(value):
                value = int(value)
            if value <= 0:
                value = 1
        except ValueError:
            print(f"The value of the entry was not a float")
            value = 1
        else:
            entry.delete(0, END)
            entry.insert(0, value-1)


root = Tk()
gui = UI(root)
root.mainloop()
