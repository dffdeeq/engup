import enum


class CompetenceEnum(str, enum.Enum):
    writing = 'writing'
    speaking = 'speaking'
    listening = 'listening'
    reading = 'reading'


class PartEnum(str, enum.Enum):
    first = 1
    second = 2
    third = 3


class SubscriptionStatusEnum(str, enum.Enum):
    active = 'active'
    inactive = 'inactive'
