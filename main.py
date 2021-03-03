import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.widgets import TextBox, Button

import matplotlib
matplotlib.use("tkagg")

'''
dirs to exclude:
  PyQt5
  
  pyinstaller .\main.py -F --exclude-module PyQt5

'''

class Main:

  def __init__(self):
    self.resolution = 500
    self.c = complex(-0.1, 0.65)
    self.new_c = complex(0, 0) 

    self.zoom_bounds = (0, 0)

    self.fig, self.ax = plt.subplots()

    self.xmin = -1.5
    self.xmax = 1.5
    self.ymin = -1.5
    self.ymax = 1.5

    self.draw(self.xmin, self.xmax, self.ymin, self.ymax)

    # self.fig.canvas.mpl_connect("scroll_event", self.zoom)
    self.fig.canvas.mpl_connect("button_press_event", self.zoomClick)
    # self.fig.canvas.mpl_connect("button_release_event", self.zoom)

    plt.subplots_adjust(top=.8)

    # c input fields
    axIm = plt.axes([.15, .93, .5, .05])
    self.tIm = TextBox(axIm, "Im(c)", initial=self.c.imag)
    self.tIm.set_val(self.c.imag)

    axRe = plt.axes([.15, .88, .5, .05])
    self.tRe = TextBox(axRe, "Re(c)", initial=self.c.real)

    self.tRe.on_text_change(self.re_changed)
    self.tIm.on_text_change(self.im_changed)

    # sumbit button
    axBtn = plt.axes([.7, .93, .2, .05])
    btn = Button(axBtn, "Neu plotten")
    btn.on_clicked(self.redraw)

    plt.show()
      
  def im_changed(self, user_in):
    try:
      self.new_c = complex(self.new_c.imag, float(user_in))
    except ValueError:
      pass

  def re_changed(self, user_in):
    try:
      self.new_c = complex(float(user_in), self.new_c.real)
    except ValueError:
      pass

  def redraw(self, event):
    self.c = self.new_c
    self.draw(self.xmin, self.xmax, self.ymin, self.ymax)

  def draw(self, xmin, xmax, ymin, ymax):
    xwidth = xmax - xmin
    yheight = ymax - ymin

    self.ax.clear()

    self.ax.imshow(self.julia(xmin, xmax, ymin, ymax), cmap=cm.binary)
    
    self.ax.set_xticks(np.linspace(0, xwidth*self.resolution, 5))
    self.ax.set_xticklabels(np.linspace(xmin, xmax, 5))
    
    self.ax.set_yticks(np.linspace(0, yheight*self.resolution, 5))
    self.ax.set_yticklabels(np.linspace(ymin, ymax, 5))

    self.fig.canvas.draw()

  
  def julia(self, xmin, xmax, ymin, ymax):
    xwidth = xmax - xmin
    ywidth = ymax - ymin
    arr = np.ones((int(xwidth*self.resolution), int(ywidth*self.resolution)))

    for x in range(int(xmin*self.resolution), int(xmax*self.resolution)):
      for y in range(int(ymin*self.resolution), int(ymax*self.resolution)):
        
        z = complex(x / self.resolution, y / self.resolution)

        for i in range(47):

          z = self.func(z)
          if abs(z) > 4:
            arr[int(x-xmin*self.resolution), int(y-ymin*self.resolution)] = 0
            break

    return arr

  def func(self, z):
    return z*z+self.c

  def zoomClick(self, event):
    print(event)
    if (event.inaxes == self.ax and not event.dblclick):
      self.zoom_bounds = (event.xdata, event.ydata)


if __name__ =="__main__":
  main = Main()