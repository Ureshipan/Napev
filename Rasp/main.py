__all__ = ['main']

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

pydub.AudioSegment.converter = r"C:\Users\Test\Documents\ffmpeg-2021-11-10-git-44c65c6cc0-full_build\bin\ffmpeg.exe"
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
font_size = 22
rec = False
bar = None
load = True
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)

theme_menu = pygame_menu.themes.THEME_DARK.copy()
theme_menu.widget_font_size = font_size

# Main menu, pauses execution of the application
menu = pygame_menu.Menu(
    height=height,
    onclose=pygame_menu.events.EXIT,
    theme=theme_menu,
    title='Choose track',
    width=width
)


def make_long_menu(load_bar):
    global load, menu
    load = True
    """
    Create a long scrolling menu.
    :return: Menu
    """

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
                                      width=width
                                      )
        track_menu.add.button('Play track', play_music, track, align=pygame_menu.locals.ALIGN_LEFT,
                              background_color=(0, 128, 0), float=False, font_size=font_size, font_color=(0, 0, 0),
                              selection_color=(0, 0, 0), border_color=(0, 0, 0))
        prbar = track_menu.add.progress_bar('Record progress:', 0, float=True, font_size=font_size, font_collor=(0, 0, 0),
                                            box_background_color=out)
        track_menu.add.button('Record the chant', ini_record, track_menu, prbar,
                              align=pygame_menu.locals.ALIGN_RIGHT, background_color=(214, 70, 54),
                              float=True, font_size=font_size, font_color=(0, 0, 0), selection_color=(0, 0, 0),
                              border_color=(0, 0, 0))
        track_menu.add.button('Listen record', lisn_chant, track_menu, prbar,
                              align=pygame_menu.locals.ALIGN_RIGHT, background_color=(154, 205, 50),
                              float=False, font_size=font_size, font_color=(0, 0, 0), selection_color=(0, 0, 0),
                              border_color=(0, 0, 0))
        track_menu.add.button('Delete record', del_chant, track_menu, prbar,
                              align=pygame_menu.locals.ALIGN_RIGHT, background_color=(139, 0, 0),
                              float=False, font_size=font_size, font_color=(0, 0, 0), selection_color=(0, 0, 0),
                              border_color=(0, 0, 0))
        track_menu.add.image('cover.png', angle=0, scale=(1, 1), float=True)

        menu.add.button(track_menu.get_title(), track_menu)

    load = False


def play_music(filepath):
    pygame.mixer.music.load(os.path.join(os.path.abspath(os.curdir), filepath))
    pygame.mixer.music.play()


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
                    input_device_index=1)

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
    """
    Main function.
    :param test: Indicate function is being tested
    :return: None
    """

    clock = pygame.time.Clock()

    # Main menu, pauses execution of the application
    loading = pygame_menu.Menu(
        height=height,
        onclose=pygame_menu.events.EXIT,
        theme=theme_menu,
        title='Подождите, идёт загрузка треков',
        width=width
    )

    load_progress = loading.add.progress_bar('Loading', font_size=(font_size + 10), font_collor=(0, 0, 0))
    load_tr = Thread(target=make_long_menu, args=(load_progress, ))
    load_tr.start()

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    tick = 0
    while load:
        clock.tick(FPS)
        loading.mainloop(
            surface=screen,
            disable_loop=True,
            fps_limit=FPS
        )

        # Update surface
        pygame.display.flip()

    loading.add.button('Начать', menu)

    while True:

        # Tick
        clock.tick(FPS)

        tick += 1
        if tick % 3 == 0:
            if rec:
                bar.set_value(bar.get_value() + 1)
                if bar.get_value() == 100:
                    rec = False
            if tick == 30:
                tick = 0

        # Paint background
        # paint_background(screen)

        # Execute main from principal menu if is enabled
        loading.mainloop(
            surface=screen,
            disable_loop=True,
            fps_limit=FPS
        )

        # Update surface
        pygame.display.flip()

        # At first loop returns
        if test:
            break


if __name__ == '__main__':
    main()
