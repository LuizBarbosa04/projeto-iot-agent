
# Comparativo Cloud — Projeto IoT Agent

## 1. Problema

Desenvolver uma solução de monitoramento IoT capaz de:

- Receber telemetria de dispositivos simulados.
- Armazenar registros históricos.
- Detectar anomalias automaticamente.
- Utilizar inteligência artificial para interpretar alertas.
- Visualizar estatísticas e gráficos de monitoramento.

## 2. Arquitetura atual

### Backend
- Python
- FastAPI
- Boto3
- Simulador de sensores

### Armazenamento
- Amazon S3 (região us-east-2)
- Arquivos JSON organizados por data
- Identificadores UUID para preservar o histórico

### Monitoramento
- Detecção de anomalias baseada em limites configurados
- Análise histórica de temperatura e umidade
- Estatísticas de média, mínimo e máximo
- Gráficos utilizando Matplotlib

### Inteligência artificial
- Ollama executado localmente
- Modelo Qwen3 8B
- Análise textual de leituras anormais

## 3. Provedores considerados

| Critério | AWS | Azure | Google Cloud |
|---|---|---|---|
| Armazenamento de objetos | S3 | Blob Storage | Cloud Storage |
| Máquinas virtuais | EC2 | Virtual Machines | Compute Engine |
| Banco de dados gerenciado | RDS | Azure Database for PostgreSQL | Cloud SQL |
| Serviços de IA | Bedrock | Azure AI | Vertex AI |

A tabela apresenta serviços equivalentes, não uma comparação
de preços ou desempenho.

## 4. Decisão inicial

A AWS foi escolhida para o protótipo devido à
possibilidade de integração com Python e Boto3,
além da experiência prática com Amazon S3.

O backend e o modelo de IA são executados localmente.
A aplicação ainda não está implantada na nuvem.

## 5. Limitações atuais

- Os sensores são simulados.
- Os limites de anomalias são demonstrativos.
- O processamento histórico é iniciado manualmente.
- Os arquivos JSON são carregados na memória.
- Não existe banco PostgreSQL integrado.
- O modelo de IA depende de uma instância local do Ollama.

## 6. Evoluções planejadas

- Monitoramento automatizado.
- Filtros por dispositivo e período.
- Relatórios históricos com IA.
- Integração com dispositivos ESP32 reais.
- Avaliação de banco de dados PostgreSQL.
- Implantação do backend em infraestrutura cloud.
- Autenticação e controle de acesso.

## 7. Considerações de segurança

- O bucket S3 permanece privado.
- As credenciais AWS não são armazenadas no código.
- O acesso local utiliza um perfil configurado no AWS CLI.
- A aplicação deve utilizar permissões mínimas necessárias.
- Uma implantação futura deverá utilizar mecanismos
  apropriados de autenticação e gerenciamento de credenciais.
