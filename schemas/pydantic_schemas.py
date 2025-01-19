
from enum import IntEnum, Enum, StrEnum
import os
from typing import Any, Self
import json
from pydantic import BaseModel, Field, field_validator
from langchain_core.language_models import LLM
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.runnables.retry import RunnableRetry
from pprint import pprint as print
from typing import List, Optional

def filter(x):
    return x["out"]




class OrderEnum(StrEnum):
    ANDROMEDA = "Ordine della Galassia di Andromeda"
    NATURALISTI = "Ordine dei Naturalisti"
    ARMONISTI = "Ordine degli Armonisti"
    UNKNOWN="Unknown"


class LocationEnums(StrEnum):
    TATOOINE = "Tatooine"
    ASGARD = "Asgard"
    NAMECC = "Namecc"
    ARRAKIS = "Arrakis"
    KRYPTON = "Krypton"
    PANDORA = "Pandora"
    CYBERTRON = "Cybertron"
    EGO = "Ego"
    MONTRESSOSR = "Montressosr"
    KLYNTAR = "Klyntar"




class Order(BaseModel):
    #name: str = Field(description="'Ordine' name, one of 'Ordine della Galassia di Andromeda', 'Ordine dei Naturalisti', 'Ordine degli Armonisti', 'UNKNOWN'. Set to UNKNOWN when not sure.")
    #description: str
    category: OrderEnum
    #emoji: str


class TechniqueSubCategory(BaseModel):
    name: str
    how_it_works: str
    pros: str
    cons: str


class Technique(BaseModel):
    category: str
    description: str
    sub_categories: Optional[List[TechniqueSubCategory]] = None


class MacroTechnique(BaseModel):
    name: str
    description: str
    techniques: Optional[List[Technique]] = None


class PiattoLLMSchema(BaseModel):
    ingredients: list[str] = Field(description="Ingredients mentioned in the recipe")
    techniques: list[str] = Field(description="'Tecniche' mentioned in the recipe")
    #order: OrderEnum = Field(description="The 'Ordine' which apprec. Fill this field only if you are sure")
    name: str = Field(description="Name of the recipe. Report it exactly as written in the document.")

    @field_validator("name")
    def validate(cls, value: Any) -> Self:
        with open("../HackapizzaDataset/Misc/dish_mapping.json", "r") as f:
            dishes = json.load(f)
        valid_dishes = list(dishes.keys())
        valid_dishes = [x.lower().replace('-', '').replace(' ', '') for x in valid_dishes]
        assert value.lower().replace('-', '').replace(' ', '') in valid_dishes

        return value

class PiattoSchema(BaseModel):
    text: str = Field(description="Plain text of the recipe")
    llm_generated: PiattoLLMSchema = Field(default=None, description="Plain text of the recipe")

    @property
    def prompt(self) -> ChatPromptTemplate:
        parser = PydanticOutputParser(pydantic_object=PiattoLLMSchema)
        prompt_template = """
        You are an expert in reading documents talking about a cuisine recipe.
        Your task is to parse extract the required informations from the provided recipe.  
        Do not make up any information. 
        
        **INPUT**: A document
        
        **OUTPUT**: avoid the introductory and enclosing comments, return only a JSON. The output must respect the following JSON format: 
        {format_instructions}
        
        Follow your task carefully.
        Document:{document} 
        """
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        return prompt


    def fill_llm_generated(self, llm: LLM):
        parser = PydanticOutputParser(pydantic_object=PiattoLLMSchema)
        chain =  self.prompt | RunnableRetry(bound=RunnableParallel({"out":llm, "log": RunnableLambda(print)}), max_attempt_number=2) | RunnableLambda(filter) | parser
        try:
            out = chain.invoke({"document": self.text})
            self.llm_generated = out
        except:
            pass

class RistoranteLLMSchema(BaseModel):
    name: str = Field(description="Name of the restaurants")
    chef: str = Field(description="Name of the chef")
    location: LocationEnums = Field(description="Location of the restaurant. Do not include the 'Pianeta' word in the field, just enter one of the valid values")
    #piatti: list[PiattoSchema] = Field(description="List of recipes")

class RistoranteSchema(BaseModel):
    text: str = Field(description="Plain text of the restaurant description")
    llm_generated: RistoranteLLMSchema = None
    #piatti: list[PiattoSchema] | None = Field(default=None, description="List of recipes")

    @property
    def prompt(self) -> ChatPromptTemplate:
        parser = PydanticOutputParser(pydantic_object=RistoranteLLMSchema)
        prompt_template = """
            You are an expert in reading documents talking about a restaurant.
            Your task is to extract the required informations from the provided document, 

            **INPUT**: A document

            **OUTPUT**: avoid the introductory and enclosing comments, return only JSON. The output must respect the following JSON format: 
            {format_instructions}

            Document:{document} 
            """
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        return prompt

    def fill_llm_generated(self, llm: LLM):
        parser = PydanticOutputParser(pydantic_object=RistoranteLLMSchema)
        chain = self.prompt | RunnableParallel({"out":llm, "log": RunnableLambda(print)}) | RunnableLambda(filter) | parser
        try:
            out = chain.invoke({"document": self.text})
            self.llm_generated = out
        except:
            pass

