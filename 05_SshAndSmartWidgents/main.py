import random
import tkinter as tk
import re

root = tk.Tk()

text = tk.Text(root)
text.grid(row=1, column=1, sticky="SWN")
canvas = tk.Canvas(root)
canvas.grid(row=1, column=2, sticky="SEN")
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(1, weight=5)

state = 0
center = None
color = None
border_color = None
border_w = None
last_oval = None
figures = []

check_expr = re.compile(r"rect~(?P<p1>\([\-+]?[0-9]+,[\-+]?[0-9]+\))"
                            r"~(?P<p2>\([\-+]?[0-9]+,[\-+]?[0-9]+\))"
                        r"~(?P<fill>#[0-9a-fA-F]{6})~(?P<border_fill>#[0-9a-fA-F]{6})~(?P<border_w>[0-9]+)")


def gen_random_color():
    return f"#{random.randrange(0, 256 ** 3):06x}"


def tuple_from_text(t):
    return tuple(list(map(int, t.strip('()').split(','))))


def text_update(event):
    global figures
    lines = text.get("1.0", tk.END).split('\n')
    for tag in text.tag_names():
        if tag != 'sel':
            text.tag_remove(tag, "1.0", tk.END)
    for fig in figures:
        canvas.delete(fig[0])
    figures = []
    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        for char in "\r\t ":
            line = line.replace(char, '')
        match = check_expr.fullmatch(line)
        if match:
            dct = match.groupdict()
            p1 = tuple_from_text(dct["p1"])
            p2 = tuple_from_text(dct["p2"])
            if state == 2 and last_oval == len(figures):
                diff = (event.x - center[0]), (event.y - center[1])
            else:
                diff = (0, 0)
            print(state)
            figures.append((canvas.create_oval(p1[0] + diff[0], p1[1] + diff[1],
                                               p2[0] + diff[0], p2[1] + diff[1], fill=dct["fill"], outline=dct["border_fill"], width=int(dct["border_w"])), p1, p2))
            if diff != (0, 0):
                text.insert(f"{idx + 1}.0", f"rect ~ {pack_tuple((p1[0] + diff[0], p1[1] + diff[1]))} ~ "
                                            f"{pack_tuple((p2[0] + diff[0], p2[1] + diff[1]))} ~ "
                                            f"{pack_tuple(dct['fill'])} ~ {dct['border_fill']} ~ {dct['border_w']}\n")
                text.delete(f"{idx + 2}.0", f"{idx + 3}.0")
        else:
            text.tag_add(str(idx), f"{idx + 1}.0", f"{idx + 1}.end")
            text.tag_config(str(idx), background="red")


def pack_tuple(t):
    return str(t)


def check_in_oval(p1, p2, q):
    mid = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    a = abs(p1[0] - p2[0]) / 2
    b = abs(p1[1] - p2[1]) / 2
    return (mid[0] - q[0]) ** 2 / a ** 2 + (mid[1] - q[1]) ** 2 / b ** 2 <= 1


def canvas_event(event: tk.Event):
    global state, center, color, border_color, border_w, last_oval
    if event.type == tk.EventType.ButtonPress:
        move_mode = False
        for idx, fig in enumerate(figures):
            if check_in_oval(fig[1], fig[2], (event.x, event.y)):
                last_oval = idx
                move_mode = True
        center = (event.x, event.y)
        if not move_mode:
            state = 1
            color = gen_random_color()
            border_color = gen_random_color()
            border_w = random.randrange(0, 4)
            last_oval = canvas.create_oval(center[0], center[1], center[0], center[1], fill=color, outline=border_color, width=border_w)
        else:
            state = 2
    elif event.type == tk.EventType.ButtonRelease:
        if state == 1:
            canvas.delete(last_oval)
            content = text.get("1.0", tk.END)
            if len(content.strip()) > 1 and content[-2] != '\n':
                text.insert(tk.END, ' \n')
            diff_x = abs(center[0] - event.x)
            diff_y = abs(center[1] - event.y)
            text.insert(tk.END, f"rect ~ {pack_tuple((center[0] - diff_x, center[1] - diff_y))} ~ " 
                                       f"{pack_tuple((center[0] + diff_x, center[1] + diff_y))} ~ "
                                       f"{pack_tuple(color)} ~ {pack_tuple(border_color)} ~ {border_w}\n")
        else:
            last_oval = None
        state = 0
        text_update(event)
    elif event.type == tk.EventType.Motion and state == 1:
            canvas.delete(last_oval)
            diff_x = abs(center[0] - event.x)
            diff_y = abs(center[1] - event.y)
            last_oval = canvas.create_oval(center[0] - diff_x, center[1] - diff_y,
                                           center[0] + diff_x, center[1] + diff_y,
                                           fill=color, outline=border_color, width=border_w)
    elif event.type == tk.EventType.Motion and state == 2:
        text_update(event)
        center = (event.x, event.y)


def text_event(event):
    text_update(event)


canvas.bind("<Button-1>", canvas_event)
canvas.bind("<Double-Button-1>", canvas_event)
canvas.bind("<ButtonRelease-1>", canvas_event)
canvas.bind("<B1-Motion>", canvas_event)
canvas.bind("<Enter>", canvas_event)
canvas.bind("<Leave>", canvas_event)

text.bind("<KeyRelease>", text_event)

root.mainloop()