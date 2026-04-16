"""
Mapeamento: vocabulário dos CSVs (2024/2025) → valores aceitos pelo formulário matricula.html.
Hipóteses documentadas onde há aproximação.
"""

# Período: CSV costuma usar "2024/01" ou "2024/1" → formulário usa "2024/1º"
PERIOD_CSV_TO_FORM = {
    "2022/01": "2022/1º",
    "2022/02": "2022/2º",
    "2023/01": "2023/1º",
    "2023/02": "2023/2º",
    "2024/01": "2024/1º",
    "2024/02": "2024/2º",
    "2025/01": "2025/1º",
    "2025/02": "2025/2º",
    "2026/01": "2026/1º",
    "2026/02": "2026/2º",
}

# Curso no CSV (trechos frequentes) → valor exato do <select name="curso">
CURSO_CSV_TO_FORM = {
    "tecnólogo em análise e desenvolvimento de sistemas": "Análise e Desenvolvimento de Sistemas",
    "análise e desenvolvimento de sistemas": "Análise e Desenvolvimento de Sistemas",
    "tecnólogo em processos gerenciais": "Outro",
    "processos gerenciais": "Outro",
    "administração": "Administração",
    "pedagogia": "Pedagogia",
    "pós graduação": "Outro",
    "gestão escolar": "Outro",
}

# Faixa etária CSV → faixa_etária do formulário (aproximação)
FAIXA_ETARIA_CSV_TO_FORM = {
    "entre 16 e 21 anos": "18 - 22 anos",
    "entre 22 e 26 anos": "23 - 27 anos",
    "entre 27 e 33 anos": "28 - 32 anos",
    "entre 34 e 39 anos": "33 - 37 anos",
    "entre 40 e 45 anos": "38 - 42 anos",
    "entre 46 e 50 anos": "+ 42 anos",
    "entre 51 e 55 anos": "+ 42 anos",
    "prefiro não declarar": "Prefiro não dizer",
}

# Amostras de bairros / divulgação vistas no CSV → meio_divulgacao do form (lista fechada)
MEIO_DIVULGACAO_SAMPLES = [
    "Amigos/Familiares",
    "Instagram",
    "Facebook",
    "Site oficial",
]

# Opções válidas do formulário (para validação antes do POST)
FORM_OPTIONS = {
    "periodo_ingresso": [
        "2022/1º",
        "2022/2º",
        "2023/1º",
        "2023/2º",
        "2024/1º",
        "2024/2º",
        "2024/3º",
        "2025/1º",
        "2025/2º",
        "2026/1º",
        "2026/2º",
    ],
    "curso": ["Administração", "Análise e Desenvolvimento de Sistemas", "Pedagogia", "Outro"],
    "fase": [f"{i}º fase" for i in range(1, 9)],
    "faixa_etaria": [
        "18 - 22 anos",
        "23 - 27 anos",
        "28 - 32 anos",
        "33 - 37 anos",
        "38 - 42 anos",
        "+ 42 anos",
    ],
    "cor_raca": ["Indígena", "Preto", "Pardo", "Branco", "Amarelo"],
    "genero": ["Masculino", "Feminino", "Transgênero", "Não Binário", "Prefiro não dizer"],
    "cidade": ["Palhoça", "São José", "Santo Amaro", "Biguaçu", "Paulo Lopes", "Florianópolis"],
    "tipo_moradia": ["Aluguel", "Casa própria", "De favor", "Hotel", "Com os pais"],
    "escolaridade": [
        "Ensino médio completo",
        "Ensino médio + técnico completo",
        "Ensino superior incompleto",
        "Ensino superior completo",
        "Pós graduação",
        "Mestrado",
        "Doutorado",
    ],
    "trabalha": ["Sim", "Não"],
    "trabalha_na_area": ["Sim", "Não"],
    "atividade_principal": [
        "Apenas estudo",
        "Estágio",
        "CLT",
        "Autônomo/trabalho informal/freelancer",
        "Empreendedor/MEI",
        "Empresário",
        "Desempregado",
        "Outro",
    ],
    "jornada_trabalho": ["0h (não trabalho)", "4h", "6h", "8h", "10h", "12h"],
    "faixa_renda": [
        "500,00 - 1000,00",
        "1100,00 - 1700,00",
        "1800,00 - 2300,00",
        "2400,00 - 3000,00",
        "3100,00 - 3700,00",
        "3800,00 - 4500,00",
        "+ 4600,00",
    ],
    "meio_transporte": ["Carro", "Moto", "Ônibus", "APPs de transporte", "Bicicleta", "Nenhum"],
    "dificuldade_frequencia": [
        "Não",
        "Tempo",
        "Período",
        "Transporte/Deslocamento",
        "Limitações tecnológicas",
        "Limitações de saúde",
        "Outros",
    ],
    "forma_alimentacao": [
        "Trago comida de casa.",
        "Compro na cantina da instituição.",
        "Compro comida fora da instituição.",
        "Não costumo me alimentar na instituição.",
    ],
    "meio_comunicacao": ["Redes sociais", "Televisão", "Rádio", "Jornais", "Sites de notícia"],
    "meio_divulgacao": [
        "Instagram",
        "Facebook",
        "Amigos/Familiares",
        "Site oficial",
        "Visita à instituição",
        "Outro",
    ],
}

FORM_FIELD_ORDER = [
    "email",
    "periodo_ingresso",
    "curso",
    "fase",
    "faixa_etaria",
    "tem_deficiencia",
    "qual_deficiencia",
    "cor_raca",
    "genero",
    "cidade",
    "tipo_moradia",
    "escolaridade",
    "trabalha",
    "trabalha_na_area",
    "atividade_principal",
    "jornada_trabalho",
    "faixa_renda",
    "tem_filhos",
    "quantos_filhos",
    "pratica_atividade_fisica",
    "qual_atividade_fisica",
    "possui_computador",
    "acesso_internet",
    "dificuldade_tecnologia",
    "meio_transporte",
    "dificuldade_frequencia",
    "forma_alimentacao",
    "meio_comunicacao",
    "meio_divulgacao",
    "segue_redes_sociais",
]
