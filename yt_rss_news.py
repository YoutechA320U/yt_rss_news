#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser
import asyncio
from io import BytesIO
from PIL import Image
import PySimpleGUI as sg

#sg.theme("Reddit")

def image_to_data(im):

    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data

def make_background(window, file, main_frame):

    global images

    def find_frames(widget):
        widgets = list(widget.children.values())
        if isinstance(widget, (sg.tk.Frame, sg.tk.LabelFrame)):
            widget.update()
            x, y = widget.winfo_rootx() - x0, widget.winfo_rooty() - y0
            width, height = widget.winfo_width(), widget.winfo_height()
            new_im = im_.crop((x, y, x+width, y+height))
            image = sg.tk.PhotoImage(data=image_to_data(new_im))
            images.append(image)
            label = sg.tk.Label(widget, image=image, padx=0, pady=0, bd=0, bg=bg)
            label.place(x=0, y=0)
            label.lower()
        for widget in widgets:
            find_frames(widget)

    size = window.size
    im_ = Image.open(file).resize(size)
    root = window.TKroot
    widgets = list(root.children.values())
    x0, y0 = root.winfo_rootx(), root.winfo_rooty()

    frame = sg.tk.Frame(root, padx=0, pady=0, bd=0, bg=bg)
    frame.place(x=0, y=0)
    images = []
    image = sg.tk.PhotoImage(data=image_to_data(im_))
    images.append(image)
    label = sg.tk.Label(frame, image=image, padx=0, pady=0, bd=0, bg=bg)
    label.pack()
    main_frame.Widget.master.place(in_=frame, anchor='center', relx=.5, rely=.5)
    frame.lower()
    frame.update()
    for widget in widgets:
        find_frames(widget)
        
bg = sg.theme_background_color()
background_image_file = 'img_data/bg1.png'
w, h = size = 750, 750  # size of background image

sg.set_options(dpi_awareness=True)
import os
if os.name == 'nt':
   txfont = 'Yu Gothic'
   txfontsize =14
   multilinewidth =50
   multilinepad1 = (0,0),(14,0)
   multilinepad2 = (14,0),(20,15)
   winico = ""

else:
   txfont = 'Courier New'
   txfontsize =14
   import simpleaudio
   multilinewidth =46
   multilinepad = (0,0),(14,0)
   winico ='img_data/chara1.png'


frame = [
         [sg.Image(filename = 'img_data/chara1.png', pad=((14,10),(14,330)), key='chara'),sg.Multiline(size=(multilinewidth, 19.4), pad=(multilinepad1), key='-OUT-', font=(txfont, txfontsize), disabled=True, enable_events=True)],
         [sg.Multiline(size=(multilinewidth-6, 6), pad=(multilinepad2),key='-IN-', font=(txfont, txfontsize), enter_submits=False)],
         [sg.Button('読み上げ',size=(10, 2), bind_return_key=True), sg.Button('おわる', size=(10, 2))],
         ]
         
layout=[[sg.Frame('',frame, size=(750, 750), border_width=0, key='FRAME')]]
location = sg.Window.get_screen_size()

window = sg.Window('yt_rss_news', layout, size=(750, 750), icon=winico, finalize=True)
images = []
make_background(window, background_image_file, window['FRAME'])

event, values = window.read(timeout=3)
window['-IN-'].update('http://www.nhk.or.jp/rss/news/cat0.xml')

news =""
task1= ""
task2= ""
reslist = ""
reslen = 0
async def anime():
    global window, reslist, reslen
    while True:
     event, values = window.read(timeout=3)
     await asyncio.sleep(0.05)
     if (reslist !="" and reslist[reslen-1] !="。" and reslist[reslen-1] !="\n" and reslist[reslen-1] !="、"):
        event, values = window.read(timeout=3)
        window['chara'].Update(filename = 'img_data/chara2.png')
        await asyncio.sleep(0.05)
        event, values = window.read(timeout=3)
        window['chara'].Update(filename = 'img_data/chara1.png')
        #await asyncio.sleep(0.01)
     if event in (sg.WIN_CLOSED, 'おわる'):
        window.close()
        break   
     if task2.done() == True:
        window.close()
        break
     
async def box():    
    global reslen, reslist, news
    while True:
      await asyncio.sleep(0.01)
      event, values = window.read(timeout=3)
      if (event == '読み上げ'):
         question = values['-IN-']
         data = feedparser.parse(values['-IN-'])
         for entry in data['entries']:
           news += "・"+ entry['title']+"\n\n"+entry['description']+"\n---------------------\n\n"
         if len(data['entries']) == 0:
            news += "RSSのURLを正しく入力してください" 
         if len(data['entries']) != 0:
            news += "以上で終わります。" 
         reslist = list(news)
         reslen < len(reslist) 
         window['-OUT-'].update('')
         event, values = window.read(timeout=3)
         window['-OUT-'].update('')
         while reslen < len(reslist):
          await asyncio.sleep(0.01)
          event, values = window.read(timeout=3)
          if (reslist[reslen-1] =="。" or reslist[reslen-1] =="\n" or reslist[reslen-1] =="、"):
             if (event == '読み上げ'):
                 reslen =len(reslist)
                 event, values = window.read(timeout=3)
                 window['-OUT-'].update('')
             await asyncio.sleep(0.3)
             if reslen !=len(reslist):
                window['-OUT-'].print(reslist[reslen], end="")
          else:
             if (event == '読み上げ'):
                 reslen =len(reslist)
                 event, values = window.read(timeout=3)
                 window['-OUT-'].update('')
             await asyncio.sleep(0.01)
             if reslen !=len(reslist):
                window['-OUT-'].print(reslist[reslen], end="")
          reslen += 1
          if event in (sg.WIN_CLOSED, 'おわる'):
              window.close()
              break  
         if reslen > 0 and reslen >= len(reslist):
          reslist =""
          news=""
          reslen =0
      if event in (sg.WIN_CLOSED, 'おわる'):
         break     
      if task1.done() == True:
         break

async def main():
    global task1 ,task2
    task1 = asyncio.create_task(anime())
    task2 = asyncio.create_task(box())
    await task1
    await task2

if __name__ == "__main__":
    asyncio.run(main())

