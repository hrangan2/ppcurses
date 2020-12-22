class PPCursesError(Exception):
    pass


class CallFailure(PPCursesError):
    pass


class GracefulExit(PPCursesError):
    pass


class DuplicateKeyDefined(PPCursesError):
    pass


class RootKeyExists(PPCursesError):
    pass


class ApplicationExit(PPCursesError):
    pass
