# Vendas Fratelli — Gestão Interna v2 corrigida

Inclui catálogo, movimentação de estoque, histórico, exportação CSV e registo manual de atendimentos.

## Atendimento
Permite registar solicitações recebidas, atribuir responsável e atualizar estados. Não se liga automaticamente às APIs do Instagram/WhatsApp e não envia mensagens.

## Executar no Windows
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Nota: usa SQLite local; para produção, configurar PostgreSQL persistente, autenticação, backups e controlo de acesso. Não armazenar credenciais no código ou no GitHub.
