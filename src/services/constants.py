from src.postgres.enums import CompetenceEnum


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
    predict_params = {
        CompetenceEnum.speaking: [
            'clear_grammar_result',
            'gr_Complexity of the verb phrase',
            # 'gr_Flexible Use of Complex Structures',
            'lr_Variety of words used',
            # 'lr_Idiomatic Vocabulary or Expressions',
            'fc_Speech rate',
            'fc_Minimal Self-Correction',
            'fc_Relevance of spoken sentences to the general purpose of a turn',
            'fc_Range of Linking Words and Discourse Markers',
            # 'pr_Pronunciation',
        ],
        CompetenceEnum.writing: [
            'clear_grammar_result',
            'ta_Appropriate word count',
            'gr_Complexity of the verb phrase',  # changed from "gr_Mix of complex & simple sentences"
            'lr_Varied vocabulary',
            'lr_Accurate spelling & word formation',
            'ta_Relevant & specific examples',
            'ta_Complete response',
            'ta_Clear & comprehensive ideas',
            'cc_Supported main points',  #
            'cc_Logical structure',
            'cc_Introduction & conclusion present',
            'cc_Variety in linking words',
            'cc_Accurate linking words'
        ],
        'to_load': [
            'ta_Relevant & specific examples',
            'ta_Complete response',
            'ta_Clear & comprehensive ideas',
            'cc_Supported main points',
            'cc_Logical structure',
            'cc_Introduction & conclusion present',
            'cc_Variety in linking words',
            'cc_Accurate linking words'
        ]
    }
