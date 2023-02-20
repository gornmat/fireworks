from enum import Enum


class Proces(Enum):
    Init = 1
    Desk_First_Assignment = 2
    Desk_First_Processing = 3
    Conf_Room_Assignment = 4
    Conf_Room_Processing = 5
    Launch_Zone_Assignment = 6
    Launch_Zone_Processing = 7
    Desk_Second_Assignment = 8
    Desk_Second_Processing = 9
    Finishing = 10
    Finished = 11


class Message(Enum):
    Req = 1
    Ack = 2
    Release = 3


global B            # ilosc biurek
global K            # ilosc sal
global P            # ilosc pol startowych
global ln           # licznosc zespolu
global clock_l      # zegar lamporta
global messages     # sekcja krytyczna
