from mpi4py import MPI

import team
from team import Proces, Message

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def send(state, message, dest):
    team.clock_l += 1
    data = {
        'state': state,
        'message_type': message,
        'src': rank,
        'ln': team.ln,
        'priority': team.clock_l
    }
    comm.send(data, dest=dest)


def max_clock(received_clock):
    team.clock_l = team.clock_l if team.clock_l > received_clock else received_clock


def receive_message():
    state = Proces.Init
    request = comm.irecv(source=MPI.ANY_SOURCE)
    while state != Proces.Finished:
        status = request.test()
        if status[0]:
            data = status[1]
            team.messages.append(data)
            max_clock(data['priority'])
            state = data['state']
            if Message.Req == data['message_type']:
                send(state=state, message=Message.Ack, dest=data['src'])
            request = comm.irecv(source=MPI.ANY_SOURCE)

    print('receive_message - WYJSCIE, rank: {}'.format(rank))
