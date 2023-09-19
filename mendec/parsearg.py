from argparse import ArgumentParser, Namespace, Action

try:
    from argparse import BooleanOptionalAction
except ImportError:

    class BooleanOptionalAction(Action):
        def __init__(self, option_strings, **kwargs):
            _option_strings = []
            for option_string in option_strings:
                _option_strings.append(option_string)

                if option_string.startswith("--"):
                    option_string = "--no-" + option_string[2:]
                    _option_strings.append(option_string)

            super().__init__(option_strings=_option_strings, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            if option_string in self.option_strings:
                setattr(namespace, self.dest, not option_string.startswith("--no-"))

        def format_usage(self):
            return " | ".join(self.option_strings)


def _names(args):
    for x in args:
        if not x:
            pass
        elif x.startswith("-"):
            yield x
        elif len(x) > 1:
            yield f"--{x}"
        else:
            yield f"-{x}"


class ArgumentParser(ArgumentParser):
    def flag(self, *args, action="store_true", **kwargs):
        self.add_argument(*_names(args), action=action, **kwargs)
        return self

    def off(self, *args, action="store_false", **kwargs):
        self.add_argument(*_names(args), action=action, **kwargs)
        return self

    def bool(self, *args, action=BooleanOptionalAction, **kwargs):
        self.add_argument(*_names(args), action=action, **kwargs)
        return self

    def param(self, *args, **kwargs):
        self.add_argument(*_names(args), **kwargs)
        return self

    def arg(self, *args, **kwargs):
        args and self.add_argument(args[0], nargs="?", **kwargs)
        return self

    def args(self, *args, **kwargs):
        args and self.add_argument(args[0], nargs="*", **kwargs)
        return self

    def const(self, *args, **kwargs):
        self.add_argument(*_names(args), action="store_const", **kwargs)
        return self

    def append(self, *args, **kwargs):
        self.add_argument(*_names(args), action="append", **kwargs)
        return self

    def append_const(self, *args, **kwargs):
        self.add_argument(*_names(args), action="append_const", **kwargs)
        return self

    def count(self, *args, **kwargs):
        self.add_argument(*_names(args), action="count", **kwargs)
        return self

    def version(self, *args, **kwargs):
        a = list(_names(args)) or ["--version"]
        self.add_argument(*a, action="version", **kwargs)
        return self

    def call(self, fn, **kwargs):
        super().set_defaults(_call=fn)
        return self

    def subparsers(self, *args, **kwargs):
        self._x_subparsers = self.add_subparsers(
            *args, parser_class=self.__class__, **kwargs
        )
        return self

    def parse_sub(self, *args, **kwargs):
        ns = self.parse_args(*args, **kwargs)
        try:
            fn = ns._call
        except AttributeError:
            pass
        else:
            fn(ns)
        return ns

    def sub(self, *args, **kwargs):
        try:
            sp = self._x_subparsers
        except AttributeError:
            self.subparsers()
            sp = self._x_subparsers

        return sp.add_parser(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def ext(self, call, *args, **kwargs):
        call(self, *args, **kwargs)
        return self


class Namespace(Namespace):
    def __getattr__(self, name):
        f = not name.startswith("_get_") and getattr(self, f"_get_{name}", None)
        if f:
            v = f()
            setattr(self, name, v)
            return v
        try:
            m = super().__getattr__
        except AttributeError:
            pass
        else:
            return m(name)
        c = self.__class__
        raise AttributeError(f"{c.__module__}.{c.__qualname__} has no attribute {name}")
