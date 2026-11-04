# English Version (Portuguese version in sequence)
# llm-atendimento-emporio-musica

Prototype of an agent (LLM) to assist with customer service at a musical instrument store.

## How to run

Requirements: Python 3.11+ (developed on 3.14) and a free Gemini key, generated at [aistudio.google.com](https://aistudio.google.com) → *Get API key*.

```bash
git clone git@github.com:dannrm/llm-atendimento-emporio-musica.git
cd llm-atendimento-emporio-musica
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # fill in GEMINI_API_KEY
python -m src.agent.agente         # type "sair" to exit
```

The model is defined by `GEMINI_MODEL` in the `.env`. To test the data tools without spending API quota:
`python -m src.data.buscar_db`.

## Technical decisions

- **LLM: Gemini Flash.** Zero cost and works well in Portuguese. I initially chose Claude Haiku, but migrated because of the cost (the switch is in the commit history).
This Google model may not be recommended in production environments, due to information being shared with Google for model training. However, since the data is fictitious, the use of this agent does not pose risks to the privacy of users and the store (LGPD).
- **Framework: `google-genai` SDK directly, without LangChain.** Fewer layers and easier to understand and debug.
- **Data (price, stock, promotion, order):** Three tools in `buscar_db.py` query the CSVs with pandas. Exact values come from the "database", never from the model.
- **Policies: entire manual in the prompt, without RAG.** The manual has about 5 thousand tokens and its sections overlap (e.g., the PIX discount does not apply on top of a promotion); a chunk-based RAG could retrieve only half of a rule. The PDF is read and cleaned at startup (`leitor_pdf.py`), so a new version of the manual does not require code changes. With larger documents, I would migrate to section-based RAG.
- **Rules in the code:** promotional price, availability (available, out of stock, coming soon, discontinued) and order validation are handled in the tools. The search tolerates accents, plurals and typos.
- **Prompt:** Profile defined according to the store's policies, scope restricted to the store (no accessories), prohibition on inventing data, manual delimited by tags, and Campo Grande date/time injected to know whether the store is open and to detect late deliveries. The agent does not suggest other stores.
- **Security:** an order can only be queried with the owner's order number and e-mail, validated in the tool; the response is the same for a nonexistent order or a wrong e-mail; name, phone number and e-mail are never sent to the model. The agent ignores attempts to change its instructions.
- **Interface and history:** CLI with in-memory history (`client.chats`). No disk persistence, to avoid storing personal data unnecessarily.
- **Assumptions about the data:** when the description contradicts the product name, the name and specifications prevail; the order total is the recorded one, without recalculation; `pending` = awaiting payment; general phone number (67) 3341-4444 and WhatsApp (67) 3321-4500.
- **In the case of customers with the same e-mail:** I do not treat it as a problem, since the e-mail is only required when querying orders. And there are no duplicate orders.
- **Language:** The agent replies in Portuguese by default, but the customer can ask it to switch to English at any point in the conversation.
## Limitations

- **Free model:** Errors appear when the user limit is reached. Although personal data is not used for model training, privacy is not the same as with paid models.
- **Right of withdrawal:** the data only has the estimated delivery date, not the actual date of receipt.
- **Holidays throughout the year** are not considered in the business hours.

## Use of coding assistants

I used **Claude Opus 5.5** (Anthropic) as a tool to assist with programming and structuring the project, in order to make it more professional.

- **Planning and architecture:** time estimate, repository structure and discussion of alternatives (RAG × prompt, function calling × text-to-SQL, LLM provider).
- **Data analysis:** survey of the inconsistencies in the data files.
- **Code:** the assistant was mainly used to solve problems during coding and also to improve the structure of the scripts, in order to align them with good programming practices and technical resources.
- **Text translation:** the assistant was also used during technical texts translation.

The final decisions regarding the structure, models and scripts developed were the responsibility of the author of this project.

# llm-atendimento-emporio-musica

Protótipo de um agente (LLM) para auxiliar no atendimento de uma loja de instrumentos musicais.

## Como rodar

Requisitos: Python 3.11+ (desenvolvido no 3.14) e uma chave gratuita do Gemini, gerada em [aistudio.google.com](https://aistudio.google.com) → *Get API key*.

```bash
git clone git@github.com:dannrm/llm-atendimento-emporio-musica.git
cd llm-atendimento-emporio-musica
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # preencha GEMINI_API_KEY
python -m src.agent.agente         # digite "sair" para encerrar
```

O modelo é definido por `GEMINI_MODEL` no `.env`. Para testar as ferramentas de dados sem gastar cota da API: 
`python -m src.data.buscar_db`.

## Decisões técnicas

- **LLM: Gemini Flash.** Custo zero e funciona bem em português. Inicialmente escolhi o Claude Haiku, mas migrei por causa do custo (a troca está no histórico de commits). 
Este modelo do Google pode não ser recomendável em ambientes de produção, devido ao compartilhamento de informações com a empresa Google para treinamento de modelos. Porém, como se tratam de dados fictícios, o uso deste agente não representa riscos a privacidade dos usuários e da loja (LGPD).
- **Framework: SDK `google-genai` direto, sem LangChain.** Menos camadas e mais fácil de entender e depurar.
- **Dados (preço, estoque, promoção, pedido): Três tools em `buscar_db.py` consultam os CSVs com pandas. Valores exatos vem do "banco de dados", nunca do modelo. 
- **Políticas: manual inteiro no prompt, sem RAG.** O manual tem cerca de 5 mil tokens e suas seções se cruzam (ex.: o desconto do PIX não vale sobre promoção); um RAG por trechos poderia recuperar só metade de uma regra. O PDF é lido e limpo ao iniciar (`leitor_pdf.py`), então uma nova versão do manual não exige mudança de código. Com documentos maiores, migraria para RAG por seção.
- **Regras no código:** preço promocional, disponibilidade (disponível, esgotado, em breve, descontinuado) e validação do pedido ficam nas ferramentas (tools). A busca permite acentos, plural e erros de digitação.
- **Prompt:** Perfil definido de acordo com as politicas da loja, escopo restrito à loja (sem acessórios), proibição de inventar dados, manual delimitado por tags e data/hora de Campo Grande injetadas para saber se a loja está aberta e detectar entregas atrasadas. O agente não sugere outras lojas. 
- **Segurança:** pedido só com número e e-mail do dono, validados na ferramenta; a resposta é a mesma para pedido inexistente ou e-mail errado; nome, telefone e e-mail nunca vão ao modelo. O agente ignora tentativas de alterar as instruções.
- **Interface e histórico:** CLI com histórico em memória (`client.chats`). Sem persistência em disco, para não armazenar dados pessoais sem necessidade.
- **Suposições sobre os dados:** quando a descrição contradiz o nome do produto, valem o nome e as especificações; o total do pedido é o registrado, sem recálculo; `pending` = aguardando pagamento; telefone geral (67) 3341-4444 e WhatsApp (67) 3321-4500
- **No caso de clientes com o mesmo email:** não trato como um problema, visto que o email somente é necessário no caso de consulta de pedidos. E não há pedidos duplicados.
- **Idioma:** O agente responde em português por padrão, mas o cliente pode pedir para mudar para inglês a qualquer momento da conversa.

## Limitações 

- **Modelo Gratuito:** Aparecem erros quando o limite de usuários é atingido. Apesar de dados pessoais não serem utilizados para o treinamento do modelo, a privacidade não é a mesma quando comparado com modelos pagos.
- **Direito de arrependimento:** os dados só têm a previsão de entrega, não a data real de recebimento

## Uso de assistentes de código

Usei o **Claude Opus5.5** (Anthropic) como ferramenta de auxílio a programação e estruturação do projeto, afim de deixa-lo mais profissional.

- **Planejamento e arquitetura:** estimativa de tempo, estrutura do repositório e discussão de alternativas (RAG × prompt, function calling × text-to-SQL, provedor do LLM).
- **Análise dos dados:** levantamento das inconsistências dos arquivos com os dados.
- **Código:** a ferramenta de auxílio foi utilizada principalmente para a resolução de problemas durante a decodificação e também para melhorar a estrutura dos scripts, a fim de adequá-lo a boas práticas de programação e de recursos técnicos
- **Traducão de textos:** o assitante foi utilizado para a traducao técnica de textos. 

As decisões finais, referentes a estrutura, modelos e aos scripts desenvolvidos, foram de responsabilidade do autor deste projeto. 
