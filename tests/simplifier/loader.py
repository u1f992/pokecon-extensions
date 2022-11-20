from Commands.PythonCommandBase import ImageProcPythonCommand

from .sequence import NAME, SEQUENCE


class Loader(ImageProcPythonCommand):

    NAME = NAME

    def __init__(self, cam):
        super().__init__(cam)

    def do(self):
        SEQUENCE.run(self)
