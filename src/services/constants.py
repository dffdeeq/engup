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
        'gr_Mix of complex & simple sentences',
        'ta_Relevant & specific examples',
        'ta_Complete response',
        'ta_Clear & comprehensive ideas',
        'lr_Accurate spelling & word formation',
        'lr_Varied vocabulary',
        'cc_Supported main points',  #
        'cc_Logical structure',
        'cc_Introduction & conclusion present',
        'cc_Variety in linking words',
        'cc_Accurate linking words'
    ]
