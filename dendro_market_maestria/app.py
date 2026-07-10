from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from datetime import datetime
import base64
import json
import secrets

app = Flask(__name__)
app.secret_key = "dendro-market-master-lab-secret"

# ==========================================================
# DENDRO MARKET - BUG BOUNTY LAB MAESTRÍA
# Laboratorio local, intencionalmente vulnerable.
# Tema: Broken Access Control avanzado, IDOR/BOLA, BFLA,
# Mass Assignment, tenant bypass y escalamiento de privilegios.
# ==========================================================

USERS = {
    101: {
        "id": 101,
        "username": "alice",
        "password": "Alice123!",
        "role": "student",
        "organization_id": 10,
        "organization": "DENDRO Academy Lima",
        "email": "alice@dendromarket.local",
        "display_name": "Alice Torres",
        "credits": 120,
        "permissions": ["order:read:self", "ticket:read:self"],
        "risk_level": "normal",
        "mfa_enabled": True,
        "is_internal": False,
        "preferences": {"theme": "dark", "language": "es"}
    },
    102: {
        "id": 102,
        "username": "bob",
        "password": "Bob123!",
        "role": "student",
        "organization_id": 10,
        "organization": "DENDRO Academy Lima",
        "email": "bob@dendromarket.local",
        "display_name": "Bob Ramos",
        "credits": 80,
        "permissions": ["order:read:self", "ticket:read:self"],
        "risk_level": "normal",
        "mfa_enabled": False,
        "is_internal": False,
        "preferences": {"theme": "light", "language": "es"}
    },
    208: {
        "id": 208,
        "username": "nora",
        "password": "Nora123!",
        "role": "student",
        "organization_id": 20,
        "organization": "DENDRO Academy Arequipa",
        "email": "nora@dendromarket.local",
        "display_name": "Nora Castillo",
        "credits": 60,
        "permissions": ["order:read:self", "ticket:read:self"],
        "risk_level": "normal",
        "mfa_enabled": True,
        "is_internal": False,
        "preferences": {"theme": "dark", "language": "es"}
    },
    305: {
        "id": 305,
        "username": "carol",
        "password": "Carol123!",
        "role": "teacher",
        "organization_id": 20,
        "organization": "DENDRO Academy Arequipa",
        "email": "carol@dendromarket.local",
        "display_name": "Carol Mendoza",
        "credits": 350,
        "permissions": ["order:read:self", "course:grade", "ticket:read:org"],
        "risk_level": "staff",
        "mfa_enabled": True,
        "is_internal": True,
        "preferences": {"theme": "dark", "language": "es"}
    },
    999: {
        "id": 999,
        "username": "admin",
        "password": "Admin123!",
        "role": "admin",
        "organization_id": 99,
        "organization": "DENDRO HQ",
        "email": "admin@dendromarket.local",
        "display_name": "Administrador DENDRO",
        "credits": 9999,
        "permissions": ["*", "refund:create", "user:read:all", "audit:read:all"],
        "risk_level": "privileged",
        "mfa_enabled": True,
        "is_internal": True,
        "preferences": {"theme": "dark", "language": "es"}
    }
}

COURSES = {
    7101: {"id": 7101, "title": "OWASP API Security", "level": "Intermedio", "price": 120, "tag": "API", "sku": "DM-API-01"},
    7102: {"id": 7102, "title": "Cloud Security Essentials", "level": "Intermedio", "price": 90, "tag": "Cloud", "sku": "DM-CLOUD-02"},
    7103: {"id": 7103, "title": "Secure DevOps Pipeline", "level": "Avanzado", "price": 200, "tag": "DevSecOps", "sku": "DM-DEVOPS-03"},
    7104: {"id": 7104, "title": "IA Security for Web Apps", "level": "Avanzado", "price": 180, "tag": "AI Security", "sku": "DM-AI-04"},
}

