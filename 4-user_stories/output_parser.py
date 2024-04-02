from __future__ import annotations
import sys
from typing import TypedDict
from pathlib import Path
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from src.add_to_JSON import write_json

class User_stories(TypedDict):
     
    fo_doc:Path 
    use_cases:dict
    user_stories:list[User_story]
    comments:str
     

class User_story(BaseModel):
     
    description:str = Field(description="3 word description of user story")
    user_story:str = Field(description="a user story in the following format: As a [description of user], I want [functionality] so that [benefit]")
    acceptance_criteria:list = Field(description="numbered list of acceptance criteria")
    #open_issues:list
    #use_case:str

load_dotenv()

model = ChatOpenAI(temperature=0)

parser = JsonOutputParser(pydantic_object=User_story)

template = """
    You are given an overview of a functional design (1) which describes the functional operation of an application. This includes a description of who can do what with the application, in the form of use cases. You given the description of a specific use case (2).
    You are also given a list of existing user stories (3) and a a user story format (4) to structure your answer.
         
    Instructions:
    - using the provided context (1) form a new user story for the use case (2)
    - avoid overlap with the existing user stories (3) (if the list is empty, provide the most basic user story)
    - use the provided user story format (4)
         
    1. Functional design: ```{functional_design}```
        
    2. Use case: ```{use_case}```
         
    3. Existing user stories: ```{user_stories_list}```

    4. {format_instructions}
         
    User stories:"""

