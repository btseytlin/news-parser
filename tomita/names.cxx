#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S     // указываем корневой нетерминал грамматики

PersonName -> Word<h-reg1, nc-agr[1]>+ Word<h-reg1, nc-agr[1]> | Word<h-reg1, nc-agr[1]> Word<l-reg, nc-agr[1]>*;
S -> PersonName interp (PersonName.Name);
//FullName -> FirstName<rt, gnc—agr[1]> Word<h—reg1, gnc—agr[1]>* | Word<h—reg1, gnc—agr[1]>* FirstName<rt, gnc—agr[1]> 