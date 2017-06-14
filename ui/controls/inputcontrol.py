from settings import ControlColors


class InputControl(object):
    """
    This object is used to catch text input
    """
    def __init__(self, question):
        self.question = question
        self.answer = ""
        self.finished = False

    def handle_input(self, key_events):
        for key_event in key_events:
            if key_event.keychar:
                if key_event.key == "ENTER":
                    self.finished = True
                    return
                if key_event.key == "BACKSPACE":
                    if len(self.answer) > 0:
                        self.answer = self.answer[:-1]
                else:
                    self.answer += key_event.char

    @property
    def text(self):
        return self.question + " " + self.answer

    def render(self, console, active):
        if active:
            color = ControlColors.ACTIVE_CONTROL_COLOR
        else:
            color = ControlColors.INACTIVE_CONTROL_COLOR
        console.setColors(fg=color, bg=ControlColors.BLACK_COLOR)
        console.printStr(self.text)
