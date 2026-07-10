# DENDRO MARKET Bug Bounty Lab · Versión Maestría

Laboratorio local para la Sesión 9: Control de Acceso Avanzado.

## Instalación

```bash
pip install -r requirements.txt
python app.py
```

Abrir:

```text
http://127.0.0.1:5009
```

## Cuentas

| Usuario | Contraseña | Rol |
|---|---|---|
| alice | Alice123! | student |
| bob | Bob123! | student |
| nora | Nora123! | student |
| carol | Carol123! | teacher |
| admin | Admin123! | admin |

## Archivos importantes

- `GUIA_ALUMNO.md`: entregar a los estudiantes.
- `GUIA_DOCENTE.md`: no entregar al inicio, contiene soluciones y proofs.
- `docs/api_public_collection.json`: colección parcial para reconocimiento.

## Objetivo

Encontrar, reproducir y reportar fallas de control de acceso tipo bug bounty:

- IDOR / BOLA.
- BFLA.
- Tenant bypass.
- Mass Assignment.
- Escalamiento de privilegios.
- Exposición de logs.

## Ajuste visual sobrio

Esta entrega usa una interfaz sobria para aula: sin brillos, sin fondos radiales, sin sombras luminosas y con el pie de página anclado al fondo de la ventana cuando el contenido es corto. El laboratorio técnico se mantiene enfocado en Control de Acceso Avanzado, IDOR, BOLA, BFLA, Mass Assignment y escalamiento de privilegios.