ORDERS = {
    84051: {"id": 84051, "public_ref": "DM-ORD-A84", "owner_id": 101, "organization_id": 10, "course_id": 7101, "amount": 120, "status": "paid", "created_at": "2026-06-18 09:30", "payment_last4": "4101"},
    84062: {"id": 84062, "public_ref": "DM-ORD-B62", "owner_id": 102, "organization_id": 10, "course_id": 7102, "amount": 90, "status": "paid", "created_at": "2026-06-18 10:10", "payment_last4": "3320"},
    91021: {"id": 91021, "public_ref": "DM-ORD-N21", "owner_id": 208, "organization_id": 20, "course_id": 7104, "amount": 180, "status": "paid", "created_at": "2026-06-18 13:45", "payment_last4": "8890"},
    97113: {"id": 97113, "public_ref": "DM-ORD-C13", "owner_id": 305, "organization_id": 20, "course_id": 7103, "amount": 200, "status": "paid", "created_at": "2026-06-18 14:20", "payment_last4": "1200"},
}

INVOICES = {
    930011: {"id": 930011, "invoice_ref": "DM-F001-24", "owner_id": 101, "organization_id": 10, "order_id": 84051, "ruc": "10000000001", "customer": "Alice Torres", "amount": 120, "tax": 21.6},
    930012: {"id": 930012, "invoice_ref": "DM-F002-24", "owner_id": 102, "organization_id": 10, "order_id": 84062, "ruc": "10000000002", "customer": "Bob Ramos", "amount": 90, "tax": 16.2},
    930021: {"id": 930021, "invoice_ref": "DM-F021-24", "owner_id": 208, "organization_id": 20, "order_id": 91021, "ruc": "20000000008", "customer": "Nora Castillo", "amount": 180, "tax": 32.4},
}

CERTIFICATES = {
    770091: {"id": 770091, "owner_id": 101, "organization_id": 10, "student": "Alice Torres", "course": "OWASP API Security", "certificate_code": "DENDRO-CERT-A-770091"},
    770092: {"id": 770092, "owner_id": 102, "organization_id": 10, "student": "Bob Ramos", "course": "Cloud Security Essentials", "certificate_code": "DENDRO-CERT-B-770092"},
    770208: {"id": 770208, "owner_id": 208, "organization_id": 20, "student": "Nora Castillo", "course": "IA Security for Web Apps", "certificate_code": "DENDRO-CERT-N-770208"},
}

TICKETS = {
    5011: {"id": 5011, "owner_id": 101, "organization_id": 10, "subject": "Problema con certificado", "message": "No puedo descargar mi certificado.", "internal_note": "Prioridad media. Cliente recurrente.", "status": "open", "messages": []},
    5012: {"id": 5012, "owner_id": 102, "organization_id": 10, "subject": "Solicitud de reembolso", "message": "Deseo devolución del curso Cloud.", "internal_note": "Verificar método de pago antes de aprobar.", "status": "review", "messages": []},
    6021: {"id": 6021, "owner_id": 208, "organization_id": 20, "subject": "Acceso al curso IA", "message": "No aparece mi módulo final.", "internal_note": "Cuenta con descuento institucional.", "status": "open", "messages": []},
}

TOKENS = {}
REFUNDS = []
AUDIT_EVENTS = []

PROOFS = {
    "IDOR_ORDER": "DM-PROOF-01-BOLA-ORDER",
    "IDOR_INVOICE": "DM-PROOF-02-IDOR-INVOICE",
    "IDOR_CERT": "DM-PROOF-03-IDOR-CERT",
    "TENANT_BYPASS": "DM-PROOF-04-TENANT-BYPASS",
    "TICKET_INTERNAL": "DM-PROOF-05-TICKET-INTERNAL",
    "TICKET_WRITE": "DM-PROOF-06-TICKET-WRITE-IDOR",
    "USER_ENUM_DEBUG": "DM-PROOF-07-USER-ENUM-DEBUG",
    "MASS_ASSIGN": "DM-PROOF-08-MASS-ASSIGNMENT",
    "ADMIN_HEADER": "DM-PROOF-09-BFLA-HEADER-ROLE",
    "REFUND_PRIVESC": "DM-PROOF-10-PRIVESC-REFUND",
    "AUDIT_SCOPE": "DM-PROOF-11-AUDIT-SCOPE-BYPASS",
}


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_audit(event_type, actor, detail, severity="info"):
    AUDIT_EVENTS.append({
        "time": now(),
        "event_type": event_type,
        "actor": actor,
        "detail": detail,
        "severity": severity,
        "request_path": request.path,
        "ip": request.remote_addr or "local"
    })


