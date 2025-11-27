import time
import os
import json

import faiss
import numpy as np
from dotenv import load_dotenv
import requests

import Middleware 


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
            "usage": {"include": True},
            "max_tokens": 32000
        }
        retry = 0
        max_retry = 3
        while retry < 3:
            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=30)
                response.raise_for_status()
                response = response.json()
                print(response['choices'][0]['message']["reasoning"])
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
            2) Anallizzali e decidi se quel parafarmaco è adatto come terapia coadivante rispetto al farmaco.
            3) Se decidi che esiste una correlazione valida, descrivermi brevemente a cosa serve il parafarmaco e spiega perché lo hai scelto.
            4) Se decidi che NON esiste una valida e diretta correlazione tra i due prodotti oppure se hai il dubbio, rispondi semplicemente con None.
            5) La risposta finale deve essere solo una stringa (in caso di correlazione) oppure None (in caso contrario).
        
            Regole:
            - Usa solo i nomi forniti.
            - Devi essere sufficientemente certo dell'utilità coadiuvante nella terapia del parafarmaco con il farmaco, restituisci esclusivamente None.
            - Usa un linguaggio semplice e chiaro comprensibile anche a chi non è del settore
            - Non inventare nulla, rispondi solo se presente nella sezione parafarmaci
            - Descrizione max 20 parole per voce.
            - Restituisci SOLO JSON valido, quindi None senza virgolette (no stringa) oppure una stringa.

            Esempio:
            input = [{{"file_name": "1002_12437", "content": "Virdex viene usato per alleviare i sintomi dell'emicrania quando questa si manifesta. Non è un trattamento preventivo, ma si assume durante l'attacco per ridurne intensità e durata"}},
                    {{"file_name": "EUGLYCEM 30CPR", "content": "VERTIGOVAL 20CPR": "Agisce migliorando le funzioni neurologiche, sostenendo la microcircolazione e riducendo sintomi associati alle alterazioni dell'equilibrio. Vertigoval aiuta a gestire sintomi associati come vertigini, nausea, instabilità e tensione nervosa"}}]
            output = None

            Esempio:
            input = [{{"file_name":"7158_25680", "content": "Monuril è un antibiotico a base di fosfomicina che uccide i batteri responsabili delle infezioni e viene utilizzato per trattare le infezioni urinarie non complicate nelle donne e adolescenti, oltre che come profilassi antibiotica perioperatoria per la biopsia prostatica transrettale negli uomini adulti"}},
                    {{"file_name": "LONGLIFE D-MANNOSE 60CPS", "content": "d-mannose\nè un integratore alimentare a base di d-mannosio, uno zucchero semplice estratto dal legno di larice o di betulla, e uva ursina.\nper la sua azione protettiva sulle cellule uroepiteliali, il d-mannosio può rappresentare un'alternativa naturale e sicura per contribuire alla riduzione delle infezioni del tratto urinario e delle cistiti infettive.\ncoopera a quest'azione l'uva ursina, una delle piante medicinali maggiormente utilizzate per favorire la funzionalità delle vie urinarie e il drenaggio dei liquidi corporei, grazie alla presenza di arbutina, composto ad attività antisettica.\nsenza glutine."}}]
            output = "Integratore che supporta le vie urinarie e riduce le cistiti; scelto perché coadiuvante all'azione di Monuril."

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
        reference_product_dict = {"file_name": similarity["reference_product"]["file_name"], "content": similarity["reference_product"]["content"]}
        reference_product_dump = json.dumps(reference_product_dict, ensure_ascii=True)

        # Creiamo la lista dei simili
        neighbor_products_list = similarity["neighbor_products"]

        # Cicliamo su tutti i suoi simili
        llm_response = {}
        llm_response[reference_product_dict["file_name"]] = {}
        for para in neighbor_products_list:
            neighbor_product_dict = {"file_name": para["product"]["file_name"], "content": para["product"]["content"]}
            neighbor_product_dump = json.dumps(neighbor_product_dict, ensure_ascii=False)
            llm_response[reference_product_dict["file_name"]][neighbor_product_dict["file_name"]] = self._call_llm(prompt=self._build_prompt(reference_product_dump, neighbor_product_dump),
                                                                                            system_prompt="",
                                                                                            model=self.model_id,
                                                                                            temperature=temperature)
            if llm_response[reference_product_dict["file_name"]][neighbor_product_dict["file_name"]] == "None":
                llm_response[reference_product_dict["file_name"]][neighbor_product_dict["file_name"]] = None
            elif llm_response[reference_product_dict["file_name"]][neighbor_product_dict["file_name"]] == "ERROR":
                llm_response[reference_product_dict["file_name"]].pop(neighbor_product_dict["file_name"])
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
        info = Middleware.middlwareDatabase.cerca_farmaco(aic,
                                        Middleware.middlwareDatabase.tipoRicercaBancadati.Codice_AIC,
                                        [Middleware.middlwareDatabase.tipoRicercaBancadati.Cl,
                                         Middleware.middlwareDatabase.tipoRicercaBancadati.Denominazione_e_Confezione])
        cl = None
        if info and len(info) > 0:
            if info[0] and len(info[0]) > 0:
                cl = info[0][0]
                denominazione = info[0][1]
        if not cl:
            return None

        # Depending of the result, find similaries
        if cl != "P": # <-- Drugs so find k para similarity
            # Convert aic to corrispondent "foglietto illustrativo" becose they are embedded like this
            file_name_foglietto = next((d[aic].strip(".txt") for d in self.mapper_drugs_foglietto if aic in d), None)
            if not file_name_foglietto: # There isn't a foglietto associated, so can't find similarity abort.
                return None
            # Find index in the chunks drugs that will be the same in faiss index
            aic_faiss_index = next((i for i, item in enumerate(self.chunks_drug) if item["file_name"] == file_name_foglietto), None)
            if aic_faiss_index:
                # Recostruction embedding from faiss index
                embedding = self.faiss_drugs.reconstruct(aic_faiss_index)
                drugs_embeddings = np.array(embedding, dtype="float32").reshape(1, -1)
                # Finally use search (cosen similarity)
                _, indices = self.faiss_para.search(drugs_embeddings, k)
                # Compose response struct for next step of pipeline
                def _convert_chunk_para_file_name_from_denominazione_to_aic(denominazione:dict, aic:str):
                    info = Middleware.middlwareDatabase.cerca_farmaco(denominazione["file_name"],
                                Middleware.middlwareDatabase.tipoRicercaBancadati.Denominazione_e_Confezione,
                                [Middleware.middlwareDatabase.tipoRicercaBancadati.Codice_AIC])
                    if info and len(info) > 0 and info[0] and len(info[0]) > 0:
                        denominazione["file_name"] = info[0][0]
                    return denominazione
                return {"reference_product": next(item for item in self.chunks_drug if item["file_name"] == file_name_foglietto),
                        "neighbor_products": [{"product": _convert_chunk_para_file_name_from_denominazione_to_aic(self.chunks_para[x], aic)} for x in indices[0]]}
            else:
                return None
        else:   # <-- Para so find k drugs foglietto similarity
            # We can use Descrizione prodotto to find chunk index, same as faiss
            aic_faiss_index = next((i for i, item in enumerate(self.chunks_para) if item["file_name"] == denominazione), None)
            if aic_faiss_index:
                # Recostruction embedding from faiss index
                embedding = self.faiss_para.reconstruct(aic_faiss_index)
                para_embeddings = np.array(embedding, dtype="float32").reshape(1, -1)
                # Finally use search (cosen similarity)
                _, indices = self.faiss_drugs.search(para_embeddings, k)
                # find a random drugs that associate to their foglietto
                def _get_random_drugs_from_foglietto(foglietto:str):
                    for coppia in self.mapper_drugs_foglietto:
                        for aic, foglietto_file_name in coppia.items():
                            if foglietto_file_name.strip(".txt") == foglietto["file_name"]:
                                foglietto["file_name"] = aic
                                return foglietto
                    return None
                # Compose response struct for next step of pipeline
                return {"reference_product": next(item for item in self.chunks_para if item["file_name"] == denominazione),
                        "neighbor_products": [{"product": _get_random_drugs_from_foglietto(self.chunks_drug[x])} for x in indices[0]]}
            else:
                return None

    # Public function

    def get_similarity_product(self, aic:str, k:int = 10, temperature:float = 0.3):
        """
        Call pipeline: similarity embedded para, validation LLM.
        Args:
            aic(str): AIC of a given get_similarity_product.
            k(int): Number of similarity given by embedding (not final result).
            temperature(float): temperature of LLM validation.
        Returns:
            list[tuple]: List of para_id and the LLM explain
        """
        product_chunks_similarities = self._find_similarity(aic, k)
        print(product_chunks_similarities["reference_product"]["file_name"])
        if not product_chunks_similarities:
            return None
        product_chunks_validated = self._validate_drug_similarity(product_chunks_similarities, temperature)
        if not product_chunks_validated:
            return None
        list_para_aic = []
        for chunk in product_chunks_validated.values():
            for product_name, llm_comment in chunk.items():
                if not llm_comment: # <- Not validate from LLM
                    continue
                # Find id by file name (same as Denominazione e confezione)
                info = Middleware.middlwareDatabase.cerca_farmaco(product_name,
                        Middleware.middlwareDatabase.tipoRicercaBancadati.Codice_AIC,
                        [Middleware.middlwareDatabase.tipoRicercaBancadati.Codice_AIC])
                # Ensure results
                if info and len(info) > 0 and info[0] and len(info[0]) > 0:
                    para_aic = info[0][0]
                    if not para_aic:
                        return None
                else:
                    return None
                # Add to list the tuple of id and LLM response
                list_para_aic.append([para_aic, llm_comment])
        print(f"RISULTATI: {list_para_aic}")
        if list_para_aic:
            return list_para_aic
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
    response = doctor_stoned.get_similarity_product("041797010")
    if response:
        print(json.dumps(response, indent=2))
    else:
        print(response)