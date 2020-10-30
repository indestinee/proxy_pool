def check_caller(caller):
    assert len(caller) > 0


def check_pos_int(value):
    assert isinstance(value, int) and value > 0