def find_user_by_username(username):
    for user in USERS.values():
        if user["username"] == username:
            return user
    return None


def public_user(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
        "organization_id": user["organization_id"],
        "organization": user["organization"],
        "email": user["email"],
        "credits": user["credits"],
        "mfa_enabled": user["mfa_enabled"],
        "permissions": user["permissions"],
        "is_internal": user["is_internal"],
        "preferences": user["preferences"]
    }


def current_user():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else auth
    uid = TOKENS.get(token)
    if uid:
        return USERS.get(uid)
    session_uid = session.get("user_id")
    if session_uid:
        return USERS.get(session_uid)
    return None


def require_api_user():
    user = current_user()
    if not user:
        return None, (jsonify({"error": "No autenticado"}), 401)
    return user, None


def make_token(user):
    # Token intencionalmente simple para laboratorio, no es la vulnerabilidad principal.
    raw = f"{user['id']}:{user['username']}:{secrets.token_hex(4)}"
    token = "dm_" + base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")
    TOKENS[token] = user["id"]
    return token


def encode_ref(kind, obj_id):
    return base64.urlsafe_b64encode(f"{kind}:{obj_id}".encode()).decode().rstrip("=")


def decode_ref(ref, expected_kind=None):
    try:
        padding = "=" * (-len(ref) % 4)
        raw = base64.urlsafe_b64decode((ref + padding).encode()).decode()
        kind, value = raw.split(":", 1)
        if expected_kind and kind != expected_kind:
            return None
        return int(value)
    except Exception:
        return None


def resolve_order(ref):
    if ref.isdigit():
        return ORDERS.get(int(ref))
    for order in ORDERS.values():
        if order["public_ref"] == ref:
            return order
    decoded = decode_ref(ref, "order")
    if decoded:
        return ORDERS.get(decoded)
    return None


def resolve_invoice(ref):
    if ref.isdigit():
        return INVOICES.get(int(ref))
    for invoice in INVOICES.values():
        if invoice["invoice_ref"] == ref:
            return invoice
    decoded = decode_ref(ref, "invoice")
    if decoded:
        return INVOICES.get(decoded)
    return None


def resolve_certificate(ref):
    if ref.isdigit():
        return CERTIFICATES.get(int(ref))
    decoded = decode_ref(ref, "cert")
    if decoded:
        return CERTIFICATES.get(decoded)
    return None


def course_summary(course_id):
    course = COURSES.get(course_id, {})
    return {"course_id": course_id, "course": course.get("title"), "sku": course.get("sku")}


def can(user, permission):
    return "*" in user.get("permissions", []) or permission in user.get("permissions", [])


