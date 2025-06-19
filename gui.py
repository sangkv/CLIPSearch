import os
import tkinter as tk
from tkinter import Menu, LabelFrame, Label, Entry, Button, Toplevel, messagebox
from PIL import Image, ImageTk
from search import CLIPSearcher


class FastImageSearchGUI:
    def __init__(self, db_path):
        self.searcher = CLIPSearcher(db_path=db_path)

        self.root = tk.Tk()
        self.root.title('Image Search')
        self.root.configure(bg='#F2F2F2')
        self.guiW, self.guiH = 1280, 720
        self.thumbW, self.thumbH = 200, 150
        self.root.geometry(f"{self.guiW}x{self.guiH}")
        self.root.resizable(False, False)

        self.font = ('Helvetica Neue', 16)
        self.cols = 5
        self.rows = 3
        self.num_results = self.cols * self.rows

        self._setup_menu()
        self._setup_search_area()
        self._setup_results_area()

        self.root.mainloop()

    def _setup_menu(self):
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(
            label="About",
            command=lambda: self._info("About", "Fast Image Search\nsangkv.work@gmail.com")
        )
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.config(menu=menubar)

    def _setup_search_area(self):
        frame = LabelFrame(self.root, bd=0, bg='#F2F2F2', width=self.guiW, height=80)
        frame.grid(row=0, column=0, pady=10)
        frame.grid_propagate(False)

        container = tk.Frame(frame, bg='#F2F2F2')
        container.place(relx=0.5, rely=0.5, anchor='center')

        self.entry = Entry(container, font=self.font, width=50, relief='groove', bd=2)
        self.entry.grid(row=0, column=0, padx=(0, 10), pady=10)
        self.entry.bind('<Return>', lambda e: self._search())

        self.btn = Button(
            container,
            text='Search',
            font=self.font,
            bg='#007aff',
            fg='white',
            activebackground='#005bb5',
            activeforeground='white',
            bd=0,
            padx=20,
            pady=5,
            command=self._search
        )
        self.btn.grid(row=0, column=1, pady=10)

    def _setup_results_area(self):
        self.result_frame = LabelFrame(self.root, bd=0, bg='#F2F2F2', width=self.guiW, height=self.guiH - 100)
        self.result_frame.grid(row=1, column=0, padx=10, pady=5)
        self.result_frame.grid_propagate(False)

        self.grid_container = tk.Frame(self.result_frame, bg='#F2F2F2')
        self.grid_container.place(relx=0.5, rely=0.5, anchor='center')

        self.labels_img = []
        self.labels_text = []
        self.image_paths = []

        for i in range(self.num_results):
            row, col = divmod(i, self.cols)

            img_label = Label(self.grid_container, bg='#FFFFFF', relief='groove', bd=1, cursor='hand2')
            img_label.grid(row=row * 2, column=col, padx=10, pady=5)
            img_label.grid_remove()
            img_label.bind("<Button-1>", lambda e, idx=i: self._open_full_image(idx))

            text_label = Label(
                self.grid_container,
                font=("Helvetica Neue", 10),
                fg='gray30',
                bg='#F2F2F2',
                wraplength=self.thumbW,
                anchor='center',
                justify='center'
            )
            text_label.grid(row=row * 2 + 1, column=col, padx=10, pady=0)
            text_label.grid_remove()

            self.labels_img.append(img_label)
            self.labels_text.append(text_label)
            self.image_paths.append(None)

    def _resize_image(self, img):
        w, h = img.size
        scale = min(self.thumbW / w, self.thumbH / h)
        return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    def _search(self):
        query = self.entry.get().strip()
        if not query:
            return

        self.btn.config(text='Searching...', state='disabled')
        self.root.update_idletasks()

        results = self.searcher.search(query_text=f'A photo of a {query}.', top_k=self.num_results)

        for i in range(self.num_results):
            self.labels_img[i].config(image='')
            self.labels_img[i].image = None
            self.labels_img[i].grid_remove()
            self.labels_text[i].config(text='')
            self.labels_text[i].grid_remove()
            self.image_paths[i] = None

        for i, (path, _) in enumerate(results):
            try:
                img = Image.open(path)
                imgtk = ImageTk.PhotoImage(self._resize_image(img))

                self.labels_img[i].config(image=imgtk)
                self.labels_img[i].image = imgtk
                self.labels_img[i].grid()

                filename = os.path.basename(path)
                short_name = self._shorten_text(filename)
                self.labels_text[i].config(text=short_name)
                self.labels_text[i].grid()
                self._add_tooltip(self.labels_text[i], filename)

                self.image_paths[i] = path
            except Exception as e:
                print(f"Error loading image {path}: {e}")

        self.entry.focus_set()
        self.btn.config(text='Search', state='normal')

    def _open_full_image(self, idx):
        path = self.image_paths[idx]
        if not path or not os.path.exists(path):
            return

        top = Toplevel(self.root)
        top.title(os.path.basename(path))
        top.configure(bg='black')

        screen_w = top.winfo_screenwidth()
        screen_h = top.winfo_screenheight()
        top.geometry(f"{screen_w//2}x{screen_h//2}+200+100")
        top.resizable(True, True)

        try:
            img = Image.open(path)
            img.thumbnail((screen_w * 0.9, screen_h * 0.9))
            imgtk = ImageTk.PhotoImage(img)

            label = Label(top, image=imgtk, bg='black')
            label.image = imgtk
            label.pack(expand=True)
        except Exception as e:
            print(f"Error opening full image: {e}")
            top.destroy()

    def _add_tooltip(self, widget, text):
        def on_enter(e):
            widget.tooltip = Toplevel(widget)
            widget.tooltip.wm_overrideredirect(True)
            widget.tooltip.configure(bg='lightyellow')
            label = Label(widget.tooltip, text=text, bg='lightyellow', font=('Helvetica', 10))
            label.pack()
            x = e.x_root + 10
            y = e.y_root + 10
            widget.tooltip.geometry(f"+{x}+{y}")
        def on_leave(e):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _shorten_text(self, text, max_len=28):
        return text if len(text) <= max_len else text[:max_len - 3] + "..."

    def _info(self, title, msg):
        messagebox.showinfo(title, msg)


if __name__ == '__main__':
    FastImageSearchGUI('image_database.db')