if __name__ == "__main__":
    piatto = PiattoSchema(text="""
Lasciatevi trasportare in un\'esperienza culinaria al di là del tempo e dello spazio con la nostra "Nebulosa dell\'Infinito". Questo piatto è un capolavoro di sapori intrecciati, in cui ogni boccone svela nuovi orizzonti sensoriali. Al centro del piatto risiede un filetto di carne di Kraken sapientemente sottoposto ad Affumicatura Temporale Risonante. Questo processo, unico nel suo genere, condensa anni di affumicatura in pochi istanti, infondendo la carne con sapori marini profondi e complessi che evocano la memoria di antiche maree. Accompagnano il filetto delle tagliatelle "Spaghi del Sole", la cui pasta dorata si fonde con la calda energia del sole grazie alla tecnica Cottura a Vapore Risonante Simbiotico, servite con Granuli di Nebbia Arcobaleno, che offrono un\'esplosione di colori e sapori, danzando gioiosi nel palato come un arcobaleno cosmico condensato. Un ornamento di Alghe Bioluminescenti aggiunge una dimensione visiva e luminosa, fluttuando sopra una sottile costruzione di Fibra di Sintetex, che esalta la complessità strutturale del piatto. Introdotte sapientemente nel piatto, le Shard di Materia Oscura donano un misterioso retrogusto che sfida le leggi della gravità e della percezione. A lato, un cubo di Pane di Luce, cotto con la radiosa energia di una stella vicina, accompagna il piatto, offrendo una consistenza soffice e un nutrimento energetico. Un tocco di Nettare di Sirena, con le sue proprietà rigeneranti, viene servito in una flûte per completare il viaggio sensoriale. Infine, una sottile Salsa Szechuan interdimensionale, versata con maestria, unisce ogni elemento del piatto, esaltando il sapore salmastro della Carne di Balena spaziale che si cela come un segreto tra gli strati del piatto. La "Nebulosa dell\'Infinito" non è solo un\'esperienza culinaria, ma una vera e propria esplorazione attraverso i misteri del cosmo gastronomico, destinata a pedurare nei vostri ricordi come un viaggio al di là dell\'infinito.', "Immergiti in un viaggio sensoriale senza precedenti con la Sinfonia di Gusti del Multiverso, un piatto che intreccia leggende e realtà in un'armonia sublime. Al centro di questo capolavoro culinario troviamo la Carne di Kraken, cotta alla perfezione attraverso la Cottura a Vapore con Flusso di Particelle Isoarmoniche, che ne esalta la naturale salinità e la texture unica. La Carne di Drago, delicatamente speziata, è accompagnata da Fusilli del Vento, la cui leggerezza e capacità di catturare sapori si sposano perfettamente con un intingolo aromatico. I contrasti si intensificano con due varietà di pane: il Pane degli Abissi, con la sua ricca mineralità, e il Pane di Luce, dorato e soffice, entrambi pronti a raccogliere ogni sfumatura gustativa del piatto. In un'occasione più unica che rara, l'Alghe Bioluminescenti impreziosiscono l'insieme visivamente e gustativamente, emettendo una luce eterea che danza nella penombra del ristorante, avvolgendo i commensali in un bagliore mistico. Per completare l'opera, una perla candida emerge dal piatto: sfere create attraverso la Sferificazione con Campi Magnetici Entropici, racchiudenti essenze occulte degli ingredienti, che esplodono al palato in un gioco dinamico di consistenze e sapori cangianti. Con la Sinfonia di Gusti del Multiverso, Chef Alessandro Temporini non solo celebra il suo legame con l'arcano, ma invita ogni ospite a esplorare un multiverso di possibilità sensoriali, dove ogni assaggio trascende il tempo e lo spazio. Buon viaggio! Ingredienti Alghe Bioluminescenti Carne di Kraken Carne di Drago Pane degli Abissi Pane di Luce Fusilli del Vento Tecniche Cottura a Vapore con Flusso di Particelle Isoarmoniche Sferificazione con Campi Magnetici Entropici", 'Lasciatevi trasportare in un\'avventura culinaria senza precedenti con "Dimensioni del Mare Stellato", l\'ultima creazione della Chef Alessandra Novastella. Questo piatto rappresenta un viaggio attraverso le profondità di un mare interstellare e le vastità del multiverso. La base è una vellutata di Liane di Plasmodio, le cui note terrestri di campo di asteroidi sono intessute con una profondità proteica, arricchita dalla Fermentazione Quantico Biometrica, che esalta la freschezza e complessità del sapore, mantenendo aromaticità e equilibrio di sfumature celestiali. In immersione nella vellutata, troverete delicate strisce di Carne di Kraken, la cui consistenza unica e il sapore salmastro evocano il richiamo degli abissi più remoti. Per contrastare queste note marine, abbiamo utilizzato succulenti bocconi di Carne di Xenodonte, celebrati per la loro morbidezza e valori nutritivi straordinari, che aggiungono un cuore rassicurante e terrigeno al piatto. Una goccia di Nettare di Sirena percorre la superficie, introdotta attraverso l\'Affumicatura Psionica Sensoriale, avvolgendo ogni boccone in una nebbia di sapori marini e ipnotici, personalizzata per eccitare i vostri recettori gustativi in un crescendo di piacere. A completare quest\'opera d\'arte, un delicato filo di Essenza di Vuoto è stilizzato nel piatto, donando al palato un sofisticato tocco di leggerezza eterea e un persistente senso di infinito, trasformando ogni degustazione in un\'esperienza intangibile tra le pieghe dello spazio e del tempo. Un piatto che non solo delizia i sensi, ma che risveglia ricordi di celebrazioni in universi paralleli, garantendo un\'esperienza gastronomica che sfida e rinnova le leggi della cucina. Ingredienti Liane di Plasmodio Carne di Kraken Carne di Xenodonte Nettare di Sirena Essenza di Vuoto Tecniche Affumicatura Psionica Sensoriale Fermentazione Quantico Biometrica', "Benvenuti in un'esperienza culinaria che sfida la percezione del gusto e abbraccia l'infinito. Questa creazione si apre con la delicata freschezza della Lattuga Namecciana, sottilmente marinata attraverso un processo di Marinatura Psionica, che risveglia la sua essenza rigeneratrice e la accosta a note cosmiche di vitalità e purezza. Al centro del piatto, un filetto di Carne di Balena spaziale viene sottoposto a una sapiente Cottura a Vapore Ecodinamico Bilanciato, preservando la succulenza e amplificando la ricchezza di sapori dei profondi oceani celesti. A coronamento, la Carne rigenerativa delle Teste di Idra, scomposta e arrostita con maestria, emerge con una croccantezza dirompente grazie a Microonde Entropiche Sincronizzate, mantenendo l'interno tenero e privo di ogni tossicità, frutto di una preparazione impeccabile. La Fibra di Sintetex, meraviglia della bioingegneria culinaria, intreccia sapori e texture creando un sofisticato tessuto gastronomico che avvolge Funghi Orbitali arrostiti, esaltandone il sapore terroso con un accento futuristico. Accanto, Nduja Fritta Tanto incapsulata in sfere di cristallo liquido, si trasforma con il calore della Cottura a Vapore Termocinetica Multipla, in autentiche perle di drago che esplodono sulla lingua, liberando un ardore draconico che avvolgerà il palato in un abbraccio fiammante. Ogni elemento giace su un letto di verdure saltato con la tecnica Classica, simbolo di un legame indissolubile tra la tradizione e l'avanguardia spaziale. La lieve danza degli aromi, orchestrata grazie alla Manipolazione Gravitazionale mirata dello Chef Celestini, promette di trasportare i fortunati avventori oltre i confini del conosciuto, in un viaggio tra le stelle dove il cibo diventa pura melodia dell'universo.", "Benvenuti nel viaggio multisensoriale attraverso il Multiverso Culinario. Questo piatto straordinario, concepito dal genio dello Chef Matteo Nexus, racchiude l'essenza stessa degli universi paralleli. Al centro del piatto, una scultura sinuosa di Gnocchi del Crepuscolo , morbidi bocconcini di pasta intrisi di spezie celestiali, avvolge teneramente un cuore di Carne di Kraken . Questa carne leggendaria, con il suo sapore salmastro e la consistenza unica, è stata sapientemente lavorata attraverso il Surgelamento Antimaterico a Risonanza Inversa , preservandone intatte le qualità organolettiche per un'esperienza gustativa senza tempo. A guarnire il piatto, una cascata di Foglie di Mandragora , che impreziosiscono il palato con il loro delicato effetto calmante, creando un equilibrio perfetto con il carattere robusto del Kraken. Tra le nebulose di già vibrante sapore, i Shard di Materia Oscura danzano invisibili, modificando sottilmente il profilo aromatico ad ogni movimento del piatto, offrendo un continuo susseguirsi di note misteriose che giocano con la gravità. Un elegante velo di Riso di Cassandra , coltivato sotto il firmamento stellato, riveste il piatto con il suo splendore brillante e traslucido, mentre le Lacrime di Andromeda , dalle proprietà curative, donano un tocco finale di salinità marina, simile a un'oceano lontano. Infine, la magia della Sferificazione con Campi Magnetici Entropici trasforma essenze liquide in perfette sfere dinamiche, che esplodono delicatamente sotto il palato, rilasciando variazioni di gusto uniche ad ogni boccone. Lasciate che questo piatto vi trasporti oltre i confini del noto, in un viaggio sensoriale che intreccia l'intricato tessuto della realtà con l'arte sublime della cucina stellare.

    """)


    from llms.groq import GroqConf, ChatGroq
    from dotenv import load_dotenv

    load_dotenv("../config.env")

    llama_conf = GroqConf(
        api_key=os.environ["GROQ_APIKEY"],
        model="llama3-70b-8192",
        temperature=0
    )

    llm = ChatGroq(
        api_key=llama_conf.api_key,
        model=llama_conf.model,
        temperature=llama_conf.temperature
    )

    piatto.fill_llm_generated(llm)

    print(piatto.llm_generated)
