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


class BlockTypeEnum(str, enum.Enum):
    type_word = 'type_word'
    true_false = 'true_false'
    multi_choice = 'multi_choice'
    choose_letter = 'choose_letter'
