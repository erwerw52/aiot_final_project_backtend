class TimelineDTO:
    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end
        self.text = text

    def to_dict(self):
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text
        }