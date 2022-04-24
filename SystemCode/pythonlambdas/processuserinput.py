import spacy
import json
import re

nlp = spacy.load('/opt/en_core_web_sm-2.1.0')
with open('data/unit_to_gram_convertion.json', 'r') as f:
    UNITS = json.load(f)
with open('data/nutritions_dict.json', 'r') as f:
    NUTRITIONS_DICT = json.load(f)


def my_preprocessing(raw_sentence): 
    token_sentence = nlp(raw_sentence)
    preprocessed_sentence = []
    for word in token_sentence:
        if not word.is_stop and word.pos_ != 'PUNCT':
            preprocessed_sentence.append(word.lemma_)
    return preprocessed_sentence

def findIngredients(input):
    print(input)
    # input = findAllUnitAndRemoveSpace(input)
    # print(input)
    ingredients = []
    arr_words = my_preprocessing(input)
    print(arr_words)
    finalinput = []
    for i in range(len(arr_words)): 
        w = arr_words[i]
        if i >0:
            lastword = finalinput[len(finalinput) - 1]
            if "{0} {1}".format(lastword,w) in NUTRITIONS_DICT:
                # override lastword
                finalinput[len(finalinput) - 1] = "{0} {1}".format(lastword,w)
                continue
            elif w in UNITS and lastword.isdigit():
                finalinput[len(finalinput) - 1] = "{0} {1}".format(lastword,w)
                continue
        finalinput.append(w)
    print(finalinput)

    for i in range(len(finalinput)):
        w = finalinput[i]
        if w in NUTRITIONS_DICT:
            # check prvious
            if i > 0:
                # check if the previous description is number and unit
                m = re.search(r'^(\d+)(.*)$', finalinput[i-1])
                if m:
                    # find unit
                    # convert unit to gram
                    n = m.group(1).strip()
                    u = m.group(2).strip()
                    nn = n
                    if u in UNITS:
                        nn = int(n) * UNITS[u]
                        print('find ingredient: %s -> %s%s (%sg)' % (w,n,u,nn))
                        ingredients.append({
                            'ingredient': w,
                            'original unit': '{0}{1}'.format(n,u),
                            'in_g': nn,
                        })
                        continue
            print('find ingredient: %s' % w)
    return ingredients

def lambda_handler(event,context):
    ingredients= findIngredients(event["body"])
    return {"statusCode": 200, "body": json.dumps(ingredients)}


# findIngredients("i have 250 kg pork want to make a meal with less than 350 cal")