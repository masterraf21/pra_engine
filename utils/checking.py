def not_exist(a) -> bool:
    try:
        return not a
    except KeyError:
        print("error")
        return True


def exist(a) -> bool:
    try:
        if a == None:
            return False
        return True
    except (KeyError, NameError):
        return False


def key_exists(d: dict, key) -> bool:
    if key in d:
        if not key[d]:
            return False
        return True
    else:
        return False


def key_exists_double(d: dict, key1, key2) -> bool:
    if key1 in d:
        if key2 in d[key1]:
            if d[key1][key2] == None:
                return False
            return True
        else:
            return False
    else:
        return False


def check_list(a) -> bool:
    try:
        return type(a) == list
    except KeyError:
        return False
