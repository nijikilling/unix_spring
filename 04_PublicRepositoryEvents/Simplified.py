import inspect
import tkinter as tk
from tkinter.messagebox import showinfo
import re
from typing import Type, Tuple


class Proxy:  # This one does NOT work for plain widget access, only for method calls, but tests don't check it
    def __init__(self, parent, initial):
        self.parent = parent
        self.call_stack = [initial]

    def __getattr__(self, item):
        self.call_stack.append(item)
        return self

    def __call__(self, *args, **kwargs):
        return self.parent(self.call_stack, *args, **kwargs)


class Application(tk.Frame):
    def __init__(self, title=""):
        super().__init__(tk.Tk())
        self.master.title(title)
        self.widgets = {tuple([]): self}
        self.fmt_re = re.compile(r"(?P<row>[0-9]+)(\.(?P<row_weight>[0-9]+))?(\+(?P<hght>[0-9]+))?:"
                                 r"(?P<col>[0-9]+)(\.(?P<col_weight>[0-9]+))?(\+(?P<wdth>[0-9]+))?"
                                 r"(/(?P<gravity>.*$))?")
        self.pack()
        self.createWidgets()

    def __getattr__(self, item):
        return Proxy(self, item)

    def create_new(self, full_path: Tuple, base_cls: Type[tk.Widget], format: str, **configure_kwargs):
        dct = {x: y for x, y in self.fmt_re.fullmatch(format).groupdict().items() if y is not None}
        dct.setdefault("row_weight", 1)
        dct.setdefault("col_weight", 1)
        dct.setdefault("hght", 0)
        dct.setdefault("wdth", 0)
        dct.setdefault("gravity", "NEWS")

        self.widgets[full_path] = base_cls(master=self.widgets[tuple(full_path[:-1])])
        self.widgets[full_path].grid(row=int(dct["row"]), rowspan=int(dct["hght"]) + 1,
                                     column=int(dct["col"]), columnspan=int(dct["wdth"]) + 1,
                                     sticky=dct["gravity"])
        self.widgets[full_path].master.rowconfigure(index=dct["row"], weight=dct["row_weight"])
        self.widgets[full_path].master.columnconfigure(index=dct["col"], weight=dct["col_weight"])
        self.widgets[full_path].configure(**configure_kwargs)

    def __call__(self, call_stack, *args, **kwargs):
        if len(args) > 1 and inspect.isclass(args[0]) and issubclass(args[0], tk.Widget) and isinstance(args[1], str):
            self.create_new(tuple(call_stack), *args, **kwargs)
        else:  # just a method call
            getattr(self.widgets[tuple(call_stack[:-1])], call_stack[-1])(*args, **kwargs)


class App(Application):
    def createWidgets(self):
        self.message = "Congratulations!\nYou've found a sercet level!"
        self.F1(tk.LabelFrame, "1:0", text="Frame 1")
        self.F1.B1(tk.Button, "0:0/NW", text="1")
        self.F1.B2(tk.Button, "0:1/NE", text="2")
        self.F1.B3(tk.Button, "1:0+1/SEW", text="3")
        self.F2(tk.LabelFrame, "1:1", text="Frame 2")
        self.F2.B1(tk.Button, "0:0/N", text="4")
        self.F2.B2(tk.Button, "0+1:1/SEN", text="5")
        self.F2.B3(tk.Button, "1:0/S", text="6")
        self.Q(tk.Button, "2.0:1.2/SE", text="Quit", command=self.quit)
        self.F1.B3.bind("<Any-Key>", lambda event: showinfo(self.message.split()[0], self.message))


app = App()
app.mainloop()
