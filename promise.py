from enum import Enum
import random

class Promise() :

    state = None

    def create_pending_rpc_promise(request_id) :
        promise = Promise()
        promise.state = PromiseState.PENDING
        promise.request_id = request_id
        return promise

    def create_successful_promise(result) :
        promise = Promise()
        promise.state = PromiseState.SUCCESS
        promise.result = result
        return promise

    def get_result(self) :
        if not self.is_successful() :
            raise ValueError("trying to retrieve result from non successful promise, state:{0}".format(self.state))
        return self.result

    def create_dependent_promise(base_promises, transformation):
        promise = Promise()
        promise.state = PromiseState.DEPENDENT
        promise.base_promises = base_promises
        promise.transformation = transformation
        return promise


    def create_failed_promise(error) :
        promise = Promise()
        promise.state = PromiseState.FAILURE
        promise.error = error
        return promise

    def get_error(self) :
        if not self.is_failed() :
            raise ValueError("trying to retrieve error from non failed promise, state:{0}".format(self.state))
        return self.error

    def then(self, transformation) :
        return Promise.create_dependent_promise([self], transformation)

    def combine(promise1, promise2, combiner_func) :
        return Promise.create_dependent_promise([promise1, promise2], combiner_func)


    def is_resolved(self) :
        if self.state in [PromiseState.SUCCESS, PromiseState.FAILURE]:
            return True
        if self.state == PromiseState.PENDING:
            return False
        return False not in map(Promise.is_resolved, self.base_promises)

    def is_successful(self) :
        return self.state == PromiseState.SUCCESS

    def is_failed(self) :
        return self.state == PromiseState.FAILURE


    def get_pending_requests(self) :
        if self.state in [PromiseState.SUCCESS, PromiseState.FAILURE]:
            return []
        if self.state == PromiseState.PENDING:
            return [self.request_id]
        return list({
            request
            for base_promise in self.base_promises
            for request in base_promise.get_pending_requests()
        })


    def resolve_request(self, request_id, result) :
        if request_id not in self.get_pending_requests() :
            raise ValueError("Request Id mismatch, existing:{0}, resolving:{1}".format(self.request_id, request_id))
        if self.state == PromiseState.PENDING:
            return Promise.create_successful_promise(result)
        if self.state == PromiseState.DEPENDENT :
            for index, base_promise in enumerate(self.base_promises) :
                if request_id in base_promise.get_pending_requests() :
                    self.base_promises[index] = base_promise.resolve_request(request_id, result)
            if self.is_resolved() :
                failed_promises = list(filter(Promise.is_failed, self.base_promises))
                if len(failed_promises) > 0:
                    return failed_promises[0]
                return Promise.create_successful_promise(
                    self.transformation(*list(map(Promise.get_result, self.base_promises))))
            return self
        return self



    def __str__(self) :
        if self.state == PromiseState.SUCCESS :
            return "{{state:SUCCESS, result:{0}}}".format(self.result)
        if self.state == PromiseState.FAILURE :
            return "{{state:FAILURE, error:{0}}}".format(self.error)
        if self.state == PromiseState.PENDING:
            return "{{state:PENDING, request_id:{0}}}".format(self.request_id)
        if self.state == PromiseState.DEPENDENT:
            return "{{state:DEPENDENT, transformation:{0}, base_promises:{1}}}".format(self.transformation, list(map(Promise.__str__, self.base_promises)))
        raise ValueError("Unrecognized PromiseState ({0})".format(self.state))


    def generate_id() :
        return "promise_{0}".format(random.randint(1000000, 9999999))




class PromiseState(Enum) :
    SUCCESS = 1
    FAILURE = 2
    PENDING = 3
    DEPENDENT = 4
