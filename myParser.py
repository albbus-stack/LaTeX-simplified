import re


def unrepr(text):
    return eval(text)


def hexint(text):
    return int(text, 16)


class Parser:
    def __call__(self, data, pattern):
        regexp, types = self.compile(pattern)
        match = regexp.match(data)
        if not match:
            raise ValueError
        groups = [data[match.start("Grp%s" % i):match.end("Grp%s" % i)]
                  for i in range(len(types))]
        return tuple(t(g) for t, g in zip(types, groups))

    def compile(self, pattern):
        chars = []
        types = []
        i = 0
        while i < len(pattern):
            if pattern[i] != "%":
                chars.append(pattern[i])
                i += 1
            elif pattern[i+1] == "%":
                chars.append("%")
                i += 2
            elif pattern[i+1] == "s":
                chars.append("(?P<Grp%s>.*?)" % len(types))
                types.append(str)
                i += 2
            elif pattern[i+1] == "r":
                chars.append("(?P<Grp%s>(?P<Par%s>['\"]).*?(?P=Par%s))"
                             % (len(types), len(types), len(types)))
                types.append(unrepr)
                i += 2
            elif pattern[i+1] == "c":
                chars.append("(?P<Grp%s>.)" % len(types))
                types.append(str)
                i += 2
            elif pattern[i+1] == "u":
                chars.append("(?P<Grp%s>[0-9]+)" % len(types))
                types.append(int)
                i += 2
            elif pattern[i+1] in "di":
                chars.append("(?P<Grp%s>[+-]?[0-9]+)" % len(types))
                types.append(int)
                i += 2
            elif pattern[i+1] in "fF":
                chars.append("(?P<Grp%s>[+-]?[0-9]*\.[0-9]*)" % len(types))
                types.append(float)
                i += 2
            elif pattern[i+1] in "xX":
                chars.append("(?P<Grp%s>0[xX]?[0-9A-Fa-f]*)" % len(types))
                types.append(hexint)
                i += 2
            else:
                raise ValueError
        return re.compile("^" + "".join(chars) + "$"), types
