import re
import pandas as pd

path = 'app\data.csv'
reflexiveVerbs = re.compile(u"((ив|ивши|ившись|ыв|ывши|ывшись)|((?<=[ая])(в|вши|вшись)))$")
reflexive = re.compile(u"(с[яь])$")
adjective = re.compile(u"(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|ую|юю|ая|яя|ою|ею)$")
participle = re.compile(u"((ивш|ывш|ующ)|((?<=[ая])(ем|нн|вш|ющ|щ)))$")
verb = re.compile(u"((ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю)|((?<=[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|нно)))$")
noun = re.compile(u"(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$")
r = re.compile(u"^(.*?[аеиоуыэюя])(.*)$")
derivationalVerb= re.compile(u".*[^аеиоуыэюя]+[аеиоуыэюя].*ость?$")
derivational = re.compile(u"ость?$")
superlative = re.compile(u"(ейше|ейш)$")
genitive = re.compile(u"и$")
feminine = re.compile(u"ь$")
doubleVerb = re.compile(u"нн$")


class Analyzer:
    isTrue = False

    
    def __init__(self, text: str, eps = 0.4, coincidences = True):
        self.words = self.prepare(text)
        self.roots = self.analyze()
        if coincidences:
            self.roots = self.coincidences(eps)


    def prepare(self, text: str):
        result = ""
        isLastSpace = True
        for i in range(len(text)):
            if text[i] == " " and not isLastSpace:
                isLastSpace = True
                result += " "
            elif text[i].isalpha() and not re.search(r'[^а-яА-Я]', text[i]):
                if len(result) == 0 and text[i].isupper():
                    result += text[i].lower()
                elif text[i].isupper() and result[-1] != " ":
                    result += " " + text[i].lower()
                else:
                    result += text[i].lower()
                isLastSpace = False
        return list(map(str, result.split(" ")))


    def sortByAlphabet(self, inputStr: str):
        return inputStr[0]


    def coincidences(self, eps: float):
        self.roots = sorted(self.roots, key=self.sortByAlphabet)
        length = len(self.roots)
        index = 1
        while index < length:
            word = self.NOP(self.roots[index-1], self.roots[index])
            if len(word) == 0:
                pass
            elif len(word)/(len(self.roots[index-1]) + len(self.roots[index])) >= eps:
                self.isTrue = True
            index += 1


    def fill_dyn_matrix(self, x, y):
        L = [[0]*(len(y)+1) for _ in range(len(x)+1)]
        for x_i,x_elem in enumerate(x):
            for y_i,y_elem in enumerate(y):
                if x_elem == y_elem:
                    L[x_i][y_i] = L[x_i-1][y_i-1] + 1
                else:
                    L[x_i][y_i] = max((L[x_i][y_i-1],L[x_i-1][y_i]))
        return L


    def NOP(self, x, y):
        L = self.fill_dyn_matrix(x, y)
        LCS = []
        x_i,y_i = len(x)-1,len(y)-1
        while x_i >= 0 and y_i >= 0:
            if x[x_i] == y[y_i]:
                LCS.append(x[x_i])
                x_i, y_i = x_i-1, y_i-1
            elif L[x_i-1][y_i] > L[x_i][y_i-1]:
                x_i -= 1
            else:
                y_i -= 1
        LCS.reverse()
        return LCS


    def analyze(self, eps = 2):
        result = []
        for word in self.words:
            word = word.replace(u'ё', u'е')
            objectMatch = re.match(r, word)
            if objectMatch == None or len(word) <= eps:
                continue
            if objectMatch.groups():
                console = objectMatch.group(1)
                rest = objectMatch.group(2)
                ending = reflexiveVerbs.sub('', rest, 1)
                if rest == ending:
                    rest = reflexive.sub('', rest, 1)
                    ending = adjective.sub('', rest, 1)
                    if ending != rest:
                        rest = participle.sub('', ending, 1)
                    else:
                        ending = verb.sub('', rest, 1)
                        if rest == ending:
                            rest = noun.sub('', rest, 1)
                        else:
                            rest = ending
                else:
                    rest = ending
                rest = genitive.sub('', rest, 1)
                if re.match(derivationalVerb, rest):
                    rest = derivational.sub('', rest, 1)
                if rest == ending:
                    rest = superlative.sub('', rest, 1)
                rest = feminine.sub('', rest, 1)
                if ending == rest:
                    rest = superlative.sub('', rest, 1)
                    rest = doubleVerb.sub(u'н', rest, 1)
                else:
                    rest = ending
                word = console + rest
            result.append(word)
        return result


def function(text: str):
    df = pd.read_csv(path)
    for vacancy_id in range(len(df['description'])):
        if vacancy_id >= 250:
            break
        if len(df['description'][vacancy_id]) <= 30:
            continue
        count = 0
        for i in list(map(str, text.split(" "))):
            for j in list(map(str, df['description'][vacancy_id].split(" "))):
                test = Analyzer(j + " " + i)
                if test.isTrue:
                    count += 1
        if count == 0:
            continue
        elif len(list(map(str, text.split(" "))))/count < 3.0:
            return [df['description'][vacancy_id], df['url'][vacancy_id]]
    return ['Ничего не найдено по данному запросу', None]