from random import randint
from threading import Thread
from mpi4py import MPI

import team
from communication_thread import receive_message
from thread import main_thread

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def init():
    team.B = 5
    team.K = 3
    team.P = 2
    team.ln = randint(1, team.B)
    team.clock_l = 0
    team.messages = []


if __name__ == '__main__':
    init()
    th1 = Thread(target=main_thread)
    th2 = Thread(target=receive_message)
    th1.start()
    th2.start()
    th1.join()
    th2.join()
