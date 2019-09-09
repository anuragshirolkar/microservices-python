from virtual_machine import VirtualMachine

class Scheduler() :

    virtual_machines = []

    def getResources(self, server, size) :
        for i in range(size) :
            self.virtual_machines.append(VirtualMachine(server))
