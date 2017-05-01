from .component import Component
from managers.echo import EchoService


class Needs(Component):
    def __init__(self, needs, metabolism, maximum_points):
        super().__init__()
        self.needs = needs
        self.metabolism = metabolism
        self.current_points = maximum_points.copy()
        self.maximum_points = maximum_points
        self.tick = 10
        self.last_threshold = maximum_points.copy()

    def update(self):
        if self.tick:
            self.tick -= 1
            return

        self.tick = 10
        for need in self.needs:
            cost = 1 * self.metabolism[need]
            if not self.current_points[need] <= -self.maximum_points[need]:
                self.current_points[need] -= cost

            for threshold, message in need.negative_threshold_messages.items():
                if self.last_threshold[need] > threshold >= self.current_points[need]:
                    EchoService.singleton.standard_context_echo(message=message)
                    self.last_threshold[need] = threshold
                    break

    @classmethod
    def create_standard(cls, metabolism, maximum_points, *args):
        """
        Creates a standard needs component from arguments.
        :param metabolism: int Modifier to drain per minute
        :param maximum_points: int Maximum points pool for needs
        :param args: need All needs to initialize.
        :return: Instance of component
        """
        _metabolism = {}
        _maximum_points = {}
        for need in args:
            _metabolism[need] = metabolism
            _maximum_points[need] = maximum_points

        return Needs(
            needs=args,
            metabolism=_metabolism,
            maximum_points=_maximum_points
        )

