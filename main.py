from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.lang.builder import Builder

import gc
gc.disable()

from kivy.core.window import Window

r = 248 / 255
g = 171 / 255
b = 141 / 255
Window.clearcolor = (r, g, b, 1)

from random import randint
from threading import Thread


class Container(AnchorLayout):

    start_box = ObjectProperty()
    doors = Builder.load_file('./desigh/doors_box.kv')
    end_box = Builder.load_file('./desigh/end_box.kv')

    wins = 0
    losses = 0

    def __init__(self):
        super().__init__()

        self.add_pool()

        self.build_sys_box()

        self.pt: int

        self.start_box.btn_play.bind(
            on_release=self.start_game
        )

        for n in range(1, 4):
            self.doors.ids[f'door{n}'].bind(
                on_release=self.open_door(n)
            )
        
        self.end_box.btn_to_start.bind(
            on_release=self.to_start
        )

        self.end_box.btn_reload.bind(
            on_release=self.reload_game
        )

        self.start_box.btn_sys.bind(
            on_release=self.press_sys(True)
        )


    def __del__(self):
        gc.collect()
        gc.enable()

    def add_pool(self):
        pool = Builder.load_file('./desigh/pool.kv')
        self.start_box.pool_box.pool = pool

        pool.results = [
            '--',
            '--',
            '--',
            '--',
            '--'
        ]

        self.start_box.pool_box.add_widget(
            pool
        )

    def press_sys(self, pt):

        def wrapper(btn):
            self.clear_widgets()

            if pt:
                self.add_widget(self.sys_box)
            else:
                self.add_widget(self.start_box)
        
        return wrapper
    
    def clear_pool(self, btn):
        self.wins = 0
        self.losses = 0

        self.start_box.pool_box.pool.results = [
            '--',
            '--',
            '--',
            '--',
            '--'
        ]

        self.set_res()
        self.set_pool()
    
    def build_sys_box(self):
        sys_box = Builder.load_file('./desigh/settings.kv')
        self.sys_box = sys_box

        sys_box.btn_sys.bind(
            on_release=self.press_sys(False)
        )

        sys_box.clear_pool.bind(
            on_release=self.clear_pool
        )

    def start_game(self, btn):
        self.clear_widgets()
        del self.sys_box
        self.pt = randint(1, 3)
        self.add_widget(self.doors)
    
    def open_door(self, n: int):

        def wrapper(btn):
            res = self.start_box.pool_box.pool.results
            res.pop(0)

            if self.pt == n:
                self.end_box.img.source = './data/cool.jpg'
                self.wins += 1
                res.append('Win')
            else:
                self.end_box.img.source = './data/loser.jpg'
                self.losses += 1
                res.append('Loss')

            self.thr_set_res = Thread(target=self.set_res, daemon=True, name='Set_res')
            self.thr_set_pool = Thread(target=self.set_pool, daemon=True, name='Set_pool')

            self.thr_set_res.start()
            self.thr_set_pool.start()

            self.clear_widgets()
            self.add_widget(self.end_box)
        
        return wrapper

    def reload_game(self, btn):
        self.clear_widgets()
        self.pt = randint(1, 3)
        self.add_widget(self.doors)

    def to_start(self, btn):
        self.thr_set_res.join()
        self.thr_set_pool.join()

        self.build_sys_box()

        self.clear_widgets()
        self.add_widget(self.start_box)
    
    def set_res(self):
        self.start_box.res.text = f'Wins: {self.wins}\nLosses: {self.losses}'

    def set_pool(self):
        pool = self.start_box.pool_box.pool
        results = self.start_box.pool_box.pool.results

        for n, res in enumerate(results, 1):
            pool.ids[f'line{n}'].text = res


class DoorGameApp(App):
    def build(self):
        return Container()


if __name__ == '__main__':
    DoorGameApp().run()
