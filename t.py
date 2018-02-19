try:
    from PIL import Image
except ImportError:
    import Image
from PIL import ImageTk

# try:
#     import Tkinter as tk  # Python2
# except ImportError:
# import tkinter as tk  # Python3s
from tkinter import *
import PIL as PILAll

import sys
import os


class ExampleApp(Frame):
    def __init__(self, master):
        Frame.__init__(self, master=None)
        self.modifications = []
        self.x = 0
        self.y = 0
        self.canvas = Canvas(self, cursor="cross", width=1800, height=1000, confine=True, scrollregion=(10, 10, 10, 10),
                             relief="groove", bg="blue")

        self.sbarv = Scrollbar(self, orient=VERTICAL)
        self.sbarh = Scrollbar(self, orient=HORIZONTAL)
        self.sbarv.config(command=self.canvas.yview)
        self.sbarh.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.sbarv.set)
        self.canvas.config(xscrollcommand=self.sbarh.set)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.sbarv.grid(row=0, column=1, stick=N + S)
        self.sbarh.grid(row=1, column=0, sticky=E + W)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<ButtonPress-3>", self.cut_paste)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Return>", self.save_images)

        # scrolling
        self.canvas.bind("<2>", lambda event: self.canvas.focus_set())
        self.canvas.bind('<Left>', self.scroll_left)
        self.canvas.bind('<Right>', self.scroll_right)
        self.canvas.bind('<Up>', self.scroll_up)
        self.canvas.bind('<Down>', self.scroll_down)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        print("open %s" % img_path)
        self.im = PILAll.Image.open(img_path)
        self.wazil, self.lard = self.im.size

        self.canvas.config(scrollregion=(0, 0, self.wazil, self.lard))
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)

    out_of_scope = 1

    def cut_paste(self, event):
        print("----cutting and pasting")

        print("BOX")
        print("-- %s | %s" % (self.start_x, self.start_y))
        print("-- %s | %s" % (self.end_x, self.end_y))
        print("DIM: %s, %s" % ((self.end_x - self.start_x), (self.end_y - self.start_y)))

        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        print("Moving to %s %s" % (curX, curY))

        diffX = (self.end_x - self.start_x)
        diffY = (self.end_y - self.start_y)

        self.modifications.append(
            ((int(self.start_x), int(self.start_y), int(self.end_x), int(self.end_y)), (int(curX), int(curY), int(curX + diffX), int(curY + diffY)))
        )

        self.start_x = None
        self.start_y = None
        self.canvas.delete(self.rect)
        self.rect = None

    def on_button_leave(self, event):
        self.out_of_scope = 2

    def save_images(self, event):
        print("SAVING")

        img = PILAll.Image.open(img_path)
        img_gt = PILAll.Image.open(gt_path)

        for mod in self.modifications:
            from_box = mod[0]
            to_box = mod[1]

            # raw image
            region = img.crop(from_box)
            img.paste(region, to_box)
            img.save(img_path_aug)

            # gt image
            region = img_gt.crop(from_box)
            img_gt.paste(region, to_box)
            img_gt.save(gt_path_aug)

        quit()

    def scroll_left(self, event):
        self.canvas.xview_scroll(-1, 'units')

    def scroll_right(self, event):
        self.canvas.xview_scroll(1, 'units')

    def scroll_up(self, event):
        self.canvas.yview_scroll(-1, 'units')

    def scroll_down(self, event):
        self.canvas.yview_scroll(1, 'units')

    def on_button_press(self, event):
        print("import Image------ Creating new selection")
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            if self.out_of_scope == 1:
                self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='blue')

    def get_out_of_scope(self, x, y):
        return self.out_of_scope

    def on_move_press(self, event):

        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        var = self.get_out_of_scope(event.x, event.y)

        # print(var, event.x, event.y)
        # expand rectangle as you drag the mouse
        if var == 1:
            self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        print("Boxed: %s %s -> %s %s" % (self.start_x, self.start_y, self.end_x, self.end_y))


files = sys.argv[1]
print(files)


base_raw = '/home/schimpf/junk/hackathon/albert/input'
base_gt = '/home/schimpf/junk/hackathon/albert/gt'

filename = os.path.splitext(os.path.basename(files))[0]

raw_image = filename+'.jpg'
img_path = base_raw + "/" + raw_image
img_path_aug = base_raw + "/aug/" + raw_image

gt_image = filename+'.png'
gt_path = base_gt + "/" + gt_image
gt_path_aug = base_gt + "/aug/" + gt_image


root = Tk()
app = ExampleApp(root)
app.grid()
root.mainloop()
