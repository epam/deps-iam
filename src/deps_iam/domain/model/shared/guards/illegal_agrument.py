__all__ = ["IllegalArgument"]


class IllegalArgument(RuntimeError):
    code = "illegal_argument"
