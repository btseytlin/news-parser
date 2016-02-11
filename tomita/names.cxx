#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

/*
PersonName -> Word<h-reg1, rt, gnc-agr[1]>  AnyWord<h-reg1, gnc-agr[1]>  AnyWord<h-reg1, gnc-agr[1]> | AnyWord<h-reg1, gnc-agr[1]>  AnyWord<h-reg1, gnc-agr[1]>  Word<h-reg1, rt, gnc-agr[1]> | Word<h-reg1, rt, gnc-agr[1]>  Word<h-reg1, gnc-agr[1]> | Word<h-reg1, gnc-agr[1]>  Word<h-reg1, rt, gnc-agr[1]> ;
ProperName -> Word<h-reg2> | Word<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]>*;// | Word<gnc-agr[1]>* Word<h-reg1, gnc-agr[1], rt>;
GenericName ->  Word<h-reg1>+;// Имя собственное
*/
/*
GeographicalNamedAfter -> ProperName 'имени' PersonName | ProperName PersonName<gram="род">;
*/
GenericName -> Word<h-reg1, gnc-agr[1]> Word<h-reg1,gnc-agr[1]>*;
PersonName -> Word<h-reg1, rt, gnc-agr[1]>  AnyWord<h-reg1, gnc-agr[1]>  AnyWord<h-reg1, gnc-agr[1]> | AnyWord<h-reg1, gnc-agr[1]>  AnyWord<h-reg1, gnc-agr[1]>  Word<h-reg1, rt, gnc-agr[1]> | Word<h-reg1, rt, gnc-agr[1]>  Word<h-reg1, gnc-agr[1]> | Word<h-reg1, gnc-agr[1]>  Word<h-reg1, rt, gnc-agr[1]> ;

Event -> Word<h-reg2> | Noun<h-reg2> | Noun<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]>*;// | Word<h-reg1, gnc-agr[1]>* Noun<h-reg1, gnc-agr[1], rt>;
GeographicalNamedAfter -> Event 'имени' PersonName | Event PersonName<gram="род">;
OtherNamed -> GeographicalNamedAfter | Event | GenericName;
S -> OtherNamed | PersonName;// | PersonName | GeographicalNamedAfter ;// | Geographical;//| Geographical | 

//FullName -> FirstName<rt, gnc—agr[1]> Word<h—reg1, gnc—agr[1]>* | Word<h—reg1, gnc—agr[1]>* FirstName<rt, gnc—agr[1]> 