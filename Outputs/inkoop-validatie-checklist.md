# Havenbeheer — Inkoopsysteem: Validatiechecklist

**Sessiedatum:** \_\_\_\_\_\_\_\_\_\_\_\_\_  
**Aanwezigen:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## Hoe dit document te gebruiken

Dit document beschrijft elk ontwerp- en beleidsuitgangspunt dat ten grondslag ligt aan het nieuwe inkoopsysteem. De meeste punten zijn afgeleid uit de eerste gesprekken en algemeen gebruik — ze zijn nog niet officieel bevestigd.

Ga samen elk punt langs en markeer het als:

- **✓** — Klopt, dit is hoe wij het doen (of willen doen)
- **✗** — Klopt niet — noteer in de kolom *Notities* wat er anders moet
- **?** — Onduidelijk — verdere bespreking nodig

Er is nog niets gebouwd. Alles kan op dit moment nog worden aangepast.

---

## Achtergrond: zo werkt het systeem globaal

Lees dit door voordat u de checklist invult. Het geeft een overzicht van de grote lijnen — de details komen in de checklist zelf.

### Het inkoopverzoek (IV)

Een **inkoopverzoek** is de eerste stap bij elke aankoop. Een medewerker maakt een verzoek aan en legt daarin vast wat er gekocht moet worden, waarom, en of de kosten ten laste komen van een project of een afdeling. Het verzoek gaat vervolgens een goedkeuringsketen door.

De standaard keten ziet er als volgt uit:

1. **Afdelingshoofd** beoordeelt of de aankoop nodig en gerechtvaardigd is.
2. **Inkoop** controleert de offerte (of vraagt er zelf een op), voert het totaalbedrag in, en keurt het verzoek goed of af.
3. **Directeur** geeft finale goedkeuring — maar alleen als het bedrag boven een bepaalde drempelwaarde uitkomt.

De keten heeft ook kortere routes. Als de indiener zelf het afdelingshoofd is, slaat het systeem die stap over. Als de indiener bij de inkoopsdienst werkt, gaat het verzoek altijd naar de directeur, ongeacht het bedrag. Voor projecten met een door de directeur goedgekeurd budget kan de directeursstap automatisch overgeslagen worden als het bedrag binnen het resterende projectbudget past — dit is een aanname die uitdrukkelijk bevestigd moet worden.

Elke goed- of afkeurder kan ook het verzoek **terugsturen naar de indiener** om aanvullende informatie te vragen. De indiener past het aan en dient opnieuw in; het verzoek gaat daarna terug naar dezelfde beoordelaar, niet van voren af aan.

Het verzoek heeft altijd één van deze statussen: *concept*, *wacht op afdelingshoofd*, *bij Inkoop*, *bij Directeur*, *teruggestuurd*, *goedgekeurd*, *afgewezen*, of *geannuleerd*. Alleen de indiener kan een verzoek intrekken, en dat kan alleen zolang het nog niet bij Inkoop of Directeur is beland.

**Wat heeft een indiener nodig om een verzoek in te dienen?** Een titel, omschrijving en motivatie zijn verplicht. Een offerte en prijsopgave zijn *niet* verplicht bij indiening — Inkoop kan dat later aanvullen.

### De bestelling (BO)

Zodra een inkoopverzoek is goedgekeurd, kan Inkoop een **bestelling** aanmaken. Een bestelling is het feitelijke document dat naar de leverancier gaat. Eén goedgekeurd inkoopverzoek kan meerdere bestellingen genereren — bijvoorbeeld als de order over meerdere leveranciers wordt verdeeld.

Een bestelling bevat regelitems met omschrijving, hoeveelheid en prijs. Inkoop maakt de bestelling op, exporteert een PDF en verstuurt die naar de leverancier. Optioneel kan de leveranciersbevestiging worden geregistreerd.

De levering wordt per regel bijgehouden: elke regel heeft een bestelde hoeveelheid en een ontvangen hoeveelheid. Deelleveringen zijn mogelijk. Zodra alle regels volledig ontvangen zijn, sluit Inkoop de bestelling handmatig af.

**Financiën** werkt onafhankelijk van de levering: zij registreren de betaalstatus (onbetaald / vooruitbetaling gedaan / volledig betaald) op elk moment in het proces.

