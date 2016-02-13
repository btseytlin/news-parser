#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

Quoted -> Word<quoted>+[nc-agr]; 
Abbr -> AnyWord<gram="abbr">;
CamelCase -> AnyWord<h-reg2>;

GenericName -> Quoted | Abbr | CamelCase;

Location ->  Noun<h-reg1, nc-agr[1], rt> Word<h-reg1, nc-agr[1]>+ | Noun<h-reg1, nc-agr[1]> Word<l-reg, nc-agr[1]>+;
OtherNamed -> Location | GenericName | Word<h-reg1, kwset=~["имена"]>+[nc-agr];// | GeographicalNamedAfter |  Event;
S -> OtherNamed<kwset=~["имена"], wff=/([^\d\s\t]+\d+[^\d\s\t]+)|(\d+[^\d\s\t]+)|([^\d\s\t]+\d+)|([^\d\s]+)/> interp (EntityName.Name);

