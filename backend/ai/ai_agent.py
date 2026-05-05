import ollama as ol
from copy import deepcopy


def culinary_agent_bielik(message):
    model = 'hf.co/speakleash/Bielik-11B-v2.2-Instruct-GGUF:latest'
    response = ol.chat(
        model=model,
        messages=message
    )
    return response


def culinary_agent_gemma(message):
    model = 'gemma4:latest'
    response = ol.chat(
        model=model,
        messages=message
    )
    return response


if __name__ == '__main__':
    ingredients = ["jajka","masło","boczek","szczypiorek","cebula"]
    base = [
{"url":"https:\/\/aniagotuje.pl\/przepis\/jajecznica","recipe_name":"Jajecznica","ingredients":[["3 \u015brednie lub du\u017ce jajka"],["50 g plasterk\u00f3w boczku surowego w\u0119dzonego"],["1 p\u0142aska \u0142y\u017cka mas\u0142a klarowanego - do 10 g"],["ma\u0142a gar\u015b\u0107 szczypiorku"],["ewentualnie szczypta soli i pieprzu"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/jajecznica-z-kurkami","recipe_name":"Jajecznica z kurkami","ingredients":[["400 gram\u00f3w kurek"],["6 du\u017cych jajek (lub wi\u0119cej)"],["3 \u0142y\u017cki mas\u0142a np. klarowanego"],["gar\u015b\u0107 \u015bwie\u017cego koperku"],["\u0142y\u017cka soku z cytryny"],["przyprawy: p\u00f3\u0142 \u0142y\u017ceczki soli, 1\/4 p\u0142askiej \u0142y\u017ceczki pieprzu"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/nalesniki-z-dyni","recipe_name":"Nale\u015bniki z dyni","ingredients":[["pulpa z dyni gotowanej Muscat de Provence","300 g"],["m\u0105ka pszenna tortowa","160 g - 1 szklanka"],["ma\u0142e jajka","3 sztuki - 150 g po rozbiciu"],["mleko","250 ml - 1 szklanka"],["cukier wanilinowy","43 g - saszetka XXL"],["roztopione mas\u0142o lub olej","50 g"],["proszek do pieczenia - mo\u017cna pomin\u0105\u0107","p\u00f3\u0142 \u0142y\u017ceczki"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/drozdzowki-z-morelami","recipe_name":"Dro\u017cd\u017c\u00f3wki z morelami","ingredients":[["4 niepe\u0142ne szklanki m\u0105ki pszennej uniwersalnej - 650 g"],["100 g prawdziwego mas\u0142a - p\u00f3\u0142 klasycznej kostki"],["150 g cukru drobnego"],["4 \u017c\u00f3\u0142tka sporych jajek - oko\u0142o 70 g"],["250 ml mleka - 1 szklanka"],["40 g \u015bwie\u017cych dro\u017cd\u017cy lub 14 g dro\u017cd\u017cy instant"],["6 dojrza\u0142ych, \u015bwie\u017cych moreli"],["80 g m\u0105ki pszennej uniwersalnej - p\u00f3\u0142 szklanki"],["50 g mas\u0142a - 1\/4 klasycznej kostki o wadze 200 g"],["50 g cukru drobnego"],["90 g cukru pudru - nieca\u0142e p\u00f3\u0142 szklanki"],["20 ml \u015bwie\u017co wyci\u015bni\u0119tego soku z cytryny - 2 \u0142y\u017cki"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/placki-z-rabarbarem","recipe_name":"Placki z rabarbarem","ingredients":[["m\u0105ka pszenna tortowa","150 g - 1 szklanka"],["m\u0142ody, \u015bwie\u017cy rabarbar","2 \u0142odygi - oko\u0142o 200 g"],["czerwona konfitura np. z wi\u015bni","1 \u0142y\u017ceczka"],["jogurt naturalny","200 g"],["bardzo du\u017ce jajka","2 sztuki - oko\u0142o 125 g po rozbiciu"],["cukier drobny lub zwyk\u0142y","30 g"],["proszek do pieczenia i soda oczyszczona","po p\u0142askiej \u0142y\u017ceczce"],["olej ro\u015blinny - do sma\u017cenia","25 g"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/kostka-biszkoptowa-z-truskawkami","recipe_name":"Ciasto z galaretk\u0105","ingredients":[["4 \u015brednie jajka"],["1\/4 szklanki drobnego cukru - 70 g"],["3\/4 szklanki m\u0105ki pszennej tortowej - 120 g"],["\u0142y\u017ceczka proszku do pieczenia"],["4 \u0142y\u017cki oleju ro\u015blinnego"],["200 g \u015bmietanki 36% - 200 ml"],["2 \u0142y\u017cki cukru"],["2 \u0142y\u017cki \u017celatyny - nie czubate"],["1\/4 szklanki wrz\u0105tu"],["2 galaretki truskawkowe"],["800 ml wrz\u0105tku"],["500 g truskawek"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/waniliowa-panna-cotta-z-musem-truskawkowym","recipe_name":"Panna cotta","ingredients":[["200 ml \u015bmietanki 30 % - nieca\u0142a szklanka"],["200 ml mleka - nieca\u0142a szklanka"],["50 g cukru waniliowego - 4 \u0142y\u017cki"],["2 ca\u0142kowicie p\u0142askie \u0142y\u017cki \u017celatyny - 14 g"],["50 ml wody"],["200 g truskawek (np. mro\u017cone)"],["\u0142y\u017ceczka miodu lub cukru waniliowego"],["2 \u0142y\u017cki soku z cytryny"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/sernik-dubajski","recipe_name":"Sernik dubajski","ingredients":[["ciastka owsiane pe\u0142noziarniste","200 g"],["mas\u0142o","40-50 g"],["p\u00f3\u0142t\u0142usty lub t\u0142usty twar\u00f3g lub wysokiej jako\u015bci ser twarogowy mielony","1 kg"],["krem pistacjowy s\u0142odzony","200 g"],["\u015bmietanka krem\u00f3wka 30 %","200 ml"],["du\u017ce jajka","3 sztuki - 170 g po rozbiciu"],["cukier drobny","150 g"],["budy\u0144 \u015bmietankowy","1 saszetka - 40 g"],["ciasto kataifi pra\u017cone","200 g"],["krem pistacjowy s\u0142odzony","400 g"],["bia\u0142a czekolada","60 g"],["czekolada mleczna","100 g"],["czekolada gorzka 64%","100 g"],["\u015bmietanka krem\u00f3wka 30 %","100 ml"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/salatka-z-granatem-orzechami-i-szynka-dojrzewajaca","recipe_name":"Sa\u0142atka z szynk\u0105 parme\u0144sk\u0105","ingredients":[["200 g szynki dojrzewaj\u0105cej - lub wi\u0119cej"],["200 g pomidork\u00f3w cherry"],["150 g mieszanki sa\u0142at lub rukoli"],["ma\u0142y owoc granatu - lub melon albo gruszka"],["100 g orzech\u00f3w w\u0142oskich \u0142uskanych lub pekan"],["malutka czerwona cebula - 60 g"],["8 \u0142y\u017cek delikatnej oliwy"],["sok z ma\u0142ej cytryny"],["2 \u0142y\u017ceczki musztardy delikatesowej"],["\u0142y\u017ceczka miodu"],["\u015bwie\u017co mielony pieprz"]]},
{"url":"https:\/\/aniagotuje.pl\/przepis\/paella","recipe_name":"Paella","ingredients":[["400 g ry\u017cu do Paelli lub ry\u017cu do Risotto - ponad 1,5 szklanki (waga przed ugotowaniem)"],["750 ml bulionu\/roso\u0142u drobiowego - 3 szklanki"],["1 filet piersi z kurczaka - oko\u0142o 230 g"],["owoce morza: 425 g mieszanki owoc\u00f3w morza - u mnie mro\u017cona; do 400 g krewetek; 110 g kalmar\u00f3w; 200 g muli"],["120 g mro\u017conego groszku - oko\u0142o 3\/4 szklanki"],["1 \u015bredniej wielko\u015bci cebula - oko\u0142o 200 g"],["1 \u015brednia papryka np. czerwona - oko\u0142o 230 g"],["300 g mi\u0119sistych pomidor\u00f3w - oko\u0142o 2 sztuki"],["4 z\u0105bki czosnku - oko\u0142o 20 g"],["70 g dobrej jako\u015bci oliwy - nieca\u0142a 1\/4 szklanki"],["120 ml bia\u0142ego, wytrawnego wina - nieca\u0142e p\u00f3\u0142 szklanki"],["zio\u0142a i przyprawy: gar\u015b\u0107 natki pietruszki: 1 listek laurowy; po \u0142y\u017ceczce soli i s\u0142odkiej papryki; p\u00f3\u0142 \u0142y\u017ceczki pieprzu; 0,12 g szafranu"],["do podania: cytryna"]]}
            ]


    system_prompt = ("""
    Jesteś botem kulinarnym, którego zadaniem jest znalezienie odpowiedniego przepisu dla użytkownika.
    Muisz ściśle przetrzegać określonych zasad:
    1. Opieraj się wyłącznie na przepisach podanych przez użytkownika.
    2. Dla każdego przepisu na własne potrzeby zdefiniuj najważniejsze składniki, gdy jednego z nich brakuje nie wolno Ci proponować tego przepisu.
    3. Jeżeli nie można zrobić żadnego z dań poinformuj o tym użytkownika.
    4. Gdy znaleziono przepis odpowiedz: 'przepis: 'tytuł'\n link: 'link' '
    5. Gdy nie znaleziono przepisu odpowiedz: Niestety nie możesz wykonać żadnego z przepisów'
    6. Twoje odpowiedzi powinny być maksymalnie krótkie
    """)

    user_text = f"""
        Mam w lodówce: {ingredients}

        Oto przepisy, które znalazłem w mojej bazie:
        ---
        {base}
        ---

        Czy mogę coś z tego ugotować?
        Pod jakim linkiem znajdę przepis?
        """
    message = [{'role': 'system', 'content': system_prompt},
               {'role': 'user', 'content': user_text}]
    for i in range(7):
        print(f"Iteracja {i}")
        res = culinary_agent_gemma(deepcopy(message))
        print(res['message']['content'])
        print("\n")


"""
Jeden z rezultatów

Iteracja 0
przepis: 'Jajecznica'
link: 'https://aniagotuje.pl/przepis/jajecznica'


Iteracja 1
przepis: Jajecznica
link: aniapotuje.pl/przepis/jajecznica


Iteracja 2
przepis: Jajecznica
link: https://aniagotuje.pl/przepis/jajecznica


Iteracja 3
przepis: Jajecznica
link: https://aniagotuje.pl/przepis/jajecznica


Iteracja 4
przepis: Jajecznica
link: 'https://aniagotuje.pl/przepis/jajecznica'


Iteracja 5
przepis: Jajecznica
link: https://aniagotuje.pl/przepis/jajecznica


Iteracja 6
Na podstawie dostępnych składników, najbardziej wykonalnym daniem jest **omlet** (lub jajecznica).

**Składniki użyte:**
*   Jajka
*   Cebula

*(Wszystkie inne składniki, takie jak warzywa, mięso, czy produkty zbożowe, są ilościowo niewystarczające lub niepasujące do stworzenia pełnowartościowego posiłku, ale omlet stanowi najprostsze danie obiadowe z tego zestawu).*"""