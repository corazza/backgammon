class Result:
    SUCCESS = 0
    FAILURE = 1
    def __init__(self, kind):
        self.kind = kind

    def on_content(self, f):
        raise NotImplementedError()

    def next(self, reason):
        raise NotImplementedError()

    def success(self):
        raise NotImplementedError()
    
    def conditional(a, message):
        if not a:
            return Failure(message)
        else:
            return Success()

class Failure(Result):
    def __init__(self, reason, parent=None):
        self.reason = reason
        self.parent = parent
        super().__init__(Result.FAILURE)

    def on_content(self, f):
        return self

    def next(self, result):
        if result.success():
            return self
        else:
            return Failure(result.reason, parent=self)

    def success(self):
        return False

    def print_reason(self):
        if self.parent is not None:
            self.parent.print_reason()
        print(self.reason)    

class Success(Result):
    def __init__(self, content=None):
        self.content = content
        super().__init__(Result.SUCCESS)

    def success(self):
        return True

    def on_content(self, f):
        return f(self.content)

    def next(self, result):
        return result
        