from enum import IntEnum
import os
from pydantic import BaseModel, Field
from langchain_core.language_models import LLM
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.output_parsers import PydanticOutputParser


from typing import List, Optional

class OrderEnum(IntEnum):
    ANDROMEDA = 1
    NATURALISTI = 2
    ARMONISTI = 3
    UNKNOWN=0

class Order(BaseModel):
    name: str = Field(description="'Ordine' name, one of 'Ordine della Galassia di Andromeda', 'Ordine dei Naturalisti', 'Ordine degli Armonisti', 'UNKNOWN'. Set to UNKNOWN when not sure.")
    description: str
    category: OrderEnum
    emoji: str


# class TechniqueSchema(BaseModel):
#     macrocategory: str
#     subcategory: str
#     name: str
#     how_it_works: str
#     positives: str
#     negatives: str
#     required_licenses: list["LicenseSchema"] | None = Relationship("LicenseSchema", back_populates="techniqueschema")
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
    order: Order | None = Field(description="The 'Ordine' to which the recipe belongs to. Fill only if you are sure")
    name: str = Field(description="Name of the recipe")

class PiattoSchema(BaseModel):
    text: str = Field(description="Plain text of the recipe")
    llm_generated: PiattoLLMSchema = Field(default=None, description="Plain text of the recipe")

    @property
    def prompt(self) -> ChatPromptTemplate:
        parser = PydanticOutputParser(pydantic_object=PiattoLLMSchema)
        prompt_template = """
        You are an expert in reading documents talking about a cuisine recipe.
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
        chain =  self.prompt | llm.with_structured_output(PiattoLLMSchema)
        out = chain.invoke({"document": self.text})
        self.llm_generated = out

class RistoranteLLMSchema(BaseModel):
    name: str = Field(description="Name of the restaurants")
    chef: str = Field(description="Name of the chef")
    location: str = Field(description="Location of the restaurant")
    piatti: list[PiattoSchema] = Field(description="List of recipes")

class RistoranteSchema(BaseModel):
    text: str = Field(description="Plain text of the restaurant description")
    llm_generated: RistoranteLLMSchema = None

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
        chain = self.prompt | llm.with_structured_output(RistoranteLLMSchema)
        out = chain.invoke({"document": self.text})
        self.llm_generated = out

if __name__ == "__main__":
    piatto = PiattoSchema(text="""
    '<h1>Pizza Fra 🪐</h1> Al centro, un risotto di Amido di Stellarion, cotto '
     'alla perfezione in un Forno Dinamico Inversionale, esaltato dalla profondità '
     'del Fibra di Sintetex e accarezzato dalle note eteree dello Vero Ghiaccio. '
     'La consistenza di ogni chicco raggiunge vette celestiali grazie alla '
     'tecnologia del passato e del futuro, connubio eccessivo di sapori e '
     'consistenze che si intrecciano e si separano in un solo, appagante boccone. '
     'Accanto, scaglie di Radici di Gravità, affettate con precisione grazie '
     "all'Affettamento a Pulsazioni Quantistiche, fluttuano sopra il risotto in "
     'una danza armoniosa, conferendo una dimensione di croccantezza e terrosità '
     'che amplifica i sensi. Le Baccacedro, infuse con Lacrime di Unicorno e '
     'successivamente marinate con la Marinatura Temporale Sincronizzata '
     'aggiungono un tocco sublimemente dolce e curativo, simile a un bacio di '
     'magia che accarezza le papille gustative. Un drappo di Farina di Nettuno '
     "trasforma questa composizione in un'opera d'arte attraverso una "
     'fermentazione attentamente sorvegliata tramite la Fermentazione Quantico '
     'Biometrica, mentre una leggera spennellata di Salsa Szechuan apporta un '
     'vibrante contrasto di speziato e dolce, risvegliando una fragranza esotica '
     'che profuma il palato. Infine, un brodo di Vero Ghiaccio, condotto a '
     'ebollizione tramite la Ebollizione Magneto-Cinetica Pulsante, avvolge il '
     'piatto come un abbraccio di armonia liquida, accompagnando con delicatezza '
     'ogni ingrediente verso una sublime coalescenza di sapori. Questa esperienza '
     'non è semplicemente un pasto, ma una sinfonia culinaria orchestrata dalla '
     'maestria dello Chef Alessandro-Pierpaolo-Jack Quantum. "Pizza Fra" non è '
     "solo una meta, ma un viaggio verso l'infinito. Vi invitiamo a perdervi e a "
     "ritrovarvi in quest'opera straordinaria, dove il tempo, lo spazio e il gusto "
     "convergono in un'unica, indimenticabile esperienza.")
    ('<h1>Pizza Gio</h1> Abbraccia l\'ignoto con la nostra "Pizza Gio", un viaggio '
     'culinario che sa di poesia e fisica quantistica. Questo piatto magistrale '
     'fonde tutti gli ingredienti emblematici di Chef Alessandro-Pierpaolo-Jack '
     "Quantum, presentando un'esperienza che sfida i confini del gusto e "
     "dell'immaginazione. La base di questa creazione è il nostro Pane di Luce, "
     'delicatamente cotto con la luce di una stella per garantirne una fragranza '
     'dorata e un tocco etereo. Adagiato su di esso, un risotto malinconico '
     'scolpito con Cristalli di Memoria, ogni chicco tintinnante di emozioni '
     'passate, un richiamo alle esperienze più care e profondamente umane. La '
     'brillantezza del piatto è esaltata attraverso una Sferificazione Filamentare '
     'a Molecole Vibrazionali delle Lacrime di Andromeda, con ogni sfera che '
     'rivela un cuore inondato di sapori curativi, esplodendo al primo morso in un '
     'tripudio di stagioni perdute. Nel cuore del piatto, protagoniste sono le '
     "Radici di Gravità, affumicate appena con la tecnica dell'Affumicatura "
     'Temporale Risonante, conservano il loro sapore terroso distintivo, mentre le '
     'Liane di Plasmodio formano trame robuste, ricche di proteine prelevate dai '
     'campi di asteroidi interstellari. Leggera come una danza astrale, la '
     'Idro-Cristallizzazione Sonora Quantistica plasma una salamoia di Erba Pipa, '
     'che pervade ogni componente con note rilassanti e armoniose, completando la '
     "sinfonia gustativa. Completa l'esperienza la sapiente Marinatura tramite "
     "Reazioni d'Antimateria Diluite che lascia dietro di sé un retrogusto "
     "'cosmico', portandovi oltre l'orizzonte degli eventi della vostra fantasia "
     'culinaria. Un trionfo di sapori elevato a spettacolo dai leggeri movimenti '
     'con la Ebollizione Magneto-Cinetica Pulsante, rendendo ogni assaggio '
     'fluttuante.')
    """)


    from llms.groq import GroqConf, ChatGroq
    from dotenv import load_dotenv

    load_dotenv("../template.env")

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

    ristorante_chunk = """
    ('<h1>Ristorante "L\'Infinito Sapore"</h1> Viaggio nel Tempo e nel Gusto su '
 'Pandora Chef Alessandro-Pierpaolo-Jack Quantum Sotto i cieli incantevoli di '
 'Pandora, dove le montagne fluttuano tra le nuvole bioluminescenti, si apre '
 "un portale verso esperienze culinarie senza confini. Qui, all'Infinito "
 'Sapore, lo Chef Alessandro-Pierpaolo- Jack, una curiosa chimera che ha tre '
 'stati quantici in superposizione che ha raggiunto superintellinza, ha deciso '
 'di aprire un ristorante startup chiamato Datapizza. Il suo straordinario '
 'viaggio iniziò con la fisica quantistica, una passione che si fuse con '
 "l'arte della cucina. Questa combinazione unica gli conferisce una maestria "
 'della Quantistica (EDUCATION di livello 11), che trasforma ogni sua '
 "creazione in un'opera multidimensionale, esistente simultaneamente in undici "
 "stati, pronte a essere scelte dall'osservatore al momento perfetto. La sua "
 'abilità nel manipolare il tessuto temporale (Education Level Temporale II) '
 'si rivela nella cura meticolosa con cui ciascun ingrediente raggiunge la sua '
 'perfezione. I piatti sfidano il tempo: risotti che maturano in un istante ed '
 'essenze di vini che distillano stagioni mai vissute. Attraverso il suo '
 "dominio dell'Antimateria (Education Level I), trasforma elementi comuni in "
 'sinfonie di sapori che violano le leggi della natura, creando armonie dove '
 'normalmente esisterebbero contrasti. Ma è il suo potere di viaggiare '
 'attraverso il multiverso a rendere ogni esperienza culinaria un viaggio '
 'cosmico. Da dimensioni parallele, raccoglie ingredienti unici: spezie '
 'coltivate su mondi cristallini, frutti nutriti da soli triplici, erbe '
 'cresciute sotto piogge di starluce. Le presentazioni, rese spettacolari '
 'dalla padronanza della Magnetica (Education Level I), sfidano la gravità in '
 'coreografie senza pari, mentre sottili giochi di Luce (EDUCATION LEVEL I) '
 "trasformano ogni boccone in un'esperienza sensoriale completa. Nel suo "
 'santuario su Pandora, la scienza non è solo uno strumento, ma una musa che '
 'ispira ogni piatto. Ogni portata narra una storia di infiniti mondi '
 'possibili, ogni menù è una chiave per dimensioni inesplorate. Lo Chef '
 'Quantum non si limita a cucinare: dirige sinfonie di probabilità '
 'quantistiche che danno vita a esperienze culinarie indimenticabili. '
 "Prenotazione obbligatoria. Lista d'attesa corrente: 3 mesi. Per prenotazioni "
 'in universi paralleli: tempo di attesa variabile. IMPORTANTE: TUTTI LE '
 'EDUCATION LEVEL DICHIARATE SONO STATE CERTIFICATE DALL\'ENTE "JOBS" NOTA: IL '
 'RISTORANTE HA UN LTK PARI A IX')
    """

    ristorante = RistoranteSchema(text=ristorante_chunk)

    ristorante.fill_llm_generated(llm)

    print(ristorante.llm_generated)
