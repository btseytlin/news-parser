#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

GenericName -> Word<h-reg1, gram="~NUM">+[gnc-agr];
PersonName -> Word<h-reg1, rt, gnc-agr[1], gram="famn">  AnyWord<h-reg1, gnc-agr[1], gram="persn">  AnyWord<h-reg1, gnc-agr[1], gram="patrn"> | AnyWord<h-reg1, gnc-agr[1], gram="famn">  AnyWord<h-reg1, gnc-agr[1], gram="patrn">  Word<h-reg1, rt, gnc-agr[1], gram="persn"> | Word<h-reg1, rt, gnc-agr[1], gram="famn">  Word<h-reg1, gnc-agr[1], gram="persn"> | Word<h-reg1, gnc-agr[1], gram="persn">  Word<h-reg1, rt, gnc-agr[1], gram="famn">;
Event -> Word<h-reg2> | Noun<h-reg2> | Noun<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]>*;
GeographicalNamedAfter -> Event 'имени' PersonName | Event PersonName<gram="род">;
OtherNamed -> GeographicalNamedAfter | Event | GenericName;
S -> OtherNamed<wff=/(\d+[^\d\s\t]+)|([^\d\s\t]+\d+)|([^\d\s]+)/> | PersonName< wff=/(\d+[^\d\s\t]+)|([^\d\s\t]+\d+)|([^\d\s]+)/>;

