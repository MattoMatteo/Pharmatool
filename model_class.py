import time
import os
import json

import faiss
import numpy as np
from dotenv import load_dotenv
import requests

from Middleware import middlwareDatabase

class DoctorStoned():
    def __init__(self,
                 API_KEY:str,
                 model_id:str,
                 path_fais_drugs:str, 
                 path_faiss_para:str,
                 path_chunks_drugs:str,
                 path_chunks_para:str,
                 path_mapper_drugs_foglietto:str):
        self.API_KEY = API_KEY
        self.model_id = model_id
        self.faiss_drugs = faiss.read_index(path_fais_drugs)
        self.faiss_para = faiss.read_index(path_faiss_para)
        with open(path_chunks_para, 'r', encoding="utf-8") as f:
            self.chunks_para = json.load(f)
        with open(path_chunks_drugs, 'r', encoding="utf-8") as f:
            self.chunks_drug = json.load(f)
        with open(path_mapper_drugs_foglietto, 'r', encoding="utf-8") as f:
            self.mapper_drugs_foglietto = json.load(f)
            

    # Private function
    def _call_llm(self, prompt,
                 system_prompt="Sei un assistente utile.",
                 model="meta-llama/llama-3.3-70b-instruct:free",
                 temperature=0.7):
        """
        Esegue una chiamata raw a OpenRouter.
        Include gestione errori e parsing JSON.
        """
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8888",
            "X-Title": "Advanced Lab"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature, # Bassa temperatura per task deterministici
            "usage": {"include": True}
            #"max_tokens": 100
        }
        retry = 0
        max_retry = 3
        while retry < 3:
            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=30)
                response.raise_for_status()
                response = response.json()
                return response['choices'][0]['message']['content'].strip()
            except Exception as e:
                print(f"⚠️ Errore API: {e}")
                retry+=1
                print(f"Retry after 10 second. Remains: {max_retry - retry}")
                time.sleep(10)
        return "ERROR"

    def _build_prompt(self, farmaco: str, para:str) -> str:
        return f"""
        Sei un assistente esperto in farmacologia.
        Compito:
        1) Ti verrà fornita la scheda tecnica di un farmaco (primo elemento della lista) e di un parafarmaco (secondo elemento della lista).
        2) Anallizzali e decidi se quel parafarmaco è adatto come terapia complementare rispetto al farmaco.
        3) Se decidi che esiste una correlazione valida, descrivermi brevemente a cosa serve il parafarmaco e spiega perché lo hai scelto.
        4) Se decidi che NON esiste una valida e diretta correlazione tra i due prodotti oppure se hai il dubbio, rispondi semplicemente con None.
        5) La risposta finale deve essere solo una stringa (in caso di correlazione) oppure None (in caso contrario).
    
        Regole:
        - Usa solo i nomi forniti.
        - Se non sei assolutamente certo della correlazione tra farmaco e parafarmaco, restituisci esclusivamente None.
        - Non fare assunzioni o deduzioni: la certezza deve essere totale. Ne va della salute della persona.
        - Usa un linguaggio semplice e chiaro comprensibile anche a chi non è del settore
        - Non inventare nulla, rispondi solo se presente nella sezione parafarmaci
        - Descrizione max 20 parole per voce.
        - Restituisci SOLO JSON valido, quindi None senza virgolette (no stringa).

        Esempio:
        input = [{{"file_name": "1002_12437", "content": "Virdex viene usato per alleviare i sintomi dell'emicrania quando questa si manifesta. Non è un trattamento preventivo, ma si assume durante l'attacco per ridurne intensità e durata"}},
                {{"file_name": "EUGLYCEM 30CPR", "content": "VERTIGOVAL 20CPR": "Agisce migliorando le funzioni neurologiche, sostenendo la microcircolazione e riducendo sintomi associati alle alterazioni dell'equilibrio. Vertigoval aiuta a gestire sintomi associati come vertigini, nausea, instabilità e tensione nervosa"}}]
        output = None

        Esempio:
        input = [{{"file_name":"7158_25680", "content": "Monuril è un antibiotico a base di fosfomicina che uccide i batteri responsabili delle infezioni e viene utilizzato per trattare le infezioni urinarie non complicate nelle donne e adolescenti, oltre che come profilassi antibiotica perioperatoria per la biopsia prostatica transrettale negli uomini adulti"}},
                {{"file_name": "LONGLIFE D-MANNOSE 60CPS", "content": "d-mannose\nè un integratore alimentare a base di d-mannosio, uno zucchero semplice estratto dal legno di larice o di betulla, e uva ursina.\nper la sua azione protettiva sulle cellule uroepiteliali, il d-mannosio può rappresentare un'alternativa naturale e sicura per contribuire alla riduzione delle infezioni del tratto urinario e delle cistiti infettive.\ncoopera a quest'azione l'uva ursina, una delle piante medicinali maggiormente utilizzate per favorire la funzionalità delle vie urinarie e il drenaggio dei liquidi corporei, grazie alla presenza di arbutina, composto ad attività antisettica.\nsenza glutine."}}]
        output = "Integratore che supporta le vie urinarie e riduce le cistiti; scelto perché complementare all'azione di Monuril."

        Ora tocca a te:
        input = [{farmaco},
                {para}]
        output = 
        """.strip()

    def _validate_drug_similarity(self, similarity:dict, temperature:float):
        """
        Args:
            similarity(dict): Dizionario composto da un elemento di "similarita_farmaci_parafarmaci.json",
                                strutturato: {"farmaco": {"title": str, "content":str, "file_name":str},
                                                "simili": [{"parafarmaco": {"title": str, "content": str, "file_name": str}}]}
            model(str): Nome del modello.
            temperature(str): Temperatura del modelo.
        Returns:
            dict: Restituisce un dizionario del tipo: {file_name_farmaco: [{"file_name_parafarmaco": str, "response": str}, ...] }
        """
        # Creiamo il dizionario con le info del farmaco e il suo dump
        farmaco_dict = {"file_name": similarity["farmaco"]["file_name"], "content": similarity["farmaco"]["content"]}
        farmaco_dump = json.dumps(farmaco_dict)

        # Creiamo la lista dei simili
        lista_simili = similarity["simili"]

        # Cicliamo su tutti i suoi simili
        llm_response = {}
        llm_response[farmaco_dict["file_name"]] = {}
        for para in lista_simili:
            para_dict = {"file_name": para["parafarmaco"]["file_name"], "content": para["parafarmaco"]["content"]}
            para_dump = json.dumps(para_dict)
            llm_response[farmaco_dict["file_name"]][para_dict["file_name"]] = self._call_llm(prompt=self._build_prompt(farmaco_dump, para_dump),
                                                                                            system_prompt="",
                                                                                            model=self.model_id,
                                                                                            temperature=temperature)
            if llm_response[farmaco_dict["file_name"]][para_dict["file_name"]] == "None":
                llm_response[farmaco_dict["file_name"]][para_dict["file_name"]] = None
            elif llm_response[farmaco_dict["file_name"]][para_dict["file_name"]] == "ERROR":
                llm_response[farmaco_dict["file_name"]].pop(para_dict["file_name"])
                continue
        return llm_response

    def _find_similarity(self, aic:str, k:int):
        """
        Function that find top k similarity from given aic.
        If given aic is a drugs find k parafarmaci otherwilse opposite.
        Returns:
            list: List of chunks items, ready for validation step.
        """
        # Define if it is a drugs or not
        info = middlwareDatabase.cerca_farmaco(aic,
                                        middlwareDatabase.tipoRicercaBancadati.Codice_AIC,
                                        [middlwareDatabase.tipoRicercaBancadati.Cl])
        cl = None
        if info and len(info) > 0:
            if info[0] and len(info[0]) > 0:
                cl = info[0][0]
        if not cl:
            return None
        
        # Convert aic to corrispondent "foglietto illustrativo" becose they are embedded like this
        file_name_foglietto = next((d[aic].strip(".txt") for d in self.mapper_drugs_foglietto if aic in d), None)
        if not file_name_foglietto: # There isn't a foglietto associated, so can't find similarity abort.
            return None
        # Depending of the result, find similaries
        if cl != "P":
            aic_faiss_index = next((i for i, item in enumerate(self.chunks_drug) if item["file_name"] == file_name_foglietto), None)
            if aic_faiss_index:
                embedding = self.faiss_drugs.reconstruct(aic_faiss_index)
                drugs_embeddings = np.array(embedding, dtype="float32").reshape(1, -1)
                _, indices = self.faiss_para.search(drugs_embeddings, k)
                return {"farmaco": next(item for item in self.chunks_drug if item["file_name"] == file_name_foglietto),
                        "simili": [{"parafarmaco": self.chunks_para[x]} for x in indices[0]]}
            else:
                return None

    # Public function

    def get_similarity_para(self, aic:str, k:int = 10, temperature:float = 0.3):
        """
        Call pipeline: similarity embedded para, validation LLM.
        Args:
            aic(str): AIC of a given Drugs.
            k(int): Number of similarity given by embedding (not final result).
            temperature(float): temperature of LLM validation.
        Returns:
            list[tuple]: List of para_id and the LLM explain
        """

        para_chunks_similarities = self._find_similarity(aic, k)
        para_chunks_validated = self._validate_drug_similarity(para_chunks_similarities, temperature)
        list_para_id = []
        for chunk in para_chunks_validated.values():
            for para_name, llm_comment in chunk.items():
                if not llm_comment:
                    continue
                # Find id by file name (same as Denominazione e confezione)
                info = middlwareDatabase.cerca_farmaco(para_name,
                        middlwareDatabase.tipoRicercaBancadati.Denominazione_e_Confezione,
                        [middlwareDatabase.tipoRicercaBancadati.ID_Farmaco])
                # Ensure results
                if info and len(info) > 0:
                    if info[0] and len(info[0]) > 0:
                        para_id = info[0][0]
                if not para_id:
                    return None
                # Add to list the tuple of id and LLM response
                list_para_id.append((para_id, llm_comment))
        if list_para_id:
            return list_para_id
        return None

load_dotenv(override=True)
API_KEY = os.getenv("OPEN_ROUTER_KEY")
if not API_KEY:
    raise ValueError("API Key non trovata. Controlla il file .env")

doctor_stoned = DoctorStoned(API_KEY, "openai/gpt-oss-120b",
                             path_fais_drugs = "./Data/faiss_farmaci.index",
                             path_faiss_para = "./Data/faiss_parafarmaci.index",
                             path_chunks_drugs = "./Data/chunks_farmaci.json",
                             path_chunks_para = "./Data/chunks_parafarmaci.json",
                             path_mapper_drugs_foglietto= "./Data/mapper_aic_foglietto_farmaco.json")

if __name__== "__main__":
    print(doctor_stoned.get_similarity_para("025680024"))