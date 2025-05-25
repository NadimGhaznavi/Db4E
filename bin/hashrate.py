#!/usr/bin/env python3

from time import time, sleep
import sys, os
import pygame

# Import DB4E modules
# The directory that this script is in
script_dir = os.path.dirname(__file__)
# DB4E modules are in the lib_dir
lib_dir = script_dir + '/../lib/'
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from MiningDb import MiningDb

class Hashrate:

    def __init__(self):
        self.pygame = pygame
        self.pygame.init()
        self.clock = self.pygame.time.Clock()
        self.font = self.pygame.font.Font('arial.ttf', 25)
        self.display = self.pygame.display.set_mode((800, 600))
        self.pygame.display.set_caption("Hashrate Monitor")

    def exit_clean(self):
        pygame.quit()
        exit()

    def pause(self):
        is_paused = True
        print("Paused")
        print(" - SPACE to resume")
        print(" - Q to quit")
        while is_paused:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.exit_clean()
                if event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_SPACE:
                        is_paused = False
                        print("Resumed")
                    if event.key == self.pygame.K_q:
                        self.exit_clean()

    def update_ui(self):
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.exit_clean
            if event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_p:
                    self.pause()

if __name__ == "__main__":
    hashrate = Hashrate()
    while True:
        hashrate.update_ui()
        sleep(1)
        print("Hashrate updated")