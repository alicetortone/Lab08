from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO
import datetime
from statistics import mean

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        lista_prezzo_medio = []
        for distrib in self._distributori:
            id = distrib.id
            prezzi = PrezzoDAO.get_prezzi(id)
            lista_prezzi_mensili = []
            for p in prezzi:
                if p.data.month == mese:
                    lista_prezzi_mensili.append(p.prezzo_litro)
            media = mean(lista_prezzi_mensili)
            lista_prezzo_medio.append((distrib.nome, media))
        return lista_prezzo_medio

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno == 8 :
            if self.__costo_ottimo == -1 or self.__costo_ottimo < costo_corrente:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        for distributore in self._distributori:
            # un loop, se necessario
            if ultimo_distributore is not None and distributore != ultimo_distributore:
                costo_spostamento = 5
            else:
                costo_spostamento = 0

            costo_carburante = 100 * prezzi_settimana[distributore.id][giorno - 1]
            nuovo_costo = costo_corrente + costo_carburante + costo_spostamento

            sequenza_parziale.append(distributore.id)

            self.__ricorsione(sequenza_parziale, giorno + 1, distributore, nuovo_costo, prezzi_settimana)
            # back tracking
            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_prima_settimana = {}
        for distrib in self._distributori:
            prezzi = PrezzoDAO.get_prezzi(distrib.id)
            lista_prezzi_prima_settimana = []
            for p in prezzi:
                #i prezzi sono riportati nel database in ordine temporale
                count = 0
                if p.data.month == mese and count < 7 :
                    lista_prezzi_prima_settimana.append(p.prezzo_litro)
                    count += 1
            prezzi_prima_settimana[distrib.id] = lista_prezzi_prima_settimana
        return prezzi_prima_settimana