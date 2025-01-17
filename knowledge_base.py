from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
import faiss
from uuid import uuid4
from typing import List

from langchain_core.runnables import chain

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(doc_content_chars_max=30000, top_k_results=1, lang='it'))

text = wikipedia.run("Renè Ferretti")
doc = Document(page_content=text, metadata={"source": "Wikipedia"})
embedder = OllamaEmbeddings(model="nomic-embed-text")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=200, add_start_index=True
)
index = faiss.IndexFlatL2(len(embedder.embed_query("hello world")))
index2 = faiss.IndexFlatL2(len(embedder.embed_query("hello world")))
vector_store = FAISS(
    embedding_function=embedder,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)
citations_vector_store = FAISS(
    embedding_function=embedder,
    index=index2,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

def citations():
    citations = """
    Sì, certo certo, però tu ascoltami bene adesso, Boris, noi dobbiamo fare una grandissima regia, io ti voglio concentrato, come l'anno scorso, capito? Dobbiamo spaccare tutto Boris! Dai, dai, dai!
Vai e dille che cominciamo con una scena facilissima ma siccome lei è una cagna, la farà di merda! Vai, vai, vai! [riferito a Corinna]
Cagna! Cagna maledetta! [riferito a Corinna]
No! Io non mi faccio imporre niente, amico mio! Il mio motto sai qual è? [...] "Qualità o morte!"
Tutti gli uomini sono dei grandi attori, tranne alcuni attori.
Forse qui quelli che vengono dall'America e vogliono insegnarci a noi come fare questo mestiere c'hanno rotto il cazzo! Quindi mi fai il cazzo del piacere di prendere la porta e andartene, chiaro?! [...] E adesso, signori, si ricomincia e siccome abbiamo perso troppo tempo, si ricomincia a fare le cose a cazzo di cane se necessario. Portiamo a casa la giornata! E vai che siamo pronti!
Come fa un notaio a essere un personaggio comico? È il personaggio che si avvicina in assoluto più alla morte, dai!
Poi io non capisco cosa c'è da ridere ne Gli occhi del cuore: stupri, tradimenti, uno che s'accoppia co n'altra e poi scopre essere la sorella. È tutto tranne che comico!
Secondo me le scene di passione sono le più noiose in assoluto. Io voglio conflitto, azione, incidenti, morti. Invece sei lì costretto a vedere due che si sbavano addosso! Oh, è da quando ero piccolo: guardavo la televisione, se vedevo due che si baciavano, speravo sempre che entrava il cattivo e l'ammazzava a tutti e due.
Fa schifo, non lo so perché, ma 'sta scena fa schifo! Io lo sapevo: le scene di sesso sono una rottura di cazzo!
Dai te prego, girala tu 'sta scena de merda de baci de merda!
Perché l'importante è usare un alcol di buona qualità, ci metti dentro le bucce di limone, attenta a togliere il bianco, se no viene amaro! E lo fai riposare per dieci giorni. Dopo dieci giorni ci aggiungi lo zucchero, mischi con l'acqua et voilà, ecco la meraviglia! [ad Arianna, riferito al limoncello]
Ma vedi Arianna, un uomo sa quando sta per arrivare la fine. Alcuni vanno a meditare davanti al mare, altri trovano conforto in famiglia, io faccio il limoncello.
Alfredo, allora senti, è molto semplice: basito lui, basita lei, macchina da presa fissa, luce un po' smarmellata e daje tutti che abbiamo fatto!
Mamma mia con questa storia della recitazione naturalistica, Alfredo! Alfredo! Due attori si devono guardare negli occhi e dire le battute chiare. Non mi fare cazzate politiche! Alfredo, li mortacci tua! Che poi me la rimandano indietro e mi tocca rigirarla. La gente la vuole così e tu me la fai così. Chiaro?
Un'attrice che non lavora, gli sventoli davanti quattro euro, ti fa pure un balletto, ti fa.
Allora voi sapete che tutti i programmi, tutte le fiction di tutte le reti di tutti palinsesti ruotano intorno ai dati auditel. Noi no! Noi no! Noi tiriamo dritti signori, oggi più che mai! Perché noi facciamo questo lavoro seriamente e per altri due motivi: A, siamo dei professionisti; B, perché siamo persone che stanno raccontando una storia, la storia di Occhi del cuore. Oggi più che mai signori, voglio che dimostriate quello di cui siamo capaci. E dai, dai, dai! Dai, dai, dai!
Oh, certo che 'sto conte è incredibile, sta in una forma straordinaria, si è fatto tutti i personaggi de 'sta serie! Secondo me si è fatto pure quelli de' 'a troupe, eh? Tranne me e Arianna che stiamo sempre a bordo set. Oh ragazzi, occhio eh! L'anno scorso un microfonista, gli sono cadute le chiavi per terra, lui si è abbassato per raccoglierle e zacchete! Il conte da dietro! Il conte da dietro!
Glielo hai detto che tra Gli occhi del cuore 1 e 2 c'è una differenza stilistica enorme, come parlare del Vecchio e del Nuovo Testamento?
Senti, a pezzo demmerda! Io vengo da Fiano Romano, ha' capito? io ti stampo 'na cinquina 'n faccia! Vieni fuori, c'ho il cric 'n macchina t'o faccio vedere io come me chiamo, 'sto stronzo! Avvocato dei miei coglioni! Capito?! Stai attento a come parli! Io t'ammazzo, a figlio de 'na mignotta! "Come mi chiamo?" [all'avvocato di Stanis]
Sta in grande forma 'sto pesce, lui è come me: in preparazione boccheggia, poi sul set spacca tutto lui. Vero, che spacchi tutto tu? [a Boris]
Corinna, tu lo sai quali sono i personaggi che rimangono nel cuore della gente? Quelli che muoiono.
Mamma mia ragazzi, io mi scuso con tutti voi veramente, ma questa fiction è veramente tremenda. Ma lascia stare, lascia stare. Ma se mi permettete un piccolo paradosso però, la batosta che abbiamo preso è un segnale positivo per il paese.
Seconda stagione
Oh, cagna fino alla fine questa! Proprio cagna fino all'ultimo! [commentando la recitazione di Corinna]
Ma chi cazzo è?! Che cazzo fai?! Sei entrato in campo, testa di cazzo! Mandate via quel pezzo di merda! Sei uno stronzo, m'hai rovinato tutto! Sei entrato in campo, porca puttana! Vai via, non ti voglio vedere mai più, capito?! Testa di cazzo, di merda, vaffanculo! Me ne vado, ciao. [riferito ad Alessandro]
Vedi, io ho fatto tanti errori nella mia vita ma li ho espiati tutti lavorando con Corinna.
"Tanti auguri Roberto"... banale. "Tanti auguri maestro"... maestro... no, no, anzi, "buon compleanno dall'allievo al maestro." "Tanti auguri poeta"... anzi "buon compleanno dall'allievo al poeta", no anzi "buon compleanno dall'allievo puntini puntini al poeta" no... "buon compleanno..." no, anzi non me ne frega 'n cazzo. [pensando il ‎messaggio di auguri per Roberto Benigni]
Tutto sommato qua ti si chiedono tre-quattro facce: basita, preoccupata, spensierata e intensa, che è la più difficile. Ma queste me le devi fare però, eh... Guarda che Stanis La Rochelle ti copre due serie da ventiquattro puntate l'una con queste faccette.
Sentite, io ho fatto tante cose brutte nella vita ma ogni tanto mi prende una fitta forte qui, nello stomaco, e capisco che oltre non posso andare.
Comunque senti, io trovo molto coraggioso da parte della rete, aver scelto te per il ruolo del commissario, anziché prendere il solito calabrese con i baffi. [a Karin]
'Tacci vostra! Quattromila a settimana pe' scrive' sta merda! [allo sceneggiatore]
Ti voglio dire solo una cosa, Stanis. Tu sei un attore straordinario, tu sei Stanis La Rochelle e io sono molto onorato di lavorare con te. E ti trovo non cambiato, ti trovo trasformato. Non è da te... non è da te... aspettare una giornata qualcuno che ti venga a vedere sul set anche se questo qualcuno si chiama Wim Wenders. Primo: perché è molto italiano aspettare Wim Wenders. Secondo: perché tu sei Stanis La Rochelle e se lui capiterà qua mentre tu stai girando, be', avrà la fortuna di vivere un'emozione, la stessa che tu dai a tutti noi tutti i giorni, Stanis.
Io non ce l'ho con te Stanis, io ce l'ho con gli sceneggiatori, questa è una scena di merda! Se li incontro, li metto sotto co' 'a machina!
Ecca là! Un'altra scena de merda de baci de merda![1] [ad Arianna; commentando una scena di passione tra Stanis e Karin]
Senti Cristina, io sono molto stanco. Io ho quasi cinquant'anni, ho la casa sfondato, questo non sarebbe grave però, eh... la cosa grave è che qui mi stanno facendo fuori, hai capito? Io presto dovrò reinventarmi tutto e credimi che a cinquant'anni non è facile. Tu sei una ragazza giovane, tu prendi duecentomila euro per sei mesi di lavoro, quando c'è gente che per mille euro al mese sfonda le strade col martello pneumatico senza battere ciglio e lotta per vivere una vita di merda. Io penso che sarebbe bello per una volta veder le cose nella giusta ottica, no? E fare semplicemente il proprio dovere senza capricci, senza problemi e in questo caso piangendo, se è il caso di piangere.
Una cosa ci tenevo a dire prima di salutarvi. Penso che le cose si possano fare diversamente. Se mai tornerò a fare questo lavoro, lo farò con una convinzione: che un'altra televisione è possibile. [alla troupe]
Terza stagione
[Prendendo il nuovo pesce rosso dall'acquario per la nuova fiction] E questo è Roger Federer, pronto per la nuova avventura! Eh, ma non ti fare illusioni, caro Federer, quelli della rete hanno detto due anni per fare Machiavelli, ma vedrai che ci mettiamo molto meno. Oh, dipende anche da te però, Roger, eh... [mostrando poi ad Alessandro i pesci del suo acquario] Guarda qua: ogni pesce una fiction, ogni fiction una sfida.
Diego, scusa, io non volevo ma sono costretto a dirti la verità. Io ho la malaria, sì è proprio così. Scusa se te lo dico così veramente, ma io c'ho proprio 'a malaria, Diego.
Capirai la sorpresina... [...] Sarà il solito regalino in albergo: il cesto con il miele, 'o zafferano e il panettone demmerda! [ultime parole famose]
Allora signori, chiedo un attimo la vostra attenzione per spende due parole prima di iniziare. Con Medical Dimension mi gioco tutto, se sbaglio questa fiction io giuro che cambio mestiere, lo giuro sulla testa di Lopez! Scherzo Diego! Vedete, io penso che in televisione si possano ancora fare cose decenti e lo voglio dimostrare con questa fiction. Certo dipenderà da tutti noi, da Arianna, da me, dalle maestranze, dagli attori. A proposito, ne approfitto per dare il benvenuto a Jasmine, che come sapete si è sempre rifiutata di fare la tv ma che invece in questo caso è qui con noi, perché crede in questo progetto. Grazie Jasmine, grazie! [tutti applaudono] Grazie, Jasmine crede in Medical Dimension. Io, signori, chiedo a tutti voi di crederci, anche agli schiavi! Non si faranno più le cose a cazzo di cane, no! Non racconteremo più cose finte! Noi racconteremo la realtà di questo Paese attraverso la vita quotidiana di un ospedale pubblico e quindi signori... dai, dai, dai! Daje che spacchiamo tutto!
Aoh, a Sergio. Questo me lo devi trattare coi guanti di velluto, me raccomando. Questo è il Roberto Saviano della sanità italiana.[2] Ha scritto un libro pazzesco.
Duccio, se tu non cambi e torni quello di venti anni fa, io ti faccio fuori, Duccio. Occhio, eh. Guarda che io su Medical Dimension passo sopra a tutto, anche all'amicizia.
No però scusa, non si può fare così. Io le scene me le preparo la sera prima. Ci penso, me le studio, eh... Tu non puoi arrivare qui e dimme: «Famme quella! Damme tre etti de quell'artra!» E che stamo all'alimentari, Lopez?
Tu sei un attore scomodo, Stanis. Tu sei il Roberto Saviano della recitazione italiana.[2] [...] E io sono convinto che sei anche un grande regista. Io non vedo l'ora di vedere la tua opera prima! Ma in questo momento a me serve a tutti i costi il Roberto Saviano! [a Stanis]
Non è quello che fa Un nonno di troppo, questo è una delle voci più importanti del teatro italiano: è un mostro sacro. E fa Un nonno di troppo perché la crisi c'è pe' tutti, pure pei mostri sacri! E tu gli devi portare rispetto, hai capito? Perché tu sei 'na merda e lui è un mostro sacro! [riferito a Remo Arcangeli e rivolto ad Alfredo]
Dai che oggi è una giornata corta ma infernale, corta ma infernale!
Ricordati che in Italia vale la regola delle tre "G": la giusta telefonata, al giusto momento, alla giusta persona!
Ecco, vedi, vedi. Qui il dottor Corelli decide di smetterla con la droga ed è proprio questa visione che lo fa cambiare dentro, perché vede questa immagine normale, questa bella signora che fa un gesto naturale, quotidiano, bellissimo... È un'epifania!! Capito? [dopo aver rivisto la scena in cui Stanis, nel ruolo di Giorgio, si sofferma su una signora che sta stendendo le lenzuola al balcone]
Brava Arianna, come sempre. Senti ma, come mai voti Berlusconi? Vabbè, dai, non ti preoccupare, me lo dici un'altra volta.
Boris, come ho potuto non sentire le tue grida?! Perché tu volevi avvertirmi, vero? Tu lo sapevi, tu avevi capito tutto. Che stupido che sono stato! [al pesce, dopo aver capito che non si tratta di Federer ma di Boris]
Allora non avete capito... Io voglio la merda del passato, io sono il re della merda, voi siete degli esseri di merda che vivono nella merda e insieme possiamo fare un grande classico! [agli sceneggiatori]
Senti non mi pija pe' culo Duccio, io vojo te. Basta con la fotografia da fighetto de 'sto stronzo. [riferito a Lorenzo] Capito, io voglio la roba tua, la roba tua, 'n tanto al chilo, hai capito? La roba tua de 'na volta, voglio che apri tutto. Voglio che smarmelli!
[Facendo il ciakkista] Occhi del cuore 3, uno bis, prima! Sì signori, avete capito bene! Occhi del cuore 3... perché a noi la qualità c'ha rotto er cazzo! Perché un'altra televisione diversa, è impossibile![3] Viva la merda!
Boris - Il film
La nostra casa è la televisione: è come la mafia, nun se ne esce se non da morti.
La casta, il libro scandalo di due giornalisti che dimostra quanto i politici italiani siano una casta che nel tempo si è attribuita ogni sorta di scandaloso privilegio. Un'élite intoccabile. Una truffa legalizzata, da tre miliardi di euro l'anno.
Molti di voi hanno diviso con me più di quindici anni di progetti. Quanta strada abbiamo fatto, eh? Tante esperienze, belle, brutte, facili, difficili. Ora, si apre una nuova fase. Ci saranno tanti altri progetti che noi faremo ancora insieme! Ma non questo film. [tutti i membri della vecchia troupe ci rimangono male] Per questo film, La casta, voi non ci sarete signori. Ma dovete capirmi... Io come regista vi chiedo di capirmi e di fidarvi...
Allora signori. Non ci sarà nessun discorsone stavolta, perché mi hanno già fatto perdere troppo tempo. Dirò solo tre parole: voglio qui Boris!
    
    """
    cit_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=10, add_start_index=True
    )
    doc = Document(page_content=citations, metadata={"source": "Wikipedia"})
    all_splits = cit_text_splitter.split_documents([doc])
    uuids = [str(uuid4()) for _ in range(len(all_splits))]
    citations_vector_store.add_documents(documents=all_splits, ids=uuids)

def ingest(text):
    all_splits = text_splitter.split_documents([doc])
    uuids = [str(uuid4()) for _ in range(len(all_splits))]
    vector_store.add_documents(documents=all_splits, ids=uuids)
    citations()
    
@chain
def retriever(query: str) -> List[Document]:
    return "\n\n".join([x.page_content for x in vector_store.similarity_search(query, k=4)])
def citations_retriever(query: str) -> List[Document]:
    return "\n\n".join([x.page_content for x in citations_vector_store.similarity_search(query, k=4)])
    
    
ingest(text)