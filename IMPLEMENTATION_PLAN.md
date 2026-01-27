# Remarkable OCR — Implementation Status

## Waar staan we nu (kort)
- **Env‑only status pagina** actief (GUI is read‑only status in env‑mode).
- **Persistente opslag** (SQLite) voor config + processed messages is live.
- **Fail‑fast startup** bij ongeldige `.env`.
- **IMAP flagging** (`MARK_AS_READ=true`) na verwerking.
- **Robuuste polling** via APScheduler.

## Nog te doen (prioriteit)

### P1 (aanbevolen)
- [ ] **Retries + backoff** voor OCR en SMTP.
- [ ] **Observability**: structured logs + metrics + uitgebreid `/health`.
- [ ] **Test suite**: unit + integration (IMAP/SMTP mocks) + e2e.
- [ ] **Test matrix** aanvullen (restart + duplicate processing).

### P2 (nice‑to‑have)
- [ ] **Deployment**: Docker + compose + systemd service.
- [ ] **UI polish**: status/details per job + basis grafieken.
- [ ] **Rate limiting** op API routes.

## Open beslissingen
- Polling interval defaults in `.env` blijven of dynamic via UI?
- Logging naar file standaard aan in headless deployments?

## Laatste wijzigingen (samenvatting)
- SQLite storage laag + processing state.
- Polling scheduler (APScheduler) in plaats van ad‑hoc tasks.
- Status dashboard in env‑mode (laatste 20 verwerkte items).

---

## ARCHIEF (verwijderd voor overzicht)
Alle oude microstappen en gedetailleerde implementatie‑logica zijn verwijderd
om dit plan leesbaar te houden. Zie git‑history voor details.
