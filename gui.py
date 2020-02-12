import glob
import math
import os
import shutil
import threading
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk

import cv2
import numpy as np
from PIL import Image, ImageTk
from texttable import *

import ninsiki


def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


class main:
    def __init__(self):
        self.iDir = os.path.abspath(os.path.dirname(__file__))
        self.fTyp = [("", "*")]
        self.loadpb = 0
        self.canvasp = 0
        self.photos = []
        self.photos2 = []
        self.photoaddr = []
        self.pages = 0
        self.prewins = 0
        self.camloads = 0
        self.root = tkinter.Tk()
        self.root.title("お年玉システム　ホーム")
        # self.root.geometry("200x300")
        self.root.resizable(0, 0)
        self.root.protocol("WM_DELETE_WINDOW", self.exitroot)

        self.frame1 = tkinter.ttk.LabelFrame(self.root, text="メニュー")
        self.frame2 = tkinter.ttk.Frame(self.frame1)
        self.Button = tkinter.ttk.Button(self.frame2, text='写真から解析', width=14)
        self.Button.grid(column=0, row=0, columnspan=2)
        self.Button.bind("<Button-1>", self.photoload)
        self.Button3 = tkinter.ttk.Button(self.frame2, text='撮影して解析', width=14)
        self.Button3.grid(column=0, row=1, columnspan=2)
        self.Button3.bind("<Button-1>", self.camload)
        self.logtext1 = tkinter.ttk.Label(self.frame1, text=("写真の数", 0, "こ"))
        self.logtext1.pack(side="bottom", anchor="w")

        self.style = tkinter.ttk.Style()
        all_theme = self.style.theme_names()
        print(all_theme)
        men = tkinter.Menu(self.root)
        self.root.config(menu=men)

        menu_file2 = tkinter.Menu(self.root)
        men.add_cascade(label="ファイル", menu=menu_file2)
        menu_file2.add_command(label="写真から解析", command=lambda: self.photoload(None))
        menu_file2.add_command(label="撮影して解析", command=lambda: self.camload(None))
        menu_file2.add_command(label="終了", command=self.exitroot)
        menu_file1 = tkinter.Menu(self.root)
        men.add_cascade(label='テーマ', menu=menu_file1)
        menu_file1.add_command(label='default', command=self.default)
        menu_file1.add_command(label='clam', command=self.clam)
        menu_file1.add_command(label='alt', command=self.alt)
        menu_file1.add_command(label='classic', command=self.classic)

        # frame.grid(row=0,column=0,sticky="ns")
        self.frame1.pack(side="left", fill="y")
        self.frame2.pack()
        self.root.mainloop()

    def photoload(self, event):
        if self.prewins == 0:
            self.prewins = 1
            self.file = tkinter.filedialog.askopenfilenames(filetypes=self.fTyp, initialdir=self.iDir)
            if len(self.file) != 0:
                try:
                    self.Button1.destroy()
                except AttributeError:
                    pass
                try:
                    self.Button2.destroy()
                except AttributeError:
                    pass
                try:
                    self.Button4.destroy()
                except AttributeError:
                    pass
                self.Button.destroy()
                self.Button3.destroy()
                self.reloadcanvas()

                self.pb = tkinter.ttk.Progressbar(
                    self.frame1,
                    orient=tkinter.HORIZONTAL,
                    mode='determinate',
                    length=120)
                self.pb.configure(maximum=10000, value=self.loadpb)
                self.pb.pack(side="bottom", anchor="w")
                self.text = tkinter.StringVar()
                self.loadpb = 0
                self.text.set(("読み込み中:", self.loadpb / 100, "%"))
                self.logtext2 = tkinter.ttk.Label(self.frame1, textvariable=self.text)
                self.logtext2.pack(side="bottom", anchor="w")

                for i in self.file:
                    try:
                        temp = expand2square(Image.open(i), (255, 255, 255))
                        self.photos.append(np.array(temp.resize((100, 100))))
                        self.photos2.append(np.array(temp.resize((600, 600))))
                        self.photoaddr.append(i)
                    except OSError:
                        tkinter.messagebox.showerror('エラー', "対応している写真を選んでください\n" + i + """
        対応しているファイルフォーマット
        BMP  DIB  EPS  GIF  ICNS
        ICO  IM   JPEG J2P  JPX 
        MSP  PCX  PNG  PPM  SGI 
        SPI  TGA  TIFF WEBP XBM 
        BLP  CUR  DCX  DDS  FLI 
        FLC  SPX  FTEX GBR  GD  
        IMT  IPTC NAA  MIC  MPO 
        PCD  PSD  WAL  WMF  XPM
        MCIDAS             PIXAR""")

                    self.loadpb += 10000.0 / len(self.file)
                    self.text.set(("読み込み中:", int(self.loadpb / 100), "%"))
                    self.pb.configure(value=self.loadpb)
                    self.pb.update()

                # root.geometry("620x300")
                self.logtext2.destroy()
                self.pb.destroy()
                self.canvasshow()
                # canvas.place(x=130, y=0, width=500, height=300)
                # canvas.grid(row=0,column=1,sticky="ns")
            self.prewins = 0

    def clam(self):
        self.style.theme_use('clam')

    def alt(self):
        self.style.theme_use('alt')

    def default(self):
        self.style.theme_use('default')

    def exitroot(self):
        if tkinter.messagebox.askyesno("確認", "本当に終了しますか？\nこれまでに行ったすべての変更が消えます。"):
            self.root.destroy()
            self.filel = glob.glob("./phototemp/*")
            for i in self.filel:
                os.remove(i)
            self.filel = glob.glob("./photos/*")
            for i in self.filel:
                os.remove(i)

    def classic(self):
        self.style.theme_use('classic')

    def reloadcanvas(self):
        if self.canvasp == 0:
            self.canvasp = 1
            self.canvas = tkinter.Canvas(self.root, width=500, height=300)
        else:
            self.canvas.destroy()
            self.canvas = tkinter.Canvas(self.root, width=500, height=300)
        self.canvas.pack(side="left", fill="y")

    def back(self, event):
        self.pages -= 1
        self.reloadcanvas()
        self.canvasshow()

    def forward(self, event):
        self.pages += 1
        self.reloadcanvas()
        self.canvasshow()

    def canvasshow(self):
        self.photo = []
        try:
            self.Button1.destroy()
        except AttributeError:
            pass
        try:
            self.Button2.destroy()
        except AttributeError:
            pass
        self.Button.destroy()
        self.Button3.destroy()

        self.canvas.bind('<ButtonPress-1>', self.canvasclick)
        # bar_y = tkinter.ttk.Scrollbar(canvas, orient=tkinter.VERTICAL)
        # bar_y.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        # bar_y.config(command=canvas.yview)
        # canvas.config(yscrollcommand=bar_y.set)
        # canvas.config(scrollregion=(0, 0, 0, math.ceil(len(photos) / 5) * 100))
        # print(pages*15,len(photos))
        self.loadpb = 0
        self.pb = tkinter.ttk.Progressbar(
            self.frame1,
            orient=tkinter.HORIZONTAL,
            mode='determinate',
            length=120)
        self.pb.configure(maximum=10000, value=self.loadpb)
        self.pb.pack(side="bottom", anchor="w")
        self.text = tkinter.StringVar()
        self.text.set(("解析中:", self.loadpb / 100, "%"))
        self.logtext2 = tkinter.ttk.Label(self.frame1, textvariable=self.text)
        self.logtext2.pack(side="bottom", anchor="w")

        for i in range(self.pages * 15, len(self.photos)):
            # print(math.ceil(len(photos) / 5) * 100)
            # for j in range(len(photos[i])):
            #     for k in range(len(photos[i][j])):
            #         color = "#" + hex(photos[i][j][k][0])[2:].rjust(2, "0") + \
            #                 hex(photos[i][j][k][1])[2:].rjust(2, "0") + hex(photos[i][j][k][2])[2:].rjust(2, "0")
            #         xy = (i - pages * 15) % 5 * 100 + k, int((i - pages * 15) / 5) * 100 + j
            #         canvas.create_line(xy, xy, fill=color)
            xy = (i - self.pages * 15) % 5 * 100, int((i - self.pages * 15) / 5) * 100
            self.photo.append(ImageTk.PhotoImage(image=Image.fromarray(self.photos[i])))
            self.canvas.create_image(xy[0], xy[1], image=self.photo[i - self.pages * 15], anchor="nw")
            if len(self.photos) - self.pages * 15 > 15:
                self.loadpb += 10000.0 / 17
            else:
                self.loadpb += 10000.0 / (len(self.photos) - self.pages * 15)
            # print(loadpb)
            self.text.set(("解析中:", int(self.loadpb / 100), "%"))
            self.pb.configure(value=self.loadpb)
            self.pb.update()
            if i - self.pages * 15 > 15:
                break

        self.pb.destroy()
        self.logtext2.destroy()

        if len(self.photos) > 15:
            if self.pages > 0:
                # print(pages)
                self.Button1 = tkinter.ttk.Button(self.frame2, text='<=', width=2)
                self.Button1.grid(column=0, row=3, sticky="w")
                self.Button1.bind("<Button-1>", self.back)
            if self.pages + 1 < math.ceil(len(self.photos) / 15):
                # print(pages+1,math.ceil(len(photos)/15))
                self.Button2 = tkinter.ttk.Button(self.frame2, text='=>', width=2)
                self.Button2.grid(column=1, row=3, sticky="e")
                self.Button2.bind("<Button-1>", self.forward)

        self.Button4 = tkinter.ttk.Button(self.frame2, text='解析する', width=14)
        self.Button4.grid(column=0, columnspan=2, row=2)
        self.Button4.bind("<Button-1>", self.kaiseki)
        self.Button = tkinter.ttk.Button(self.frame2, text='写真から解析', width=14)
        self.Button.grid(column=0, row=0, columnspan=2)
        self.Button.bind("<Button-1>", self.photoload)
        self.Button3 = tkinter.ttk.Button(self.frame2, text='撮影して解析', width=14)
        self.Button3.grid(column=0, row=1, columnspan=2)
        self.Button3.bind("<Button-1>", self.camload)
        self.logtext1.destroy()
        self.logtext1 = tkinter.ttk.Label(self.frame1, text=("写真の数", len(self.photos), "こ"))
        self.logtext1.pack(side="bottom", anchor="w")

    def camload(self, event):
        try:
            self.Button4.destroy()
        except AttributeError:
            pass
        if self.prewins == 0:
            self.prewins = 1
            i = 0
            self.selectcam = 0
            flag = True
            captures = []

            while flag:
                capture = cv2.VideoCapture(i)
                capture.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)
                capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 3000)
                ret, frame = capture.read()
                flag = ret
                if flag:
                    i += 1
                    captures.append(capture)
            print(len(captures))
            self.captures = captures
            for i in self.captures:
                if i != self.captures[self.selectcam]:
                    i.release()
            window = tkinter.Toplevel()
            self.window = window
            self.window.title("撮影して解析")
            self.window.protocol("WM_DELETE_WINDOW", self.destructor)

            self.canvas2 = tkinter.Canvas(window, width=500, height=500)
            self.canvas2.pack()

            self.close_btn = tkinter.ttk.Button(window, text="閉じる", width=14)
            self.close_btn.pack(side="left", anchor="nw")
            self.close_btn.configure(command=self.destructor)

            self.close_btn = tkinter.ttk.Button(window, text="撮影", width=14)
            self.close_btn.pack(anchor="ne")
            self.close_btn.configure(command=self.photograph)

            self.delay = int(1000 / 30)
            self.update()

            self.window.mainloop()

    # キャンバスに表示されているカメラモジュールの映像を
    # 15ミリ秒ごとに更新する
    def update(self):
        _, self.f = self.captures[self.selectcam].read()
        if len(self.captures) != 0:
            self.f = cv2.cvtColor(self.f, cv2.COLOR_BGR2RGB)
            try:
                self.f2 = ninsiki.ninsiki(self.f)[0]
            except IndexError:
                pass
            self.photo2 = ImageTk.PhotoImage(
                image=expand2square(Image.fromarray(self.f2), (255, 255, 255)).resize((500, 500)))
            self.canvas2.create_image(0, 0, image=self.photo2, anchor="nw")

            self.window.after(self.delay, self.update)
        else:
            self.canvas.destroy()
            loadlabel = tkinter.ttk.Label(self.window, text="カメラがありません", font=("", 20))
            loadlabel.pack()

    # Closeボタンの処理
    def destructor(self):
        self.prewins = 0
        self.window.destroy()
        self.captures[self.selectcam].release()
        if len(self.photos2) != 0:
            self.reloadcanvas()
            self.canvasshow()

    def photograph(self):
        self.photo2 = []
        self.window.destroy()
        self.captures[self.selectcam].release()

        self.filen = len(glob.glob("./phototemp/*"))
        Image.fromarray(self.f).save("./phototemp/" + str(self.filen) + ".jpg")
        self.temp = expand2square(Image.fromarray(self.f), (255, 255, 255))
        self.photos.append(np.array(self.temp.resize((100, 100))))
        self.photos2.append(np.array(self.temp.resize((600, 600))))
        self.photoaddr.append("./phototemp/" + str(self.filen) + ".jpg")
        self.prewin = tkinter.Toplevel()
        self.prewin.protocol("WM_DELETE_WINDOW", lambda: self.add(None))
        self.prewin.resizable(0, 0)
        self.prewin.title("確認")
        self.prewin = self.prewin
        loadlabel = tkinter.ttk.Label(self.prewin, text="読み込み中...", font=("", 20))
        loadlabel.pack()
        precanvas = tkinter.Canvas(self.prewin, width=300, height=300)

        self.photo2.append(ImageTk.PhotoImage(image=Image.fromarray(self.photos2[len(self.photos2) - 1])))
        precanvas.create_image(0, 0, image=self.photo2[len(self.photo2) - 1], anchor="nw")
        loadlabel.destroy()
        precanvas.pack()

        removeb1 = tkinter.ttk.Button(self.prewin, text='撮り直す', width=14)
        removeb1.pack(anchor="nw", side="left")
        removeb1.bind("<Button-1>", self.retake)
        removeb2 = tkinter.ttk.Button(self.prewin, text='撮影した画像を消去', width=14)
        removeb2.pack(anchor="nw", side="left")
        removeb2.bind("<Button-1>", self.deleteimg)
        exitb = tkinter.ttk.Button(self.prewin, text='解析リストに追加', width=14)
        exitb.pack(anchor="ne")
        exitb.bind("<Button-1>", self.add)

    def exitprewin(self, event):
        self.prewin.destroy()
        self.prewins = 0
        if len(self.photos2) != 0:
            self.reloadcanvas()
            self.canvasshow()

    def deleteimg(self, event):
        if tkinter.messagebox.askyesno('確認', '本当に消去しますか？'):
            del self.photos[len(self.photos) - 1]
            del self.photos2[len(self.photos2) - 1]
            del self.photoaddr[len(self.photoaddr) - 1]
            self.exitprewin2(None)
            if len(self.photos2) != 0:
                self.reloadcanvas()
                self.canvasshow()

    def retake(self, event):
        if tkinter.messagebox.askyesno('確認', '本当に撮り直しますか？'):
            del self.photos[len(self.photos) - 1]
            del self.photos2[len(self.photos2) - 1]
            del self.photoaddr[len(self.photoaddr) - 1]
            if len(self.photos2) != 0:
                self.reloadcanvas()
                self.canvasshow()
            self.exitprewin2(None)
            self.camload(None)

    def add(self, event):
        self.exitprewin2(None)
        self.reloadcanvas()
        self.canvasshow()

    def canvasclick(self, event):
        print(event.x, event.y)
        self.clickno = math.ceil(event.x / 100) + (math.ceil(event.y / 100) - 1) * 5 + self.pages * 15
        print(self.clickno)
        if self.clickno <= len(self.photos):
            self.thtemp = threading.Thread(target=self.thto, args=(self.photos2[self.clickno - 1],))
            self.thtemp.start()

    def thto(self, img):
        if self.prewins == 0:
            self.prewins = 1
            self.prewin = tkinter.Toplevel()
            self.prewin.resizable(0, 0)
            self.prewin.protocol("WM_DELETE_WINDOW", lambda: self.exitprewin2(None))
            self.prewin.title("プレビュー")
            self.loadlabel = tkinter.ttk.Label(self.prewin, text="読み込み中...", font=("", 20))
            self.loadlabel.pack()
            self.precanvas = tkinter.Canvas(self.prewin, width=600, height=600)

            self.photo2 = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.precanvas.create_image(0, 0, image=self.photo2, anchor="nw")
            self.loadlabel.destroy()
            self.precanvas.pack()

            removeb = tkinter.ttk.Button(self.prewin, text='解析リストから除外', width=14)
            removeb.pack(anchor="nw", side="left")
            removeb.bind("<Button-1>", self.deleteimg2)
            exitb = tkinter.ttk.Button(self.prewin, text='閉じる', width=14)
            exitb.pack(anchor="ne")
            exitb.bind("<Button-1>", self.exitprewin2)

    def exitprewin2(self, event):
        self.prewin.destroy()
        self.prewins = 0

    def deleteimg2(self, event):
        if tkinter.messagebox.askyesno('確認', '本当に除外しますか？'):
            del self.photos[self.clickno - 1]
            del self.photos2[self.clickno - 1]
            del self.photoaddr[len(self.photoaddr) - 1]
            self.exitprewin2(None)
            if len(self.photos) != 0:
                self.reloadcanvas()
                self.canvasshow()
            else:
                self.canvasp = 0
                self.canvas.destroy()

    def stop(self):
        pass

    def selected(self, event):
        th = threading.Thread(target=self.to)
        th.start()

    def to(self):
        time.sleep(0.2)
        for item in self.imgList.selection():
            print(int(item[1:]))
            if self.prewinp == 0:
                self.prewinp = 1
                self.prewinpr = tkinter.Toplevel()
                self.prewinpr.resizable(0, 0)
                self.prewinpr.protocol("WM_DELETE_WINDOW", self.exitprewin3)
                self.prewinpr.title("プレビュー")
                loadlabel = tkinter.ttk.Label(self.prewinpr, text="読み込み中...", font=("", 20))
                loadlabel.pack()
                precanvas = tkinter.Canvas(self.prewinpr, width=600, height=600)

                self.photo2 = ImageTk.PhotoImage(image=Image.fromarray(self.photos2[int(item[1:])-1]))
                precanvas.create_image(0, 0, image=self.photo2, anchor="nw")
                loadlabel.destroy()
                precanvas.pack()

    def exitprewin3(self):
        self.prewinp = 0
        self.prewinpr.destroy()


    def kaiseki(self, event):
        if tkinter.messagebox.askyesno('確認', '本当に解析しますか？'):
            self.filel = glob.glob("./photos/*")
            for i in self.filel:
                os.remove(i)
            self.prewins = 1
            self.prewinp = 0
            self.loadpb = 0.0
            self.loadwin = tkinter.Toplevel()
            self.loadwin.resizable(0, 0)
            self.loadwin.protocol("WM_DELETE_WINDOW", self.stop)
            self.pb = tkinter.ttk.Progressbar(
                self.loadwin,
                orient=tkinter.HORIZONTAL,
                mode='determinate',
                length=120)
            self.pb.configure(maximum=100, value=self.loadpb)
            self.pb.pack(side="bottom", anchor="w")
            self.text = tkinter.StringVar()
            self.text.set(("ファイルのコピー中...", self.loadpb, "%"))
            self.logtext2 = tkinter.ttk.Label(self.loadwin, textvariable=self.text)
            self.logtext2.pack()

            for i in self.photoaddr:
                shutil.copy(i, "./photos")
                self.loadpb += 25 / len(self.photoaddr)
                self.text.set(("ファイルのコピー中...", self.loadpb, "%"))
                self.pb.configure(value=self.loadpb)
                self.pb.update()

            self.text.set(("認識中...", self.loadpb, "%"))
            self.pb.configure(value=self.loadpb)
            self.pb.update()
            self.filel = glob.glob("./photos/*")
            self.kekkap = [["path", "ok?", "number", "tousen"]]
            self.kekka = []
            for i in self.filel:
                temp = ninsiki.run(np.array(Image.open(i)), i)
                temp.append("落選")
                self.kekka.append(temp)
                self.kekkap.append(temp)
                self.loadpb += 50 / len(self.filel)
                self.text.set(("認識中...", self.loadpb, "%"))
                self.pb.configure(value=self.loadpb)
                self.pb.update()

            atarif = open("atari.csv")
            self.atari = atarif.read()
            atarif.close()
            temp = self.atari.split("\n")
            self.atari = []
            l = 0
            for i in temp:
                self.atari.append(i.split(","))
                l += len(i.split(","))
            del self.atari[len(self.atari) - 1]

            for i in range(len(self.kekka)):
                for j in self.atari:
                    for k in range(1, len(j)):
                        if self.kekka[i][2][len(j[k]) * -1:] == j[k]:
                            if self.kekka[i][3] == "落選":
                                self.kekka[i][3] = j[0] + "等賞"
                                print(j[0])
                                self.kekkap[i + 1][3] = j[0] + "等賞"
                            self.loadpb += 25 / (l * len(self.kekka))
                            self.text.set(("認識中...", self.loadpb, "%"))
                            self.pb.configure(value=self.loadpb)
                            self.pb.update()

            table = Texttable()
            table.add_rows(self.kekkap)
            print(table.draw())

            self.loadwin.destroy()
            self.prewin = tkinter.Toplevel()
            self.prewin.title("結果")
            self.prewin.protocol("WM_DELETE_WINDOW", lambda: self.exitprewin2(None))
            self.imgList = tkinter.ttk.Treeview(self.prewin)
            self.imgList.configure(column=(1, 2, 3), show="headings")
            self.imgList.column(1, width=420)
            self.imgList.column(2, width=40)
            self.imgList.column(3, width=40)
            self.imgList.heading(1, text="パス")
            self.imgList.heading(2, text="番号")
            self.imgList.heading(3, text="当選")
            for i in self.kekka:
                self.imgList.insert("", "end", values=(i[0], str(i[2]), i[3]))
            self.imgList.bind("<Button-1>", self.selected)
            self.imgList.pack(anchor="w", fill="x")


if __name__ == '__main__':
    main()
