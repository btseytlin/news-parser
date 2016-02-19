#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

Generic -> Word<gram="~V,~A,~ADV,~APRO,~brev,~poss", ~quoted, h-reg1,wff=/([^\s]{4,})/, gnc-agr[1]> Word<~quoted, h-reg1,wff=/([^\s]{4,})/, gnc-agr[1]>*;
Quoted -> Word<h-reg1, quoted,gnc-agr[1]> Word<quoted,gnc-agr[1]>*;
Abbr -> AnyWord<gram="abbr">;
Geog -> Geo | AnyWord<kwtype='названия_стран'>;
CamelCase -> AnyWord<h-reg2>;

Event -> Noun<h-reg1, gnc-agr[1], rt> Adj<l-reg, gnc-agr[1]> Word<l-reg, gram="род" ,gnc-agr[1]>; // Турнир четырех наций
Event -> Adj<h-reg1, gnc-agr[1]> Noun<gnc-agr[1], rt> Word<gram="~V,~ADV,~A,~ADVPRO,~APRO,~brev,~poss",gnc-agr[1]>* Noun<gnc-agr[1]>; //Мюнхенской конференции по безопасности / Донецкая область / Хорошая конференция удалых молодцов 
Event -> Adj<h-reg1, gnc-agr[1]> Noun<gnc-agr[1], rt>;
GenericName -> Quoted | Abbr | CamelCase;

Location ->  Noun<~quoted, h-reg1, gnc-agr[1], rt> Word<~quoted, h-reg1, gnc-agr[1]>+ | Noun<~quoted, h-reg1, gnc-agr[1]> Word<gram="~V",~quoted, l-reg, gnc-agr[1]>+;
Location -> Adj<h-reg1, gnc-agr[1]> AnyWord<kwtype='маркеры_локаций',gnc-agr[1]>;
Location -> AnyWord<h-reg1, kwtype='маркеры_локаций'> Noun<h-reg1>;
OtherNamed -> Location<wff=/([^\s]{4,})/> | GenericName | Event<wff=/([^\s]{4,})/> | Generic | Geog;// | GeographicalNamedAfter |  Event;
S -> OtherNamed<kwset=~["имена", "стоп_слова"], wff=/([^\d\s]+\d+[^\d\s]+)|(\d+[^\d\s]+)|([^\d\s]+\d+)|([^\d\s]{2,})/> interp (EntityName.Name);

