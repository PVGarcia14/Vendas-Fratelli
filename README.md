# Fratelli — Gestão Interna (v3 administrativa)

## O que foi acrescentado
- Aba **Auditoria** para consultar e exportar eventos administrativos.
- Registos de auditoria para cadastro/edição de produtos, movimentações de estoque e alterações de atendimento.
- Botão para criar e descarregar um backup consistente do banco SQLite.
- Variáveis opcionais `FRATELLI_DB_PATH` e `FRATELLI_BACKUP_DIR` para definir caminhos de banco e backup.

## Executar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Importante
- Faça uma cópia do `fratelli.db` atual antes de substituir a aplicação.
- O backup criado pelo botão fica inicialmente na pasta `backups/`. Baixe-o e guarde-o fora do servidor.
- Esta versão ainda não implementa login individual; por isso a auditoria não identifica qual pessoa executou a ação.
- Em hospedagem com disco efêmero, o banco local pode ser perdido. Para produção, configure banco gerido persistente, autenticação e backups externos.
