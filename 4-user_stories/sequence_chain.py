from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate
from chain_prompts import user_story_prompt, criteria_prompt, evaluate_prompt, summarize_prompt

#import api keys for OpenAI en Langsmith
load_dotenv()

llm = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
    temperature=0,
)


def create_chain(llm, prompt:PromptTemplate, output_key:str):
    """initializes a single llm chain"""
    return LLMChain(
        llm=llm,
        prompt=prompt,
        output_key=output_key
    )


def create_seq_chain():
    """initializes a sequence of llm chains"""
    chain1 = create_chain(llm, user_story_prompt(), "user_stories")
    chain2 = create_chain(llm, criteria_prompt(), "criteria")
    chain3 = create_chain(llm, evaluate_prompt(), "evaluation")
    chain4 = create_chain(llm, summarize_prompt(), "summaries")
    return SequentialChain(
        chains=[chain1, chain2, chain3, chain4],
        input_variables=["functional_design", "use_case", "user_stories_list"],
        output_variables=["summaries"],
        verbose=True
    )

def simple_seq():
    """initializes a simple sequence of llm chains"""
    chain1 = create_chain(llm, user_story_prompt(), "user_stories")
    chain2 = create_chain(llm, criteria_prompt(), "criteria")
    return SequentialChain(
        chains=[chain1, chain2],
        input_variables=["functional_design", "use_case", "user_stories_list"],
        output_variables=["criteria"],
        verbose=True
    )

def generate_user_stories(fo_summary, use_case, no_stories, user_stories_list=[]):
    seq_chain = simple_seq()
    while len(user_stories_list) < no_stories:
        user_stories_list.append(seq_chain.invoke(
            {
                "functional_design": fo_summary,
                "use_case": use_case,
                "user_stories_list": user_stories_list
            }
        )['criteria'])
    return user_stories_list
        
print(generate_user_stories(
    fo_summary = """De nieuwe applicatie, werktitel “Inkooptool ICTU”, zal op termijn meerdere inkoopprocessen ondersteunen zoals inhuur professionals, inhuur uitzendkrachten, inkoop hardware en enkelvoudige en meervoudige onderhandse uitvragen. Voor nu is voorzien dat elk van de inkoopprocessen op maat ontwikkelde functionaliteit nodig zal hebben binnen de inkooptool, maar dat de overlap groot genoeg is om veel functionalteit te kunnen hergebruiken tussen de inkoopprocssen.
Dit globaal functioneel ontwerp beschrijft de hoofdfuncties van de “Inkooptool ICTU”. Deze hoofdfuncties zijn:
A.	Aanvraag
1.	Aanvraag opstellen. Het opstellen, controleren en versturen van aanvragen.
2.	Ontvangst offertes. Het registreren en controleren van ontvangen offertes. 
3.	Gunning. Het vastleggen van de voorlopige gunning van offertes.
B.	Contractregistratie
4.	Afsluiten overeenkomst. Het opstellen en/of vastleggen en versturen van de eenzijdig ondertekende (nadere) overeenkomst en het registreren van de tweezijdig ondertekende (nadere) overeenkomst. 
5.	Wijzigen overeenkomst. Het opstellen en/of vastleggen en versturen van de eenzijdig ondertekende gewijzigde (nadere) overeenkomsten het registreren van de tweezijdig ondertekende gewijzigde (nadere) overeenkomst.
Let op: overige contracten worden nog niet ondersteund door het aanvraagdeel van de applicatie.
Daarnaast biedt de software de volgende ondersteunende functies:
1.	Anonimiseren persoonsgegevens.
2.	Rapportages met aanvragen en nadere overeenkomsten waarbij de raampartij nog actie moet ondernemen.
3.	Rapportages met aflopende contracten.
4.	No-bid analyse.
5.	Beheer beschikbare sluitingsdatums en -tijden.
6.	Indexering tarieven.
7.	Export naar CSV.
8.	Zoeken aanvragen en overeenkomsten.
""",
use_case = """UC1.3 – Versturen aanvraag
Aspect	Beschrijving
Doel	Aanvraag versturen naar raampartijen
Actor(en)	Aanvrager
Precondities	De aanvraag is als aanvraag-gecontroleerd gemarkeerd
Trigger	
Primaire scenario	1)	Indien het gaat om een inICTU3 aanvraag vult de aanvrager de aanvraag aan met datum en tijdstip van het afstemmingsoverleg (bij default suggereert het systeem een datum twee werkdagen na de huidige datum).
2)	De aanvrager kiest een sluitingsdatum en -tijd uit een lijst van beschikbare sluitingsdatums en -tijden die het systeem aanbiedt. Het systeem biedt alleen sluitingsdatums en -tijden aan die minimaal vier werkdagen liggen na de datum en tijdstip van het afstemmingsoverleg indien van toepassing. In andere gevallen  biedt het systeem alleen sluitingsdatums en -tijden aan die minimaal vier werkdagen liggen na de datum van uitvraag.
a)	Als er geen geschikte sluitingsdatum en -tijd beschikbaar is vraagt de aanvrager (buiten de applicatie om) aan de afdeling Inkoop een extra sluitingsdatum en -tijd te maken voor de aanvraag. 
b)	Een inkoper wijst de aanvraag aan een sluitingsdatum en -tijd toe (het systeem laat toe dat de inkoper het maximum aantal aanvragen voor de sluitingsdatum en -tijd overschrijdt).
3)	De aanvrager verstuurt de aanvraag (met daarin de gekozen datum en tijd van het afstemmingsoverleg (indien van toepassing), de sluitingsdatum en -tijd, de kerngegevens en de aanvraag professional als bijlage) naar de raampartijen (van het perceel van de aanvraag) en markeert daarmee de aanvraag als aanvraag-verzonden. Het systeem noteert de verzenddatum.
a)	Het systeem controleert voor verzenden dat de datum en tijd van het afstemmingsoverleg minimaal één werkdag in de toekomst ligt en dat de sluitingsdatum en -tijd minimaal vier werkdagen later is dan het afstemmingsoverleg indien van toepassing, of in andere gevallen de datum van uitvraag. Als de datums hier niet aan voldoen verstuurt het systeem de aanvraag niet en waarschuwt de gebruiker dat niet aan de voorwaarden wordt voldaan.	
 """,
 no_stories=4
))