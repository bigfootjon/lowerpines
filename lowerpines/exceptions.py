# pyre-strict


class InvalidOperationException(Exception):
    pass


class NoneFoundException(Exception):
    pass


class MultipleFoundException(Exception):
    pass


class GroupMeApiException(Exception):
    pass


class TimeoutException(GroupMeApiException):
    pass


class UnauthorizedException(GroupMeApiException):
    pass
