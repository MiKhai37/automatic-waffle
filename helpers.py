from os import listdir
import csv


def getAvailLangs(dirPath='./static/dictionaries/'):
    """Return available languages"""
    dictFileNames = listdir(dirPath)
    langs = []
    for name in dictFileNames:
        for pos, letter in enumerate(name):
            if letter.isupper():
                firstCapIndex = pos
                break
        langs.append(name[0:firstCapIndex])
    return langs


def createDictionary(lang, dirPath='./static/dictionaries/'):
    """
    Create and return the dictionary in the chosen language
        Parameters:
            lang (string): identifier for chosen language
            dirPath (string): path of the directory where dictionaries are stored
        Returns:
            words (list): the list of words contained into the dictionary
    """
    dictFilenames = listdir(dirPath)
    for name in dictFilenames:
        if name[0:len(lang)] == lang:
            dictPath = dirPath + name
            break

    with open(dictPath, 'r') as dictTxt:
        lines = dictTxt.readlines()
        words = [line[:-1] for line in lines]

    return words


def createDistribution(lang, format='list', dirPath='./static/letterDistributions/'):
    """
    Create and return the letter distribution in the chosen language
        Parameters:
            lang (string): identifier for chosen language
            format (0 or 1): 0 is for list format, 1 is for dict format
            dirPath (string): path of the directory where letter distributions are stored
        Returns:
            distribution (list|dict)
                format='list' : a list representing the letter distribution [letter, count, value]
                format='dict' : a dict representing the letter distribution {letter: {value: value, count: count}}
    """
    distFilenames = listdir(dirPath)
    for name in distFilenames:
        if name[0:len(lang)] == lang:
            distPath = dirPath + name

    with open(distPath, 'r') as distCsv:
        csvReader = csv.reader(distCsv)
        header = next(csvReader)
        if format == 'list':
            distribution = [[row[0].strip(), int(row[2].strip()), int(row[1].strip())] for row in csvReader]
        elif format == 'dict':
            distribution = {row[0].strip(): {header[1].strip(): int(row[1].strip()),
                                     header[2].strip(): int(row[2].strip())} for row in csvReader}
        else:
            print('format invalide')
            return False

    return distribution


# langs = getAvailLangs()
# print(langs)

# words = createDictionary('fr')
# distList = createDistribution('fr', 0)
# distDict = createDistribution('fr', 1)

# print(words)
# print(distList)
# print(distDict)
