#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Импортируем библиотеку pygame
import pygame
from pygame import *
from pytmx import load_pygame

#Объявляем переменные
from interface import Interface

WIN_WIDTH = 1100  #Ширина создаваемого окна
WIN_HEIGHT = 600  # Высота
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)  # Группируем ширину и высоту в одну переменную
BACKGROUND_COLOR = "#dddddd"


def main():
    pygame.init()  # Инициация PyGame, обязательная строчка
    screen = pygame.display.set_mode(DISPLAY)  # Создаем окошко
    pygame.display.set_caption("Alert system")  # Пишем в шапку
    clock = pygame.time.Clock()
    fps = 30

    interface = Interface(BACKGROUND_COLOR, DISPLAY)

    while 1:  # Основной цикл программы
        for e in pygame.event.get():  # Обрабатываем события
            if e.type == QUIT:
                raise SystemExit("QUIT")
        interface.update()
        screen.blit(interface.image, (0, 0))  # Каждую итерацию необходимо всё перерисовывать
        pygame.display.update()  # обновление и вывод всех изменений на экран
        clock.tick_busy_loop(fps)


if __name__ == "__main__":
    main()