@app.route("/")
def index():
    return render_template("index.html", user=current_user(), courses=COURSES)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        user = find_user_by_username(request.form.get("username"))
        if user and user["password"] == request.form.get("password"):
            session["user_id"] = user["id"]
            add_audit("web_login", user["username"], "Inicio de sesión web")
            return redirect(url_for("dashboard"))
        error = "Credenciales inválidas"
    return render_template("login.html", error=error, user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login_page"))
    my_orders = [{**o, **course_summary(o["course_id"]), "encoded_ref": encode_ref("order", o["id"])} for o in ORDERS.values() if o["owner_id"] == user["id"]]
    my_tickets = [t for t in TICKETS.values() if t["owner_id"] == user["id"]]
    my_certs = [{**c, "encoded_ref": encode_ref("cert", c["id"])} for c in CERTIFICATES.values() if c["owner_id"] == user["id"]]
    return render_template("dashboard.html", user=user, my_orders=my_orders, my_tickets=my_tickets, my_certs=my_certs)


@app.route("/market")
def market():
    return render_template("market.html", user=current_user(), courses=COURSES)


@app.route("/bounty")
def bounty():
    return render_template("bounty.html", user=current_user())


@app.route("/admin")
def admin_page():
    user = current_user()
    if not user:
        return redirect(url_for("login_page"))
    if user["role"] != "admin":
        return render_template("admin_denied.html", user=user)
    return render_template("admin.html", user=user, users=USERS, orders=ORDERS, refunds=REFUNDS, audit_events=AUDIT_EVENTS)


@app.route("/docs/<path:filename>")
def docs(filename):
    return send_from_directory("docs", filename)


# ================= API PÚBLICA / AUTENTICACIÓN =================

@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "ok",
        "service": "DENDRO MARKET",
        "version": "2.0-master-lab",
        "environment": "training",
        "docs_hint": "/docs/api_public_collection.json"
    })


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    user = find_user_by_username(data.get("username"))
    if user and user["password"] == data.get("password"):
        token = make_token(user)
        add_audit("api_login", user["username"], "Token API emitido")
        return jsonify({"message": "Login correcto", "token": token, "user": public_user(user)})
    return jsonify({"error": "Credenciales inválidas"}), 401


@app.route("/api/me")
def api_me():
    user, err = require_api_user()
    if err:
        return err
    return jsonify(public_user(user))


@app.route("/api/catalog")
def api_catalog():
    return jsonify(list(COURSES.values()))


# ================= API DE NEGOCIO CON FALLAS DE AUTORIZACIÓN =================

@app.route("/api/my/orders")
def api_my_orders():
    user, err = require_api_user()
    if err:
        return err
    result = []
    for o in ORDERS.values():
        if o["owner_id"] == user["id"]:
            result.append({**o, **course_summary(o["course_id"]), "encoded_ref": encode_ref("order", o["id"])})
    return jsonify({"orders": result})


@app.route("/api/orders/search")
def api_order_search():
    user, err = require_api_user()
    if err:
        return err
    q = (request.args.get("q") or "").lower()
    # VULNERABLE: búsqueda global filtra metadatos de otros usuarios y revela referencias.
    results = []
    for o in ORDERS.values():
        course = COURSES.get(o["course_id"], {})
        owner = USERS[o["owner_id"]]
        if not q or q in course.get("title", "").lower() or q in o["public_ref"].lower():
            results.append({
                "public_ref": o["public_ref"],
                "encoded_ref": encode_ref("order", o["id"]),
                "course": course.get("title"),
                "owner_hint": owner["display_name"][0] + "***",
                "organization_id": o["organization_id"],
                "status": o["status"]
            })
    return jsonify({"results": results, "note": "Search endpoint for customer support portal"})


@app.route("/api/orders/<path:order_ref>")
def api_order_detail(order_ref):
    user, err = require_api_user()
    if err:
        return err
    order = resolve_order(order_ref)
    if not order:
        return jsonify({"error": "Orden no encontrada"}), 404
    payload = {**order, **course_summary(order["course_id"]), "encoded_invoice_ref": None}
    for inv in INVOICES.values():
        if inv["order_id"] == order["id"]:
            payload["encoded_invoice_ref"] = encode_ref("invoice", inv["id"])
            payload["invoice_ref"] = inv["invoice_ref"]
    # VULNERABLE: devuelve el objeto aunque no pertenezca al usuario.
    if order["owner_id"] != user["id"]:
        payload["proof"] = PROOFS["IDOR_ORDER"]
        add_audit("suspicious_order_access", user["username"], f"Accedió orden ajena {order['id']}", "warning")
    return jsonify(payload)