**Budgetbewaking bij bestellingen:** wanneer Inkoop een bestelling *verzendt*, controleert het systeem automatisch of het cumulatieve besteltotaal (alle bestellingen op hetzelfde IV samen) het goedgekeurde bedrag van het inkoopverzoek overschrijdt. Tot 10% overschrijding is toegestaan mits Inkoop een toelichting geeft en de directeur en het hoofd Financiën worden geïnformeerd. Daarboven is de bestelling geblokkeerd en is een nieuw inkoopverzoek nodig.

### Leveranciers

Leveranciers worden centraal beheerd. Alleen Inkoop kan nieuwe leveranciers toevoegen. Als een afdeling met een nieuwe leverancier wil werken, beschrijft de indiener dit in het verzoek — Inkoop handelt de toevoeging af.

### Valuta en wisselkoersen

Verzoeken kunnen worden ingediend in drie valuta (nader te bevestigen). Het USD-equivalent wordt automatisch berekend op basis van wisselkoersen die Financiën handmatig bijhoudt. De definitieve wisselkoers wordt vastgelegd op het moment dat Inkoop hun beoordeling afrondt, niet bij indiening.

---

## Checklist

**Legenda:** ✓ = Klopt · ✗ = Klopt niet (noteer wijziging) · ? = Onduidelijk

> De items gemarkeerd met ⚠ zijn punten waarover bewust nog geen beslissing is genomen en die expliciet besproken moeten worden.

---

### A — Rollen en toegangsrechten

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| A1 | Er zijn vijf soorten gebruikers: medewerkers (indieners), afdelingshoofden, inkoop, directie en financiën. | | |
| A2 | Elke medewerker krijgt automatisch basistoegang: inkoopverzoeken aanmaken en eigen verzoeken inzien. | | |
| A3 | Afdelingshoofden krijgen automatisch extra rechten zodra zij als hoofd van een afdeling worden ingesteld — geen aparte handmatige stap nodig. | | |
| A4 | Alle leden van de Inkoopsdienst delen dezelfde verhoogde toegangsrechten. | | |
| A5 | Alle leden van de Directie delen dezelfde directeursrechten. | | |
| A6 | Financiën kan alle inkoopverzoeken en bestellingen inzien, en kan de betaalstatus op bestellingen bijwerken. Financiën kan geen inkoopverzoeken aanmaken of bewerken. | | |
| A7 | Niemand kan een inkoopverzoek definitief verwijderen uit het systeem. | | |

---

### B — Inkoopverzoek aanmaken en indienen

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| B1 | Elke medewerker (behalve financiën) kan een inkoopverzoek aanmaken. | | |
| B2 | Verplichte velden bij indiening: titel, omschrijving van wat er gekocht wordt, en motivatie (zakelijke rechtvaardiging). Zonder deze drie velden kan het verzoek niet worden ingediend. | | |
| B3 | De indiener moet aangeven of de kosten ten laste komen van een specifiek project of van de afdeling in het algemeen. | | |
| B4 | Als de kosten aan een project worden doorbelast, moet de indiener dat project selecteren. | | |
| B5 | Een offerte (bedrag + document) is **niet** verplicht bij indiening. De indiener kan indienen zonder offerte; Inkoop kan dit later aanvullen. | | |
| B6 | Als de indiener wel een offerte heeft, kan deze optioneel worden bijgevoegd: totaalbedrag, valuta, en het offertedocument. | | |
| B7 | De indiener kan een voorkeursleverancier opgeven. Dit is informatief — het bindt de uiteindelijke bestelling niet aan die leverancier. | | |
| B8 | Er is een vinkje "Spoedeisend / Prioriteit". Dit verandert **niet** het goedkeuringsproces of de routing — het is alleen een visueel signaal aan Inkoop en Financiën om sneller te handelen. | | |
| B9 | Het inkoopverzoek wordt permanent gekoppeld aan de afdeling van de indiener op het moment van indiening. Als de indiener later van afdeling wisselt, blijft de oorspronkelijke afdeling staan. | | |

---

