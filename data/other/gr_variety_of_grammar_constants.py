GR_VARIETY_OF_GRAMMAR_CONJUNCTIONS = r'\b(and|but|or|nor|for|so|yet|because|although|since|unless|until|while|whereas|as|if|when|before|after|once|that|who|whom|which|whose|whomever|whoever|whatever|whichever)\b'
GR_VARIETY_OF_GRAMMAR_TENSES = {
    'present_simple': r'\b(am|is|are|do|does|has|have)\b',
    'present_continuous': r'\b(am|is|are) \w+ing\b',
    'past_simple': r'\b(was|were|did|had)\b',
    'past_continuous': r'\b(was|were) \w+ing\b',
    'present_perfect': r'\b(has|have) \w+ed\b',
    'past_perfect': r'\bhad \w+ed\b',
    'future_simple': r'\b(will|shall)\b',
    'future_continuous': r'\b(will be|shall be) \w+ing\b',
    'future_perfect': r'\b(will have|shall have) \w+ed\b'
}

GR_VARIETY_OF_GRAMMAR_WEIGHTS = {
    'present_simple': 1,
    'present_continuous': 2,
    'past_simple': 2,
    'past_continuous': 2,
    'present_perfect': 2,
    'past_perfect': 3,
    'future_simple': 2,
    'future_continuous': 2,
    'future_perfect': 3
}
