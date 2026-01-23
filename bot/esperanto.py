def esperanto(vorto):

    suffixes = ('is', 'as', 'os')

    if vorto.endswith(suffixes):
        vorto = vorto[:-2] + "i"

    if vorto.endswith('jn'):
        vorto = vorto[:-2]

    if vorto.endswith('j') and vorto not in {'kaj'}:
        vorto = vorto[:-1]

    if vorto.endswith('n') and vorto not in {'kun', 'sen', 'en', 'nun'}:
        vorto = vorto[:-1]

    vorto = vorto.replace("cx", "ĉ").replace("sx", "ŝ").replace("gx", "ĝ").replace("hx", "ĥ").replace("ux", "ŭ")

    return vorto
