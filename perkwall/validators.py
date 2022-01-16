from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def is_ascii(input_string):
    return all(ord(char) < 128 for char in input_string)


class UnexpectedCharValidator:
    def validate(self, password, user=None):
        if not is_ascii(str(password)):
            raise ValidationError(
                _('The password must contain only English letters, numbers or specials symbols.'),
                code='password_contain_unexpected_character'
            )

    def get_help_text(self):
        return _(
            'The password must contain only English letters, numbers or specials symbols.'
        )