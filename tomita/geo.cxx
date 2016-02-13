#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

Quoted -> Word<quoted>+[gnc-agr]; 
Abbr -> AnyWord<gram="abbr">;
CamelCase -> AnyWord<h-reg2>;

GenericName -> Quoted | Abbr | CamelCase;

Location ->  Noun<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]>+ | Noun<h-reg1, gnc-agr[1]> Word<l-reg, gnc-agr[1]>+;
//GeographicalNamedAfter -> Event 'имени' PersonName | Event PersonName<gram="род">;

OtherNamed -> Location | GenericName | Word<h-reg1, kwset=~["имена"]>+[gnc-agr];// | GeographicalNamedAfter |  Event;
S -> OtherNamed<kwset=~["имена"], wff=/([^\d\s\t]+\d+[^\d\s\t]+)|(\d+[^\d\s\t]+)|([^\d\s\t]+\d+)|([^\d\s]+)/> interp (EntityName.Name);

