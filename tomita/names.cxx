#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

//PersonName -> Word<h-reg1, gnc—agr[1]>  Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>;
//PersonFirstAndLastName -> Word<h-reg1, gnc-agr[1]> Word<h-reg1, gnc-agr[1]>;
//PersonFirstAndLastName -> (Word<h-reg1, gnc-agr[1]>) Word<h-reg1, gram="имя", gnc-agr[1]> (Word<h-reg1, gnc-agr[1]>);
//PersonFullName -> Word<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]> Word<h-reg1, gnc-agr[1]>;

OneLetter -> Word<h-reg1, wfm=/[^\d\.]{1}/> Punct<wfm=/\./>;
FistName -> Word<~quoted, kwset=~["названия_стран", "стоп_слова"], h-reg1, wfm=/[^\d]{2,}/>;
SecondName -> Word<~quoted, kwset=~["названия_стран", "стоп_слова"],h-reg1, wfm=/[^\d]{2,}/>;
PatrName -> Word<~quoted,kwset=~["названия_стран", "стоп_слова"],h-reg1, wfm=/[^\d]{2,}/>;
FullName -> FistName<rt,gnc-agr[1]> (SecondName<gnc-agr[1]>) (PatrName<gnc-agr[1]>);
FullName -> (SecondName<gnc-agr[1]>) (PatrName<gnc-agr[1]>) FistName<rt,gnc-agr[1]>;
FullName -> SecondName<rt,gnc-agr[1]> (FistName<gnc-agr[1]>) (PatrName<gnc-agr[1]>);
FullName -> (FistName<gnc-agr[1]>) (PatrName<gnc-agr[1]>) SecondName<rt, gnc-agr[1]>;
//DottedName -> FistName<rt> OneLetter+;
//DottedName ->  OneLetter+ SecondName<rt>;
//DottedName ->  SecondName<rt> OneLetter+;

SpecialCase -> Word<rt, gn-agr[1]> 'де'<h-reg1> Word<gn-agr[1]>; // Маттиа Де Шильо
PersonName ->  FullName<wfm=/[^\d]{3,}/> | SpecialCase;// | DottedName;
//PersonName -> Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>;
//PersonName -> Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]> Word<h-reg1, gnc—agr[1]> ;
//Event -> AnyWord<h-reg2> | Noun<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>+ | Noun<h-reg1, gnc—agr[1]> Word<l-reg, gnc—agr[1]>+;
//GeographicalNamedAfter -> Event 'имени' PersonName | Event PersonName<gram="род">;

S -> PersonName<wfm=/([^\d\s]+\d+[^\d\s]+)|(\d+[^\d\s]+)|([^\d\s]+\d+)|([^\d\s\.]{4,})/> interp (EntityName.Name);

