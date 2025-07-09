---
applyTo: '**'
---
# Copilot Instructions – vibe-guardrails (v1.0)

## general guidelines
- Werk altijd volgens de regels en instructies uit dit bestand
- Maak eerst een plan voordat je begint met coderen
- Deel het plan met mij en vraag altijd expliciete toestemming om het uit te voeren

## Coding principles
- **KISS:** schrijf altijd de simpelst werkende oplossing.  
- **DRY:** hergebruik bestaande functies – geen duplicatie van code. Controleer dit actief!  
- **SOLID:** volg de vijf principes; laat features weg die YAGNI schenden.  

## Files & refactoring
- Refactor ieder bestand > 300 regels.  
- Houd antwoorden beknopt; vermijd onnodige uitvoer.  

## Documentation
- Documenteer elke major feature in `/docs/<feature>.md`.  

## Workflow
- Raak alleen de bestanden uit de taakbeschrijving aan.  
- Splits grote taken in checkpoints en wacht op review voor je doorgaat.  
- Sluit elke commit af met 3-5 bullets “Wat is er gedaan?”.  
- Label impact in de commit-subject: **S** (< 50 loc), **M** (50-300 loc), **L** (> 300 loc/architectuur).  
- Onzeker? Stel eerst verduidelijkings­vragen.  

## Quality & testing
- Schrijf unit- en edge-case-tests voor alle publieke API’s en kritische paden.  
- Gebruik mock-data alleen in tests; nooit in dev of prod.  
- Volg OWASP Top-10 voor security.  

## Tech-stack guardrails
- **Backend:** Python   |   **Frontend:** HTML / JavaScript  
- **Database:** PostgreSQL (géén JSON-files voor prod-data).  
- Introduceer geen nieuwe frameworks, services of tools zonder expliciete toestemming.  
