class TextTemplates:
    SPEECH_REQUEST_TEMPLATE = (
        'Part 1:\n'
        '{q_a_part_1}\n'
        'Part 2:\n'
        '{q_a_part_2}\n'
        'Part 3:\n'
        '{q_a_part_3}'
    )


class NeuralNetworkConstants:
    predict_params = [
        'gr_Clear and correct grammar',
        'ta_Relevant & specific examples',
        'ta_Complete response',
        'ta_Clear & comprehensive ideas',
        'cc_Supported main points',  #
        'cc_Logical structure',
        'cc_Introduction & conclusion present',
        'cc_Variety in linking words',
        'cc_Accurate linking words'
    ]
