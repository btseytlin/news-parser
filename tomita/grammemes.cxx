#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT ROOT     // указываем корневой нетерминал грамматики


A -> AnyWord<gram="A", kwset=~["имена"]> interp(A.Name);
ADV -> AnyWord<gram="ADV", kwset=~["имена"]> interp(ADV.Name);
ADVPRO -> AnyWord<gram="ADVPRO", kwset=~["имена"]> interp(ADVPRO.Name);
ANUM -> AnyWord<gram="ANUM", kwset=~["имена"]> interp(ANUM.Name);
APRO -> AnyWord<gram="APRO", kwset=~["имена"]> interp(APRO.Name);
COM -> AnyWord<gram="COM", kwset=~["имена"]> interp(COM.Name);
CONJ -> AnyWord<gram="CONJ", kwset=~["имена"]> interp(CONJ.Name);
INTJ ->  AnyWord<gram="INTJ", kwset=~["имена"]> interp(INTJ.Name);
NUM -> AnyWord<gram="NUM", kwset=~["имена"]> interp(NUM.Name);
PART -> AnyWord<gram="PART", kwset=~["имена"]> interp(PART.Name);
PR -> AnyWord<gram="PR", kwset=~["имена"]> interp(PR.Name);
SPRO ->  AnyWord<gram="SPRO", kwset=~["имена"]> interp(SPRO.Name);
V -> AnyWord<gram="V", kwset=~["имена"]> interp(V.Name);
S -> AnyWord<gram="S", kwset=~["имена"]> interp(S.Name);
ROOT -> S | A | ADV | ADVPRO | ANUM | APRO | COM | CONJ | INTJ | NUM | PART | PR | SPRO | V;