@app.route("/api/billing/invoices/<path:invoice_ref>")
def api_invoice_detail(invoice_ref):
    user, err = require_api_user()
    if err:
        return err
    invoice = resolve_invoice(invoice_ref)
    if not invoice:
        return jsonify({"error": "Comprobante no encontrado"}), 404
    payload = dict(invoice)
    payload["encoded_ref"] = encode_ref("invoice", invoice["id"])
    # VULNERABLE: no valida owner_id ni organization_id.
    if invoice["owner_id"] != user["id"]:
        payload["proof"] = PROOFS["IDOR_INVOICE"]
        add_audit("suspicious_invoice_access", user["username"], f"Accedió invoice ajeno {invoice['id']}", "warning")
    return jsonify(payload)


@app.route("/api/certificates/<path:cert_ref>")
def api_certificate_detail(cert_ref):
    user, err = require_api_user()
    if err:
        return err
    cert = resolve_certificate(cert_ref)
    if not cert:
        return jsonify({"error": "Certificado no encontrado"}), 404
    payload = dict(cert)
    # VULNERABLE: no valida owner_id.
    if cert["owner_id"] != user["id"]:
        payload["proof"] = PROOFS["IDOR_CERT"]
    return jsonify(payload)


@app.route("/api/support/tickets")
def api_my_tickets():
    user, err = require_api_user()
    if err:
        return err
    scope = request.args.get("scope", "mine")
    # VULNERABLE: scope=org y X-Org-ID permite elegir tenant.
    org_id = int(request.headers.get("X-Org-ID", user["organization_id"]))
    if scope == "org":
        selected = [t for t in TICKETS.values() if t["organization_id"] == org_id]
        result = []
        for t in selected:
            item = dict(t)
            if org_id != user["organization_id"]:
                item["proof"] = PROOFS["TENANT_BYPASS"]
            result.append(item)
        return jsonify({"tickets": result, "scope": scope, "trusted_org_header": org_id})
    return jsonify({"tickets": [t for t in TICKETS.values() if t["owner_id"] == user["id"]]})


@app.route("/api/support/tickets/<int:ticket_id>")
def api_ticket_detail(ticket_id):
    user, err = require_api_user()
    if err:
        return err
    ticket = TICKETS.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket no encontrado"}), 404
    payload = dict(ticket)
    # VULNERABLE: filtra por org confiando en X-Org-ID, no en el usuario real.
    header_org = int(request.headers.get("X-Org-ID", user["organization_id"]))
    if ticket["organization_id"] == header_org:
        if ticket["owner_id"] != user["id"]:
            payload["proof"] = PROOFS["TICKET_INTERNAL"]
        return jsonify(payload)
    return jsonify({"error": "No autorizado para esta organización"}), 403


@app.route("/api/support/tickets/<int:ticket_id>/messages", methods=["POST"])
def api_ticket_message(ticket_id):
    user, err = require_api_user()
    if err:
        return err
    ticket = TICKETS.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket no encontrado"}), 404
    data = request.json or {}
    msg = {
        "from": user["username"],
        "text": data.get("text", ""),
        "time": now()
    }
    # VULNERABLE: cualquier autenticado puede escribir en cualquier ticket.
    ticket["messages"].append(msg)
    add_audit("ticket_message", user["username"], f"Mensaje en ticket {ticket_id}")
    payload = {"message": "Mensaje registrado", "ticket_id": ticket_id, "new_message": msg}
    if ticket["owner_id"] != user["id"]:
        payload["proof"] = PROOFS["TICKET_WRITE"]
    return jsonify(payload), 201


@app.route("/api/users")
def api_users():
    user, err = require_api_user()
    if err:
        return err
    include = request.args.get("include")
    if include == "debug":
        # VULNERABLE: parámetro de soporte revela usuarios completos.
        return jsonify({"users": [public_user(u) for u in USERS.values()], "proof": PROOFS["USER_ENUM_DEBUG"]})
    return jsonify({"users": [{"id": u["id"], "display_name": u["display_name"], "organization": u["organization"]} for u in USERS.values() if u["organization_id"] == user["organization_id"]]})


