
class Server :

    services = {}

    def __init__(self, client_id) :
        pass

    def execute(self, service_name, rpc_name, request) :
        return self.services[service_name].execute(rpc_name, request)

    def get_dependencies(self) :
        return {client.server_name for service in self.services.values() for client in service.clients.values()}
    

    def update_client_addresses(self, out_qs) :
        [client.update_addresses(out_qs[client.server_name]) for service in self.services.values() for client in service.clients.values()]

