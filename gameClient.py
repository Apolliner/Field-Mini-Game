"""
    Тестирование возможности реализации сервера многопользовательской игры через синхронный сервер, изменяющий
    игровой мир, записанный в БД SQLite, ApiServer на основе flask, позволяющее получать данные из БД и записывать в БД,
    а так же клиенты, работающие с ApiServer, выводящие картинку на экран и принимающие изображение экрана.

    Здесь реализуется клиент игры, работающий с API.
"""

import os
import json
import time
import requests
import asyncio
from pathlib import Path
from flask_restful import Resource
import os
import keyboard

def calculation_move_person(position:list, game_field_used:list):
    """
        Спрашивает ввод и рассчитывает местоположение персонажа
        position = [field_position[y, x]]
    """
    displacement_occurred = False
    move = keyboard.read_key()
    if move == 'w' or move == 'up' or move == 'ц':
        if game_field_used[position[0] - 1][position[1]] == '▲':
            pass
        else:
            position[0] -= 1
    elif move == 'a' or move == 'left' or move == 'ф':
        if game_field_used[position[0]][position[1] - 1] == '▲':
            pass
        else:
            position[1] -= 1
    elif move == 's' or move == 'down' or move == 'ы':
        if game_field_used[position[0] + 1][position[1]] == '▲':
            pass
        else:
            position[0] += 1
    elif move == 'd' or move == 'right' or move == 'в':
        if game_field_used[position[0]][position[1] + 1] == '▲':
            pass
        else:
            position[1] += 1
    else: pass
    return position


map = [['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.'],
       ['.','.','.','.','.','.','.','.','.','.']]

def main_loop():
    url = "http://127.0.0.1:5000/base"
    headers = {'Content-Type': 'application/json'}
    raw_answer = requests.post(url, headers=headers)
    #print(F"raw_answer - {raw_answer}")
    answer = json.loads(raw_answer.content)
    position = [answer['y'], answer['x']]
    count = answer['count']
    while True:
        data = {"count": count, "y": position[0], "x": position[1]}
        json_data = json.dumps(data)

        raw_answer = requests.put(url, data=json_data, headers=headers)
        answer = json.loads(raw_answer.content)
        position = [answer['owner']['y'], answer['owner']['x']]
        entity_position_list = list()
        for entity in answer['other']:
            entity_position_list.append([entity['y'], entity['x']])

        position = calculation_move_person(position, map)

        printing_map = ''
        for number_line, line in enumerate(map):
            printing_line = ''
            for number_tile, tile in enumerate(line):
                if [number_line, number_tile] == position:
                    printing_line += '☺' + ' '
                elif [number_line, number_tile] in  entity_position_list:
                    printing_line += '☻' + ' '
                else:
                    printing_line += str(tile) + ' '
            printing_map += printing_line + '\n'
        os.system('cls' if os.name == 'nt' else 'clear')
        print(printing_map)
        time.sleep(0.1)

main_loop()
