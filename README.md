# Fratelli Gestão Interna v4 — acesso e auditoria

## Incluído
- Login individual configurado via Streamlit Community Cloud Secrets.
- Perfis `admin` e `user`; operações de alteração e backups exigem perfil `admin`.
- Auditoria inclui o utilizador autenticado.
- Migração da tabela de auditoria v3 para acrescentar a coluna `actor`.
- Mantém catálogo, estoque, atendimento, exportação e backup SQLite.

## Configurar utilizadores
1. Faça download do banco atual ou crie backup antes de atualizar.
2. Execute localmente `python gerar_credenciais.py` para cada utilizador.
3. Copie cada bloco produzido para **Streamlit Community Cloud → App → Settings → Secrets**.
4. Exemplo estrutural (não use estes valores literalmente):
   ```toml
   [users.admin]
   salt = "salt_hex_gerado"
   password_hash = "hash_gerado"
   role = "admin"

   [users.operador]
   salt = "outro_salt_hex"
   password_hash = "outro_hash"
   role = "user"
   ```
5. Não coloque palavras-passe nem `secrets.toml` no GitHub.

## Persistência de dados — importante
Esta versão ainda usa SQLite. No Streamlit Community Cloud, o sistema de arquivos local pode não ser persistente após reinícios ou redeploys. Login e auditoria não resolvem isso. Antes de depender da aplicação em produção, configure um banco gerido persistente (por exemplo PostgreSQL/Supabase) e migre o SQLite de forma controlada, com backup e validação. Esta entrega **não** faz migração automática para PostgreSQL.