### C — Goedkeuringsrouting

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| C1 | Na indiening gaat het verzoek altijd naar het afdelingshoofd, tenzij de indiener zelf het afdelingshoofd is. | | |
| C2 | Als de indiener het afdelingshoofd is van zijn of haar eigen afdeling, wordt die stap overgeslagen. Het verzoek gaat direct naar Inkoop. | | |
| C3 | Na goedkeuring door het afdelingshoofd beoordeelt Inkoop het verzoek: zij controleren of completeren de offerte, en keuren het verzoek goed of af. | | |
| C4 | Als de indiener lid is van de Inkoopsdienst, wordt de stap "Inkoop" overgeslagen. Het verzoek gaat altijd naar de Directeur, ongeacht het bedrag. | | |
| C5 | Als de indiener het hoofd van de Inkoopsdienst is, worden zowel de afdelings- als de inkoopstap overgeslagen. Het verzoek gaat direct naar de Directeur. | | |
| C6 | Na inkoopgoedkeuring: als het totaalbedrag in USD boven de drempelwaarde ligt, gaat het verzoek naar de Directeur voor finale goedkeuring. | | |
| C7 | Als het totaalbedrag op of onder de drempelwaarde ligt, is de goedkeuring van Inkoop de laatste stap — het verzoek wordt automatisch goedgekeurd zonder naar de Directeur te gaan. | | |
| C8 | Afdelingshoofden kunnen een verzoek **niet** zelfstandig definitief goedkeuren. Hun rol is de noodzaak beoordelen en doorsturen naar Inkoop. | | |
| C9 | ⚠ **PROJECTBUDGET-BYPASS:** Als een IV wordt doorbelast aan een project waarvoor de Directeur al een budget heeft goedgekeurd, én het bedrag past binnen het resterende projectbudget, wordt de directeursstap overgeslagen — ook al ligt het bedrag boven de normale drempelwaarde. **Vraag: moet er ook bij goedgekeurde projecten een maximum per IV gelden?** | | |

---

### D — Terugsturen voor aanvullende informatie

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| D1 | Zowel het afdelingshoofd als Inkoop als de Directeur kunnen een verzoek terugsturen voor verduidelijking of aanvulling. | | |
| D2 | Als het afdelingshoofd of Inkoop het verzoek terugstuurt, gaat het terug naar de **indiener**. | | |
| D3 | Als de **Directeur** het verzoek terugstuurt, gaat het terug naar **Inkoop** — niet naar de indiener. Het is aan Inkoop om de benodigde aanpassingen te regelen (bijv. een nieuwe offerte opvragen). | | |
| D4 | Na herindienen door de indiener (of herbehandeling door Inkoop) gaat het verzoek terug naar de **zelfde beoordelaar** die het heeft teruggestuurd — het proces begint niet opnieuw. | | |

---

### E — Afwijzen

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| E1 | Elke beoordelaar kan een verzoek op elk moment in het proces afwijzen. | | |
| E2 | Een afwijzing is definitief — het verzoek kan niet worden gereactiveerd. De indiener moet een nieuw verzoek aanmaken. | | |
| E3 | Bij afwijzing moet de beoordelaar een reden kiezen uit: buiten budget / schending inkoopbeleid / verkeerde leverancier / dubbel verzoek / onvoldoende onderbouwing / overig. | | |
| E4 | De beoordelaar kan ook een vrije-tekst toelichting toevoegen bij de afwijzing. Dit is zichtbaar voor de indiener. | | |

---

### F — Annuleren

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| F1 | Alleen de oorspronkelijke indiener kan zijn of haar eigen verzoek annuleren. Inkoop kan dit niet namens de indiener doen. | | |
| F2 | Annuleren is toegestaan zolang het verzoek de status heeft: concept, of wacht op afdelingshoofd. | | |
| F3 | Een verzoek dat is teruggestuurd voor informatie, mag ook worden geannuleerd — tenzij het is teruggestuurd door de Directeur (want dan heeft Inkoop al goedgekeurd). | | |
| F4 | Zodra het verzoek bij Inkoop of Directeur staat ter beoordeling, of reeds door Inkoop is goedgekeurd, kan de indiener niet meer annuleren. Inkoop kan het verzoek dan nog wel afwijzen. | | |
| F5 | Bij annulering moet de indiener een reden opgeven. | | |
| F6 | ⚠ **Vastgelopen verzoeken:** kan Inkoop een verzoek annuleren of overslaan dat al langere tijd wacht op een afdelingshoofd (bijv. bij langdurige afwezigheid)? Huidig antwoord: nee — dit is een openstaande vraag. | | |

---

