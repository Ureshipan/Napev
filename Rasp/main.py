__all__ = ['main']
#bruh
import pyaudio
import pydub
import wave

import io

import pygame
import pygame_menu

import os

from tinytag import TinyTag

from PIL import Image

from threading import Thread

pydub.AudioSegment.converter = r"ffmpeg-2021-11-15-git-9e8cdb24cd-full_build\bin\ffmpeg.exe"
CHUNK = 1024
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
pygame.init()
pygame.mixer.init()
info = pygame.display.Info()
FPS = 30
width = info.current_w
height = info.current_h
WINDOW_SIZE = (width, height)
font_size = 25
start_pos = 0
rec = False
bar = None
load = True
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)

theme_menu = pygame_menu.themes.THEME_DARK.copy()
theme_menu.widget_font_size = font_size

menu = pygame_menu.Menu(
    height=height,
    onclose=pygame_menu.events.EXIT,
    theme=theme_menu,
    title='Выберете трек',
    width=width,
    mouse_motion_selection=True
)


def make_long_menu(load_bar):
    global load, menu
    load = True

    path = 'mp3 music/'
    files = []
    for root, dirs, file in os.walk(path):
        files = file
    for i in range(len(files)):
        files[i] = 'mp3 music/' + files[i]

    pr = 0
    for track in files:
        pr += 1
        print(int(pr / len(files) * 100))
        load_bar.set_value(int(pr / len(files) * 100))
        tag = TinyTag.get(track, image=True)
        f = open('cover.png', 'wb')
        f.write(tag.get_image())
        f.close()
        img_data = tag.get_image()
        img = Image.open(io.BytesIO(img_data))
        obj_for_count = img.load()
        img_for_size = Image.open(io.BytesIO(img_data))
        sq = [0, 0, 0]
        count = img_for_size.size[0] * img_for_size.size[1]

        im_width = img_for_size.size[0]
        im_height = img_for_size.size[1]

        f.close()

        for i in range(im_width):
            for j in range(im_height):
                sq[0] += obj_for_count[i, j][0]  # r
                sq[1] += obj_for_count[i, j][1]  # g
                sq[2] += obj_for_count[i, j][2]  # b

        out = [0, 0, 0]

        out[0] = int(sq[0] / count)
        out[1] = int(sq[1] / count)
        out[2] = int(sq[2] / count)

        print('[{}]: \"{}\" Success'.format(tag.artist, tag.title))
        theme = pygame_menu.themes.THEME_GREEN.copy()
        theme.title_font_size = font_size
        theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
        theme.background_color = out
        track_menu = pygame_menu.Menu(height=height,
                                      onclose=pygame_menu.events.EXIT,
                                      theme=theme,
                                      title='[{}] {}'.format('-'.join(', '.join(tag.artist.split('/')).split(':')),
                                                             '-'.join(', '.join(tag.title.split('/')).split(':'))),
                                      width=width,
                                      columns=3,
                                      rows=[3, 2, 3]
                                      )

        btncol = (out[0] // 2, out[1] // 2, out[2] // 2)
        textcol = (out[0] // 2 + 100, out[1] // 2 + 100, out[2] // 2 + 100)
        track_menu.add.button('Прослушать трек', play_music, track, background_color=btncol, float=False,
                              font_size=font_size, font_color=textcol,
                              selection_color=textcol, border_color=(0, 0, 0))
        track_menu.add.button('>>10>>', ff, background_color=btncol, float=False, font_size=font_size,
                              font_color=textcol, selection_color=textcol, border_color=(0, 0, 0))
        track_menu.add.button('<<10<<', rev, background_color=btncol, float=False, font_size=font_size,
                              font_color=textcol, selection_color=textcol, border_color=(0, 0, 0))
        prbar = track_menu.add.progress_bar('Прогресс записи:', 0, float=False, font_size=font_size,
                                            font_collor=textcol, box_background_color=out)
        track_menu.add.image('cover.png', angle=0, scale=(1, 1), float=False)
        track_menu.add.button('Записать напев', ini_record, track_menu, prbar,  background_color=btncol,
                              float=False, font_size=font_size, font_color=textcol, selection_color=textcol,
                              border_color=(0, 0, 0))
        track_menu.add.button('Прослушать запись', lisn_chant, track_menu, prbar, background_color=btncol,
                              float=False, font_size=font_size, font_color=textcol, selection_color=textcol,
                              border_color=(0, 0, 0))
        track_menu.add.button('Удалить запись', del_chant, track_menu, prbar, background_color=btncol,
                              float=False, font_size=font_size, font_color=textcol, selection_color=textcol,
                              border_color=(0, 0, 0))

        menu.add.button(track_menu.get_title(), track_menu)

    load = False


def play_music(filepath):
    global start_pos
    start_pos = 0
    pygame.mixer.music.load(os.path.join(os.path.abspath(os.curdir), filepath))
    pygame.mixer.music.play()


def ff():
    global start_pos
    oldsongtime = pygame.mixer.music.get_pos()
    change = 10000
    pygame.mixer.stop()
    start_pos += (oldsongtime + change) // 1000
    pygame.mixer.music.play(0, start=start_pos)


def rev():
    global start_pos
    oldsongtime = pygame.mixer.music.get_pos()
    change = 10000
    pygame.mixer.stop()
    start_pos += (oldsongtime - change) // 1000
    pygame.mixer.music.play(0, start=start_pos)


def reco(men):
    if not os.path.exists('chants/' + str(men.get_title()) + '/'):
        os.mkdir('chants/' + str(men.get_title()) + '/')

    wavfilename = 'chants/' + str(men.get_title()) + '/{}.wav'.format(
        len(os.listdir('chants/' + str(men.get_title()) + '/')))

    mp3filename = 'chants/' + str(men.get_title()) + '/{}.mp3'.format(
        len(os.listdir('chants/' + str(men.get_title()) + '/')))

    p = pyaudio.PyAudio()
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=p.get_default_input_device_info()['index'])

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(wavfilename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    print('saving')
    wf.close()

    sound = pydub.AudioSegment.from_wav(wavfilename)
    sound.export(mp3filename, format="mp3")
    os.remove(wavfilename)


def ini_record(men, barx):
    global rec, bar
    if not rec:
        rec = True
        bar = barx

        th = Thread(target=reco, args=(men,))
        th.start()


def lisn_chant(men, barx):
    if barx.get_value() == 100:
        filename = 'chants/' + str(men.get_title()) + '/{}.mp3'.format(
            len(os.listdir('chants/' + str(men.get_title()) + '/')) - 1)
        pygame.mixer.music.load(os.path.join(os.path.abspath(os.curdir), filename))
        pygame.mixer.music.play()


def del_chant(men, barx):
    print('deleting')
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    if barx.get_value() == 100:
        filename = 'chants/' + str(men.get_title()) + '/{}.mp3'.format(
            len(os.listdir('chants/' + str(men.get_title()) + '/')) - 1)
        print(filename)
        os.remove(os.path.join(os.path.abspath(os.curdir), filename))
        barx.set_value(0)


def main(test=False):
    global rec

    clock = pygame.time.Clock()

    loading = pygame_menu.Menu(
        height=height,
        onclose=pygame_menu.events.EXIT,
        theme=theme_menu,
        title='Подождите, идёт загрузка треков',
        width=width
    )

    load_progress = loading.add.progress_bar('', font_size=(font_size + 10), progress_text_font_color=(0, 0, 0),
                                             width=(width - 300))
    load_tr = Thread(target=make_long_menu, args=(load_progress, ))
    load_tr.start()

    tick = 0
    while load:
        clock.tick(FPS)
        loading.mainloop(
            surface=screen,
            disable_loop=True,
            fps_limit=FPS
        )

        pygame.display.flip()

    loading.add.button('Начать', menu)

    while True:

        clock.tick(FPS)

        tick += 1
        if tick % 3 == 0:
            if rec:
                bar.set_value(bar.get_value() + 1)
                if bar.get_value() == 100:
                    rec = False
            if tick == 30:
                tick = 0

        loading.mainloop(
            surface=screen,
            disable_loop=True,
            fps_limit=FPS
        )

        pygame.display.flip()

        if test:
            break


if __name__ == '__main__':
    main()
