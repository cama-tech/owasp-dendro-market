# DENDRO MARKET · Guía del alumno

## Misión

Ustedes forman parte de un programa privado de bug bounty. DENDRO MARKET es una plataforma académica simulada. El equipo de desarrollo asegura que la aplicación es segura porque casi todos los endpoints requieren login.

Su misión es comprobar si la aplicación aplica correctamente **autorización por objeto, por función y por organización**.

## Alcance autorizado

- `http://127.0.0.1:5009`
- `http://localhost:5009`

## Prohibido

- Atacar sistemas reales.
- Escanear redes externas.
- Hacer DoS o estrés de recursos.
- Usar fuerza bruta masiva.
- Borrar archivos del equipo anfitrión.
- Modificar el laboratorio para fabricar evidencias.

## Cuentas de prueba

| Usuario | Contraseña | Rol visible |
|---|---|---|
| alice | Alice123! | student |
| bob | Bob123! | student |
| nora | Nora123! | student |
| carol | Carol123! | teacher |
| admin | Admin123! | admin |

> Recomendación: no inicien con admin. Primero comparen lo que puede hacer un usuario normal frente a otro usuario normal.

## Herramientas recomendadas

- Navegador y DevTools.
- Burp Suite Community u OWASP ZAP.
- curl.
- Postman o Insomnia.
- jq para leer JSON.
- Editor de texto para documentar hallazgos.

## Punto de partida

```bash
curl http://127.0.0.1:5009/api/health
```

Login por API:

```bash
curl -X POST http://127.0.0.1:5009/api/login \
-H "Content-Type: application/json" \
-d '{"username":"alice","password":"Alice123!"}'
```

Usen el token recibido así:

```bash
curl http://127.0.0.1:5009/api/me \
-H "Authorization: Bearer TOKEN_AQUI"
```

## Objetivo mínimo

Cada equipo debe entregar al menos tres hallazgos válidos:

1. Uno de acceso a objeto ajeno.
2. Uno de acceso a función no autorizada o escalamiento.
3. Uno con impacto de negocio o exposición sensible.

## Reglas de validación

Un hallazgo cuenta solo si demuestra:

- usuario utilizado;
- endpoint afectado;
- request reproducible;
- respuesta obtenida;
- por qué el acceso no corresponde;
- impacto;
- severidad;
- mitigación.

## Plantilla de reporte

```text
Título:
Resumen:
Activo afectado:
Usuario utilizado:
Pasos de reproducción:
Request:
Respuesta relevante:
Impacto:
Severidad:
Categoría:
Mitigación recomendada:
```

## Pistas de bajo nivel

- Revisen recursos identificados por referencias o códigos.
- Comparen respuestas entre Alice, Bob y Nora.
- Observen si la aplicación confía en parámetros, headers o campos JSON.
- Busquen diferencias entre lo que bloquea la interfaz y lo que realmente bloquea la API.
- No reporten solo una flag o un proof. Expliquen el impacto.
