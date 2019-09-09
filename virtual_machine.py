from operator import itemgetter
import itertools
from message import Message, MessageType
from promise import Promise

class VirtualMachine :

    id = None
    server = None
    in_q = None
    out_qs = {}
    out_servers = {}

    def __init__(self, id,  server_cls, in_q, out_qs, out_servers) :
        self.id = id
        self.in_q = in_q
        self.out_qs = out_qs
        self.server = server_cls(id)
        self.out_servers = out_servers

        # list of servers that the current server depends on.
        dependencies = self.server.get_dependencies()
        self.server.update_client_addresses(VirtualMachine.__create_server_to_output_q_map(out_servers, out_qs, dependencies))


    def start(self) :
        promise_holder = PromiseHolder()
        while True :
            message = self.in_q.get()
            if message.is_stop() :
                return
            if message.is_request() :
                promise = self.execute_rpc(
                    message.payload.service_name,
                    message.payload.method_name,
                    message.payload.request)
                if promise.is_successful() :
                    self.out_qs[message.sender].put(Message(message.request_id, MessageType.RESPONSE, promise.get_result(), self.id))
                else :
                    promise_holder.put_promise(message, promise)
            if message.is_response() :
                incoming_message, result = promise_holder.resolve_request(message.request_id, message.payload)
                if result != None and incoming_message != None:
                    sender = incoming_message.sender
                    incoming_request_id = incoming_message.request_id
                    self.out_qs[sender].put(Message(incoming_request_id, MessageType.RESPONSE, result, self.id))
            if message.is_error() :
                promise_holder.reject_request(message.request_id, message.payload)
        pass

    def execute_rpc(self, service_name, rpc_name, request) :
        return self.server.execute(service_name, rpc_name, request)


    def __create_server_to_output_q_map(out_servers, out_qs, dependencies) :
        return {server:[out_qs[id] for id, server in id_server_pair_group]
                for server, id_server_pair_group
                in itertools.groupby(out_servers.items(), itemgetter(1))
                if server in dependencies}


class PromiseHolder() :

    outgoing_request_id_to_promise_id_map = {}
    promise_id_to_promise_map = {}
    promise_id_to_incoming_message_map = {}

    def put_promise(self, incoming_message, promise) :
        request_ids = promise.get_pending_requests()
        promise_id = Promise.generate_id()
        self.promise_id_to_promise_map[promise_id] = promise
        self.promise_id_to_incoming_message_map[promise_id] = incoming_message
        for request_id in request_ids :
            self.outgoing_request_id_to_promise_id_map[request_id] = promise_id

    def resolve_request(self, request_id, result) :
        promise_id = self.outgoing_request_id_to_promise_id_map[request_id]
        promise = self.promise_id_to_promise_map[promise_id]
        promise = promise.resolve_request(request_id, result)
        self.promise_id_to_promise_map[promise_id] = promise
        if promise.is_successful() :
            incoming_message = self.promise_id_to_incoming_message_map.pop(promise_id)
            self.promise_id_to_promise_map.pop(promise_id)
            self.outgoing_request_id_to_promise_id_map.pop(request_id)
            return (incoming_message, promise.get_result())
        if promise.is_failed() :
            incoming_message = self.promise_id_to_incoming_message_map.pop(promise_id)
            self.promise_id_to_promise_map.pop(promise_id)
            self.outgoing_request_id_to_promise_id_map.pop(request_id)
            return (incoming_message, promise.get_error())
        return (None, None)

    def reject_request(self, request_id, error) :
        raise ValueError("Not implemented, request_id:{0}, error:{1}".format(request_id, error))


