#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

GenericName -> Word<h-reg1, gnc-agr[1]> Word<h-reg1,gnc-agr[1]>*;
PersonName -> Word<h-reg1, rt, gnc-agr[1], gram="фам">  AnyWord<h-reg1, gnc-agr[1], gram="имя">  AnyWord<h-reg1, gnc-agr[1], gram="отч"> | AnyWord<h-reg1, gnc-agr[1], gram="фам">  AnyWord<h-reg1, gnc-agr[1], gram="отч">  Word<h-reg1, rt, gnc-agr[1], gram="имя"> | Word<h-reg1, rt, gnc-agr[1], gram="фам">  Word<h-reg1, gnc-agr[1], gram="имя"> | Word<h-reg1, gnc-agr[1], gram="имя">  Word<h-reg1, rt, gnc-agr[1], gram="фам"> ;

Event -> Word<h-reg2> | Noun<h-reg2> | Noun<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]>*;
GeographicalNamedAfter -> Event 'имени' PersonName | Event PersonName<gram="род">;
OtherNamed -> GeographicalNamedAfter | Event | GenericName;
S -> OtherNamed | PersonName;

