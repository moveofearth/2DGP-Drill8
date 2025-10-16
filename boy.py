from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a
import state_machine

from state_machine import StateMachine


class Idle:

    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.wait_start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        if get_time() - self.boy.wait_start_time > 5:
            self.boy.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        if self.boy.face_dir == 1:  # right
            self.boy.image.clip_draw(self.boy.frame * 100, 300, 100, 100, self.boy.x, self.boy.y)
        else:  # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 200, 100, 100, self.boy.x, self.boy.y)


class Sleep:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        pass

    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 300, 100, 100, 3.141592 / 2, '',
                                               self.boy.x - 25, self.boy.y - 25, 100, 100)
        else:
            self.boy.image.clip_composite_draw(self.boy.frame * 100, 200, 100, 100, -3.141592 / 2, '',
                                                   self.boy.x + 25, self.boy.y - 25, 100, 100)


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e) or right_up(e):
            self.boy.dir = self.boy.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        self.boy.x += self.boy.dir * 5

    def draw(self):
        if self.boy.face_dir == 1:  # right
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y)
        else:  # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y)


class AutoRun:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.dir = 1
        self.boy.run_start_time = get_time()
        pass

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8

        if get_time() - self.boy.run_start_time > 5:
            self.boy.state_machine.handle_state_event(('AUTO_RUN_OVER', None))

        if self.boy.face_dir == 1:
            self.boy.x = min(self.boy.x + 10, 780)
        else:
            self.boy.x = max(self.boy.x - 10, 20)

    def draw(self):
        if self.boy.face_dir == 1:  # right
            self.boy.image.clip_draw(self.boy.frame * 100, 100, 100, 100, self.boy.x, self.boy.y, 300, 300)
        else:  # face_dir == -1: # left
            self.boy.image.clip_draw(self.boy.frame * 100, 0, 100, 100, self.boy.x, self.boy.y, 300, 300)



def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'

def auto_run_over(e):
    return e[0] == 'AUTO_RUN_OVER'


# == time_out = lambda e : e[0] == 'TIME_OUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('animation_sheet.png')

        self.IDLE = Idle(self)
        self.SLEEP = Sleep(self)
        self.RUN = Run(self)
        self.AUTO_RUN = AutoRun(self)
        self.state_machine = StateMachine(
            self.AUTO_RUN,
            {
                self.SLEEP: {space_down: self.IDLE},
                self.IDLE: {time_out: self.SLEEP, right_down: self.RUN, left_down: self.RUN, left_up: self.RUN, right_up: self.RUN},
                self.RUN: {right_up: self.IDLE, left_up: self.IDLE, left_down: self.IDLE, right_down: self.IDLE},
                self.AUTO_RUN: {}
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
