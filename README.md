# Fratelli Commerce — Gestão Interna (MVP)

Aplicação Streamlit para gerir **catálogo e inventário interno** da Cachaça Fratelli.

> Este MVP não processa vendas, checkout, pagamentos, emissão fiscal ou expedição. Antes de qualquer operação comercial, valide os requisitos legais e fiscais aplicáveis no Brasil.

## Funcionalidades

- Catálogo de produtos com SKU, preço de referência e estado ativo/inativo.
- Estoque atual por produto.
- Registo de entradas e saídas com histórico.
- Exportação de catálogo e movimentações para CSV.
- Base de dados SQLite local para desenvolvimento.

## Produtos de demonstração

A base de dados é inicializada com três produtos de demonstração. Os preços são referências editáveis, não uma oferta pública.

## Executar localmente

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

A aplicação abrirá no endereço local apresentado pelo Streamlit.

## Publicar no GitHub

1. Crie um repositório privado no GitHub, por exemplo `fratelli-commerce`.
2. Extraia os ficheiros deste projeto para uma pasta local.
3. Abra o terminal nessa pasta e execute:

```bash
git init
git add .
git commit -m "Initial Fratelli internal inventory MVP"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/fratelli-commerce.git
git push -u origin main
```

Substitua `SEU-USUARIO` pelo seu utilizador GitHub e use a URL real do repositório criado.

## Publicar no Streamlit Community Cloud

1. Envie o código para o GitHub.
2. Entre no Streamlit Community Cloud e ligue a sua conta GitHub.
3. Escolha o repositório, a branch `main` e o ficheiro `app.py`.
4. Clique em Deploy.

## Atenção sobre a base de dados

O SQLite cria `fratelli.db` localmente. Em plataformas cloud, o sistema de ficheiros pode ser temporário e a base de dados pode não ser persistente. Não use este modo como base de dados de produção. Para produção, migre para PostgreSQL gerido e configure backups, autenticação, controlo de acesso e segredos em variáveis de ambiente.

## Segurança e próximos passos

- Adicionar login e perfis de acesso antes de disponibilizar a equipa.
- Migrar SQLite para PostgreSQL antes de produção.
- Criar testes automatizados e rotina de backup.
- Rever obrigações fiscais, LGPD, regras de publicidade e proteção de menores com profissionais qualificados.