@app.route("/api/account/profile", methods=["PATCH"])
def api_profile_update():
    user, err = require_api_user()
    if err:
        return err
    data = request.json or {}
    before_permissions = list(user.get("permissions", []))
    # VULNERABLE: actualización masiva. Debía permitir solo display_name y preferences.
    user.update(data)
    add_audit("profile_update", user["username"], f"Actualización de perfil: {json.dumps(data)}", "warning")
    payload = {"message": "Perfil actualizado", "user": public_user(user)}
    if user.get("permissions") != before_permissions or "role" in data or "organization_id" in data or "credits" in data:
        payload["proof"] = PROOFS["MASS_ASSIGN"]
    return jsonify(payload)


@app.route("/api/org/reports/monthly")
def api_org_report():
    user, err = require_api_user()
    if err:
        return err
    # VULNERABLE: org_id es controlado por el cliente.
    org_id = int(request.args.get("org_id", user["organization_id"]))
    org_orders = [o for o in ORDERS.values() if o["organization_id"] == org_id]
    total = sum(o["amount"] for o in org_orders)
    result = {
        "organization_id": org_id,
        "orders": len(org_orders),
        "revenue": total,
        "private_breakdown": org_orders
    }
    if org_id != user["organization_id"]:
        result["proof"] = PROOFS["TENANT_BYPASS"]
    return jsonify(result)


# ================= API ADMINISTRATIVA CON FALLAS DE AUTORIZACIÓN =================

@app.route("/api/admin/metrics")
def api_admin_metrics():
    user, err = require_api_user()
    if err:
        return err
    effective_role = user["role"]
    # VULNERABLE: modo preview confía en cabecera enviada por el cliente.
    if request.args.get("preview") == "1" and request.headers.get("X-Dendro-Client") == "admin-console":
        effective_role = request.headers.get("X-Effective-Role", effective_role)
    if effective_role != "admin":
        return jsonify({"error": "Solo administradores"}), 403
    return jsonify({
        "message": "Métricas administrativas",
        "users": len(USERS),
        "orders": len(ORDERS),
        "refunds": len(REFUNDS),
        "proof": PROOFS["ADMIN_HEADER"] if user["role"] != "admin" else "ADMIN-LEGIT"
    })


@app.route("/api/admin/refunds", methods=["POST"])
def api_refund_create():
    user, err = require_api_user()
    if err:
        return err
    data = request.json or {}
    if not can(user, "refund:create"):
        return jsonify({"error": "No autorizado para crear reembolsos"}), 403
    order = resolve_order(str(data.get("order_ref", ""))) or ORDERS.get(int(data.get("order_id", 0) or 0))
    if not order:
        return jsonify({"error": "Orden no encontrada"}), 404
    refund = {
        "id": len(REFUNDS) + 1,
        "order_id": order["id"],
        "amount": data.get("amount", order["amount"]),
        "requested_by": user["username"],
        "status": "approved",
        "created_at": now()
    }
    REFUNDS.append(refund)
    add_audit("refund_created", user["username"], f"Reembolso {refund}", "critical")
    payload = {"message": "Reembolso aprobado", "refund": refund}
    if user["role"] != "admin":
        payload["proof"] = PROOFS["REFUND_PRIVESC"]
    return jsonify(payload), 201


@app.route("/api/audit/events")
def api_audit_events():
    user, err = require_api_user()
    if err:
        return err
    scope = request.args.get("scope", "mine")
    # VULNERABLE: el alcance all es controlado por el cliente.
    if scope == "all":
        return jsonify({"events": AUDIT_EVENTS, "proof": PROOFS["AUDIT_SCOPE"] if user["role"] != "admin" else "ADMIN-AUDIT"})
    return jsonify({"events": [e for e in AUDIT_EVENTS if e["actor"] == user["username"]]})


if __name__ == "__main__":
    app.run(debug=True, port=5009)
