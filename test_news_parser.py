from news_parser import fuzzy_levenshtein, post_process_tomita_facts, parse_tomita_output, get_overlaps, Comparison, NewsMessage, preprocess, pdebug, compile_huge_strs, decompile_huge_strs

import unittest 


_debug = False
stderr_set = True
partial_match_threshold = 0.65

class TestFuzzyMatch(unittest.TestCase):
    def test_exact(self):
        words = ['Эльвира Набиуллина', 'Эльвира Набиуллина']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), True)

    def test_different_form(self):
        words = ['Эльвира Набиуллина', 'Эльвирой Набиуллининой']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), True)

    def test_different(self):
        words = ['Эльвира Набиуллина', 'Банк России']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), False)

    def test_misspel(self):
        words = ['Эльвира Набиуллина', 'Эльвриа Набилулина']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), True)

    def test_exact_letters_moved(self):
        words = ['Эльвира Набиуллина', 'Нал лувниьаабЭриил']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), False)

    def test_different_order(self):
        words = ['Эльвира Набиуллина', 'Набиуллина Эльвира']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), True)

    def test_extra_word(self):
        words = ['Эльвира Набиуллина', 'Набиуллина Эльвира Алексеевна']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), True)

    def test_lacking_word(self):
        words = ['Эльвира Набиуллина', 'Набиуллина']
        self.assertEqual(fuzzy_levenshtein(words[0],words[1]), True)

class TextChunkingAndPatritioning(unittest.TestCase):
    def test_compile_huge_strs(self):
        terminator =  "..[[[___]]]"
        terminator_for_parsing = "[[[___]]]"
        texts = [
        "7 февраля Дом-музей А. Л. Чижевского",
        "169,90руб -6%  11% Четвертина",
        "И вот сейчас при поддержке Г. Г. Фоминой"
        ]
        huge_strs = compile_huge_strs(texts, 2)
        #print(huge_strs)
        should_be = ["7 февраля Дом-музей А. Л. Чижевского"+terminator+"169,90руб -6%  11% Четвертина"+terminator, "И вот сейчас при поддержке Г. Г. Фоминой"+terminator]
        #print(huge_strs)
        self.assertEqual(huge_strs, should_be)

    def test_decompile_huge_strs(self):
        terminator =  "..[[[___]]]"
        terminator_for_parsing = "[[[___]]]"
        output_chunks = ["7 февраля Дом-музей А. Л. Чижевского"+terminator+"169,90руб -6%  11% Четвертина"+terminator, "И вот сейчас при поддержке Г. Г. Фоминой"+terminator]
        source_texts = decompile_huge_strs(output_chunks)
        #print(source_texts)
        should_be =  [
            "7 февраля Дом-музей А. Л. Чижевского..",
            "169,90руб -6%  11% Четвертина..",
            "И вот сейчас при поддержке Г. Г. Фоминой.."
        ]
        self.assertEqual(source_texts, should_be)




class TextProcessing(unittest.TestCase):
    def test_preprocess(self):
        text = "\"      ...7 февраля Дом-музей А. Л. Чижевского приглашает всех калужан и гостей города на День открытых дверей. Вход в музей свободный. \"     "
        clear = "7 февраля Дом-музей А. Л. Чижевского приглашает всех калужан и гостей города на День открытых дверей. Вход в музей свободный."
        self.assertEqual(preprocess(text), clear)

    def test_parse_tomita_output(self):
        text = """
                Курс рубля близок к фундаментальным уровням , риска для финансовой стабильности нет , считает глава российского Центробанка Эльвира Набиуллина 

            S

            {

                Name = курс

            }

            S

            {

                Name = рубль

            }

            A

            {

                Name = близок

            }

            PR

            {

                Name = к

            }

            A

            {

                Name = фундаментальный

            }

            S

            {

                Name = уровень

            }

            S

            {

                Name = риск

            }

            PR

            {

                Name = для

            }

            A

            {

                Name = финансовая

            }

            S

            {

                Name = стабильность

            }

            ADV

            {

                Name = нет

            }

            PART

            {

                Name = нет

            }

            S

            {

                Name = нет

            }

            V

            {

                Name = считать

            }

            S

            {

                Name = глава

            }

            A

            {

                Name = российский

            }

            EntityName

            {

                Name = Центробанк

            }

            EntityName

            {

                Name = Эльвира Набиуллина

            }

        """
        facts_dict = {'EntityName': ['эльвира набиуллина', 'центробанк'], 'ADV': ['нет'], 'V': ['считать'], 'PR': ['к', 'для'], 'A': ['близок', 'фундаментальный', 'финансовая', 'российский'], 'S': ['глава', 'уровень', 'риск', 'стабильность', 'курс', 'рубль']}
        #print(parse_tomita_output(text)['EntityName'])
        dict1 = parse_tomita_output(text)
        dict2 = facts_dict
        diffkeys = [k for k in dict1 if not sorted(dict1[k]) == sorted(dict2[k])] #seek keys that exist in one dict, and not in the other

        self.assertEqual(len(diffkeys)==0, True)

    def test_get_overlaps(self):
        facts1 = {'EntityName': ['эльвира набиуллина', 'центробанк'], 'ADV': ['нет'], 'V': ['считать'], 'PR': ['к', 'для'], 'A': ['близок', 'фундаментальный', 'финансовая', 'российский'], 'S': ['глава', 'уровень', 'риск', 'стабильность', 'курс', 'рубль']}

        facts2 = {'ADV': ['да', 'сейчас'], 'V': ['заявить', 'передавать', 'пойду', 'стать', 'уточнил', 'полагать'], 'EntityName': ['банк россия', 'набиуллин', 'эльвира набиуллина', 'тасс'], 'S': ['рубль', 'курс', 'глава'], 'A': ['обоснованный', 'близок', 'фундаментально', 'текущий', 'должен'], 'APRO': ['этот', 'свой'], 'ADVPRO': ['что', 'куда'], 'PART': ['не'], 'PR': ['к', 'при'], 'CONJ': ['чтобы']}

        overlaps = get_overlaps(facts1, facts2)

        self.assertEqual(overlaps, {'ADV': 0, 'V': 0, 'EntityName': 1, 'S': 3, 'A': 1, 'PR': 1})
        
if __name__ == '__main__':
    unittest.main()
