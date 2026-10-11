# Fratelli Commerce v2 — Gestão Interna

MVP Streamlit para catálogo, inventário e registo manual de atendimentos.

## Inclui
- Catálogo de produtos e preços de referência.
- Entradas e saídas de estoque com histórico.
- Registo manual de atendimentos recebidos por Instagram, WhatsApp Business, e-mail, telefone ou outro canal.
- Estados de atendimento: Novo, Em atendimento e Encerrado.
- Responsável interno, notas e histórico de alterações.
- Exportação CSV do catálogo, movimentações e atendimentos.

## Limites desta versão
- Não está ligada às APIs do Instagram ou WhatsApp e não envia mensagens.
- Não processa vendas, pagamentos, faturação ou expedição.
- Não possui autenticação multiutilizador.
- Usa SQLite local, que pode não persistir em ambientes cloud.

## Executar no Windows PowerShell
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Antes de usar com dados reais, configure autenticação, banco de dados PostgreSQL gerido, backups, controlo de acesso e revisão de privacidade/LGPD.
