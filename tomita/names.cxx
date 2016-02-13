#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

GenericName -> Word<quoted>+[gnc-agr] | Word<gram="abbr">;
//PersonName -> Word<h-reg1, gnc—agr[1]>  Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>;
//PersonFirstAndLastName -> Word<h-reg1, gnc-agr[1]> Word<h-reg1, gnc-agr[1]>;
//PersonFirstAndLastName -> (Word<h-reg1, gnc-agr[1]>) Word<h-reg1, gram="имя", gnc-agr[1]> (Word<h-reg1, gnc-agr[1]>);
//PersonFullName -> Word<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]> Word<h-reg1, gnc-agr[1]>;

FistName -> Word<h-reg1, gram="имя">;
SecondName -> Word<h-reg1>;
FullName -> FistName<rt,gnc-agr[1]> (SecondName<gnc-agr[1]>);

PersonName -> FullName;
//PersonName -> Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>;
//PersonName -> Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]> Word<h-reg1, gnc—agr[1]> ;
//Event -> AnyWord<h-reg2> | Noun<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>+ | Noun<h-reg1, gnc—agr[1]> Word<l-reg, gnc—agr[1]>+;
//GeographicalNamedAfter -> Event 'имени' PersonName | Event PersonName<gram="род">;

S -> PersonName<wff=/([^\d\s\t]+\d+[^\d\s\t]+)|(\d+[^\d\s\t]+)|([^\d\s\t]+\d+)|([^\d\s]+)/> interp (EntityName.Name);

