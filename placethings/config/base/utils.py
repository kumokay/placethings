from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def time_str_to_ms(time_repr_str):
    """
    Args:
        time_repr_str (str): e.g. 100sec, 10ms; float is not allowed
    Returns:
        num (int): ms
    """
    is_parsing_unit = False
    num = 0
    cnt = 0
    for ch in time_repr_str:
        if ch.isdigit():
            assert is_parsing_unit is False
            num = num * 10 + int(ch)
            cnt += 1
        else:
            break
    unit_str = time_repr_str[cnt:].lower()
    if unit_str == 'min':
        num *= 60 * 1000
    elif unit_str == 'sec':
        num *= 1000
    elif unit_str == 'ms':
        num *= 1
    else:
        assert False
    return num


def size_str_to_bits(byte_repr_str):
    """
    Args:
        byte_repr_str (str): e.g. 100MB, 10Kb; float is not allowed
    Returns:
        num (int): bytes
    """
    is_parsing_unit = False
    num = 0
    cnt = 0
    for ch in byte_repr_str:
        if ch.isdigit():
            assert is_parsing_unit is False
            num = num * 10 + int(ch)
            cnt += 1
        else:
            break
    unit_str = byte_repr_str[cnt:]
    cnt = 0
    for ch in unit_str:
        cnt += 1
        if ch.lower() == 'k':
            num = num * 1024
        elif ch.lower() == 'm':
            num = num * 1024 * 1024
        elif ch.lower() == 'g':
            num = num * 1024 * 1024 * 1024
        elif ch == 'B':
            num = num * 8
            assert cnt == len(unit_str)
        elif ch == 'b':
            num = num * 1
            assert cnt == len(unit_str)
        else:
            # invalid format
            assert(False)
    return num
