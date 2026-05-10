# Havenbeheer — Inkoop: Procesoverzicht

*Validatiesessie · Alle weergegeven stappen en regels zijn aannames ter bevestiging*

---

## Deel 1 — Inkoopverzoek (IV): goedkeuringscyclus

```mermaid
flowchart TD
    START([Medewerker dient aanvraag in]) --> DEPT_CHECK{Is de indiener zelf afdelingshoofd?}

    DEPT_CHECK -- Ja: stap overgeslagen --> PROC_CHECK
    DEPT_CHECK -- Nee --> DEPT[Afdelingshoofd beoordeelt en keurt goed of wijst af]

    DEPT -- Goedgekeurd --> PROC_CHECK{Is de indiener lid van Inkoop?}
    DEPT -- Afgewezen --> REJECTED([Afgewezen])

    PROC_CHECK -- Ja: altijd naar Directeur --> DIR
    PROC_CHECK -- Nee --> PROC[Inkoop controleert offerte voert totaalbedrag en valuta in voegt offertedocument toe]

    PROC -- Goedgekeurd --> THRESHOLD{Totaal in USD boven drempelwaarde?}
    PROC -- Afgewezen --> REJECTED

    THRESHOLD -- Nee: automatisch goedgekeurd --> APPROVED
    THRESHOLD -- Ja --> DIR[Directeur geeft finale goedkeuring of wijst af]

    DIR -- Goedgekeurd --> APPROVED([Aanvraag goedgekeurd Inkoop kan bestelling aanmaken])
    DIR -- Afgewezen --> REJECTED

    style APPROVED fill:#dcfce7,stroke:#4ade80,color:#14532d
    style REJECTED fill:#fee2e2,stroke:#fca5a5,color:#991b1b
    style START fill:#dbeafe,stroke:#93c5fd,color:#1e40af
    style DEPT fill:#dcfce7,stroke:#86efac,color:#166534
    style PROC fill:#fff7ed,stroke:#fdba74,color:#9a3412
    style DIR fill:#f3e8ff,stroke:#d8b4fe,color:#6b21a8
```

### Kortere routes en uitzonderingen

| Situatie | Wat er gebeurt |
|---|---|
| Indiener is zelf het afdelingshoofd | Stap "Afdelingshoofd" overgeslagen → direct naar Inkoop |
| Indiener is lid van de Inkoopsdienst | Stap "Inkoop" overgeslagen → altijd naar Directeur, ongeacht bedrag |
| Indiener is hoofd van de Inkoopsdienst | Beide stappen overgeslagen → direct naar Directeur |
| IV doorbelast aan goedgekeurd project én past binnen resterend budget | ⚠ Directeurstap overgeslagen, ook boven drempelwaarde — **ter bevestiging** |

### Wanneer mag de indiener annuleren?

| Status van het verzoek | Annuleren toegestaan? |
|---|---|
| Concept | ✓ Ja |
| Wacht op afdelingshoofd | ✓ Ja |
| Teruggestuurd door afdelingshoofd of Inkoop | ✓ Ja |
| Teruggestuurd door Directeur | ✗ Nee — Inkoop heeft al goedgekeurd |
| Bij Inkoop of Directeur ter beoordeling | ✗ Nee |
| Goedgekeurd / afgewezen / geannuleerd | ✗ Nee — definitief afgesloten |

---

## Deel 2 — Bestelling (BO): uitvoeringscyclus

```mermaid
flowchart TD
    PR_OK([Inkoopverzoek goedgekeurd]) --> PO_CREATE[Inkoop maakt bestelling aan, voegt regels toe: omschrijving,hoeveelheid, eenheidsprijs]

    PO_CREATE --> BUDGET_CHECK{Budgetcontrole bij verzenden: cumulatief BO-totaal vs. bedrag van inkoopverzoek?}

    BUDGET_CHECK -- "Binnen bedrag: normaal" --> PO_SEND
    BUDGET_CHECK -- "> 110%: geblokkeerd" --> BLOCKED([Geblokkeerd — nieuwe IV vereist])
    WARN --> PO_SEND
    BUDGET_CHECK -- "101–110%: waarschuwing" --> WARN[Toelichting verplicht. Directeur + Financiën geïnformeerd]
    

    PO_SEND[Inkoop verzendt bestelling naar leverancier als PDF] --> CONFIRM{Leverancier bevestigt?optionele stap}

    CONFIRM --> RECEIVE[Goederen ontvangen. Inkoop registreert hoeveelheid per regel. Deelleveringen mogelijk]

    RECEIVE --> INV[Inkoop ontvangt factuur van leverancier en stuurt door naar Financiën]

    INV --> ALL_REC{Alle regels volledig ontvangen?}
    ALL_REC -- Nee: deellevering --> RECEIVE
    ALL_REC -- Ja: systeem meldt Inkoop --> COMPLETE[Inkoop controleert\nen sluit bestelling af]

    INV --> FINANCE[Financiën verwerkt betaling\naan leverancier\nregistreert betaalstatus]

    COMPLETE --> DONE([Bestelling afgerond\nvergrendeld voor wijzigingen])
    FINANCE -.-> DONE

    style DONE fill:#dcfce7,stroke:#4ade80,color:#14532d
    style BLOCKED fill:#fee2e2,stroke:#fca5a5,color:#991b1b
    style PR_OK fill:#dcfce7,stroke:#4ade80,color:#14532d
    style FINANCE fill:#e0f2fe,stroke:#7dd3fc,color:#075985
    style INV fill:#e0f2fe,stroke:#7dd3fc,color:#075985
    style PO_CREATE fill:#fff7ed,stroke:#fdba74,color:#9a3412
    style PO_SEND fill:#fff7ed,stroke:#fdba74,color:#9a3412
    style COMPLETE fill:#fff7ed,stroke:#fdba74,color:#9a3412
    style RECEIVE fill:#fff7ed,stroke:#fdba74,color:#9a3412
```

### Statuswaarden bestelling

| Status | Betekenis |
|---|---|
| `concept` | Aangemaakt, nog niet verzonden |
| `verzonden` | Verstuurd naar leverancier |
| `bevestigd` | Leverancier heeft bevestigd (optioneel) |
| `gedeeltelijk_ontvangen` | Minimaal één regel deels ontvangen |
| `ontvangen` | Alle regels volledig ontvangen — nog af te sluiten |
| `afgerond` | Inkoop heeft afgesloten — vergrendeld |
| `gesloten` | Afgesloten met reden — vergrendeld |
| `geannuleerd` | Ingetrokken vóór verzending |

---

## Diagrammen aanpassen

De diagrammen zijn geschreven in **Mermaid**. U kunt ze live bewerken op [mermaid.live](https://mermaid.live) — plak de code van een diagram, pas aan en kopieer terug.

Basisnotatie:

| Syntax | Betekenis |
|---|---|
| `[Tekst]` | Stap (rechthoek) |
| `{Tekst}` | Beslissing (ruit) |
| `([Tekst])` | Begin- of eindpunt (ovaal) |
| `A --> B` | Pijl van A naar B |
| `A -- Label --> B` | Pijl met label |
| `A -. Label .-> B` | Gestippelde pijl |
| `style X fill:#kleur,stroke:#rand` | Kleur van een knoop aanpassen |
