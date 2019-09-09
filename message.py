from enum import Enum

class MessageType() :
    REQUEST = 1
    RESPONSE = 2
    ERROR = 3
    STOP = 4

class Message() :

    request_id = None
    message_type = None
    payload = None
    sender = None

    def __init__(self, request_id, message_type, payload, sender) :
        self.request_id = request_id
        self.message_type = message_type
        self.payload = payload
        self.sender = sender


    def is_request(self) :
        return self.message_type == MessageType.REQUEST

    def is_response(self) :
        return self.message_type == MessageType.RESPONSE

    def is_error(self) :
        return self.message_type == MessageType.ERROR

    def is_stop(self) :
        return self.message_type == MessageType.STOP

class RequestPayload() :

    service_name = None
    method_name = None
    request = None

    def __init__(self, service_name, method_name, request) :
        self.service_name = service_name
        self.method_name = method_name
        self.request = request

    def __str__(self) :
        return "{{service_name:{0}, method_name:{1}, request:{2}}}".format(self.service_name, self.method_name, self.request)

