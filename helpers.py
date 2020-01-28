def concrete_inc_dec(entry, operand: str):
    """Concrete function to add or substract the value from an input"""
    old_value = entry.get().split()[0]
    value = float(old_value)
    if operand == "+":
        value += 1
    else:
        value -= 1
        if value < 0:
            value = 0
    if value == int(value):
        value = int(value)
    entry.delete(0, "end")
    entry.insert(0, value)