# Fratelli Gestão Interna v4.1

## Correção principal
Agora pode configurar o primeiro administrador diretamente em Streamlit Community Cloud → Settings → Secrets, sem executar o gerador de credenciais.

Cole nos Secrets, substituindo o texto da palavra-passe por uma palavra-passe forte escolhida por si:

```toml
[users.admin]
password = "SUBSTITUA_PELA_SUA_PALAVRA_PASSE"
role = "admin"
```

Para criar um utilizador de consulta:
```toml
[users.operador]
password = "OUTRA_PALAVRA_PASSE_FORTE"
role = "user"
```

Guarde credenciais apenas em Streamlit Secrets. Nunca publique `secrets.toml` nem credenciais no GitHub. A aplicação também aceita o formato `salt` + `password_hash` da versão 4.

## Instalação
1. Faça backup do banco SQLite atual.
2. Substitua `app.py` no GitHub pelo ficheiro deste pacote.
3. Em Streamlit Community Cloud → Settings → Secrets, cole o bloco acima e substitua o texto da palavra-passe.
4. Guarde e reinicie a aplicação.

## Importante
A versão continua a usar SQLite. Em Streamlit Community Cloud, arquivos locais podem não persistir após reinícios ou redeploys. Faça backup externo e planeie uma migração para banco persistente antes de depender da aplicação em produção.
