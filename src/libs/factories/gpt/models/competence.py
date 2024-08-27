import enum


class Competence(str, enum.Enum):
    writing = 'writing'
    speaking = 'speaking'
    listening = 'listening'
    reading = 'reading'
