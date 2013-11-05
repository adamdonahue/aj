"""Sequence utilities."""

def loneItem(items, default=None):
    """Extracts an item from a singleton list, or default if
    the list is empty.  Otherwise throws an exception.

    """
    if items is None:
        return
    if not items:
        return default
    items = list(items)
    if len(items) != 1:
        raise RuntimeError("Not a singleton list")
    return items[0]

def isLoneItem(items):
    """Returns True if the list has exactly one item,
    False otherwise.

    """
    if not items:
        return False
    try:
        loneItem(items)
    except:
        return False
    return True
