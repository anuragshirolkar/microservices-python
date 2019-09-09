from multiprocessing import Process, Pipe, Queue
import time


def my_process(id, incoming_conn, outgoing_conns) :
    for out_id, outgoing_conn in outgoing_conns.items() :
        print("{0}: sending request from {1} to {2}".format(id, id, out_id))
        outgoing_conn.put(["request", id, out_id])
    for i in range(4) :
        data = incoming_conn.get()
        if data[0] == "request" :
            print("{0}: received request from {1} to {2}".format(id, data[1], data[2]))
            outgoing_conns[data[1]].put(["response", id, data[1]])
        else :
            print("{0}: recieved response from {1} to {2}".format(id, data[1], data[2]))


if __name__ == '__main__':
    q0 = Queue()
    q1 = Queue()
    q2 = Queue()

    p0 = Process(target=my_process, args=(0, q0, {1:q1, 2:q2}))
    p1 = Process(target=my_process, args=(1, q1, {0:q0, 2:q2}))
    p2 = Process(target=my_process, args=(2, q2, {0:q0, 1:q1}))

    p0.start()
    p1.start()
    p2.start()

    time.sleep(1)

    p0.join()
    p1.join()
    p2.join()