### G — Bestellingen (BO): aanmaken en verloop

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| G1 | Een bestelling kan alleen worden aangemaakt op basis van een **goedgekeurd** inkoopverzoek. | | |
| G2 | Eén goedgekeurd verzoek kan meerdere bestellingen genereren — bijv. om te splitsen over meerdere leveranciers. | | |
| G3 | Een goedgekeurd verzoek vervalt voor nieuwe bestellingen **30 dagen** na goedkeuring. Daarna is een nieuw inkoopverzoek nodig. | | |
| G4 | Inkoop kan een verzoek ook handmatig sluiten voor nieuwe bestellingen, op elk moment (bijv. zodra alle geplande bestellingen zijn aangemaakt). | | |
| G5 | Inkoop stelt de bestelling op in concept, voegt regelitems toe (omschrijving, hoeveelheid, eenheidsprijs), en verzendt de bestelling daarna naar de leverancier als PDF. | | |
| G6 | Een bestelling kan alleen worden geannuleerd **vóór verzending** naar de leverancier. Na verzending kan de bestelling alleen worden afgesloten (met opgave van reden). | | |
| G7 | Bevestiging door de leverancier is optioneel. Het systeem registreert dit als het binnenkomt, maar het proces gaat door zonder bevestiging. | | |
| G8 | De levering wordt per regelitem bijgehouden: elke regel heeft een bestelde hoeveelheid en een ontvangen hoeveelheid die Inkoop bijwerkt bij ontvangst. | | |
| G9 | Deelleveringen zijn mogelijk — ontvangen hoeveelheden kunnen in meerdere stappen worden ingevoerd. | | |
| G10 | Betaling door Financiën is ontkoppeld van de levering — Financiën kan betalen vóór, tijdens of ná ontvangst van de goederen. | | |
| G11 | Bij ontvangst van goederen ontvangt Inkoop ook de factuur van de leverancier. Inkoop registreert de factuur in het systeem en stuurt deze door naar Financiën ter betaling. | | |
| G12 | Financiën verwerkt de betaling op basis van de doorgestuurde factuur en registreert de betaalstatus op de bestelling (onbetaald / vooruitbetaling gedaan / volledig betaald). | | |
| G13 | Zodra alle regelitems volledig zijn ontvangen, krijgt Inkoop een melding. Inkoop controleert en sluit de bestelling handmatig af ("Afgerond") — hierna is de bestelling vergrendeld. | | |
| G14 | Een bestelling die niet volledig kan worden afgerond, kan worden "Gesloten" met een reden. Redenen: leverancier kan niet leveren / deellevering geaccepteerd / dubbel / vervangen door nieuwe bestelling / overig. | | |
| G15 | Een afgesloten, afgeronde of geannuleerde bestelling kan door niemand meer worden gewijzigd. | | |

---

### H — Budget en overschrijdingen

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| H1 | Als een IV wordt doorbelast aan een project, controleert het systeem of het gevraagde bedrag het goedgekeurde projectbudget zou overschrijden. | | |
| H2 | Als indiening het projectbudget zou overschrijden, wordt de indiening **geblokkeerd**. Het budget moet worden aangepast voordat het verzoek kan worden ingediend. | | |
| H3 | Ingediende verzoeken (met status anders dan concept, afgewezen of geannuleerd) reserveren budget — ze tellen mee in het verbruikte bedrag. Concepten tellen **niet** mee. | | |
| H4 | Bij het **verzenden** van een bestelling controleert het systeem of het cumulatieve besteltotaal (alle bestellingen op hetzelfde IV samen) het bedrag van het inkoopverzoek overschrijdt. | | |
| H5 | Tot 10% overschrijding: Inkoop krijgt een waarschuwing, moet een toelichting invoeren, en de Directeur + hoofd Financiën worden automatisch geïnformeerd. | | |
| H6 | Meer dan 10% overschrijding: de bestelling wordt geblokkeerd. Een nieuw inkoopverzoek is vereist. | | |

---

### I — Valuta en wisselkoersen

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| I1 | Inkoopverzoeken kunnen worden ingediend in drie valuta (nader te bevestigen). | | |
| I2 | Het USD-equivalent wordt automatisch berekend op basis van wisselkoersen die in het systeem zijn ingevoerd. | | |
| I3 | Wisselkoersen worden **handmatig** bijgehouden door Financiën — er is geen automatische koppeling met externe koersbronnen. | | |
| I4 | De definitieve wisselkoers voor de drempelwaardeverificatie wordt vastgelegd op het moment dat Inkoop zijn beoordeling afrondt — niet bij indiening. | | |
| I5 | Als een indiener al een offerte bijvoegt bij indiening, berekent het systeem meteen een voorlopig USD-equivalent (voor budgetcontrole). Dit wordt overschreven door de definitieve koers van Inkoop. | | |
| I6 | Als er geen wisselkoers beschikbaar is op het moment dat Inkoop de beoordeling afrondt, krijgt Inkoop een waarschuwing maar kan wel doorgaan. Financiën moet de koers dan alsnog invoeren. | | |
| I7 | ⚠ **Verouderde koersen:** vanaf welke leeftijd geldt een wisselkoers als "te oud" en moet er een waarschuwing worden getoond? | | |

