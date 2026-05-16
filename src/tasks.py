"""Definição das 3 tarefas do domínio e-commerce."""

TAREFAS: dict[str, dict] = {
    "classificacao": {
        "nome": "Classificação de Sentimento",
        "descricao": "Classifica avaliações de clientes em POSITIVO, NEGATIVO ou NEUTRO.",
        "instrucao": (
            "Analise o texto da avaliação do cliente e classifique o sentimento "
            "como exatamente uma das opções: POSITIVO, NEGATIVO ou NEUTRO. "
            "Considere o tom geral, palavras-chave e contexto da mensagem."
        ),
        "contexto": (
            "Plataforma de e-commerce brasileira. As avaliações são escritas por clientes "
            "após receberem seus pedidos. A classificação será usada para priorizar "
            "atendimento e análise de qualidade."
        ),
        "formato_saida": (
            "Responda com JSON: {\"sentimento\": \"POSITIVO|NEGATIVO|NEUTRO\", "
            "\"confianca\": 0.0-1.0, \"justificativa\": \"breve explicação\"}"
        ),
        "rotulos_validos": ["POSITIVO", "NEGATIVO", "NEUTRO"],
        "passos_raciocinio": [
            "Identifique palavras com carga emocional positiva ou negativa.",
            "Avalie se o cliente menciona problemas objetivos (entrega, produto, suporte).",
            "Pondere o tom geral: crítica construtiva pode ser NEUTRO.",
            "Determine o sentimento dominante e estime sua confiança (0-1).",
        ],
    },

    "extracao": {
        "nome": "Extração de Entidades",
        "descricao": "Extrai número de pedido, data, valor e intenção de mensagens de suporte.",
        "instrucao": (
            "Extraia as seguintes entidades da mensagem de suporte ao cliente: "
            "número do pedido, data da compra, valor pago e intenção do cliente. "
            "Se alguma entidade não estiver presente, use null."
        ),
        "contexto": (
            "Sistema de suporte ao cliente de e-commerce. Mensagens chegam por chat, "
            "e-mail e WhatsApp. A extração alimenta automações de CRM e triagem de tickets."
        ),
        "formato_saida": (
            "Responda com JSON: {\"numero_pedido\": \"#XX-0000 ou null\", "
            "\"data_compra\": \"DD/MM/AAAA ou null\", "
            "\"valor\": \"R$0,00 ou null\", "
            "\"intencao\": \"cancelamento|devolucao|rastreamento|nota_fiscal|outro\"}"
        ),
        "rotulos_validos": ["cancelamento", "devolucao", "rastreamento", "nota_fiscal", "outro"],
        "passos_raciocinio": [
            "Procure padrões de número de pedido (ex: #XX-0000).",
            "Identifique datas no formato brasileiro DD/MM/AAAA.",
            "Localize valores monetários precedidos de R$.",
            "Infira a intenção do cliente pelo verbo principal da solicitação.",
        ],
    },

    "geracao": {
        "nome": "Geração de Descrição de Produto",
        "descricao": "Gera descrições persuasivas de produtos para e-commerce.",
        "instrucao": (
            "Crie uma descrição de produto para e-commerce em português brasileiro. "
            "A descrição deve ser persuasiva, destacar os benefícios principais, "
            "usar linguagem acessível e terminar com uma chamada para ação. "
            "Máximo de 80 palavras."
        ),
        "contexto": (
            "Marketplace B2C brasileiro com público variado (18-55 anos). "
            "As descrições aparecem em páginas de produto, e-mails marketing e anúncios. "
            "Alta conversão é o objetivo principal."
        ),
        "formato_saida": (
            "Retorne apenas o texto da descrição, sem marcações, entre 50 e 80 palavras. "
            "Inclua o nome do produto, categoria, preço e pelo menos 2 benefícios."
        ),
        "rotulos_validos": [],
        "passos_raciocinio": [
            "Identifique o público-alvo pelo tipo de produto e categoria.",
            "Liste os benefícios mais relevantes para esse público.",
            "Escolha um gatilho emocional adequado (segurança, status, praticidade).",
            "Estruture: benefício principal → detalhes → preço → CTA.",
        ],
    },
}
