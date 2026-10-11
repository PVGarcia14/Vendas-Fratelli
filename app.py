import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = Path(__import__("os").environ.get("FRATELLI_DB_PATH", str(APP_DIR / "fratelli.db")))
BACKUP_DIR = Path(__import__("os").environ.get("FRATELLI_BACKUP_DIR", str(APP_DIR / "backups")))

st.set_page_config(page_title="Fratelli | Gestão Interna", page_icon="📦", layout="wide")

PRODUCT_SEED = [
    ("FR-MON-700", "Fratelli Montanhas", 166.20, 0, True),
    ("FR-DES-700", "Fratelli Desertos", 162.20, 0, True),
    ("FR-CAN-700", "Fratelli Cânions", 175.20, 0, True),
]

def create_backup():
    """Cria uma cópia consistente do banco SQLite, se ele já existir."""
    if not DB_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"fratelli_backup_{stamp}.db"
    source = sqlite3.connect(DB_PATH)
    target = sqlite3.connect(backup_path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return backup_path


def log_audit(conn, action, entity, details):
    """Registra uma alteração administrativa sem guardar credenciais."""
    conn.execute(
        "INSERT INTO audit_events (action, entity, details, created_at) VALUES (?, ?, ?, ?)",
        (action, entity, str(details)[:1500], datetime.now().isoformat(timespec="seconds"))
    )


def get_audit_events(limit=500):
    with connect() as conn:
        rows = conn.execute(
            "SELECT action, entity, details, created_at FROM audit_events ORDER BY id DESC LIMIT ?",
            (int(limit),)
        ).fetchall()
        return pd.DataFrame([dict(r) for r in rows])


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_support_cases():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM support_cases ORDER BY updated_at DESC").fetchall()
        return pd.DataFrame([dict(r) for r in rows])

def create_support_case(channel, contact_name, contact_handle, topic, summary, assigned_to):
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        cur = conn.execute("""INSERT INTO support_cases
            (channel, contact_name, contact_handle, topic, summary, status, assigned_to, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'Novo', ?, ?, ?)""",
            (channel, contact_name.strip(), contact_handle.strip(), topic, summary.strip(), assigned_to.strip(), now, now))
        case_id = cur.lastrowid
        conn.execute("INSERT INTO support_events (case_id, event_type, details, created_at) VALUES (?, ?, ?, ?)",
                     (case_id, "Caso criado", f"Canal: {channel}; assunto: {topic}", now))
        log_audit(conn, "Criação", "Atendimento", f"caso_id={case_id}; canal={channel}; assunto={topic}")
        return case_id

def update_support_case(case_id, status, assigned_to, note):
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute("UPDATE support_cases SET status=?, assigned_to=?, updated_at=? WHERE id=?",
                     (status, assigned_to.strip(), now, int(case_id)))
        conn.execute("INSERT INTO support_events (case_id, event_type, details, created_at) VALUES (?, ?, ?, ?)",
                     (int(case_id), "Atualização", f"Estado: {status}; responsável: {assigned_to.strip()}; nota: {note.strip()}", now))
        log_audit(conn, "Atualização", "Atendimento", f"caso_id={int(case_id)}; estado={status}; responsável={assigned_to.strip()}")

def get_support_events(case_id):
    with connect() as conn:
        rows = conn.execute("""SELECT event_type, details, created_at FROM support_events
                               WHERE case_id=? ORDER BY id DESC""", (int(case_id),)).fetchall()
        return pd.DataFrame([dict(r) for r in rows])

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                unit_price REAL NOT NULL DEFAULT 0,
                stock_qty INTEGER NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)
        conn.execute("""CREATE TABLE IF NOT EXISTS support_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL, contact_name TEXT NOT NULL, contact_handle TEXT,
            topic TEXT NOT NULL, summary TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Novo',
            assigned_to TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS support_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
            event_type TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES support_cases(id)
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            entity TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            now = datetime.now().isoformat(timespec="seconds")
            conn.executemany(
                "INSERT INTO products (sku, name, unit_price, stock_qty, active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                [(sku, name, price, stock, int(active), now) for sku, name, price, stock, active in PRODUCT_SEED]
            )

def get_products(include_inactive=True):
    with connect() as conn:
        query = "SELECT * FROM products"
        if not include_inactive:
            query += " WHERE active = 1"
        query += " ORDER BY name"
        return pd.DataFrame([dict(r) for r in conn.execute(query).fetchall()])

def get_movements(limit=500):
    with connect() as conn:
        rows = conn.execute("""
            SELECT m.id, p.sku, p.name, m.movement_type, m.quantity, m.note, m.created_at
            FROM stock_movements m
            JOIN products p ON p.id = m.product_id
            ORDER BY m.id DESC LIMIT ?
        """, (limit,)).fetchall()
        return pd.DataFrame([dict(r) for r in rows])

def add_product(sku, name, unit_price, stock_qty, active):
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute(
            "INSERT INTO products (sku, name, unit_price, stock_qty, active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (sku.strip(), name.strip(), float(unit_price), int(stock_qty), int(active), now)
        )
        log_audit(conn, "Cadastro", "Produto", f"SKU={sku.strip()}; nome={name.strip()}; estoque inicial={int(stock_qty)}")

def update_product(product_id, sku, name, unit_price, active):
    with connect() as conn:
        conn.execute(
            "UPDATE products SET sku=?, name=?, unit_price=?, active=? WHERE id=?",
            (sku.strip(), name.strip(), float(unit_price), int(active), int(product_id))
        )
        log_audit(conn, "Edição", "Produto", f"id={int(product_id)}; SKU={sku.strip()}; nome={name.strip()}; ativo={bool(active)}")

def adjust_stock(product_id, delta, note):
    if delta == 0:
        raise ValueError("A quantidade da movimentação não pode ser zero.")
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        row = conn.execute("SELECT stock_qty FROM products WHERE id=?", (int(product_id),)).fetchone()
        if row is None:
            raise ValueError("Produto não encontrado.")
        new_qty = int(row["stock_qty"]) + int(delta)
        if new_qty < 0:
            raise ValueError("O estoque não pode ficar negativo.")
        conn.execute("UPDATE products SET stock_qty=? WHERE id=?", (new_qty, int(product_id)))
        movement_type = "ENTRADA" if delta > 0 else "SAÍDA"
        conn.execute(
            "INSERT INTO stock_movements (product_id, movement_type, quantity, note, created_at) VALUES (?, ?, ?, ?, ?)",
            (int(product_id), movement_type, abs(int(delta)), note.strip(), now)
        )
        log_audit(conn, "Movimentação de estoque", "Estoque", f"produto_id={int(product_id)}; tipo={movement_type}; quantidade={abs(int(delta))}; observação={note.strip()}")

init_db()

st.title("📦 Fratelli | Gestão Interna")
st.caption("MVP administrativo para catálogo e inventário. Não processa vendas, pagamentos, faturação nem expedição.")

products = get_products()
active_products = products[products["active"] == 1] if not products.empty else products
c1, c2, c3 = st.columns(3)
c1.metric("Produtos cadastrados", int(len(products)))
c2.metric("Produtos ativos", int(len(active_products)))
c3.metric("Unidades em estoque", int(products["stock_qty"].sum()) if not products.empty else 0)

tab_catalog, tab_stock, tab_history, tab_support, tab_audit, tab_export = st.tabs(
    ["Catálogo", "Movimentar estoque", "Histórico", "Atendimento", "Auditoria", "Exportar dados"]
)

with tab_catalog:
    st.subheader("Catálogo de produtos")
    if not products.empty:
        display = products[["sku", "name", "unit_price", "stock_qty", "active"]].copy()
        display["active"] = display["active"].map({1: "Sim", 0: "Não"})
        display = display.rename(columns={
            "sku": "SKU", "name": "Produto", "unit_price": "Preço de referência (R$)",
            "stock_qty": "Estoque (un.)", "active": "Ativo"
        })
        st.dataframe(display, use_container_width=True, hide_index=True)
    with st.expander("Cadastrar produto"):
        with st.form("add_product_form", clear_on_submit=True):
            sku = st.text_input("SKU", placeholder="FR-NOVO-700")
            name = st.text_input("Nome do produto")
            price = st.number_input("Preço de referência (R$)", min_value=0.0, step=1.0, format="%.2f")
            stock = st.number_input("Estoque inicial (unidades)", min_value=0, step=1)
            active = st.checkbox("Produto ativo", value=True)
            submitted = st.form_submit_button("Cadastrar")
            if submitted:
                if not sku.strip() or not name.strip():
                    st.error("Preencha SKU e nome do produto.")
                else:
                    try:
                        add_product(sku, name, price, int(stock), active)
                        st.success("Produto cadastrado.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Esse SKU já existe. Use um SKU único.")
    with st.expander("Editar produto existente"):
        if not products.empty:
            options = {f'{r["sku"]} — {r["name"]}': int(r["id"]) for _, r in products.iterrows()}
            selected_label = st.selectbox("Produto", list(options.keys()))
            row = products[products["id"] == options[selected_label]].iloc[0]
            with st.form("edit_product_form"):
                edit_sku = st.text_input("SKU", value=str(row["sku"]))
                edit_name = st.text_input("Nome", value=str(row["name"]))
                edit_price = st.number_input("Preço de referência (R$)", min_value=0.0, value=float(row["unit_price"]), step=1.0, format="%.2f")
                edit_active = st.checkbox("Produto ativo", value=bool(row["active"]))
                edit_submitted = st.form_submit_button("Guardar alterações")
                if edit_submitted:
                    if not edit_sku.strip() or not edit_name.strip():
                        st.error("SKU e nome são obrigatórios.")
                    else:
                        try:
                            update_product(int(row["id"]), edit_sku, edit_name, edit_price, edit_active)
                            st.success("Produto atualizado.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Esse SKU já está atribuído a outro produto.")

with tab_stock:
    st.subheader("Entrada ou saída de estoque")
    if products.empty:
        st.info("Cadastre um produto primeiro.")
    else:
        product_options = {f'{r["sku"]} — {r["name"]} (saldo: {int(r["stock_qty"])})': int(r["id"]) for _, r in products.iterrows()}
        with st.form("stock_form", clear_on_submit=True):
            chosen = st.selectbox("Produto", list(product_options.keys()))
            movement = st.radio("Tipo de movimento", ["Entrada", "Saída"], horizontal=True)
            quantity = st.number_input("Quantidade", min_value=1, step=1)
            note = st.text_input("Observação / referência")
            save = st.form_submit_button("Registar movimento")
            if save:
                delta = int(quantity) if movement == "Entrada" else -int(quantity)
                try:
                    adjust_stock(product_options[chosen], delta, note)
                    st.success("Movimento registado.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

with tab_history:
    st.subheader("Histórico de movimentações")
    history = get_movements()
    if history.empty:
        st.info("Ainda não existem movimentações.")
    else:
        st.dataframe(history.rename(columns={
            "sku": "SKU", "name": "Produto", "movement_type": "Tipo",
            "quantity": "Quantidade", "note": "Observação", "created_at": "Data/hora"
        }).drop(columns=["id"]), use_container_width=True, hide_index=True)

with tab_support:
    st.subheader("Registo de atendimento")
    st.info("Registo manual de solicitações recebidas. Esta versão não se liga automaticamente ao Instagram ou WhatsApp e não envia mensagens. Recolha apenas os dados necessários.")
    with st.expander("Registar novo atendimento"):
        with st.form("support_case_form", clear_on_submit=True):
            channel = st.selectbox("Canal", ["Instagram", "WhatsApp Business", "E-mail", "Telefone", "Outro"])
            contact_name = st.text_input("Nome ou identificação do contacto")
            contact_handle = st.text_input("Identificador público / referência (opcional)")
            topic = st.selectbox("Assunto", ["Informação institucional", "Qualidade do produto", "Entrega existente", "Reclamação", "Privacidade / dados", "Outro"])
            summary = st.text_area("Resumo da solicitação", max_chars=1500)
            assigned_to = st.text_input("Responsável interno (opcional)")
            submitted = st.form_submit_button("Guardar atendimento")
            if submitted:
                if not contact_name.strip() or not summary.strip():
                    st.error("Preencha a identificação e o resumo.")
                else:
                    case_id = create_support_case(channel, contact_name, contact_handle, topic, summary, assigned_to)
                    st.success(f"Atendimento #{case_id} registado.")
                    st.rerun()

    cases = get_support_cases()
    if cases.empty:
        st.info("Ainda não há atendimentos registados.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filtrar por estado", ["Todos", "Novo", "Em atendimento", "Encerrado"])
        with col2:
            channel_filter = st.selectbox("Filtrar por canal", ["Todos"] + sorted(cases["channel"].dropna().unique().tolist()))
        filtered = cases.copy()
        if status_filter != "Todos":
            filtered = filtered[filtered["status"] == status_filter]
        if channel_filter != "Todos":
            filtered = filtered[filtered["channel"] == channel_filter]
        st.dataframe(filtered[["id", "channel", "contact_name", "topic", "status", "assigned_to", "updated_at"]].rename(columns={
            "id": "N.º", "channel": "Canal", "contact_name": "Contacto", "topic": "Assunto",
            "status": "Estado", "assigned_to": "Responsável", "updated_at": "Atualizado em"
        }), use_container_width=True, hide_index=True)

        options = {f'#{int(r["id"])} — {r["contact_name"]} — {r["topic"]}': int(r["id"]) for _, r in cases.iterrows()}
        selected = st.selectbox("Atendimento para atualizar", list(options.keys()))
        selected_id = options[selected]
        current = cases[cases["id"] == selected_id].iloc[0]
        with st.form("update_support_form"):
            status = st.selectbox("Novo estado", ["Novo", "Em atendimento", "Encerrado"],
                                  index=["Novo", "Em atendimento", "Encerrado"].index(str(current["status"])))
            assignee = st.text_input("Responsável", value=str(current["assigned_to"] or ""))
            note = st.text_area("Nota interna", max_chars=1000)
            save_update = st.form_submit_button("Guardar atualização")
            if save_update:
                update_support_case(selected_id, status, assignee, note or "Estado atualizado.")
                st.success("Atendimento atualizado.")
                st.rerun()
        with st.expander("Histórico do atendimento"):
            events = get_support_events(selected_id)
            if not events.empty:
                st.dataframe(events.rename(columns={"event_type": "Evento", "details": "Detalhes", "created_at": "Data/hora"}),
                             use_container_width=True, hide_index=True)

with tab_audit:
    st.subheader("Auditoria de alterações")
    st.caption("Registo administrativo de operações feitas pela aplicação. Não identifica utilizadores porque esta versão ainda não tem login individual.")
    audit = get_audit_events()
    if audit.empty:
        st.info("Ainda não há eventos de auditoria.")
    else:
        st.dataframe(
            audit.rename(columns={
                "action": "Ação", "entity": "Área", "details": "Detalhes", "created_at": "Data/hora"
            }),
            use_container_width=True,
            hide_index=True
        )
        st.download_button(
            "Descarregar auditoria CSV",
            data=audit.to_csv(index=False).encode("utf-8-sig"),
            file_name="fratelli_auditoria.csv",
            mime="text/csv"
        )
    st.divider()
    st.subheader("Cópia de segurança")
    st.write("Cria uma cópia consistente do banco SQLite atual. Guarde também uma cópia fora do servidor.")
    if st.button("Criar backup agora"):
        try:
            backup_path = create_backup()
            if backup_path:
                st.success(f"Backup criado: {backup_path.name}")
                st.download_button(
                    "Descarregar backup criado",
                    data=backup_path.read_bytes(),
                    file_name=backup_path.name,
                    mime="application/octet-stream"
                )
            else:
                st.warning("O banco de dados ainda não existe; não foi criado backup.")
        except Exception as exc:
            st.error(f"Não foi possível criar o backup: {exc}")

with tab_export:
    st.subheader("Exportar dados")
    current_products = get_products()
    current_movements = get_movements()
    current_support = get_support_cases()
    st.download_button(
        "Descarregar catálogo CSV",
        data=current_products.to_csv(index=False).encode("utf-8-sig"),
        file_name="fratelli_catalogo.csv",
        mime="text/csv"
    )
    st.download_button(
        "Descarregar atendimentos CSV",
        data=current_support.to_csv(index=False).encode("utf-8-sig"),
        file_name="fratelli_atendimentos.csv",
        mime="text/csv"
    )
    st.download_button(
        "Descarregar movimentações CSV",
        data=current_movements.to_csv(index=False).encode("utf-8-sig"),
        file_name="fratelli_movimentacoes.csv",
        mime="text/csv"
    )
    current_audit = get_audit_events()
    st.download_button(
        "Descarregar auditoria CSV",
        data=current_audit.to_csv(index=False).encode("utf-8-sig"),
        file_name="fratelli_auditoria.csv",
        mime="text/csv"
    )

st.divider()
st.caption("MVP administrativo. O backup manual e a auditoria ajudam na recuperação e rastreabilidade, mas não substituem armazenamento persistente, autenticação individual, controlo de acesso e backups externos em produção.")
