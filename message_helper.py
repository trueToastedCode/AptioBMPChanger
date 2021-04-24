def print_msg(lines, align='center', decoration=('▱', '', '', '▱')):
    lines = lines.split('\n')
    horizontal_len = max(list(map(lambda s: len(s), lines))) + 2 + len(decoration[1]) + len(decoration[2])
    print(decoration[0] * horizontal_len)
    for line in lines:
        space = horizontal_len - (2 + len(decoration[1]) + len(decoration[2])) - len(line)
        if align == 'center':
            if space % 2 != 0:
                l = int((space - 1) / 2)
                r = l + 1
            else:
                l = int(space / 2)
                r = l
            print(f'{decoration[1]} {" " * l}{line}{" " * r} {decoration[2]}')
        elif align == 'left':
            print(f'{decoration[1]} {line}{" " * space} {decoration[2]}')
        elif align == 'right':
            print(f'{decoration[1]} {" " * space}{line} {decoration[2]}')
    print(decoration[3] * horizontal_len)