prompt = PromptTemplate(
    template=template,
    input_variables=["functional_design", "use_case", "user_stories_list"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | model | parser

answer = chain.invoke({
    "functional_design": """The proposed application, tentatively named "Inkooptool ICTU," is designed to support the procurement processes of ICTU, initially focusing on the hiring of external professionals through a new framework agreement, inICTU3, and eventually supporting other procurement processes such as hiring temporary staff, purchasing hardware, and handling single and multiple tender requests. The application is necessitated by the significant differences between the new inICTU3 framework agreement and the current one, which the existing custom application cannot support. The application aims to bridge the gap until an ERP solution can take over the procurement processes.

**Functionality Summary:**

1. **Request Process:**
   - **Creating Requests:** Users can draft, check, and send out requests for proposals (RFPs).
   - **Receiving Offers:** The application allows for the registration and checking of received offers from vendors.
   - **Awarding Contracts:** Users can record preliminary awards of contracts based on the offers received.

2. **Contract Registration:**
   - **Finalizing Contracts:** The application supports drafting, sending, and registering signed contracts with vendors.
   - **Modifying Contracts:** Users can draft and send modifications to contracts and register these changes once agreed upon by both parties.

3. **Supporting Functions:**
   - Anonymization of personal data after a certain period.
   - Generation of reports on pending actions from vendors, expiring contracts, and no-bid analyses.
   - Management of closing dates and times for RFPs.
   - Indexing of rates and exporting data to CSV.
   - Searching for requests and contracts within the system.

**Data Collections:**
- **Requests:** Linked to a specific project or department and related to the intended hiring of one or more external professionals.
- **Offers:** Each offer is linked to a specific request and vendor, proposing one candidate per offer.
- **Contracts:** Each contract relates to one candidate and, by extension, to one request. Contracts can be modified through addendums.

**Statuses and Validation:**
- The application manages various statuses for requests, offers, and contracts to track their progress through the procurement process.
- It enforces business rules such as maximum working hours per candidate and sends notifications for status changes.

**Use Cases:**
- The document outlines use cases for the main functions, including creating and sending requests, receiving and evaluating offers, selecting candidates, finalizing contracts, and modifying contracts. Each use case details the goal, actors, preconditions, triggers, and primary scenarios.

This summary provides a foundation for constructing user stories for the development of the "Inkooptool ICTU," focusing on supporting the procurement processes, particularly the hiring of external professionals through the inICTU3 framework agreement and beyond.
""",
"use_case": """UC1.1:Registreren aanvraag

Aspect	Beschrijving
Doel	Externe medewerkers inhuren voor project of afdeling
Actor(en)	Aanvrager
Trigger	Het project of de afdeling van de aanvrager heeft een inhuurbehoefte
Primaire scenario	1)	De aanvrager maakt een een nieuwe aanvraag in het systeem. De nieuwe aanvraag heeft automatisch de status aanvraag-incompleet en krijgt een uniek aanvraagnummer dat door het systeem wordt gegenereerd en niet wijzigbaar is. Het formaat is AV -<JJJJMMDD>-<volgnummer>. De datum is de huidige datum op het moment dat de aanvraag wordt gemaakt (en gebruikt de tijdzone CET/CEST). Het volgnummer start bij 1 en reset ieder dag als de eerste aanvraag op een specifieke datum wordt gemaakt. Het volgnummer heeft twee voorloopnullen.
Merk op dat de aanvrager ook een “Aanvraag professional”-document (in het geval van inICTU3) of een “Aanvraagformulier IFAR” (in het geval van IFAR) met informatie als eisen, wensen en beoordelingssystematiek maakt en dat in het inkoopdossier op Sharepoint plaatst.
a)	De gebruiker kan een nieuwe aanvraag baseren op een bestaande aanvraag, waarbij de relevante, niet-tijdgevoelige  gegevens worden gekopieerd (relevante gegevens nog nader te bepalen). De gebruiker kan de bestaande aanvraag zoeken via UC6.8 – Zoeken aanvraag. De nieuwe aanvraag krijgt een nieuw aanvraagnummer. Alle kerngegevens van de bestaande aanvraag worden gekopieerd naar de nieuwe aanvraag, en zijn wijzigbaar door de aanvrager.
2)	De aanvrager voert de kerngegevens van de aanvraag in:
a)	Raamovereenkomst en/of perceel (vaste keuzelijst met de percelen uit inICTU3 en de IFAR raamovereenkomst, geen default waarde). Let op: de gebruiker kiest dus perceel en raamovereenkomst in één keer als het gaat om een inICTU3-aanvraag.
b)	Omschrijving van de functie (vrije tekst, verplicht).
c)	Aanvrager (dit is bij default de gebruiker, maar de gebruiker kan een andere aanvrager kiezen uit de vaste lijst van aanvragers). In dit laatste geval stuurt het systeem een notificatie naar die aanvrager. Als de aanvrager later gewijzigd wordt stuurt het systeem een notificatie naar de oude en de nieuwe aanvrager. 
d)	Contactpersoon (vrije tekst). Het is de bedoeling dat dit een ICTU-medewerker is, toevoegen als instructie in the applicatie.
e)	Geplande startdatum en geplande einddatum.
f)	Gemiddeld aantal uren per week (minimaal 1, maximaal 40).
g)	Totaal aantal uren (minimaal 1).
h)	Projectcode en -naam (gebruikers krijgen bestaande projectcodes en -namen als suggestie maar kunnen ook nieuwe projectcodes en namen toevoegen).
i)	VOG-categorieën (vaste keuzelijst).
j)	Aantal in te huren kandidaten (default: 1, minimaal 1, geen maximum).
k)	Of er screening van de kandidaat zal plaatsvinden (ja/nee). Merk op: screening is niet hetzelfde als een VOG, maar betreft een screening door bijvoorbeeld Politie, AIVD of MIVD. 
l)	Opmerkingen (vrije tekst; deze tekst wordt meegezonden bij de aanvraag naar de raampartijen).
3)	Als de aanvraag voor een inICTU3-perceel is, voert de aanvrager ook de volgende kerngegevens in:
a)	Functiecategorie (vaste keuzelijst, let op: per perceel is er een andere keuzelijst).
b)	Minimaal aantal aan te bieden kandidaten per raampartij. Het minimaal aantal aan te bieden kandidaten is minimaal 0 en heeft geen maximum. Merk op: een reden om het minimaal aantal aan te bieden kandidaten op nul te zetten is dat er een bekende kandidaat is. De aanvraag telt daardoor niet mee voor KPI-1 en het minimaal aantal aan te bieden kandidaten is dan ook 0.
c)	Maximaal aantal aan te bieden kandidaten per raampartij. 
i)	Als het minimaal aantal aan te bieden kandidaten 0 is, dan is het maximaal aantal aan te bieden kandidaten minimaal 2 en heeft geen maximum. 
ii)	Anders is het maximaal aantal aan te bieden kandidaten minimaal 1, groter of gelijk aan het minimaal aantal aan te bieden kandidaten en heeft geen maximum.
4)	Als de aanvraag voor IFAR is, voert de aanvrager ook de volgende kerngegevens in:
a)	Schaal van de functie (getal uit een vaste keuzelijst).
b)	De vraag “Welke ‘conflicterende werkzaamheden’ kent deze functie (volgens ARAR)?” (vrije tekst).
c)	Minimaal en maximaal aantal aan te bieden kandidaten per raampartij (het minimaal aantal aan te bieden kandidaten is minimaal 1 en heeft geen maximum, het maximaal aantal aan te bieden kandidaten is minimaal 1, groter of gelijk aan het minimaal aan te bieden kandidaaten en heeft geen maximum).
5)	Het systeem logt het aanmaken van de nieuwe aanvraag. De loginformatie bevat de gebruikersnaam, datum en -tijd, aanvraagnummer en de verplichte velden.
6)	De aanvrager markeert de aanvraag als aanvraag-te-controleren. Nadat de status is veranderd in aanvraag-te-controleren kan de aanvrager (en ook de inkoper) de velden van de aanvraag niet meer wijzigen (behalve de status).
7)	Het systeem notificeert de inkopers.""",
"user_stories_list": []})

write_json(answer)