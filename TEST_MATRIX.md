# Test Matrix

Deze matrix beschrijft handmatige en geautomatiseerde scenario's om regressies te voorkomen.
Focus op **restart** gedrag en **duplicate processing**.

## Legend
- Type: manual / automated
- Env: gui / env / hybrid

## Core scenarios

1) **Restart: persistente state**
   - Type: manual
   - Env: env
   - Steps:
     1. Start app met geldige `.env` en `AUTO_START_POLLING=true`.
     2. Laat een email met PDF binnenkomen en wacht op verwerking.
     3. Stop app (`Ctrl+C`) en start opnieuw.
   - Expected:
     - `processed_messages` bevat het eerder verwerkte message_id.
     - `/health` blijft `status=healthy`.
     - Geen dubbele verwerking van dezelfde message_id.

2) **Restart: scheduler herstart**
   - Type: manual
   - Env: gui/env
   - Steps:
     1. Start polling via UI of env auto-start.
     2. Check `/health` → `scheduler_running=true`.
     3. Restart app.
   - Expected:
     - Scheduler start opnieuw (`scheduler_running=true`).
     - Polling hervat zonder errors.

3) **Duplicate processing: IMAP same message_id**
   - Type: automated (unit/integration)
   - Env: n/a
   - Coverage:
     - `config.storage.is_message_processed` en `mark_message_processed` tests.
     - `tests/test_email_handler_imap.py` verwerkt 1x en markeert.
   - Expected:
     - `mark_message_processed` voorkomt dubbel verwerken.

4) **Duplicate processing: restart with same message_id**
   - Type: manual
   - Env: env
   - Steps:
     1. Verwerk een email (zorg voor IMAP message_id).
     2. Restart app.
     3. Laat dezelfde message_id nogmaals zichtbaar zijn (bijv. re‑send of IMAP copy).
   - Expected:
     - Geen dubbele OCR + geen dubbele notificatie.

5) **Duplicate processing: concurrent polls**
   - Type: manual
   - Env: gui
   - Steps:
     1. Start polling.
     2. Trigger meerdere polls vlak na elkaar (of korte interval).
   - Expected:
     - `max_instances=1` voorkomt overlap.
     - Geen dubbele processing.

## Notes
- Voor handmatige stappen kun je `/metrics` gebruiken om counters te controleren.
- Voor storage gedrag kun je de DB inspecteren via `sqlite3 ./data/remarkable.db`.
