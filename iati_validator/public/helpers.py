def trim(val, max_len):
    if not val or len(val) <= max_len:
        return val
    return val[:max_len - 1] + '…'
