from mpi4py import MPI
import team
from team import Proces, Message
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
one_repeat_true_infinite_loop_false = True


def clock_increment():
    team.clock_l += 1


def send(state, message, dest):
    data = {
        'state': state,
        'message_type': message,
        'src': rank,
        'ln': team.ln,
        'priority': team.clock_l
    }
    comm.send(data, dest=dest)


def send_all(state, message):
    clock_increment()
    for i in range(size):
        send(state=state, message=message, dest=i)


def log(state, message):
    print('Proces: {}, Lamport: {}, {}'.format(rank, team.clock_l, message))


def get_messages(state, message_type):
    tmp = []
    for message in team.messages:
        if state == message['state'] and message_type == message['message_type']:
            tmp.append(message)
    return tmp


def filter_messages(state, message_type):
    tmp = get_messages(state, message_type)
    return size == len(tmp)


def verify_releases(state):
    tmp = get_messages(state, Message.Release)
    tmp = [data['src'] for data in tmp]
    return rank in tmp


def verify_Desk_First_Processing():
    requests = get_messages(Proces.Desk_First_Assignment, Message.Req)
    releases = get_messages(Proces.Conf_Room_Assignment, Message.Release)

    requests = sorted(requests, key=lambda d: (d['priority'], d['src']))
    releases = [data['src'] for data in releases]

    requests = [request for request in requests if not (request['src'] in releases)]
    table_sum = 0
    for req in requests:
        if rank == req['src']:
            break
        if team.B >= table_sum + req['ln']:
            table_sum += req['ln']
    return team.B >= table_sum + team.ln


def verify_single_field_request(messages_type, release_type, number_of_available_fields):
    messages = get_messages(messages_type, Message.Req)
    releases = get_messages(release_type, Message.Release)

    messages = sorted(messages, key=lambda d: d['priority'])
    releases = sorted(releases, key=lambda d: d['priority'])

    messages = [data['src'] for data in messages]
    releases = [data['src'] for data in releases]

    for release in releases:
        if release in messages:
            messages.remove(release)

    return rank in messages[:number_of_available_fields]


def main_thread():
    state = Proces.Init
    conf_room_assignment_flag = True
    launch_zone_assignment_flag = True
    desk_second_assignment_flag = True

    while state != Proces.Finished:
        if state == Proces.Init:  # 1
            log(state, 'Ubiegam sie o biurka')
            state = Proces.Desk_First_Assignment
            send_all(state=state, message=Message.Req)

        elif state == Proces.Desk_First_Assignment:  # 2
            if filter_messages(state=state, message_type=Message.Ack):
                clock_increment()
                state = Proces.Desk_First_Processing

        elif state == Proces.Desk_First_Processing:  # 3
            if verify_Desk_First_Processing():
                clock_increment()
                log(state, 'Biore {} biurek'.format(team.ln))
                state = Proces.Conf_Room_Assignment
                send_all(state=state, message=Message.Release)
                log(state, 'Zwalniam {} biurek'.format(team.ln))

        elif state == Proces.Conf_Room_Assignment:  # 4
            if conf_room_assignment_flag and verify_releases(state):
                conf_room_assignment_flag = False
                log(state, 'Ubiegam sie o sale')
                send_all(state=state, message=Message.Req)

            if filter_messages(state=state, message_type=Message.Ack):
                clock_increment()
                state = Proces.Conf_Room_Processing

        elif state == Proces.Conf_Room_Processing:  # 5
            if verify_single_field_request(Proces.Conf_Room_Assignment, Proces.Launch_Zone_Assignment, team.K):
                clock_increment()
                log(state, 'Zajmuje sale')
                state = Proces.Launch_Zone_Assignment
                send_all(state=state, message=Message.Release)
                log(state, 'Zwalniam sale')

        elif state == Proces.Launch_Zone_Assignment:  # 6
            if launch_zone_assignment_flag and verify_releases(state):
                launch_zone_assignment_flag = False
                send_all(state=state, message=Message.Req)
                log(state, 'Ubiegam sie o pole')

            if filter_messages(state=state, message_type=Message.Ack):
                clock_increment()
                state = Proces.Launch_Zone_Processing

        elif state == Proces.Launch_Zone_Processing:  # 7
            if verify_single_field_request(Proces.Launch_Zone_Assignment, Proces.Desk_Second_Assignment, team.P):
                clock_increment()
                log(state, 'Zajmuje pole')
                state = Proces.Desk_Second_Assignment
                send_all(state=state, message=Message.Release)
                log(state, 'Zwalniam pole')

        elif state == Proces.Desk_Second_Assignment:  # 8
            if desk_second_assignment_flag and verify_releases(state):
                desk_second_assignment_flag = False
                send_all(state=state, message=Message.Req)
                log(state, 'Ubiegam sie o biurko')

            if filter_messages(state=state, message_type=Message.Ack):
                clock_increment()
                state = Proces.Desk_Second_Processing

        elif state == Proces.Desk_Second_Processing:  # 9
            if verify_single_field_request(Proces.Desk_Second_Assignment, Proces.Finishing, team.B):
                clock_increment()
                log(state, 'Zajmuje biurko')
                state = Proces.Finishing
                send_all(state=state, message=Message.Release)
                log(state, 'Zwalniam biurko')

        elif state == Proces.Finishing:
            time.sleep(5)
            if one_repeat_true_infinite_loop_false:
                state = Proces.Finished
                send(state=state, message=Message.Req, dest=rank)
            else:
                state = Proces.Init
                team.messages = []
                conf_room_assignment_flag = True
                launch_zone_assignment_flag = True
                desk_second_assignment_flag = True

        elif state == Proces.Finished:
            pass

    print('main_thread - WYJSCIE, rank: {}'.format(rank))
