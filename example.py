from service import Service
from server import Server
from virtual_machine import VirtualMachine
from multiprocessing import Queue, Process
from message import Message, MessageType, RequestPayload
from promise import Promise
import time

class ExampleService(Service) :

    example_service_client = None

    def __init__(self, vm_id) :
        self.example_service_client = ExampleService.client(vm_id)
        self.clients['ExampleService'] = self.example_service_client

    def get_factorial(self, n) :
        print('ExampleService.get_factorial has been called with request: {0}'.format(n))
        if n < 2:
            return Promise.create_successful_promise(1)
        return self.example_service_client.get_factorial(n-1).then(lambda fac_n_1: fac_n_1 * n)

    def get_fibonacci(self, n) :
        # print('ExampleService.get_fibonacci has been called with request: {0}'.format(n))
        if n < 2:
            return Promise.create_successful_promise(n)
        return Promise.combine(
            self.example_service_client.get_fibonacci(n-2),
            self.example_service_client.get_fibonacci(n-1),
            lambda fib_n_2, fib_n_1: fib_n_1 + fib_n_2)

    server_name = 'ExampleServer'
    service_name = 'ExampleService'
    rpcs = {
        'get_factorial': get_factorial,
        'get_fibonacci': get_fibonacci,
    }

class ExampleServer(Server) :

    services = {
        'ExampleService':None
    }

    def __init__(self, vm_id) :
        self.services['ExampleService'] = ExampleService(vm_id)

n = int(input())

q = Queue()
master_q = Queue()

vm = VirtualMachine(1, ExampleServer, q, {0:master_q, 1:q}, {0:'MasterServer', 1:'ExampleServer'})


process = Process(target=vm.start, args=())

process.start()

q.put(Message(1234, MessageType.REQUEST, RequestPayload('ExampleService', 'get_fibonacci', n), 0))

print("result:", master_q.get().payload)

print("stopping...")
q.put(Message(None, MessageType.STOP, None, None))


print("joining...")
process.join()

