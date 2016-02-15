#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

//PersonName -> Word<h-reg1, gnc—agr[1]>  Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>;
//PersonFirstAndLastName -> Word<h-reg1, gnc-agr[1]> Word<h-reg1, gnc-agr[1]>;
//PersonFirstAndLastName -> (Word<h-reg1, gnc-agr[1]>) Word<h-reg1, gram="имя", gnc-agr[1]> (Word<h-reg1, gnc-agr[1]>);
//PersonFullName -> Word<h-reg1, gnc-agr[1], rt> Word<h-reg1, gnc-agr[1]> Word<h-reg1, gnc-agr[1]>;

FistName -> Word<kwset=~["названия_стран", "стоп_слова"], h-reg1, wff=/[^\d]{2,}/, gram="имя">;
SecondName -> Word<kwset=~["названия_стран", "стоп_слова"],h-reg1, wff=/[^\d]{2,}/>  | Word<kwset=~["названия_стран", "стоп_слова"],h-reg1, wff=/[^\d]{1}/> Punct<wff=/\./>;
PatrName -> Word<kwset=~["названия_стран", "стоп_слова"],h-reg1, wff=/[^\d]{2,}/>  | Word<kwset=~["названия_стран", "стоп_слова"],h-reg1, wff=/[^\d]{1}/> Punct<wff=/\./>;
FullName -> FistName<rt,gnc-agr[1]> (SecondName<gnc-agr[1]>) (PatrName<gnc-agr[1]>);

PersonName -> FullName;
//PersonName -> Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>;
//PersonName -> Word<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]> Word<h-reg1, gnc—agr[1]> ;
//Event -> AnyWord<h-reg2> | Noun<h-reg1, gnc—agr[1], rt> Word<h-reg1, gnc—agr[1]>+ | Noun<h-reg1, gnc—agr[1]> Word<l-reg, gnc—agr[1]>+;
//GeographicalNamedAfter -> Event 'имени' PersonName | Event PersonName<gram="род">;

S -> PersonName<wff=/([^\d\s]+\d+[^\d\s]+)|(\d+[^\d\s]+)|([^\d\s]+\d+)|([^\d\s]{2,})/> interp (EntityName.Name);

