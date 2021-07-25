import tkinter as tk
from tkinter.constants import LEFT

from cv2 import imwrite
import numpy as np
from PIL import Image, ImageTk

from julia import julia, STANDARD_BOUNDS
from tkinter.filedialog import asksaveasfilename
from tkinter.simpledialog import askinteger
from tkinter.messagebox import showinfo
from threading import Thread
from math import floor


def format_float(n, decimals=0):
  exp = 0
  while True:
    if n > 1:
      multiplier = 10 ** decimals
      if exp == 0:
        return str(floor(n * multiplier + 0.5) / multiplier)
      else:
        return str(floor(n * multiplier + 0.5) / multiplier) + " * 10^-" + str(exp)
    n *= 10
    exp += 1


class Gui(tk.Tk):

  def __init__(self):
    super().__init__()

    self.current_zoom = None
    self.c_real = tk.DoubleVar(self, value=-0.1)
    self.c_imag = tk.DoubleVar(self, value=0.655)

    self.max_it = tk.IntVar(self, value=70)
    self.radius = tk.DoubleVar(self, value=3)

    self.width = 450

    self.showing = None
    self.jm = None
    self.bounds = STANDARD_BOUNDS

    self.settings_frame = tk.Frame(self)
    
    tk.Label(self.settings_frame, text="Re(c)").pack(pady=5, padx=5)
    tk.Entry(self.settings_frame, textvariable=self.c_real).pack(pady=5, padx=5)

    tk.Label(self.settings_frame, text="Im(c)").pack(pady=5, padx=5)
    tk.Entry(self.settings_frame, textvariable=self.c_imag).pack(pady=5, padx=5)

    tk.Label(self.settings_frame, text="Maximale Iterationen *10").pack(pady=5, padx=5)
    tk.Entry(self.settings_frame, textvariable=self.max_it).pack(pady=5, padx=5)

    tk.Label(self.settings_frame, text="Grenzbetrag").pack(pady=5, padx=5)
    tk.Entry(self.settings_frame, textvariable=self.radius).pack(pady=5, padx=5)


    tk.Button(self.settings_frame, text="Anzeigen", command=self.show_new).pack()
    tk.Button(self.settings_frame, text="Bild Speichern unter", command=self.save_dialog).pack()

    self.settings_frame.pack(side=LEFT, padx=10)

    self.canvas = tk.Canvas(self, width=450, height=450)
    self.canvas.pack(side=LEFT)

    self.canvas.bind("<ButtonPress>", self.start_zoom)
    self.canvas.bind("<ButtonRelease>", self.zoom)
    self.canvas.bind("<B1-Motion>", self.motion)

    self.after(500, lambda: self.bind("<Configure>", self.resize))
    # self.after(500, lambda: self.resize(None))

  def show_new(self):
    self.bounds = STANDARD_BOUNDS
    self.show()

  def get_user_input(self):
    try:
      c = complex(self.c_real.get(), self.c_imag.get())
      max_it = self.max_it.get()
      radius = self.radius.get()
      return c, max_it, radius
    except tk.TclError:
      tk.messagebox.showinfo("Error", "falsche Eingabe")

  def show(self, new=True):
    self.canvas.delete("julia_set", "zoom_rect", "legende")

    if new:
      self.jm = julia(self.get_user_input(), int(self.width*1.5), bounds=self.bounds)

    im = Image.fromarray(self.jm * 255)

    # resize im to fit canvas
    ratio = im.width/im.height
    if im.height > im.width:
      height = self.width
      width = int(ratio * height)
    else:
      width = self.width
      height = int(ratio**-1 * width)

    im = im.resize((width, height))

    ph = ImageTk.PhotoImage(im, master=self)

    label = tk.Label(self)
    label.image = ph
    self.canvas.create_image(im.width//2, self.width - im.height//2, image=ph, tags="julia_set")
    self.canvas.create_text(self.width//2, 10, text=format_float(self.bounds[1] - self.bounds[0], decimals=2), tags="legende", fill="green")
    self.canvas.create_text(10, self.width//2, text=format_float(self.bounds[3] - self.bounds[2], decimals=2), tags="legende", angle=90, fill="green")

    self.showing = True

  def start_zoom(self, e):
    self.current_zoom = (e.x, e.y)

  def zoom(self, e):
    if self.current_zoom is None:
      return

    if np.sqrt((self.current_zoom[0] - e.x) ** 2 + (self.current_zoom[1] - e.y) ** 2) < 5:
      self.current_zoom = None
      self.canvas.delete("zoom_rect")
      return

    scale = max(self.bounds[1] - self.bounds[0], self.bounds[3] - self.bounds[2])

    self.bounds = (self.bounds[0] + (min(self.current_zoom[0], e.x) / self.width * scale),
                   self.bounds[0] + (max(self.current_zoom[0], e.x) / self.width * scale),
                   self.bounds[2] + ((self.width - max(self.current_zoom[1], e.y)) / self.width * scale),
                   self.bounds[2] + ((self.width - min(self.current_zoom[1], e.y)) / self.width * scale))

    self.current_zoom = None
    self.show()

  def motion(self, e):
    if self.current_zoom is not None:
      self.canvas.delete("zoom_rect")
      self.canvas.create_rectangle(self.current_zoom[0], self.current_zoom[1], e.x, e.y, tags="zoom_rect", outline="red")

  def save_dialog(self):
    if self.showing:
      filename = asksaveasfilename(defaultextension=".png")

      if filename is None or filename == "":
        return

      resolution = askinteger("Auflösung wählen", "Willst du eine höhere Auflösung haben?")

      self.canvas.create_text(225, 50, text="Bild wird noch gespeichert", fill="red", tags="flash_msg")
      Thread(target=self.save, args=(filename, resolution)).start()

  def save(self, filename, resolution):
    if resolution is not None:
      self.jm = julia(self.get_user_input(), resolution, bounds=self.bounds)
    imwrite(filename, self.jm*255)
    self.canvas.delete("flash_msg")
    showinfo("Bild gespeichert", "Das Bild wurde erfolgreich gespeichert")

  def resize(self, e):
    if e.widget == self:
      height = self.winfo_height()
      width = self.winfo_width() - self.settings_frame.winfo_width()

      # print(e.__dict__)
      old_width = self.width
      self.width = min(height, width) - 10

      if old_width == self.width:
        return

      self.canvas.configure(width=self.width, height=self.width)


      if self.jm is not None:
        self.show(new=False)

      self.unbind("<Configure>")
      self.after(200, lambda: self.bind("<Configure>", self.resize))


if __name__ == "__main__":
  Gui()

  tk.mainloop()