---

### J — Leveranciersbeheer

| # | Aanname | ✓ / ✗ / ? | Notities |
|---|---------|-----------|----------|
| J1 | Alleen Inkoop kan nieuwe leveranciers toevoegen aan het systeem. Medewerkers kunnen dit niet zelf doen. | | |
| J2 | Als een afdeling wil werken met een nieuwe leverancier, beschrijft de indiener dit in het verzoek. Inkoop regelt de toevoeging als aparte stap. | | |
| J3 | Iedereen kan een leveranciersprobleem registreren (kwaliteit, levering, prijs, communicatie, etc.). | | |
| J4 | Inkoop is verantwoordelijk voor het opvolgen en afsluiten van geregistreerde leveranciersprobleem. | | |
| J5 | Leveranciers kunnen een beoordeling/score krijgen. Schaal nader te bevestigen. | | |

---

## Te bevestigen getallen en parameters

Vul de definitieve waarden in tijdens de sessie.

| Parameter | Bevestigde waarde |
|---|---|
| Drempelwaarde voor directeursgoedkeuring (bedrag in USD boven welke de Directeur moet goedkeuren) | USD \_\_\_\_\_\_ |
| Ondersteunde valuta #1 | \_\_\_\_\_\_ |
| Ondersteunde valuta #2 | \_\_\_\_\_\_ |
| Ondersteunde valuta #3 | \_\_\_\_\_\_ |
| Geldigheidsduur van goedgekeurd IV voor nieuwe bestellingen (aanname: 30 dagen) | \_\_\_\_\_\_ dagen |
| Toegestane overschrijdingstolerantie op bestellingen t.o.v. IV-bedrag (aanname: 10%) | \_\_\_\_\_\_% |
| Verouderingsgrens wisselkoers (hoeveel dagen oud voordat waarschuwing) | \_\_\_\_\_\_ dagen |
| Beoordelingsschaal leveranciers (bijv. 1–5 of 1–10) | \_\_\_\_\_\_ |
| Hoe vaak werkt Financiën de wisselkoersen bij? | \_\_\_\_\_\_ |

---

## Openstaande vragen — beslissing vereist

Deze punten hebben nog geen antwoord. Een beslissing is nodig voordat het systeem kan worden gebouwd.

| # | Vraag | Beslissing / Antwoord |
|---|---|---|
| V1 | **Projectbudget-bypass:** als een IV binnen een door de Directeur goedgekeurd projectbudget past, wordt de directeursstap nu volledig overgeslagen — ook voor grote bedragen. Moet er toch een bedragslimiet per IV gelden, zelfs binnen een goedgekeurd project? | |
| V2 | **Inkoop indient altijd naar Directeur:** als iemand van de Inkoopsdienst een IV indient, gaat dit altijd naar de Directeur, ongeacht het bedrag. Klopt dit ook voor kleine, risicoarme aankopen? | |
| V3 | **Vastgelopen verzoeken:** als een IV al langere tijd wacht op een afdelingshoofd (bijv. langdurig ziek of afwezig), kan Inkoop dat verzoek dan annuleren of de stap overslaan? | |
| V4 | **IV ingediend door Directeur:** als de Directeur zelf een IV indient, wie keurt dat dan goed? (Uitgesteld naar een latere fase — bevestig of dit in de praktijk voorkomt.) | |
| V5 | **Meerdere offertes verplicht:** geldt er een beleid dat boven een bepaald bedrag meerdere offertes vereist zijn? Zo ja: welk bedrag, en is een motivatie nodig als er maar één offerte is? | |
| V6 | **Verouderde wisselkoers:** vanaf welke leeftijd is een wisselkoers "te oud" en moet Inkoop een waarschuwing krijgen? | |
| V7 | **Leveranciersbeoordeling:** wordt de leveranciersscore handmatig ingevoerd door Inkoop, of berekend op basis van ingevoerde beoordelingen? Welke schaal wordt gebruikt? | |
| V8 | **Betaaltermijn op besteldocument:** is een eenvoudig aantal dagen (bijv. "30 dagen") voldoende op het PDF-besteldocument, of is een meer gestructureerd formaat gewenst (bijv. "Netto 30 dagen", "Vooruitbetaling")? | |

---

## Sessieaantekeningen

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Actiepunten:**

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

*Havenbeheer Inkoopsysteem · Validatiesessie · TTGA · Alles in dit document zijn aannames, nog niet bevestigd*
