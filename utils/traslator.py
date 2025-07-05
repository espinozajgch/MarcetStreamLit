import json

with open("assets/files/paises_traducidos.json", "r", encoding="utf-8") as f:
    PAISES_TRADUCIDOS = json.load(f)

TRADUCCIONES = {
    "PESO Y % GRASA": {
        "es": "PESO Y % GRASA",
        "en": "WEIGHT AND % FAT",
        "it": "PESO E % DI GRASSO",
        "de": "GEWICHT UND % FETT",
        "fr": "POIDS ET % DE GRAISSE",
        "ca": "PES I % DE GREIX",
        "pt": "PESO E % DE GORDURA",
        "ar": "الوزن و٪ الدهون"
    },
    "Evolución de la Distancia Acumulada": {
        "en": "Evolution of Accumulated Distance",
        "it": "Evoluzione della Distanza Accumulata",
        "de": "Entwicklung der Zurückgelegten Distanz",
        "fr": "Évolution de la Distance Accumulée",
        "ca": "Evolució de la Distància Acumulada",
        "pt": "Evolução da Distância Acumulada",
        "ar": "تطور المسافة التراكمية"
    },
    "DISTANCIA ACUMULADA (M)": {
        "en": "ACCUMULATED DISTANCE (M)",
        "it": "DISTANZA ACCUMULATA (M)",
        "de": "ZURÜCKGELEGTE DISTANZ (M)",
        "fr": "DISTANCE ACCUMULÉE (M)",
        "ca": "DISTÀNCIA ACUMULADA (M)",
        "pt": "DISTÂNCIA ACUMULADA (M)",
        "ar": "المسافة التراكمية (متر)"
    },
    "Evolución de la Potencia Muscular de Salto (CMJ)": {
        "en": "Evolution of Jump Muscle Power (CMJ)",
        "it": "Evoluzione della Potenza Muscolare del Salto (CMJ)",
        "de": "Entwicklung der Sprungkraft (CMJ)",
        "fr": "Évolution de la Puissance Musculaire de Saut (CMJ)",
        "ca": "Evolució de la Potència Muscular del Salt (CMJ)",
        "pt": "Evolução da Potência Muscular do Salto (CMJ)",
        "ar": "تطور القوة العضلية للقفز (CMJ)"
    },
    "POTENCIA MUSCULAR DE SALTO (CMJ)": {
        "es": "POTENCIA MUSCULAR DE SALTO (CMJ)",
        "en": "JUMP MUSCULAR POWER (CMJ)",
        "it": "POTENZA MUSCOLARE DEL SALTO (CMJ)",
        "de": "SPRUNGKRAFT DER MUSKULATUR (CMJ)",
        "fr": "PUISSANCE MUSCULAIRE DU SAUT (CMJ)",
        "ca": "POTÈNCIA MUSCULAR DEL SALT (CMJ)",
        "pt": "POTÊNCIA MUSCULAR DO SALTO (CMJ)",
        "ar": "القوة العضلية للقفز (CMJ)"
        },
    "Evolución del Tiempo Total en Repeticiones de Sprint": {
        "en": "Evolution of Total Time in Sprint Repetitions",
        "it": "Evoluzione del Tempo Totale nelle Ripetizioni di Sprint",
        "de": "Entwicklung der Gesamtzeit bei Sprintwiederholungen",
        "fr": "Évolution du Temps Total lors des Répétitions de Sprint",
        "ca": "Evolució del Temps Total en Repeticions d'Esprint",
        "pt": "Evolução do Tempo Total em Repetições de Sprint",
        "ar": "تطور الوقت الإجمالي في تكرارات العدو"
    },
    "Evolución de la Velocidad en Repeticiones de Sprint": {
        "en": "Evolution of Speed in Sprint Repetitions",
        "it": "Evoluzione della Velocità nelle Ripetizioni di Sprint",
        "de": "Entwicklung der Geschwindigkeit bei Sprintwiederholungen",
        "fr": "Évolution de la Vitesse lors des Répétitions de Sprint",
        "ca": "Evolució de la Velocitat en Repeticions d'Esprint",
        "pt": "Evolução da Velocidade nas Repetições de Sprint",
        "ar": "تطور السرعة في تكرارات العدو السريع"
    },
    "Evolución de la Agilidad (IZQ y DER)": {
        "en": "Agility Evolution (LEFT & RIGHT)",
        "it": "Evoluzione dell'Agilità (SIN & DES)",
        "de": "Agilitätsentwicklung (LI & RE)",
        "fr": "Évolution de l'Agilité (GAUCHE & DROITE)",
        "ca": "Evolució de l'Agilitat (ESQ i DRE)",
        "pt": "Evolução da Agilidade (ESQ e DIR)",
        "ar": "تطور الرشاقة (يسار ويمين)"
    },
    "AGILIDAD (IZQ Y DER)": {
        "es": "AGILIDAD (IZQ Y DER)",
        "en": "AGILITY (LEFT AND RIGHT)",
        "it": "AGILITÀ (SINISTRA E DESTRA)",
        "de": "AGILITÄT (LINKS UND RECHTS)",
        "fr": "AGILITÉ (GAUCHE ET DROITE)",
        "ca": "AGILITAT (ESQUERRA I DRETA)",
        "pt": "AGILIDADE (ESQ E DIR)",
        "ar": "الرشاقة (يسار ويمين)"
    },
    "Evolución del Sprint": {
        "en": "Sprint Evolution",
        "it": "Evoluzione dello Sprint",
        "de": "Sprint-Entwicklung",
        "fr": "Évolution du Sprint",
        "ca": "Evolució de l'Sprint",
        "pt": "Evolução do Sprint",
        "ar": "تطور العدو السريع"
    },
    "SPRINT": {
        "en": "SPRINT EVOLUTION",
        "it": "EVOLUZIONE DELLO SPRINT",
        "de": "SPRINT-ENTWICKLUNG",
        "fr": "ÉVOLUTION DU SPRINT",
        "ca": "EVOLUCIÓ DE L'SPRINT",
        "pt": "EVOLUÇÃO DO SPRINT",
        "ar": "تطور العدو السريع"
    },
    "DIFERENCIA %": {
        "en": "DIFFERENCE %",
        "it": "DIFFERENZA %",
        "de": "DIFFERENZ %",
        "fr": "DIFFÉRENCE %",
        "ca": "DIFERÈNCIA %",
        "pt": "DIFERENÇA %",
        "ar": "النسبة المئوية للاختلاف"
    },
    "505-IZQ (SEG)": {
        "en": "505-LEFT (SEC)",
        "it": "505-SIN (SEC)",
        "de": "505-LI (SEK)",
        "fr": "505-GAUCHE (SEC)",
        "ca": "505-ESQ (SEG)",
        "pt": "505-ESQ (SEG)",
        "ar": "505-يسار (ثانية)"
    },
    "505-DER (SEG)": {
        "en": "505-RIGHT (SEC)",
        "it": "505-DES (SEC)",
        "de": "505-RE (SEK)",
        "fr": "505-DROITE (SEC)",
        "ca": "505-DRE (SEG)",
        "pt": "505-DIR (SEG)",
        "ar": "505-يمين (ثانية)"
    },
    "VELOCIDAD (M/S)": {
        "en": "SPEED (M/S)",
        "it": "VELOCITÀ (M/S)",
        "de": "GESCHWINDIGKEIT (M/S)",
        "fr": "VITESSE (M/S)",
        "ca": "VELOCITAT (M/S)",
        "pt": "VELOCIDADE (M/S)",
        "ar": "السرعة (م/ث)"
    },
    "TIEMPO (SEG)": {
        "en": "TIME (SEC)",
        "it": "TEMPO (SEC)",
        "de": "ZEIT (SEK)",
        "fr": "TEMPS (SEC)",
        "ca": "TEMPS (SEG)",
        "pt": "TEMPO (SEG)",
        "ar": "الوقت (ثانية)"
    },
    "TIEMPO 0-5M (SEG)": {
        "en": "TIME 0-5M (SEC)",
        "it": "TEMPO 0-5M (SEC)",
        "de": "ZEIT 0-5M (SEK)",
        "fr": "TEMPS 0-5M (SEC)",
        "ca": "TEMPS 0-5M (SEG)",
        "pt": "TEMPO 0-5M (SEG)",
        "ar": "الوقت 0-5م (ثانية)"
    },
    "TIEMPO 0-40M (SEG)": {
        "en": "TIME 0-40M (SEC)",
        "it": "TEMPO 0-40M (SEC)",
        "de": "ZEIT 0-40M (SEK)",
        "fr": "TEMPS 0-40M (SEC)",
        "ca": "TEMPS 0-40M (SEG)",
        "pt": "TEMPO 0-40M (SEG)",
        "ar": "الوقت 0-40م (ثانية)"
    },
    "VEL 0-5M (M/S)": {
        "en": "SPEED 0-5M (M/S)",
        "it": "VEL 0-5M (M/S)",
        "de": "GESCHW 0-5M (M/S)",
        "fr": "VIT 0-5M (M/S)",
        "ca": "VEL 0-5M (M/S)",
        "pt": "VEL 0-5M (M/S)",
        "ar": "السرعة 0-5م (م/ث)"
    },
    "VEL 0-40M (M/S)": {
        "en": "SPEED 0-40M (M/S)",
        "it": "VEL 0-40M (M/S)",
        "de": "GESCHW 0-40M (M/S)",
        "fr": "VIT 0-40M (M/S)",
        "ca": "VEL 0-40M (M/S)",
        "pt": "VEL 0-40M (M/S)",
        "ar": "السرعة 0-40م (م/ث)"
    },
    "ALTURA DE SALTO (CM)": {
        "en": "JUMP HEIGHT (CM)",
        "it": "ALTEZZA DEL SALTO (CM)",
        "de": "SPRUNGHÖHE (CM)",
        "fr": "HAUTEUR DE SAUT (CM)",
        "ca": "ALÇADA DEL SALT (CM)",
        "pt": "ALTURA DO SALTO (CM)",
        "ar": "ارتفاع القفزة (سم)"
    },
    "PROMEDIO": {
        "en": "AVERAGE",
        "it": "MEDIA",
        "de": "DURCHSCHNITT",
        "fr": "MOYENNE",
        "ca": "MITJANA",
        "pt": "MÉDIA",
        "ar": "المتوسط"
    },
    "Evolución del Peso y % Grasa": {
        "en": "Evolution of Weight and Fat %",
        "it": "Evoluzione del Peso e Grasso %",
        "de": "Entwicklung von Gewicht und Fett %",
        "fr": "Évolution du Poids et de la Graisse %",
        "ca": "Evolució del Pes i del Greix %",
        "pt": "Evolução do Peso e % de Gordura",
        "ar": "تطور الوزن ونسبة الدهون (%)"
    },
    "ZONA OPTIMA %": {
        "en": "OPTIMAL FAT ZONE %",
        "it": "ZONA OTTIMALE DI GRASSO %",
        "de": "OPTIMALE FETTZONE %",
        "fr": "ZONE OPTIMALE DE GRAISSE %",
        "ca": "ZONA ÒPTIMA DE GREIX %",
        "pt": "ZONA ÓTIMA DE GORDURA %",
        "ar": "منطقة الدهون المثلى (%)"
    },
    "Evolución de la Altura (cm)": {
        "en": "Height Evolution (cm)",
        "it": "Evoluzione dell'Altezza (cm)",
        "de": "Größenentwicklung (cm)",
        "fr": "Évolution de la Taille (cm)",
        "ca": "Evolució de l'Alçada (cm)",
        "pt": "Evolução da Altura (cm)",
        "ar": "تطور الطول (سم)"
    },
    "ALTURA OPTIMA": {
        "en": "OPTIMAL HEIGHT",
        "it": "ALTEZZA OTTIMALE",
        "de": "OPTIMALE KÖRPERGRÖSSE",
        "fr": "TAILLE OPTIMALE",
        "ca": "ALÇADA ÒPTIMA",
        "pt": "ALTURA ÓTIMA",
        "ar": "الطُول الأَمْثَل"
    },
    "TIEMPO OPTIMO": {
        "en": "OPTIMAL TIME",
        "it": "TEMPO OTTIMALE",
        "de": "OPTIMALE ZEIT",
        "fr": "TEMPS OPTIMAL",
        "ca": "TEMPS ÒPTIM",
        "pt": "TEMPO ÓTIMO",
        "ar": "الزَّمَن الأَمْثَل"
    },
    "DISTANCIA OPTIMA": {
        "en": "OPTIMAL DISTANCE",
        "it": "DISTANZA OTTIMALE",
        "de": "OPTIMALE DISTANZ",
        "fr": "DISTANCE OPTIMALE",
        "ca": "DISTÀNCIA ÒPTIMA",
        "pt": "DISTÂNCIA ÓTIMA",
        "ar": "المَسَافَة الأَمْثَل"
    },
    "VELOCIDAD OPTIMA": {
        "en": "OPTIMAL SPEED",
        "it": "VELOCITÀ OTTIMALE",
        "de": "OPTIMALE GESCHWINDIGKEIT",
        "fr": "VITESSE OPTIMALE",
        "ca": "VELOCITAT ÒPTIMA",
        "pt": "VELOCIDADE ÓTIMA",
        "ar": "السُّرْعَة الأَمْثَل"
    },

    # Secciones
    "COMPOSICIÓN CORPORAL": {
        "en": "BODY COMPOSITION",
        "it": "COMPOSIZIONE CORPOREA",
        "de": "KÖRPERZUSAMMENSETZUNG",
        "fr": "COMPOSITION CORPORELLE",
        "ca": "COMPOSICIÓ CORPORAL",
        "pt": "COMPOSIÇÃO CORPORAL",
        "ar": "تركيب الجسم"
    },
    "POTENCIA MUSCULAR (SALTO CON CONTRAMOVIMIENTO)": {
        "en": "MUSCULAR POWER (COUNTER MOVEMENT JUMP)",
        "it": "POTENZA MUSCOLARE (SALTO CONTRO MOVIMENTO)",
        "de": "MUSKELKRAFT (GEGENBEWEGUNGSSPRUNG)",
        "fr": "PUISSANCE MUSCULAIRE (SAUT À CONTRE-MOUVEMENT)",
        "ca": "POTÈNCIA MUSCULAR (SALT AMB CONTRAMOVIMENT)",
        "pt": "POTÊNCIA MUSCULAR (SALTO COM CONTRAMOVIMENTO)",
        "ar": "القدرة العضلية (قفزة مع حركة عكسية)"
    },
    "EVOLUCIÓN DEL SPRINT (0-5M)": {
        "en": "SPRINT EVOLUTION (0-5M)",
        "it": "EVOLUZIONE DELLO SPRINT (0-5M)",
        "de": "SPRINT-ENTWICKLUNG (0-5M)",
        "fr": "ÉVOLUTION DU SPRINT (0-5M)",
        "ca": "EVOLUCIÓ DE L'SPRINT (0-5M)",
        "pt": "EVOLUÇÃO DO SPRINT (0-5M)",
        "ar": "تطور السرعة (0-5م)"
    },
    "EVOLUCIÓN DEL SPRINT (0-40M)": {
        "en": "SPRINT EVOLUTION (0-40M)",
        "it": "EVOLUZIONE DELLO SPRINT (0-40M)",
        "de": "SPRINT-ENTWICKLUNG (0-40M)",
        "fr": "ÉVOLUTION DU SPRINT (0-40M)",
        "ca": "EVOLUCIÓ DE L'SPRINT (0-40M)",
        "pt": "EVOLUÇÃO DO SPRINT (0-40M)",
        "ar": "تطور السرعة (0-40م)"
    },
    "VELOCIDAD EN EL CAMBIO DE DIRECCIÓN (AGILIDAD 505)": {
        "en": "CHANGE OF DIRECTION SPEED (AGILITY 505)",
        "it": "VELOCITÀ DI CAMBIO DIREZIONE (AGILITÀ 505)",
        "de": "RICHTUNGSWECHSELGESCHWINDIGKEIT (AGILITÄT 505)",
        "fr": "VITESSE DE CHANGEMENT DE DIRECTION (AGILITÉ 505)",
        "ca": "VELOCITAT EN EL CANVI DE DIRECCIÓ (AGILITAT 505)",
        "pt": "VELOCIDADE NA MUDANÇA DE DIREÇÃO (AGILIDADE 505)",
        "ar": "السرعة في تغيير الاتجاه (رشاقة 505)"
    },
    "RESISTENCIA INTERMITENTE DE ALTA INTENSIDAD (YO-YO TEST)": {
        "en": "HIGH-INTENSITY INTERMITTENT ENDURANCE (YO-YO TEST)",
        "it": "RESISTENZA INTERMITTENTE AD ALTA INTENSITÀ (YO-YO TEST)",
        "de": "HOCHINTENSIVES INTERMITTIERENDES AUSDAUERTRAINING (YO-YO TEST)",
        "fr": "ENDURANCE INTERMITTENTE À HAUTE INTENSITÉ (YO-YO TEST)",
        "ca": "RESISTÈNCIA INTERMITENT D'ALTA INTENSITAT (TEST YO-YO)",
        "pt": "RESISTÊNCIA INTERMITENTE DE ALTA INTENSIDADE (TESTE YO-YO)",
        "ar": "التحمل المتقطع عالي الشدة (اختبار يو-يو)"
    },
    "CAPACIDAD DE REALIZAR SPRINT'S REPETIDOS (RSA)": {
        "en": "REPEATED SPRINT ABILITY (RSA)",
        "it": "CAPACITÀ DI SPRINT RIPETUTI (RSA)",
        "de": "WIEDERHOLTE SPRINTFÄHIGKEIT (RSA)",
        "fr": "CAPACITÉ DE SPRINTS RÉPÉTÉS (RSA)",
        "ca": "CAPACITAT DE REALITZAR ESPRINTS REPETITS (RSA)",
        "pt": "CAPACIDADE DE REALIZAR SPRINTS REPETIDOS (RSA)",
        "ar": "القدرة على تكرار العدو السريع (RSA)"
    },

    # Métricas con unidades
    "ALTURA-(CM)": {
        "en": "JUMP HEIGHT (CM)",
        "it": "ALTEZZA DEL SALTO (CM)",
        "de": "SPRUNGHÖHE (CM)",
        "fr": "HAUTEUR DE SAUT (CM)",
        "ca": "ALÇADA DEL SALT (CM)",
        "pt": "ALTURA (CM)",
        "ar": "الطول (سم)"
    },
    "ALTURA (CM)": {
        "en": "HEIGHT (CM)",
        "it": "ALTEZZA (CM)",
        "de": "KÖRPERGRÖSSE (CM)",
        "fr": "TAILLE (CM)",
        "ca": "ALÇADA (CM)",
        "pt": "ALTURA (CM)",
        "ar": "الطول (سم)"
    },
    "PESO (KG)": {
        "en": "WEIGHT (KG)",
        "it": "PESO (KG)",
        "de": "GEWICHT (KG)",
        "fr": "POIDS (KG)",
        "ca": "PES (KG)",
        "pt": "PESO (KG)",
        "ar": "الوزن (كغ)"
    },
    "GRASA (%)": {
        "en": "FAT (%)",
        "it": "GRASSO (%)",
        "de": "FETT (%)",
        "fr": "GRAISSE (%)",
        "ca": "GREIX (%)",
        "pt": "GORDURA (%)",
        "ar": "الدهون (%)"
    },

    # Datos personales
    "NACIONALIDAD": {
        "en": "NATIONALITY",
        "it": "NAZIONALITÀ",
        "de": "NATIONALITÄT",
        "fr": "NATIONALITÉ",
        "ca": "NACIONALITAT",
        "pt": "NACIONALIDADE",
        "ar": "الجنسية"
    },
    "F. DE NACIMIENTO": {
        "en": "BIRTH DATE",
        "it": "D. DI NASCITA",
        "de": "GEBURTSDATUM",
        "fr": "D. DE NAISSANCE",
        "ca": "D. DE NAIXEMENT",
        "pt": "D. DE NASCIMENTO",
        "ar": "تاريخ الميلاد"
    },
    "EDAD": {
        "en": "AGE",
        "it": "ETÀ",
        "de": "ALTER",
        "fr": "ÂGE",
        "ca": "EDAT",
        "pt": "IDADE",
        "ar": "العمر"
    },
    "DEMARCACIÓN": {
        "en": "POSITION",
        "it": "RUOLO",
        "de": "POSITION",
        "fr": "POSTE",
        "ca": "DEMARCACIÓ",
        "pt": "POSIÇÃO",
        "ar": "المركز"
    },
    "CATEGORIA": {
        "en": "CATEGORY",
        "it": "CATEGORIA",
        "de": "KATEGORIE",
        "fr": "CATÉGORIE",
        "ca": "CATEGORIA",
        "pt": "CATEGORIA",
        "ar": "الفئة"
    },
    "EQUIPO": {
        "en": "TEAM",
        "it": "SQUADRA",
        "de": "MANNSCHAFT",
        "fr": "ÉQUIPE",
        "ca": "EQUIP",
        "pt": "EQUIPE",
        "ar": "الفريق"
    },

    # Escala visual
    "Escala de valoración": {
        "en": "Assessment Scale",
        "it": "Scala di valutazione",
        "de": "Bewertungsskala",
        "fr": "Échelle d'évaluation",
        "ca": "Escala de valoració",
        "pt": "Escala de Avaliação",
        "ar": "مقياس التقييم"
    },
    "Óptimo": {
        "en": "Optimal",
        "it": "Ottimale",
        "de": "Optimal",
        "fr": "Optimal",
        "ca": "Òptim",
        "pt": "Ótimo",
        "ar": "مثالي"
    },
    "Promedio": {
        "en": "Average",
        "it": "Media",
        "de": "Durchschnitt",
        "fr": "Moyenne",
        "ca": "Promig",
        "pt": "Média",
        "ar": "متوسط"
    },
    "Crítico": {
        "en": "Critical",
        "it": "Critico",
        "de": "Kritisch",
        "fr": "Critique",
        "ca": "Crític",
        "pt": "Crítico",
        "ar": "حرج"
    },
    "DEPARTAMENTO DE OPTIMIZACIÓN DEL RENDIMIENTO DEPORTIVO": {
        "en": "DEPARTMENT OF SPORTS PERFORMANCE OPTIMIZATION",
        "it": "DIPARTIMENTO DI OTTIMIZZAZIONE DELLE PRESTAZIONI SPORTIVE",
        "de": "ABTEILUNG FÜR OPTIMIERUNG DER SPORTLICHEN LEISTUNG",
        "fr": "DÉPARTEMENT D'OPTIMISATION DE LA PERFORMANCE SPORTIVE",
        "ca": "DEPARTAMENT D'OPTIMITZACIÓ DEL RENDIMENT ESPORTIU",
        "pt": "DEPARTAMENTO DE OTIMIZAÇÃO DO DESEMPENHO ESPORTIVO",
        "ar": "قسم تحسين الأداء الرياضي"
    },
    "INFORME INDIVIDUAL - INFORME FÍSICO": {
        "en": "INDIVIDUAL REPORT - PHYSICAL REPORT",
        "it": "RAPPORTO INDIVIDUALE - RAPPORTO FISICO",
        "de": "EINZELBERICHT - PHYSISCHER BERICHT",
        "fr": "RAPPORT INDIVIDUEL - RAPPORT PHYSIQUE",
        "ca": "INFORME INDIVIDUAL - INFORME FÍSIC",
        "pt": "RELATÓRIO INDIVIDUAL - RELATÓRIO FÍSICO",
        "ar": "تقرير فردي - تقرير بدني"
    },

    # Demarcaciones
    "PORTERA": {
        "en": "GOALKEEPER",
        "it": "PORTIERA",
        "de": "TORHÜTERIN",
        "fr": "GARDIENNE",
        "ca": "PORTERA",
        "pt": "GOLEIRA",
        "ar": "حارسة مرمى"
    },
    "DELANTERA": {
        "en": "FORWARD",
        "it": "ATTACCANTE",
        "de": "STÜRMERIN",
        "fr": "ATTAQUANTE",
        "ca": "DAVANTERA",
        "pt": "ATACANTE",
        "ar": "مهاجمة"
    },
    "PORTERO": {
        "en": "GOALKEEPER", "it": "PORTIERE", "de": "TORWART", "fr": "GARDIEN", "ca": "PORTER",
        "pt": "GOLEIRO", "ar": "حارس مرمى"
    },
    "LATERAL DERECHO": {
        "en": "RIGHT BACK", "it": "TERZINO DESTRO", "de": "RECHTER VERTEIDIGER", "fr": "LATÉRAL DROIT", "ca": "LATERAL DRET",
        "pt": "LATERAL DIREITO", "ar": "ظهير أيمن"
    },
    "LATERAL IZQUIERDO": {
        "en": "LEFT BACK", "it": "TERZINO SINISTRO", "de": "LINKER VERTEIDIGER", "fr": "LATÉRAL GAUCHE", "ca": "LATERAL ESQUERRE",
        "pt": "LATERAL ESQUERDO", "ar": "ظهير أيسر"
    },
    "DEFENSA CENTRAL": {
        "en": "CENTER BACK", "it": "DIFENSORE CENTRALE", "de": "INNENVERTEIDIGER", "fr": "DÉFENSEUR CENTRAL", "ca": "DEFENSA CENTRAL",
        "pt": "ZAGUEIRO CENTRAL", "ar": "قلب دفاع"
    },
    "MEDIOCENTRO DEFENSIVO": {
        "en": "DEFENSIVE MIDFIELDER", "it": "CENTROCAMPISTA DIFENSIVO", "de": "DEFENSIVER MITTELFELDSPIELER", "fr": "MILIEU DÉFENSIF", "ca": "PIVOT DEFENSIU",
        "pt": "VOLANTE DEFENSIVO", "ar": "وسط مدافع"
    },
    "MEDIOCENTRO": {
        "en": "MIDFIELDER", "it": "CENTROCAMPISTA", "de": "MITTELFELDSPIELER", "fr": "MILIEU", "ca": "CENTRECAMPISTA",
        "pt": "MEIO-CAMPISTA", "ar": "وسط"
    },
    "MEDIAPUNTA": {
        "en": "ATTACKING MIDFIELDER", "it": "TREQUARTISTA", "de": "OFFENSIVER MITTELFELDSPIELER", "fr": "MILIEU OFFENSIF", "ca": "MITJAPUNTA",
        "pt": "MEIA ATACANTE", "ar": "وسط هجومي"
    },
    "EXTREMO": {
        "en": "WINGER", "it": "ALA", "de": "FLÜGELSPIELER", "fr": "AILIER", "ca": "EXTREM",
        "pt": "PONTA", "ar": "جناح"
    },
    "DELANTERO": {
        "en": "FORWARD", "it": "ATTACCANTE", "de": "STÜRMER", "fr": "ATTAQUANT", "ca": "DAVANTER",
        "pt": "ATACANTE", "ar": "مهاجم"
    },
    # Categorías
    "CADETE": {
        "en": "CADET", "it": "CADETTO", "de": "KADETTE", "fr": "CADET", "ca": "CADET",
        "pt": "CADETE", "ar": "ناشئ"
    },
    "JUVENIL": {
        "en": "YOUTH", "it": "GIOVANILE", "de": "JUGEND", "fr": "JEUNE", "ca": "JUVENIL",
        "pt": "JUVENIL", "ar": "شباب"
    },
    "CHECK-IN": {
        "en": "CHECK-IN", "it": "CHECK-IN", "de": "CHECK-IN", "fr": "CHECK-IN", "ca": "CHECK-IN",
        "pt": "CHECK-IN", "ar": "تسجيل الدخول"
    },
    "CHECK IN": {
        "en": "CHECK IN", "it": "CHECK IN", "de": "CHECK IN", "fr": "CHECK IN", "ca": "CHECK IN",
        "pt": "CHECK IN", "ar": "تسجيل الدخول"
    },

    "LATERAL": {
        "es": "LATERAL",
        "en": "FULLBACK",
        "fr": "LATÉRAL",
        "it": "TERZINO",
        "de": "AUSSENVERTEIDIGER",
        "ca": "LATERAL",
        "pt": "LATERAL",
        "ar": "الظهير"
    },
    "EXTREMO DERECHO": {
        "es": "EXTREMO DERECHO",
        "en": "RIGHT WINGER",
        "fr": "AILIER DROIT",
        "it": "ALA DESTRA",
        "de": "RECHTSAUSSEN",
        "ca": "EXTREM DRET",
        "pt": "EXTREMO DIREITO",
        "ar": "الجناح الأيمن"
    },
    "EXTREMO IZQUIERDO": {
        "es": "EXTREMO IZQUIERDO",
        "en": "LEFT WINGER",
        "fr": "AILIER GAUCHE",
        "it": "ALA SINISTRA",
        "de": "LINKSAUSSEN",
        "ca": "EXTREM ESQUERRE",
        "pt": "EXTREMO ESQUERDO",
        "ar": "الجناح الأيسر"
    },


    "ANTROPOMETRIA": {
        "en": "ANTHROPOMETRY",
        "it": "ANTROPOMETRIA",
        "de": "ANTHROPOMETRIE",
        "fr": "ANTHROPOMÉTRIE",
        "ca": "ANTROPOMETRIA",
        "pt": "ANTROPOMETRIA",
        "ar": "القياسات الجسمية"
    },
    "AGILIDAD": {
        "en": "AGILITY",
        "it": "AGILITÀ",
        "de": "AGILITÄT",
        "fr": "AGILITÉ",
        "ca": "AGILITAT",
        "pt": "AGILIDADE",
        "ar": "رشاقة"
    },
    "REPORTE": {
        "en": "REPORT",
        "it": "RAPPORTO",
        "de": "BERICHT",
        "fr": "RAPPORT",
        "ca": "INFORME",
        "pt": "RELATÓRIO",
        "ar": "تقرير"
    },
    "años": {
        "en": "years old",
        "it": "anni",
        "de": "Jahre alt",
        "fr": "ans",
        "ca": "anys",
        "pt": "anos",
        "ar": "سنة"
    },
    "Max": {
        "en": "Max",
        "it": "Max",
        "de": "Max",
        "fr": "Max",
        "ca": "Max",
        "pt": "Max",
        "ar": "ماكس"
    },
    "Min:": {
        "en": "Min:",
        "it": "Minimo:",
        "de": "Minimal:",
        "fr": "Min :",
        "ca": "Mínim:",
        "pt": "Mínimo:",
        "ar": "الحد الأدنى:"
    },
    "ID": {
        "en": "ID",
        "it": "ID",
        "de": "ID",
        "fr": "ID",
        "ca": "ID",
        "pt": "ID",
        "ar": "معرّف"
    },
    "No Disponible": {
        "en": "Unavailable",
        "it": "Non disponibile",
        "de": "Nicht verfügbar",
        "fr": "Non disponible",
        "ca": "No disponible",
        "pt": "Indisponível",
        "ar": "غير متوفر"
    },
    "No disponible": {
        "en": "Unavailable",
        "it": "Non disponibile",
        "de": "Nicht verfügbar",
        "fr": "Non disponible",
        "ca": "No disponible",
        "pt": "Indisponível",
        "ar": "غير متوفر"
    },
    "OBSERVACIONES": {
        "es": "OBSERVACIONES",
        "en": "OBSERVATIONS",
        "it": "OSSERVAZIONI",
        "de": "BEOBACHTUNGEN",
        "fr": "OBSERVATIONS",
        "ca": "OBSERVACIONS",
        "pt": "OBSERVAÇÕES",
        "ar": "ملاحظات"
    },
    "AGILIDAD (Pierna Izquierda y Pierna Derecha)": {
        "en": "AGILITY (Left Leg and Right Leg)",
        "it": "AGILITÀ (Gamba Sinistra e Gamba Destra)",
        "de": "AGILITÄT (Linkes Bein und Rechtes Bein)",
        "fr": "AGILITÉ (Jambe Gauche et Jambe Droite)",
        "ca": "AGILITAT (Cama Esquerra i Cama Dreta)",
        "pt": "AGILIDADE (Perna Esquerda e Perna Direita)",
        "ar": "المرونة (الساق اليسرى والساق اليمنى)"
    },
    "Evolución de la Agilidad (Pierna Izquierda y Pierna Derecha)": {
        "en": "Agility Progression (Left Leg and Right Leg)",
        "it": "Evoluzione dell'Agilità (Gamba Sinistra e Gamba Destra)",
        "de": "Entwicklung der Agilität (Linkes Bein und Rechtes Bein)",
        "fr": "Évolution de l'Agilité (Jambe Gauche et Jambe Droite)",
        "ca": "Evolució de l'Agilitat (Cama Esquerra i Cama Dreta)",
        "pt": "Evolução da Agilidade (Perna Esquerda e Perna Direita)",
        "ar": "تطور المرونة (الساق اليسرى والساق اليمنى)"
    },
    ## PESO Y GRASA
    "Tu nivel de grasa corporal está en el rango ideal para un futbolista de alto rendimiento.": {
        "es": "Tu nivel de grasa corporal está en el rango ideal para un futbolista de alto rendimiento.",
        "en": "Your body fat level is within the ideal range for a high-performance football player.",
        "it": "Il tuo livello di grasso corporeo è nella gamma ideale per un calciatore ad alte prestazioni.",
        "de": "Dein Körperfettanteil liegt im idealen Bereich für einen Hochleistungssportler.",
        "fr": "Votre taux de graisse corporelle est dans la plage idéale pour un footballeur de haut niveau.",
        "ca": "El teu nivell de greix corporal està dins del rang ideal per a un futbolista d'alt rendiment.",
        "pt": "Seu nível de gordura corporal está dentro da faixa ideal para um jogador de futebol de alto rendimento.",
        "ar": "نسبة الدهون في جسمك تقع ضمن النطاق المثالي للاعب كرة قدم عالي الأداء."
    },
    "Grasa corporal >15%: mayor riesgo de lesiones, fatiga precoz, menor eficiencia y rendimiento físico.\nRecomendamos seguimiento con nutricionista deportivo.\n": {
        "es": "Grasa corporal >15%: mayor riesgo de lesiones, fatiga precoz, menor eficiencia y rendimiento físico.\nRecomendamos seguimiento con nutricionista deportivo.\n",
        "en": "Body fat >15%: higher risk of injuries, early fatigue, lower efficiency and physical performance.\nWe recommend follow-up with a sports nutritionist.\n",
        "it": "Grasso corporeo >15%: maggiore rischio di infortuni, affaticamento precoce, minore efficienza e prestazioni fisiche.\nSi consiglia un monitoraggio con un nutrizionista sportivo.\n",
        "de": "Körperfett >15%: höheres Risiko für Verletzungen, frühzeitige Ermüdung, geringere Effizienz und körperliche Leistung.\nWir empfehlen eine Nachsorge durch einen Sporternährungsberater.\n",
        "fr": "Graisse corporelle >15 % : risque accru de blessures, fatigue précoce, moindre efficacité et performance physique.\nNous recommandons un suivi avec un nutritionniste du sport.\n",
        "ca": "Greix corporal >15%: més risc de lesions, fatiga precoç, menor eficiència i rendiment físic.\nRecomanem un seguiment amb un nutricionista esportiu.\n",
        "pt": "Gordura corporal >15%: maior risco de lesões, fadiga precoce, menor eficiência e desempenho físico.\nRecomendamos acompanhamento com nutricionista esportivo.\n",
        "ar": "دهون الجسم >15٪: زيادة خطر الإصابات، التعب المبكر، انخفاض الكفاءة والأداء البدني.\nننصح بالمتابعة مع اختصاصي تغذية رياضية.\n"
    },
    "Grasa <7%: riesgo de lesiones, fatiga y desequilibrio hormonal.\nRecomendamos seguimiento con nutricionista deportivo.": {
        "es": "Grasa <7%: riesgo de lesiones, fatiga y desequilibrio hormonal.\nRecomendamos seguimiento con nutricionista deportivo.",
        "en": "Fat <7%: risk of injuries, fatigue and hormonal imbalance.\nWe recommend follow-up with a sports nutritionist.",
        "it": "Grasso <7%: rischio di infortuni, affaticamento e squilibrio ormonale.\nSi consiglia un monitoraggio con un nutrizionista sportivo.",
        "de": "Fett <7%: Risiko für Verletzungen, Ermüdung und hormonelles Ungleichgewicht.\nWir empfehlen eine Nachsorge durch einen Sporternährungsberater.",
        "fr": "Graisse <7 % : risque de blessures, de fatigue et de déséquilibre hormonal.\nNous recommandons un suivi avec un nutritionniste du sport.",
        "ca": "Greix <7%: risc de lesions, fatiga i desequilibri hormonal.\nRecomanem un seguiment amb un nutricionista esportiu.",
        "pt": "Gordura <7%: risco de lesões, fadiga e desequilíbrio hormonal.\nRecomendamos acompanhamento com nutricionista esportivo.",
        "ar": "دهون <7٪: خطر الإصابة، التعب واختلال التوازن الهرموني.\nننصح بالمتابعة مع اختصاصي تغذية رياضية."
    },
    #CMJ
    "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento.": {
        "es": "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento.",
        "en": "Your CMJ level is within the optimal performance range.",
        "it": "Il tuo livello nel CMJ è all'interno dell'intervallo ottimale di rendimento.",
        "de": "Dein CMJ-Wert liegt im optimalen Leistungsbereich.",
        "fr": "Votre niveau au CMJ se situe dans la plage optimale de performance.",
        "ca": "El teu nivell en el CMJ està dins del rang òptim de rendiment.",
        "pt": "O seu nível no CMJ está dentro da faixa ideal de desempenho.",
        "ar": "مستواك في اختبار CMJ يقع ضمن النطاق الأمثل للأداء."
    },
    "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento.\nEl objetivo es mejorar la eficiencia en la técnica de salto y mantener o incrementar levemente el rendimiento.": {
        "en": "Your CMJ level is within the optimal performance range.\nThe goal is to improve jump technique efficiency and slightly maintain or increase performance.",
        "it": "Il tuo livello di CMJ è all'interno della gamma ottimale di prestazioni.\nL'obiettivo è migliorare l'efficienza della tecnica di salto e mantenere o aumentare leggermente le prestazioni.",
        "de": "Dein CMJ-Wert liegt im optimalen Leistungsbereich.\nZiel ist es, die Sprungtechnik zu verbessern und die Leistung leicht zu halten oder zu steigern.",
        "fr": "Votre niveau de CMJ est dans la plage de performance optimale.\nL'objectif est d'améliorer l'efficacité de la technique de saut et de maintenir ou d'augmenter légèrement la performance.",
        "ca": "El teu nivell de CMJ està dins del rang òptim de rendiment.\nL'objectiu és millorar l'eficiència de la tècnica de salt i mantenir o augmentar lleugerament el rendiment.",
        "pt": "Seu nível de CMJ está dentro da faixa ideal de desempenho.\nO objetivo é melhorar a eficiência da técnica de salto e manter ou aumentar ligeiramente o desempenho.",
        "ar": "مستوى قفزك العمودي (CMJ) ضمن النطاق الأمثل للأداء.\nالهدف هو تحسين كفاءة تقنية القفز والحفاظ أو زيادة الأداء قليلاً.",
        "es": "Tu nivel en el CMJ está dentro del rango óptimo de rendimiento.\nEl objetivo es mejorar la eficiencia en la técnica de salto y mantener o incrementar levemente el rendimiento."
    },
    "Mejorar la eficiencia en la técnica de salto.\nNecesidad de trabajo de potencia de tren inferior.": {
        "en": "Improve jump technique efficiency.\nNeed for lower body power training.",
        "it": "Migliora l'efficienza della tecnica di salto.\nNecessità di lavoro sulla potenza degli arti inferiori.",
        "de": "Verbessere die Effizienz der Sprungtechnik.\nNotwendigkeit von Krafttraining für den Unterkörper.",
        "fr": "Améliorer l'efficacité de la technique de saut.\nNécessité de travail de puissance du bas du corps.",
        "ca": "Millorar l'eficiència en la tècnica de salt.\nNecessitat de treball de potència del tren inferior.",
        "pt": "Melhorar a eficiência da técnica de salto.\nNecessidade de trabalho de potência de membros inferiores.",
        "ar": "تحسين كفاءة تقنية القفز.\nالحاجة إلى تدريب قوة الجزء السفلي من الجسم.",
        "es": "Mejorar la eficiencia en la técnica de salto.\nNecesidad de trabajo de potencia de tren inferior."
    },
    "Masa muscular insuficiente.\nNecesidad de trabajo de fuerza y potencia de tren inferior.\nMejorar la técnica de salto.": {
        "en": "Insufficient muscle mass.\nNeed for strength and lower body power training.\nImprove jump technique.",
        "it": "Massa muscolare insufficiente.\nNecessità di lavoro di forza e potenza degli arti inferiori.\nMigliorare la tecnica di salto.",
        "de": "Unzureichende Muskelmasse.\nBedarf an Kraft- und Unterkörpertraining.\nVerbesserung der Sprungtechnik.",
        "fr": "Masse musculaire insuffisante.\nNécessité de travailler la force et la puissance du bas du corps.\nAméliorer la technique de saut.",
        "ca": "Massa muscular insuficient.\nNecessitat de treball de força i potència del tren inferior.\nMillorar la tècnica de salt.",
        "pt": "Massa muscular insuficiente.\nNecessidade de treino de força e potência de membros inferiores.\nMelhorar a técnica de salto.",
        "ar": "كتلة عضلية غير كافية.\nالحاجة إلى تدريب القوة والطاقة للجزء السفلي من الجسم.\nتحسين تقنية القفز.",
        "es": "Masa muscular insuficiente.\nNecesidad de trabajo de fuerza y potencia de tren inferior.\nMejorar la técnica de salto."
    },
    #SPRINT
    "Tu nivel de fuerza horizontal para el sprint es excelente para tu edad y categoría.": {
        "en": "Your horizontal sprint strength level is excellent for your age and category.",
        "it": "Il tuo livello di forza orizzontale nello sprint è eccellente per la tua età e categoria.",
        "de": "Dein horizontales Sprintkraftniveau ist ausgezeichnet für dein Alter und deine Kategorie.",
        "fr": "Votre niveau de force horizontale au sprint est excellent pour votre âge et votre catégorie.",
        "ca": "El teu nivell de força horitzontal en l'esprint és excel·lent per a la teva edat i categoria.",
        "pt": "Seu nível de força horizontal no sprint é excelente para sua idade e categoria.",
        "ar": "مستوى القوة الأفقية لديك في العدو ممتاز بالنسبة لعمرك وفئتك.",
        "es": "Tu nivel de fuerza horizontal para el sprint es excelente para tu edad y categoría."
    },
    "Necesidad de trabajo técnico de zancada y frecuencia de paso.\nIdentificar si el déficit está en la aceleración inicial o en la fase de velocidad máxima.\nMejorar tu potencia en tramos cortos.": {
        "en": "Need to improve stride technique and step frequency.\nIdentify whether the deficit is in the initial acceleration or maximum speed phase.\nImprove your power in short sprints.",
        "it": "Necessità di migliorare la tecnica del passo e la frequenza.\nIdentificare se il deficit è nell'accelerazione iniziale o nella fase di velocità massima.\nMigliora la tua potenza nei tratti brevi.",
        "de": "Notwendigkeit, die Schrittlänge und -frequenz zu verbessern.\nDefizite in der Startbeschleunigung oder der Maximalgeschwindigkeit identifizieren.\nVerbessere deine Kraft auf kurzen Strecken.",
        "fr": "Besoin d'améliorer la technique de foulée et la fréquence des pas.\nIdentifier si le déficit se situe dans l'accélération initiale ou la phase de vitesse maximale.\nAméliorer votre puissance sur les courtes distances.",
        "ca": "Necessitat de millorar la tècnica de la gambada i la freqüència del pas.\nIdentificar si el dèficit està en l'acceleració inicial o en la fase de velocitat màxima.\nMillorar la teva potència en trams curts.",
        "pt": "Necessidade de melhorar a técnica de passada e frequência.\nIdentificar se o déficit está na aceleração inicial ou na fase de velocidade máxima.\nMelhore sua potência em trechos curtos.",
        "ar": "الحاجة لتحسين تقنية الخطوة وتكرارها.\nتحديد ما إذا كان النقص في التسارع الأولي أو في مرحلة السرعة القصوى.\nحسّن قوتك في المسافات القصيرة.",
        "es": "Necesidad de trabajo técnico de zancada y frecuencia de paso.\nIdentificar si el déficit está en la aceleración inicial o en la fase de velocidad máxima.\nMejorar tu potencia en tramos cortos."
    },
    "Tienes un margen muy grande de mejora en el trabajo de fuerza de tren inferior.\nNecesidad de trabajo técnico de zancada y frecuencia de paso.\nEs fundamental mejorar tu potencia en tramos cortos y largos.": {
        "en": "You have a wide margin for improvement in lower body strength.\nNeed to improve stride technique and step frequency.\nIt is essential to improve your power in both short and long sprints.",
        "it": "Hai un ampio margine di miglioramento nella forza del treno inferiore.\nNecessità di migliorare la tecnica della falcata e la frequenza.\nÈ fondamentale migliorare la tua potenza nei tratti brevi e lunghi.",
        "de": "Du hast großes Verbesserungspotenzial bei der Beinmuskulatur.\nNotwendigkeit, Technik und Frequenz zu verbessern.\nEs ist entscheidend, deine Kraft in kurzen und langen Sprints zu steigern.",
        "fr": "Vous avez une grande marge de progression dans la force du bas du corps.\nBesoin d'améliorer la technique et la fréquence de foulée.\nIl est essentiel d'améliorer votre puissance sur les sprints courts et longs.",
        "ca": "Tens un gran marge de millora en la força del tren inferior.\nNecessitat de millorar la tècnica i la freqüència de la gambada.\nÉs fonamental millorar la teva potència en trams curts i llargs.",
        "pt": "Você tem uma grande margem de melhora na força dos membros inferiores.\nNecessidade de melhorar a técnica e a frequência da passada.\nÉ fundamental melhorar sua potência em trechos curtos e longos.",
        "ar": "لديك هامش كبير لتحسين قوة الجزء السفلي من الجسم.\nالحاجة لتحسين تقنية الخطوة وتكرارها.\nمن الضروري تحسين قوتك في المسافات القصيرة والطويلة.",
        "es": "Tienes un margen muy grande de mejora en el trabajo de fuerza de tren inferior.\nNecesidad de trabajo técnico de zancada y frecuencia de paso.\nEs fundamental mejorar tu potencia en tramos cortos y largos."
    },
    #AGILIDAD
    "La jugadora presenta un nivel de simetría funcional adecuado (<5%) entre ambas piernas en el cambio de dirección.": {
        "es": "La jugadora presenta un nivel de simetría funcional adecuado (<5%) entre ambas piernas en el cambio de dirección.",
        "en": "The player shows an adequate level of functional symmetry (<5%) between both legs in change of direction.",
        "it": "La giocatrice presenta un livello adeguato di simmetria funzionale (<5%) tra entrambe le gambe nel cambio di direzione.",
        "de": "Die Spielerin weist ein angemessenes Maß an funktioneller Symmetrie (<5 %) zwischen beiden Beinen bei Richtungswechseln auf.",
        "fr": "La joueuse présente un niveau adéquat de symétrie fonctionnelle (<5 %) entre les deux jambes lors du changement de direction.",
        "ca": "La jugadora presenta un nivell adequat de simetria funcional (<5%) entre ambdues cames en el canvi de direcció.",
        "pt": "A jogadora apresenta um nível adequado de simetria funcional (<5%) entre ambas as pernas na mudança de direção.",
        "ar": "تُظهر اللاعبة مستوى مناسبًا من التناسق الوظيفي (<5%) بين الساقين عند تغيير الاتجاه."
    },
    "La jugadora presenta un nivel de simetría funcional adecuado (<4%) entre ambas piernas en el cambio de dirección.": {
        "es": "La jugadora presenta un nivel de simetría funcional adecuado (<4%) entre ambas piernas en el cambio de dirección.",
        "en": "The player shows an adequate level of functional symmetry (<4%) between both legs in change of direction.",
        "it": "La giocatrice presenta un livello adeguato di simmetria funzionale (<4%) tra entrambe le gambe nel cambio di direzione.",
        "de": "Die Spielerin weist ein angemessenes Maß an funktioneller Symmetrie (<4 %) zwischen beiden Beinen bei Richtungswechseln auf.",
        "fr": "La joueuse présente un niveau adéquat de symétrie fonctionnelle (<4 %) entre les deux jambes lors du changement de direction.",
        "ca": "La jugadora presenta un nivell adequat de simetria funcional (<4%) entre ambdues cames en el canvi de direcció.",
        "pt": "A jogadora apresenta um nível adequado de simetria funcional (<4%) entre ambas as pernas na mudança de direção.",
        "ar": "تُظهر اللاعبة مستوى مناسبًا من التناسق الوظيفي (<4%) بين الساقين عند تغيير الاتجاه."
    },
   "La jugadora presenta un nivel de simetría funcional adecuado (<3%) entre ambas piernas en el cambio de dirección.": {
        "es": "La jugadora presenta un nivel de simetría funcional adecuado (<3%) entre ambas piernas en el cambio de dirección.",
        "en": "The player shows an adequate level of functional symmetry (<3%) between both legs in change of direction.",
        "it": "La giocatrice presenta un livello adeguato di simmetria funzionale (<3%) tra entrambe le gambe nel cambio di direzione.",
        "de": "Die Spielerin weist ein angemessenes Maß an funktioneller Symmetrie (<3 %) zwischen beiden Beinen bei Richtungswechseln auf.",
        "fr": "La joueuse présente un niveau adéquat de symétrie fonctionnelle (<3 %) entre les deux jambes lors du changement de direction.",
        "ca": "La jugadora presenta un nivell adequat de simetria funcional (<3%) entre ambdues cames en el canvi de direcció.",
        "pt": "A jogadora apresenta um nível adequado de simetria funcional (<3%) entre ambas as pernas na mudança de direção.",
        "ar": "تُظهر اللاعبة مستوى مناسبًا من التناسق الوظيفي (<3%) بين الساقين عند تغيير الاتجاه."
    },
    "El jugador presenta un nivel de simetría funcional adecuado (<5%) entre ambas piernas en el cambio de dirección.": {
        "en": "The player shows an adequate level of functional symmetry (<5%) between both legs in change of direction.",
        "it": "Il giocatore presenta un livello adeguato di simmetria funzionale (<5%) tra entrambe le gambe nel cambio di direzione.",
        "de": "Der Spieler weist ein angemessenes Maß an funktioneller Symmetrie (<5 %) zwischen beiden Beinen bei Richtungswechseln auf.",
        "fr": "Le joueur présente un niveau adéquat de symétrie fonctionnelle (<5 %) entre les deux jambes lors du changement de direction.",
        "ca": "El jugador presenta un nivell adequat de simetria funcional (<5%) entre ambdues cames en el canvi de direcció.",
        "pt": "O jogador apresenta um nível adequado de simetria funcional (<5%) entre as duas pernas na mudança de direção.",
        "ar": "يُظهر اللاعب مستوى مناسبًا من التماثل الوظيفي (<5٪) بين الساقين عند تغيير الاتجاه.",
        "es": "El jugador presenta un nivel de simetría funcional adecuado (<5%) entre ambas piernas en el cambio de dirección."
    },
    "Ligera asimetría funcional entre ambas piernas en el cambio de dirección.\nAunque se encuentra dentro de un rango aceptable, es recomendable aplicar estrategias preventivas para evitar que esta diferencia aumente y afecte el rendimiento o aumente el riesgo de lesión.": {
        "en": "Slight functional asymmetry between both legs in change of direction.\nAlthough within an acceptable range, preventive strategies are recommended to avoid worsening and risk of injury.",
        "it": "Leggera asimmetria funzionale tra entrambe le gambe nel cambio di direzione.\nAnche se entro limiti accettabili, si raccomandano strategie preventive per evitare peggioramenti e rischi di infortunio.",
        "de": "Leichte funktionelle Asymmetrie zwischen beiden Beinen bei Richtungswechsel.\nObwohl im akzeptablen Bereich, werden präventive Maßnahmen empfohlen, um eine Verschlechterung und Verletzungen zu vermeiden.",
        "fr": "Légère asymétrie fonctionnelle entre les deux jambes lors du changement de direction.\nBien que dans une plage acceptable, il est recommandé d’appliquer des stratégies préventives pour éviter une détérioration et un risque accru de blessure.",
        "ca": "Lleugera asimetria funcional entre ambdues cames en el canvi de direcció.\nTot i que dins d’un rang acceptable, és recomanable aplicar estratègies preventives per evitar que aquesta diferència augmenti i afecti el rendiment o el risc de lesió.",
        "pt": "Assimetria funcional leve entre ambas as pernas na mudança de direção.\nEmbora esteja dentro de uma faixa aceitável, recomenda-se aplicar estratégias preventivas para evitar que a diferença aumente e afete o desempenho ou o risco de lesão.",
        "ar": "اختلاف بسيط في الأداء الوظيفي بين الساقين عند تغيير الاتجاه.\nرغم أنه ضمن النطاق المقبول، يُوصى باتباع استراتيجيات وقائية لمنع تفاقم الفارق أو زيادة خطر الإصابة.",
        "es": "Ligera asimetría funcional entre ambas piernas en el cambio de dirección.\nAunque se encuentra dentro de un rango aceptable, es recomendable aplicar estrategias preventivas para evitar que esta diferencia aumente y afecte el rendimiento o aumente el riesgo de lesión."
    },
    "Asimetría >10% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva.\n- Necesidad de mejora de la técnica de frenado.\n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings).\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria.": {
        "en": "Asymmetry >10% in change of direction represents:\n- Deficit in eccentric strength and/or reactive power.\n- Need to improve braking technique.\n- Increased risk of musculoskeletal injury, especially hamstrings and ACL.\n- Limitation in ability to perform explosive actions (turns, feints, dribbles).\n\nWe recommend a specific unilateral training plan for the weaker leg.",
        "it": "Asimmetria >10% nel cambio di direzione rappresenta:\n- Deficit di forza eccentrica e/o potenza reattiva.\n- Necessità di migliorare la tecnica di frenata.\n- Maggior rischio di infortuni muscoloscheletrici, soprattutto agli ischiocrurali e al LCA.\n- Limitazione nella capacità di eseguire azioni esplosive (cambi di direzione, finte, dribbling).\n\nRaccomandiamo un piano di allenamento unilaterale specifico per la gamba più debole.",
        "de": "Asymmetrie >10 % bei Richtungswechseln bedeutet:\n- Defizit an exzentrischer Kraft und/oder Reaktivkraft.\n- Notwendigkeit zur Verbesserung der Bremstechnik.\n- Erhöhtes Risiko für muskuloskelettale Verletzungen, insbesondere an den hinteren Oberschenkelmuskeln und dem Kreuzband.\n- Eingeschränkte Fähigkeit zu explosiven Bewegungen (Drehungen, Finten, Dribblings).\n\nWir empfehlen ein spezielles einseitiges Trainingsprogramm für das schwächere Bein.",
        "fr": "Asymétrie >10 % lors du changement de direction indique :\n- Déficit de force excentrique et/ou de puissance réactive.\n- Besoin d'améliorer la technique de freinage.\n- Risque accru de blessure musculo-squelettique, notamment des ischio-jambiers et du LCA.\n- Capacité limitée à effectuer des actions explosives (tours, feintes, dribbles).\n\nNous recommandons un plan d'entraînement unilatéral spécifique pour la jambe déficitaire.",
        "ca": "Asimetria >10% en el canvi de direcció representa:\n- Dèficit de força excèntrica i/o potència reactiva.\n- Necessitat de millorar la tècnica de frenada.\n- Augment del risc de lesió musculoesquelètica, especialment en isquiotibials i LCA.\n- Limitació de la capacitat per realitzar accions explosives (girs, fintes, driblatges).\n\nRecomanem un pla específic d'entrenament unilateral per a la cama deficitària.",
        "pt": "Assimetria >10% na mudança de direção representa:\n- Déficit de força excêntrica e/ou potência reativa.\n- Necessidade de melhorar a técnica de frenagem.\n- Maior risco de lesão musculoesquelética, especialmente nos isquiotibiais e LCA.\n- Limitação na capacidade de realizar ações explosivas (giros, fintas, dribles).\n\nRecomendamos um plano de treino unilateral específico para a perna mais fraca.",
        "ar": "الاختلاف >10٪ في تغيير الاتجاه يشير إلى:\n- ضعف في القوة اللامركزية و/أو الطاقة التفاعلية.\n- الحاجة لتحسين تقنية الإيقاف.\n- زيادة خطر الإصابة العضلية الهيكلية، خاصة في عضلات الفخذ الخلفية والرباط الصليبي الأمامي.\n- ضعف القدرة على تنفيذ الحركات المتفجرة (كالتفافات، تمويهات، مراوغات).\n\nننصح بخطة تدريب أحادية الساق مخصصة للساق الأضعف.",
        "es": "Asimetría >10% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva.\n- Necesidad de mejora de la técnica de frenado.\n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings).\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria."
    },
    "Asimetría >7% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva.\n- Necesidad de mejora de la técnica de frenado.\n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings).\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria.": {
        "en": "Asymmetry >7% in change of direction represents:\n- Deficit in eccentric strength and/or reactive power.\n- Need to improve braking technique.\n- Increased risk of musculoskeletal injury, especially hamstrings and ACL.\n- Limitation in ability to perform explosive actions (turns, feints, dribbles).\n\nWe recommend a specific unilateral training plan for the weaker leg.",
        "it": "Asimmetria >7% nel cambio di direzione rappresenta:\n- Deficit di forza eccentrica e/o potenza reattiva.\n- Necessità di migliorare la tecnica di frenata.\n- Maggior rischio di infortuni muscoloscheletrici, soprattutto agli ischiocrurali e al LCA.\n- Limitazione nella capacità di eseguire azioni esplosive (cambi di direzione, finte, dribbling).\n\nRaccomandiamo un piano di allenamento unilaterale specifico per la gamba più debole.",
        "de": "Asymmetrie >7 % bei Richtungswechseln bedeutet:\n- Defizit an exzentrischer Kraft und/oder Reaktivkraft.\n- Notwendigkeit zur Verbesserung der Bremstechnik.\n- Erhöhtes Risiko für muskuloskelettale Verletzungen, insbesondere an den hinteren Oberschenkelmuskeln und dem Kreuzband.\n- Eingeschränkte Fähigkeit zu explosiven Bewegungen (Drehungen, Finten, Dribblings).\n\nWir empfehlen ein spezielles einseitiges Trainingsprogramm für das schwächere Bein.",
        "fr": "Asymétrie >7 % lors du changement de direction indique :\n- Déficit de force excentrique et/ou de puissance réactive.\n- Besoin d'améliorer la technique de freinage.\n- Risque accru de blessure musculo-squelettique, notamment des ischio-jambiers et du LCA.\n- Capacité limitée à effectuer des actions explosives (tours, feintes, dribbles).\n\nNous recommandons un plan d'entraînement unilatéral spécifique pour la jambe déficitaire.",
        "ca": "Asimetria >7% en el canvi de direcció representa:\n- Dèficit de força excèntrica i/o potència reactiva.\n- Necessitat de millorar la tècnica de frenada.\n- Augment del risc de lesió musculoesquelètica, especialment en isquiotibials i LCA.\n- Limitació de la capacitat per realitzar accions explosives (girs, fintes, driblatges).\n\nRecomanem un pla específic d'entrenament unilateral per a la cama deficitària.",
        "pt": "Assimetria >7% na mudança de direção representa:\n- Déficit de força excêntrica e/ou potência reativa.\n- Necessidade de melhorar a técnica de frenagem.\n- Maior risco de lesão musculoesquelética, especialmente nos isquiotibiais e LCA.\n- Limitação na capacidade de realizar ações explosivas (giros, fintas, dribles).\n\nRecomendamos um plano de treino unilateral específico para a perna mais fraca.",
        "ar": "الاختلاف >7٪ في تغيير الاتجاه يشير إلى:\n- ضعف في القوة اللامركزية و/أو الطاقة التفاعلية.\n- الحاجة لتحسين تقنية الإيقاف.\n- زيادة خطر الإصابة العضلية الهيكلية، خاصة في عضلات الفخذ الخلفية والرباط الصليبي الأمامي.\n- ضعف القدرة على تنفيذ الحركات المتفجرة (كالتفافات، تمويهات، مراوغات).\n\nننصح بخطة تدريب أحادية الساق مخصصة للساق الأضعف.",
        "es": "Asimetría >7% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva.\n- Necesidad de mejora de la técnica de frenado.\n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings).\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria."
    },
    "Asimetría > 5.5% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva\n- Necesidad de mejora de la técnica de frenado \n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings)\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria.": {
        "en": "Asymmetry > 5.5% in change of direction represents:\n- Deficit in eccentric strength and/or reactive power\n- Need to improve braking technique\n- Increased risk of musculoskeletal injury, especially hamstrings and ACL\n- Limitation in ability to perform explosive actions (turns, feints, dribbles)\n\nWe recommend a specific unilateral training plan for the weaker leg.",
        "it": "Asimmetria >5,5% nel cambio di direzione rappresenta:\n- Deficit di forza eccentrica e/o potenza reattiva\n- Necessità di migliorare la tecnica di frenata\n- Maggior rischio di infortuni muscoloscheletrici, soprattutto agli ischiocrurali e al LCA\n- Limitazione nella capacità di eseguire azioni esplosive (cambi di direzione, finte, dribbling)\n\nRaccomandiamo un piano di allenamento unilaterale specifico per la gamba più debole.",
        "de": "Asymmetrie >5,5 % bei Richtungswechseln bedeutet:\n- Defizit an exzentrischer Kraft und/oder Reaktivkraft\n- Notwendigkeit zur Verbesserung der Bremstechnik\n- Erhöhtes Risiko für muskuloskelettale Verletzungen, insbesondere an den hinteren Oberschenkelmuskeln und dem Kreuzband\n- Eingeschränkte Fähigkeit zu explosiven Bewegungen (Drehungen, Finten, Dribblings)\n\nWir empfehlen ein spezielles einseitiges Trainingsprogramm für das schwächere Bein.",
        "fr": "Asymétrie >5,5 % lors du changement de direction indique :\n- Déficit de force excentrique et/ou de puissance réactive\n- Besoin d'améliorer la technique de freinage\n- Risque accru de blessure musculo-squelettique, notamment des ischio-jambiers et du LCA\n- Capacité limitée à effectuer des actions explosives (tours, feintes, dribbles)\n\nNous recommandons un plan d'entraînement unilatéral spécifique pour la jambe déficitaire.",
        "ca": "Asimetria >5,5% en el canvi de direcció representa:\n- Dèficit de força excèntrica i/o potència reactiva\n- Necessitat de millorar la tècnica de frenada\n- Augment del risc de lesió musculoesquelètica, especialment en isquiotibials i LCA\n- Limitació de la capacitat per realitzar accions explosives (girs, fintes, driblatges)\n\nRecomanem un pla específic d'entrenament unilateral per a la cama deficitària.",
        "pt": "Assimetria >5,5% na mudança de direção representa:\n- Déficit de força excêntrica e/ou potência reativa\n- Necessidade de melhorar a técnica de frenagem\n- Maior risco de lesão musculoesquelética, especialmente nos isquiotibiais e LCA\n- Limitação na capacidade de realizar ações explosivas (giros, fintas, dribles)\n\nRecomendamos um plano de treino unilateral específico para a perna mais fraca.",
        "ar": "الاختلاف >5.5٪ في تغيير الاتجاه يشير إلى:\n- ضعف في القوة اللامركزية و/أو الطاقة التفاعلية\n- الحاجة لتحسين تقنية الإيقاف\n- زيادة خطر الإصابة العضلية الهيكلية، خاصة في عضلات الفخذ الخلفية والرباط الصليبي الأمامي\n- ضعف القدرة على تنفيذ الحركات المتفجرة (كالتفافات، تمويهات، مراوغات)\n\nننصح بخطة تدريب أحادية الساق مخصصة للساق الأضعف.",
        "es": "Asimetría > 5.5% en el cambio de dirección representa:\n- Déficit de fuerza excéntrica y/o potencia reactiva\n- Necesidad de mejora de la técnica de frenado \n- Incremento en el riesgo de lesión musculoesquelética, sobre todo en isquiosurales y LCA.\n- Limitación de la capacidad de realizar acciones explosivas (con giros, fintas, driblings)\n\nRecomendamos un plan específico de entrenamiento unilateral de la pierna deficitaria."
    },
    "FECHA": {
        "es": "FECHA",
        "en": "DATE",
        "it": "DATA",
        "de": "DATUM",
        "fr": "DATE",
        "ca": "DATA",
        "pt": "DATA",
        "ar": "التاريخ"
    },
    "Porcentajes > 15% de grasa corporal representa:\n"
    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
    "- Acelera la aparición de fatiga.\n"
    "- Disminuye la eficiencia energética y el rendimiento físico.\n"
    "- Afecta parámetros hormonales y metabólicos.\n"
    "- Recomendamos realizar un seguimiento con un nutricionista deportivo.": {
        "en": "Percentages > 15% of body fat represent:\n- Increase in musculoskeletal injury incidence.\n- Accelerates onset of fatigue.\n- Decreases energy efficiency and physical performance.\n- Affects hormonal and metabolic parameters.\n- We recommend follow-up with a sports nutritionist.",
        "it": "Percentuali > 15% di grasso corporeo rappresentano:\n- Aumento dell'incidenza di lesioni muscoloscheletriche.\n- Accelera la comparsa della fatica.\n- Riduce l'efficienza energetica e le prestazioni fisiche.\n- Influenza i parametri ormonali e metabolici.\n- Si consiglia un follow-up con un nutrizionista sportivo.",
        "de": "Prozentsätze > 15% Körperfett bedeuten:\n- Erhöhte Häufigkeit von muskuloskelettalen Verletzungen.\n- Beschleunigt das Auftreten von Ermüdung.\n- Verringert die Energieeffizienz und die körperliche Leistungsfähigkeit.\n- Beeinträchtigt hormonelle und metabolische Parameter.\n- Wir empfehlen eine Nachsorge mit einem Sporternährungsberater.",
        "fr": "Des pourcentages > 15 % de masse grasse corporelle représentent :\n- Augmentation de l'incidence des blessures musculo-squelettiques.\n- Accélère l'apparition de la fatigue.\n- Diminue l'efficacité énergétique et les performances physiques.\n- Affecte les paramètres hormonaux et métaboliques.\n- Nous recommandons un suivi avec un nutritionniste sportif.",
        "ca": "Percentatges > 15% de greix corporal representa:\n- Augment de la incidència de lesions musculoesquelètiques.\n- Accelera l'aparició de fatiga.\n- Disminueix l'eficiència energètica i el rendiment físic.\n- Afecta els paràmetres hormonals i metabòlics.\n- Es recomana un seguiment amb un nutricionista esportiu.",
        "pt": "Porcentagens > 15% de gordura corporal representam:\n- Aumento na incidência de lesões musculoesqueléticas.\n- Acelera o aparecimento da fadiga.\n- Diminui a eficiência energética e o desempenho físico.\n- Afeta os parâmetros hormonais e metabólicos.\n- Recomendamos acompanhamento com um nutricionista esportivo.",
        "ar": "تشير النسب > 15٪ من الدهون في الجسم إلى:\n- زيادة في حدوث الإصابات العضلية الهيكلية.\n- تسريع ظهور التعب.\n- انخفاض الكفاءة الطاقية والأداء البدني.\n- يؤثر على المعايير الهرمونية والتمثيل الغذائي.\n- نوصي بالمتابعة مع أخصائي تغذية رياضي."
    },
    "Porcentajes > 17% de grasa corporal representa:\n"
    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
    "- Acelera la aparición de fatiga.\n"
    "- Disminuye la eficiencia energética y el rendimiento físico.\n"
    "- Afecta parámetros hormonales y metabólicos.\n"
    "- Recomendamos realizar un seguimiento con un nutricionista deportivo.": {
        "en": "Percentages > 17% of body fat represent:\n- Increase in musculoskeletal injury incidence.\n- Accelerates onset of fatigue.\n- Decreases energy efficiency and physical performance.\n- Affects hormonal and metabolic parameters.\n- We recommend follow-up with a sports nutritionist.",
        "it": "Percentuali > 17% di grasso corporeo rappresentano:\n- Aumento dell'incidenza di lesioni muscoloscheletriche.\n- Accelera la comparsa della fatica.\n- Riduce l'efficienza energetica e le prestazioni fisiche.\n- Influenza i parametri ormonali e metabolici.\n- Si consiglia un follow-up con un nutrizionista sportivo.",
        "de": "Prozentsätze > 17% Körperfett bedeuten:\n- Erhöhte Häufigkeit von muskuloskelettalen Verletzungen.\n- Beschleunigt das Auftreten von Ermüdung.\n- Verringert die Energieeffizienz und die körperliche Leistungsfähigkeit.\n- Beeinträchtigt hormonelle und metabolische Parameter.\n- Wir empfehlen eine Nachsorge mit einem Sporternährungsberater.",
        "fr": "Des pourcentages > 17 % de masse grasse corporelle représentent :\n- Augmentation de l'incidence des blessures musculo-squelettiques.\n- Accélère l'apparition de la fatigue.\n- Diminue l'efficacité énergétique et les performances physiques.\n- Affecte les paramètres hormonaux et métaboliques.\n- Nous recommandons un suivi avec un nutritionniste sportif.",
        "ca": "Percentatges > 17% de greix corporal representa:\n- Augment de la incidència de lesions musculoesquelètiques.\n- Accelera l'aparició de fatiga.\n- Disminueix l'eficiència energètica i el rendiment físic.\n- Afecta els paràmetres hormonals i metabòlics.\n- Es recomana un seguiment amb un nutricionista esportiu.",
        "pt": "Porcentagens > 17% de gordura corporal representam:\n- Aumento na incidência de lesões musculoesqueléticas.\n- Acelera o aparecimento da fadiga.\n- Diminui a eficiência energética e o desempenho físico.\n- Afeta os parâmetros hormonais e metabólicos.\n- Recomendamos acompanhamento com um nutricionista esportivo.",
        "ar": "تشير النسب > 15٪ من الدهون في الجسم إلى:\n- زيادة في حدوث الإصابات العضلية الهيكلية.\n- تسريع ظهور التعب.\n- انخفاض الكفاءة الطاقية والأداء البدني.\n- يؤثر على المعايير الهرمونية والتمثيل الغذائي.\n- نوصي بالمتابعة مع أخصائي تغذية رياضي."
    },
    "Porcentajes > 15% de grasa corporal representa:\n"
    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
    "- Acelera la aparición de fatiga.\n"
    "- Disminuye la eficiencia energética y el rendimiento físico.\n"
    "- Afecta parámetros hormonales y metabólicos.\n"
    "- Recomendamos realizar un seguimiento con un nutricionista.": {
        "en": "Percentages > 15% of body fat represent:\n- Increase in musculoskeletal injury incidence.\n- Accelerates onset of fatigue.\n- Decreases energy efficiency and physical performance.\n- Affects hormonal and metabolic parameters.\n- We recommend follow-up with a nutritionist.",
        "it": "Percentuali > 15% di grasso corporeo rappresentano:\n- Aumento dell'incidenza di lesioni muscoloscheletriche.\n- Accelera la comparsa della fatica.\n- Riduce l'efficienza energetica e le prestazioni fisiche.\n- Influenza i parametri ormonali e metabolici.\n- Si consiglia un follow-up con un nutrizionista.",
        "de": "Prozentsätze > 15% Körperfett bedeuten:\n- Erhöhte Häufigkeit von muskuloskelettalen Verletzungen.\n- Beschleunigt das Auftreten von Ermüdung.\n- Verringert die Energieeffizienz und die körperliche Leistungsfähigkeit.\n- Beeinträchtigt hormonelle und metabolische Parameter.\n- Wir empfehlen eine Nachsorge mit einem Sporternährungsberater.",
        "fr": "Des pourcentages > 15 % de masse grasse corporelle représentent :\n- Augmentation de l'incidence des blessures musculo-squelettiques.\n- Accélère l'apparition de la fatigue.\n- Diminue l'efficacité énergétique et les performances physiques.\n- Affecte les paramètres hormonaux et métaboliques.\n- Nous recommandons un suivi avec un nutritionniste.",
        "ca": "Percentatges > 15% de greix corporal representa:\n- Augment de la incidència de lesions musculoesquelètiques.\n- Accelera l'aparició de fatiga.\n- Disminueix l'eficiència energètica i el rendiment físic.\n- Afecta els paràmetres hormonals i metabòlics.\n- Es recomana un seguiment amb un nutricionista.",
        "pt": "Porcentagens > 15% de gordura corporal representam:\n- Aumento na incidência de lesões musculoesqueléticas.\n- Acelera o aparecimento da fadiga.\n- Diminui a eficiência energética e o desempenho físico.\n- Afeta os parâmetros hormonais e metabólicos.\n- Recomendamos acompanhamento com um nutricionista.",
        "ar": "تشير النسب > 15 من الدهون في الجسم إلى:\n- زيادة في حدوث الإصابات العضلية الهيكلية.\n- تسريع ظهور التعب.\n- انخفاض الكفاءة الطاقية والأداء البدني.\n- يؤثر على المعايير الهرمونية والتمثيل الغذائي.\n- نوصي بالمتابعة مع أخصائي تغذية رياضي."
    },
    "Porcentajes > 17% de grasa corporal representa:\n"
    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
    "- Acelera la aparición de fatiga.\n"
    "- Disminuye la eficiencia energética y el rendimiento físico.\n"
    "- Afecta parámetros hormonales y metabólicos.\n"
    "- Recomendamos realizar un seguimiento con un nutricionista.": {
        "en": "Percentages > 17% of body fat represent:\n- Increase in musculoskeletal injury incidence.\n- Accelerates onset of fatigue.\n- Decreases energy efficiency and physical performance.\n- Affects hormonal and metabolic parameters.\n- We recommend follow-up with a nutritionist.",
        "it": "Percentuali > 17% di grasso corporeo rappresentano:\n- Aumento dell'incidenza di lesioni muscoloscheletriche.\n- Accelera la comparsa della fatica.\n- Riduce l'efficienza energetica e le prestazioni fisiche.\n- Influenza i parametri ormonali e metabolici.\n- Si consiglia un follow-up con un nutrizionista.",
        "de": "Prozentsätze > 17% Körperfett bedeuten:\n- Erhöhte Häufigkeit von muskuloskelettalen Verletzungen.\n- Beschleunigt das Auftreten von Ermüdung.\n- Verringert die Energieeffizienz und die körperliche Leistungsfähigkeit.\n- Beeinträchtigt hormonelle und metabolische Parameter.\n- Wir empfehlen eine Nachsorge mit einem Sporternährungsberater.",
        "fr": "Des pourcentages > 17 % de masse grasse corporelle représentent :\n- Augmentation de l'incidence des blessures musculo-squelettiques.\n- Accélère l'apparition de la fatigue.\n- Diminue l'efficacité énergétique et les performances physiques.\n- Affecte les paramètres hormonaux et métaboliques.\n- Nous recommandons un suivi avec un nutritionniste.",
        "ca": "Percentatges > 17% de greix corporal representa:\n- Augment de la incidència de lesions musculoesquelètiques.\n- Accelera l'aparició de fatiga.\n- Disminueix l'eficiència energètica i el rendiment físic.\n- Afecta els paràmetres hormonals i metabòlics.\n- Es recomana un seguiment amb un nutricionista.",
        "pt": "Porcentagens > 17% de gordura corporal representam:\n- Aumento na incidência de lesões musculoesqueléticas.\n- Acelera o aparecimento da fadiga.\n- Diminui a eficiência energética e o desempenho físico.\n- Afeta os parâmetros hormonais e metabólicos.\n- Recomendamos acompanhamento com um nutricionista.",
        "ar": "تشير النسب > 17 من الدهون في الجسم إلى:\n- زيادة في حدوث الإصابات العضلية الهيكلية.\n- تسريع ظهور التعب.\n- انخفاض الكفاءة الطاقية والأداء البدني.\n- يؤثر على المعايير الهرمونية والتمثيل الغذائي.\n- نوصي بالمتابعة مع أخصائي تغذية رياضي."
    },
    "Porcentajes menores al 7% de grasa corporal representan:\n"
    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
    "- Aceleración en la aparición de la fatiga.\n"
    "- Disminución de la eficiencia energética y del rendimiento físico.\n"
    "- Alteraciones en parámetros hormonales y metabólicos.\n"
    "- Se recomienda realizar un seguimiento con un nutricionista deportivo.": {
        "en": "Body fat percentages below 7% represent:\n- Increase in musculoskeletal injury incidence.\n- Accelerated onset of fatigue.\n- Decrease in energy efficiency and physical performance.\n- Alterations in hormonal and metabolic parameters.\n- Follow-up with a sports nutritionist is recommended.",
        "it": "Percentuali di grasso corporeo inferiori al 7% rappresentano:\n- Aumento dell'incidenza di lesioni muscoloscheletriche.\n- Accelerazione dell'insorgenza della fatica.\n- Riduzione dell'efficienza energetica e delle prestazioni fisiche.\n- Alterazioni nei parametri ormonali e metabolici.\n- Si raccomanda un follow-up con un nutrizionista sportivo.",
        "de": "Körperfettanteile unter 7% bedeuten:\n- Erhöhte Häufigkeit von muskuloskelettalen Verletzungen.\n- Beschleunigter Beginn von Ermüdung.\n- Verringerte Energieeffizienz und körperliche Leistungsfähigkeit.\n- Veränderungen hormoneller und metabolischer Parameter.\n- Eine Nachsorge durch einen Sporternährungsberater wird empfohlen.",
        "fr": "Des pourcentages de graisse corporelle inférieurs à 7 % représentent :\n- Augmentation de l'incidence des blessures musculo-squelettiques.\n- Apparition accélérée de la fatigue.\n- Diminution de l'efficacité énergétique et des performances physiques.\n- Altérations des paramètres hormonaux et métaboliques.\n- Un suivi avec un nutritionniste sportif est recommandé.",
        "ca": "Els percentatges de greix corporal inferiors al 7% representen:\n- Augment en la incidència de lesions musculoesquelètiques.\n- Aceleració en l'aparició de fatiga.\n- Disminució de l'eficiència energètica i del rendiment físic.\n- Alteracions en paràmetres hormonals i metabòlics.\n- Es recomana fer un seguiment amb un nutricionista esportiu.",
        "pt": "Porcentagens de gordura corporal abaixo de 7% representam:\n- Aumento na incidência de lesões musculoesqueléticas.\n- Aceleração do aparecimento da fadiga.\n- Diminuição da eficiência energética e do desempenho físico.\n- Alterações em parâmetros hormonais e metabólicos.\n- Recomenda-se acompanhamento com um nutricionista esportivo.",
        "ar": "تشير النسب المئوية للدهون في الجسم التي تقل عن 7٪ إلى:\n- زيادة في حدوث الإصابات العضلية الهيكلية.\n- تسريع في ظهور التعب.\n- انخفاض في الكفاءة الطاقية والأداء البدني.\n- تغيرات في المعايير الهرمونية والتمثيل الغذائي.\n- يُوصى بالمتابعة مع اختصاصي تغذية رياضية."
    },
    "Porcentajes menores al 8% de grasa corporal representan:\n"
    "- Aumento en la incidencia de lesiones músculoesqueléticas.\n"
    "- Aceleración en la aparición de la fatiga.\n"
    "- Disminución de la eficiencia energética y del rendimiento físico.\n"
    "- Alteraciones en parámetros hormonales y metabólicos.\n"
    "- Se recomienda realizar un seguimiento con un nutricionista deportivo.": {
        "en": "Body fat percentages below 8% represent:\n- Increase in musculoskeletal injury incidence.\n- Accelerated onset of fatigue.\n- Decrease in energy efficiency and physical performance.\n- Alterations in hormonal and metabolic parameters.\n- Follow-up with a sports nutritionist is recommended.",
        "it": "Percentuali di grasso corporeo inferiori al 8% rappresentano:\n- Aumento dell'incidenza di lesioni muscoloscheletriche.\n- Accelerazione dell'insorgenza della fatica.\n- Riduzione dell'efficienza energetica e delle prestazioni fisiche.\n- Alterazioni nei parametri ormonali e metabolici.\n- Si raccomanda un follow-up con un nutrizionista sportivo.",
        "de": "Körperfettanteile unter 8% bedeuten:\n- Erhöhte Häufigkeit von muskuloskelettalen Verletzungen.\n- Beschleunigter Beginn von Ermüdung.\n- Verringerte Energieeffizienz und körperliche Leistungsfähigkeit.\n- Veränderungen hormoneller und metabolischer Parameter.\n- Eine Nachsorge durch einen Sporternährungsberater wird empfohlen.",
        "fr": "Des pourcentages de graisse corporelle inférieurs à 8 % représentent :\n- Augmentation de l'incidence des blessures musculo-squelettiques.\n- Apparition accélérée de la fatigue.\n- Diminution de l'efficacité énergétique et des performances physiques.\n- Altérations des paramètres hormonaux et métaboliques.\n- Un suivi avec un nutritionniste sportif est recommandé.",
        "ca": "Els percentatges de greix corporal inferiors al 8% representen:\n- Augment en la incidència de lesions musculoesquelètiques.\n- Aceleració en l'aparició de fatiga.\n- Disminució de l'eficiència energètica i del rendiment físic.\n- Alteracions en paràmetres hormonals i metabòlics.\n- Es recomana fer un seguiment amb un nutricionista esportiu.",
        "pt": "Porcentagens de gordura corporal abaixo de 8% representam:\n- Aumento na incidência de lesões musculoesqueléticas.\n- Aceleração do aparecimento da fadiga.\n- Diminuição da eficiência energética e do desempenho físico.\n- Alterações em parâmetros hormonais e metabólicos.\n- Recomenda-se acompanhamento com um nutricionista esportivo.",
        "ar": "تشير النسب المئوية للدهون في الجسم التي تقل عن 7٪ إلى:\n- زيادة في حدوث الإصابات العضلية الهيكلية.\n- تسريع في ظهور التعب.\n- انخفاض في الكفاءة الطاقية والأداء البدني.\n- تغيرات في المعايير الهرمونية والتمثيل الغذائي.\n- يُوصى بالمتابعة مع اختصاصي تغذية رياضية."
    },
    "Excelente estado de potencia de miembro inferior para el fútbol femenino": {
        "es": "Excelente estado de potencia de miembro inferior para el fútbol femenino",
        "en": "Excellent lower limb power condition for women's football",
        "it": "Eccellente condizione di potenza degli arti inferiori per il calcio femminile",
        "de": "Ausgezeichneter Zustand der Beinmuskulatur für Frauenfußball",
        "fr": "Excellente condition de puissance des membres inférieurs pour le football féminin",
        "ca": "Excel·lent estat de potència dels membres inferiors per al futbol femení",
        "pt": "Excelente condição de potência dos membros inferiores para o futebol feminino",
        "ar": "حالة ممتازة لقوة الأطراف السفلية لكرة القدم النسائية"
    }
}

def traducir(texto, idioma="es"):
    return TRADUCCIONES.get(texto, {}).get(idioma, texto)

def traducir_lista(palabras, idioma_destino="en"):
    palabras_traducidas = []
    for palabra in palabras:
        traduccion = TRADUCCIONES.get(palabra, {}).get(idioma_destino, palabra)
        palabras_traducidas.append(traduccion)
    return palabras_traducidas

def traducir_pais(pais, idioma="es"):
    """
    Devuelve la traducción de un país al idioma deseado.
    
    Args:
        pais (str): Nombre del país en español.
        idioma (str): Código del idioma destino (ej. 'en', 'fr', etc.).

    Returns:
        str: Traducción del país si está disponible, o el nombre original si no existe traducción.
    """
    return PAISES_TRADUCIDOS.get(pais, {}).get(idioma, pais)
