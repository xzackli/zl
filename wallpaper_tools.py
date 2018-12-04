import os
import ctypes
from ctypes import wintypes

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps
import numpy as np


def set_background(image, folder="Users\\xzack\\Projects\\zl"):
    drive = "c:\\"
    image_path = os.path.join(drive, folder, image)

    SPI_SETDESKWALLPAPER  = 0x0014
    SPIF_UPDATEINIFILE    = 0x0001
    SPIF_SENDWININICHANGE = 0x0002

    user32 = ctypes.WinDLL('user32')
    SystemParametersInfo = user32.SystemParametersInfoW
    SystemParametersInfo.argtypes = ctypes.c_uint,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint
    SystemParametersInfo.restype = wintypes.BOOL
    SystemParametersInfo(
        SPI_SETDESKWALLPAPER, 0, image_path,
        SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE)


class Textbox:
    """
    Class for adding text to.
    """
    def __init__(self, x, y, w, h, fontsize,
                 titlefontsize=144, color=(255,255,255,),
                 textpad=40):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.fontsize = fontsize
        self.titlefontsize = titlefontsize
        self.color = color
        self.textpad = textpad

    def draw_outline(self, img_draw, width=4):
        draw.line( (self.x, self.y, self.x+self.w, self.y),
            fill=self.color, width=width )
        draw.line( (self.x, self.y, self.x, self.y+self.h),
            fill=self.color, width=width)
        draw.line( (self.x+self.w, self.y, self.x+self.w, self.y+self.h),
            fill=self.color, width=width)
        draw.line( (self.x, self.y+self.h, self.x+self.w, self.y+self.h),
            fill=self.color, width=width)

    def draw_bg(self, img):
        np_img = np.array(img)
        np_img[self.y:self.y+self.h,self.x:self.x+self.w] = (0.75 *
            np_img[self.y:self.y+self.h,self.x:self.x+self.w]).astype(int)
        return Image.fromarray(np_img)

    def draw(self, img, text, font, outline=False, bg=False, toptext=None, lefttext=None):
        if outline:
            self.draw_outline(draw)
        if bg:
            img = self.draw_bg(img)

        draw = ImageDraw.Draw(img)

        if len(text) > 0 :
            if "\n" in text:
                draw.text((self.x+self.textpad, self.y+self.textpad), text,
                          (255,255,255),font=font, spacing=int(self.fontsize*0.5))
            else:
                draw.text((self.x+self.textpad, self.y+self.textpad), text,
                          (255,255,255),font=font)

        if toptext is not None:
            w_, h_ = draw.textsize(toptext,font)
            draw.text((self.x+int(self.w/2 - w_/2), self.y-self.textpad - self.fontsize), toptext,
                  (255,255,255),font=font)
        if lefttext is not None:
            w_, h_ = draw.textsize(lefttext,font)
            draw.text((self.x - w_ - self.textpad, self.y + int(self.h/2 - h_/2)), lefttext,
                  (255,255,255),font=font)


        return img
