def localize_text(localized_text, locale='en'):
    """ Get a value from a FRIS LocalizedText object """

    if localized_text is None:
        return None

    for text in localized_text.texts.text:
        if text.locale == locale:
            return text._value_1

    return None