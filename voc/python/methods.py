from ..java import Method as JavaMethod, opcodes as JavaOpcodes

from .blocks import Block
from .opcodes import ASTORE_name, ICONST_val


POSITIONAL_OR_KEYWORD = 1
VAR_POSITIONAL = 2
KEYWORD_ONLY = 3
VAR_KEYWORD = 4

CO_VARARGS = 0x0004
CO_VARKEYWORDS = 0x0008


class Method(Block):
    def __init__(self, parent, name, parameters, returns=None, static=False, commands=None):
        super().__init__(parent, commands=commands)
        self.name = name
        self.parameters = parameters

        if returns is None:
            self.returns = {}
        else:
            self.returns = returns

        self.add_self()
        # Load args and kwargs, but don't expose those names into the localvars.
        self.localvars[None] = len(self.localvars)
        self.localvars[None] = len(self.localvars)
        # Then reserve space for all the *actual* arguments.
        for i, arg in enumerate(self.parameters):
            self.localvars[arg['name']] = len(self.localvars)

        self.static = static

    @property
    def descriptor(self):
        return self.parent.descriptor

    @property
    def signature(self):
        return_descriptor = 'V' if self.returns.get('annotation') is None else 'Lorg/python/Object;'
        return '([Lorg/python/Object;Ljava/util/Hashtable;)%s' % return_descriptor

    def add_self(self):
        pass

    @property
    def method_name(self):
        return self.name

    @property
    def module(self):
        return self.parent

    def tweak(self, code):
        # Delete the 'args' and 'kwargs' from the locals namespace,
        # but move all the content into
        # Load all the arguments into locals
        setup = []
        for i, arg in enumerate(self.parameters):
            setup.extend([
                JavaOpcodes.ALOAD_0(),
                ICONST_val(i),
                JavaOpcodes.AALOAD(),
                ASTORE_name(self.localvars, arg['name']),
            ])

        return self.void_return(setup + code)

    def transpile(self):
        code = super().transpile()

        return JavaMethod(
            self.method_name,
            self.signature,
            static=self.static,
            attributes=[
                code
            ]
        )


class InitMethod(Method):
    def __init__(self, parent, parameters, commands=None):
        super().__init__(
            parent, '__init__',
            parameters=parameters[1:],
            returns={},
            commands=commands
        )

    @property
    def method_name(self):
        return '<init>'

    @property
    def klass(self):
        return self.parent

    @property
    def module(self):
        return self.klass.module

    def add_self(self):
        self.localvars['self'] = 0

    def tweak(self, code):
        # If the block is an init method, make sure it invokes super().<init>
        super_found = False
        for opcode in code:
            if isinstance(opcode, JavaOpcodes.INVOKESPECIAL) and opcode.method.name == '<init>':
                super_found = True
                break

        if not super_found:
            code = [
                JavaOpcodes.ALOAD_0(),
                JavaOpcodes.INVOKESPECIAL(self.klass.superclass, '<init>', '()V'),
            ] + code

        return self.ignore_empty(self.void_return(code))


class MainMethod(Method):
    def __init__(self, parent, commands=None):
        super().__init__(
            parent, '__main__',
            parameters=[{'name': 'args', 'annotation': 'argv'}],
            returns={},
            static=True,
            commands=commands
        )

    @property
    def method_name(self):
        return 'main'

    @property
    def module(self):
        return self.parent

    @property
    def signature(self):
        return '([Ljava/lang/String;)V'

    def tweak(self, code):
        return self.ignore_empty(
            self.void_return(code)
        )


def extract_parameters(code):
    pos_count = code.co_argcount
    arg_names = code.co_varnames
    positional = arg_names[0: pos_count]
    keyword_only_count = code.co_kwonlyargcount
    keyword_only = arg_names[pos_count:pos_count + keyword_only_count]
    annotations = {}  # func.__annotations__
    defs = None  # func.__defaults__
    kwdefaults = None  # func.__kwdefaults__

    if defs:
        pos_default_count = len(defs)
    else:
        pos_default_count = 0

    parameters = []

    # Non-keyword-only parameters w/o defaults.
    non_default_count = pos_count - pos_default_count
    for name in positional[0: non_default_count]:
        parameters.append({
            'name': name,
            'annotation': annotations.get(name),
            'kind': POSITIONAL_OR_KEYWORD
        })

    # ... w/ defaults.
    for offset, name in enumerate(positional[non_default_count: len(positional)]):
        parameters.append({
            'name': name,
            'annotation': annotations.get(name),
            'kind': POSITIONAL_OR_KEYWORD,
            'default': defs[offset]
        })

    # *args
    if code.co_flags & CO_VARARGS:
        name = arg_names[pos_count + keyword_only_count]
        annotation = annotations.get(name)
        parameters.append({
            'name': name,
            'annotation': annotation,
            'kind': VAR_POSITIONAL
        })

    # Keyword-only parameters.
    for name in keyword_only:
        default = None
        if kwdefaults is not None:
            default = kwdefaults.get(name)

        parameters.append({
            'name': name,
            'annotation': annotations.get(name),
            'kind': KEYWORD_ONLY,
            'default': default
        })

    # **kwargs
    if code.co_flags & CO_VARKEYWORDS:
        index = pos_count + keyword_only_count
        if code.co_flags & CO_VARARGS:
            index += 1

        name = arg_names[index]
        parameters.append({
            'name': name,
            'annotation': annotations.get(name),
            'kind': VAR_KEYWORD
        })

    return parameters