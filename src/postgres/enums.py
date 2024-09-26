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
    true_false = 'true_false'
    match_headings = 'match_headings'
    match_notions = 'match_notions'
    complete_sentence = 'complete_sentence'
    one_option_choice = 'one_option_choice'
