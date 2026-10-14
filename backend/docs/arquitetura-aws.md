
# Arquitetura AWS — Projeto IoT Agent

## Objetivo

Simular um dispositivo ESP32 enviando dados de telemetria
para uma API Python, com armazenamento na AWS.

## Arquitetura

ESP32 simulado (Python)
        |
        | HTTP POST /telemetria
        v
FastAPI + Pydantic
        |
        | Boto3 + IAM
        v
Amazon S3 (us-east-2)

## Tecnologias

- Python
- FastAPI
- Pydantic
- Boto3
- AWS IAM
- Amazon S3

## Funcionamento

1. O simulador gera temperatura e umidade.
2. Os dados são enviados via HTTP POST.
3. O FastAPI valida os dados recebidos.
4. Cada leitura recebe um timestamp UTC e um UUID.
5. O Boto3 envia o registro JSON para o S3.
6. A API confirma o armazenamento ao cliente.

## Segurança

- Bucket privado, sem acesso público.
- Autenticação AWS por perfil local.
- Permissões IAM limitadas ao bucket do projeto.
- Credenciais não armazenadas no código-fonte.
- Arquivos .env excluídos pelo .gitignore.

## Organização dos objetos S3

telemetria/AAAA/MM/DD/UUID.json

## Limitações atuais

- O dispositivo ESP32 é simulado.
- A API executa localmente.
- O endpoint GET consulta apenas a memória da aplicação.
- O S3 armazena os registros de forma persistente.

## Próximas melhorias

- Integração com agentes de IA.
- Detecção de anomalias na telemetria.
- Consulta de dados históricos armazenados no S3.
- Implantação da API em ambiente cloud.
