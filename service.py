from promise import Promise
from message import Message, MessageType, RequestPayload
import random

class Service :

    server_name = None
    service_name = None
    rpcs = None
    clients = {}

    @classmethod
    def client(cls, client_id) :
       return Client(cls.server_name, cls.service_name, cls.rpcs.keys(), client_id)

    def execute(self, rpc_name, request) :
        return self.rpcs[rpc_name](self, request)


class Client() :

    server_name = None
    service_name = None
    out_qs = []
    client_id = None

    def __init__(self, server, service, methods, client_id):
        self.server_name = server
        self.service_name = service
        self.client_id = client_id
        for method in methods :
            self.__set_method(method)

    def __set_method(self, method_name) :
        def method(request) :
            request_id = random.randint(1000000, 9999999)
            self.out_qs[0].put(
                Message(
                    request_id, MessageType.REQUEST,
                    RequestPayload(self.service_name, method_name, request),
                    self.client_id))
            return Promise.create_pending_rpc_promise(request_id)
        setattr(self, method_name, method)

    def update_addresses(self, out_qs) :
        self.out_qs = out_qs


