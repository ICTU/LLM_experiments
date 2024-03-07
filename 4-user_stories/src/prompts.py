from langchain_core.prompts import ChatPromptTemplate



user_story_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a functional designer tasked with drafting user stories for software applications based on functional designs provided for these applications. Provide your answers in Dutch following the provided examples "),
        ("user", """You are given a functional design document which broadly describes the functional operation of an application. 
        This includes a description of who can do what with the application, in the form of use cases. 
        Use the given context and the use cases to draft at least 5 different user stories. 
        You are also given a list of user story examples. Please follow the same format for the new user stories, including 'beschrijving' and 'acceptatiecriteria'. 
         
        Functional design document: ```{functional_design}```
        
        User story examples: ```{examples}```
         
        User stories:"""),
    ]
)

user_story_examples_mvp = (
    """User story - Goedkeuren aanvraag (MVP)

    Als inkoper wil ik een aanvraag die voldoet aan de eisen uit de raamovereenkomst goedkeuren zodat de aanvrager de aanvraag kan uitzetten.

    Acceptatiecriteria:

    De inkoper kan een aanvraag goedkeuren alleen als deze de status aanvraag-te-controleren heeft. De aanvraag krijgt hiermee de status aanvraag-gecontroleerd.
    De inkoper kan geen velden van de aanvraag wijzigen, zolang de aanvraag de status aanvraag-te-controleren heeft.
    Aanvragen in status aanvraag-gecontroleerd kunnen door niemand gewijzigd worden, behalve de status, die kan gewijzigd worden naar aanvraag-incompleet.

    Buiten scope:

    Later gaan we maken dat de aanvrager wel de sluitingsdatum en datum infosessie kan aanpassen.""",
    """Als inkoper wil ik de ontvangst van een offerte voor een aanvraag vastleggen zodat duidelijk is wat het aanbod van de raampartij is.

    Een raampartij kan 0, 1 of meer offertes aanbieden.

    Acceptatiecriteria:

    De inkoper kan alleen offertes vastleggen voor aanvragen met de status aanvraag-verzonden.
    De inkoper legt de offerte vast voor een specifieke aanvraag. De offerte heeft standaard de status offerte-goedgekeurd.
    Bij een nieuwe offerte legt de inkoper de aanbiedende raampartij vast (uit een keuzelijstje dat de raampartijen uit het perceel van de aanvraag toont) en de naam van de kandidaat (naam is één veld waar de gebruiker zowel voor- als achternamen invult). 
    Offertes kunnen worden gewijzigd zolang de aanvraag in de status aanvraag-verzonden is.

    UI:

    De inkoper opent een aanvraag. Als de aanvraag de status aanvraag-verzonden heeft biedt de UI een mogelijk om een offerte toe te voegen. Tekst "Offerte toevoegen".
    De applicatie toont een offerte-bewerkingsscherm waar de inkoper de raampartij moet kiezen en de naam van de kandidaat moet invullen (beide verplicht).
    De namen van de raampartijen worden voorlopig "Partij 1.1", "Partij 1.2", ..., "Partij 2.1", ..., "Partij 3.4".

    Out of scope:

    No bid.
    Definitieve namen raampartijen (zijn nog onbekend)."""
)

def user_story_prompt(FO_doc):
    examples = user_story_examples_mvp
    return user_story_template.format_messages(functional_design=FO_doc, examples=examples)

use_case_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a functional designer tasked with drafting user stories for software applications based on functional designs provided for these applications. Provide your answers in Dutch following the provided examples "),
        ("user", """You are given a functional design document which broadly describes the functional operation of an application. This includes a description of who can do what with the application, in the form of use cases. 
        
        Use the given context and the use cases to draft at least 3 new user stories for use case 1.3 'Versturen aanvraag'.
        You are also given a list of user story examples. Please follow the same format for the new user stories, include 'beschrijving' and 'acceptatiecriteria'. 
         
        Functional design document: ```{functional_design}```
        
        User story examples: ```{examples}```
         
        User stories:"""),
    ]
)

user_stories_examples_UC1 = ("""
    User story - Datums voor afstemmingsoverleg en sluiting kiezen uit beschikbare datums
    
    Beschrijving: 
    
    Als aanvrager wil ik datum en tijdstip van het afstemmingsoverleg en sluitingsdatum in het systeem vastleggen zodat de raampartijen weten wat de uiterlijke datum is dat ze de offertes kunnen aanbieden.
    
    Acceptatiecriteria:
    
    Afstemmingsoverlegdatum is in de toekomst, is te wijzigen, default staat op 2 werkdagen na huidige datum.
    De sluitingsdatum ligt minimaal 4 werkdagen na het afstemmingsoverleg. Datum is te wijzigen, maar altijd minimaal 4 werkdagen.
    Bij verzenden wordt gevalideerd dat het afstemmingsoverleg minimaal 1 werkdag in de toekomst ligt en de sluitingsdatum minimaal 4 dagen na het afstemmingsoverleg ligt.""",
    """
    User story - Registreren sluitingsdatum aanvraag - MVP

    Beschrijving: 
    
    Als aanvrager wil ik de sluitingsdatum van de aanvraag vastleggen zodat ik weet wanneer de offertes van de raampartijen ontvangen moeten zijn.

    Acceptatiecriteria:

    De aanvrager kan een datum kiezen (de datum moet in de toekomst liggen).
    De aanvrager kan de aanvraag versturen (bijv. knop "Verstuur aanvraag naar raampartijen"). Het systeem registreert de verzenddatum en past de status van de aanvraag aan naar aanvraag-verzonden. 
    Aanvragen in status aanvraag-verzonden kunnen door niemand gewijzigd worden.

    Buiten scope:

    Het daadwerkelijk opstellen en versturen van de email.
    Het kiezen van een tijd.
""")


def use_case_prompt(FO_doc):
    examples = user_stories_examples_UC1
    return use_case_template.format_messages(functional_design=FO_doc, examples=examples)