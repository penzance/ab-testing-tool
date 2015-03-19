from django import template

register = template.Library()


@register.filter(name='lookup_in')
def lookup_in(value, arg):
    """
    This looks up :value: in :arg:, which should be a python dict
    :param value: the key to lookup in the dictionary pointed to by param 'arg'
    :param arg: the python dictionary to lookup param 'value' in
    :return the result of the lookup in the dictionary
    """
    return arg[value]
