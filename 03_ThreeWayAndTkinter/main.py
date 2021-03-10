import functools
import random
import tkinter as tk
from tkinter import messagebox

top = tk.Tk()
for i in range(4):
    top.columnconfigure(i, weight=1, minsize=40)
for i in range(5):
    top.rowconfigure(i, weight=1, minsize=40)
buttons = [None] * 16


def exit_handler():
    top.quit()


def resize_handler(event):
    for i in range(4):
        for j in range(4):
            if buttons[i * 4 + j] is not None:
                buttons[i * 4 + j].grid(column=j, row=i + 1, sticky=(tk.N, tk.S, tk.E, tk.W))
    again_button.grid(column=0, row=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
    close_button.grid(column=2, row=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
    print(event)


def again_handler():
    random.shuffle(buttons)
    resize_handler(None)


def click_callback(btn):
    def can_swap(dy, dx):
        return 0 <= y + dy < 4 and 0 <= x + dx < 4 and buttons[(y + dy) * 4 + x + dx] is None
    y, x = btn.grid_info()["row"] - 1, btn.grid_info()["column"]
    for dx, dy in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
        if can_swap(dy, dx):
            print("Swapped", y, x, y + dy, x + dx)
            buttons[(y + dy) * 4 + (x + dx)], buttons[y * 4 + x] = buttons[y * 4 + x], None
            resize_handler(None)
            break
    if [(el.grid_info()["row"] - 1) * 4 + el.grid_info()["column"] if el else None for el in buttons] == list(range(15)) + [None]:
        messagebox.showinfo("Congrats!", "you won!")
        again_handler()


again_button = tk.Button(top, text="Again", command=again_handler)
close_button = tk.Button(top, text="Exit", command=exit_handler)
for id in range(15):
    buttons[id] = tk.Button(text=str(id))
    buttons[id].configure(command=functools.partial(click_callback, buttons[id]))
again_handler()
top.bind("<Configure>", resize_handler)
top.mainloop()