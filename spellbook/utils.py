import string


def listformatter(listtoformat):

    FilterCharacters = ["[", "]"]
    for i in FilterCharacters:
        listtoformat = str(listtoformat).replace(i, "")

    if listtoformat.startswith(", "):
        listtoformat = listtoformat[2:]

    if listtoformat.endswith(", "):
        listtoformat = listtoformat[:-2]

    return listtoformat


def processStringToList(spellList):
    return sorted(set(string.capwords(str.lower(x.strip()))
                      for x in spellList.split(",")))
