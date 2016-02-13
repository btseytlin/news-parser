#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT ROOT     // указываем корневой нетерминал грамматики


A -> AnyWord<gram="A", kwset=~["имена", "названия"]> interp(A.Name);
ADV -> AnyWord<gram="ADV", kwset=~["имена", "названия"]> interp(ADV.Name);
ADVPRO -> AnyWord<gram="ADVPRO", kwset=~["имена", "названия"]> interp(ADVPRO.Name);
ANUM -> AnyWord<gram="ANUM", kwset=~["имена", "названия"]> interp(ANUM.Name);
APRO -> AnyWord<gram="APRO", kwset=~["имена", "названия"]> interp(APRO.Name);
COM -> AnyWord<gram="COM", kwset=~["имена", "названия"]> interp(COM.Name);
CONJ -> AnyWord<gram="CONJ", kwset=~["имена", "названия"]> interp(CONJ.Name);
INTJ ->  AnyWord<gram="INTJ", kwset=~["имена", "названия"]> interp(INTJ.Name);
NUM -> AnyWord<wff=/(\d+)/> {outgram = "NUM"}| AnyWord<gram="NUM", kwset=~["имена", "названия"]> interp(NUM.Name);
PART -> AnyWord<gram="PART", kwset=~["имена", "названия"]> interp(PART.Name);
PR -> AnyWord<gram="PR", kwset=~["имена", "названия"]> interp(PR.Name);
SPRO ->  AnyWord<gram="SPRO", kwset=~["имена", "названия"]> interp(SPRO.Name);
V -> AnyWord<gram="V", kwset=~["имена", "названия"]> interp(V.Name);
S -> AnyWord<gram="S", kwset=~["имена", "названия"]> interp(S.Name);
ROOT -> S | A | ADV | ADVPRO | ANUM | APRO | COM | CONJ | INTJ | NUM | PART | PR | SPRO | V;