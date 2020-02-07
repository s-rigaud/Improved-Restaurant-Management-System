from tkinter import ttk, Toplevel, Button

__all__ = ["ToolTip"]


class ToolTipSkeletton:
    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None
        self.x = 0
        self.y = 0
        self.text = text
        style = ttk.Style()
        style.configure(
            "tooltip.TLabel",
            font="tahoma 10 normal",
            foreground="#000",
            background="#fff",
            justify="left",
            borderwidth=3,
        )

    def showtip(self):
        "Display text in tooltip window"
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.attributes("-topmost", True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, style="tooltip.TLabel")
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class ToolTip:
    def __init__(self, widget, text: str):
        self.toolTip = ToolTipSkeletton(widget, text)
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event):
        self.toolTip.showtip()

    def leave(self, event):
        self.toolTip.hidetip()


if __name__ == "__main__":
    root = Tk()
    button = Button(root, text="click me")
    button.pack()
    ToolTip(button, "Hi")
    root.mainloop()
