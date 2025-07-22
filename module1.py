import pandas as pd
from datetime import datetime, time, timedelta
import json
import os
import re

class PlantaoManager:
    def __init__(self, arquivo_csv, meu_nome, idioma='pt'):
        self.arquivo_csv = arquivo_csv
        self.meu_nome = meu_nome
        self.idioma = idioma
        self.plantoes = None
        self.plantonistas_info = {}
        self.escalations_info = {}

        self._carregar_plantoes()
        self._carregar_contatos()

    def _carregar_plantoes(self):
        try:
            self.plantoes = pd.read_csv(self.arquivo_csv)
            # Converte a coluna 'Data' para datetime com formato dd/mm/yyyy
            self.plantoes['Data'] = pd.to_datetime(self.plantoes['Data'], format='%d/%m/%Y')
        except Exception as e:
            print(f"Erro ao carregar CSV: {e}")
            self.plantoes = pd.DataFrame(columns=['Data','Entrada','Saida','Plantonista','Escalation'])

    def _carregar_contatos(self):
        self.plantonistas_info = self._carregar_json('plantonistas.json')
        self.escalations_info = self._carregar_json('escalations.json')

    def _carregar_json(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _salvar_json(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_plantao_por_data(self, data_consulta):
        # data_consulta é datetime.date
        for _, row in self.plantoes.iterrows():
            data_plantao = row['Data'].date()

            entrada_str = row['Entrada']
            saida_str = row['Saida']

            entrada = datetime.strptime(entrada_str, "%H:%M").time()
            saida = datetime.strptime(saida_str, "%H:%M").time()

            # Ajuste para plantões que passam da meia-noite
            inicio = datetime.combine(data_plantao, entrada)
            if saida <= entrada:
                fim = datetime.combine(data_plantao + timedelta(days=1), saida)
            else:
                fim = datetime.combine(data_plantao, saida)

            if inicio.date() <= data_consulta <= fim.date():
                # Verifica se o data_consulta está dentro do intervalo
                data_consulta_dt = datetime.combine(data_consulta, time.min)
                if inicio <= data_consulta_dt < fim:
                    return row
        return None

    def responder(self, entrada):
        entrada = entrada.lower()

        # Pergunta pelo próximo plantão do usuário
        if ('próximo plantão' in entrada) or ('next on-call' in entrada):
            return self._proximo_plantao()

        # Pergunta se tem plantão numa data
        match_data = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', entrada)
        if match_data:
            data_str = match_data.group(1)
            try:
                data = datetime.strptime(data_str, '%d/%m/%Y').date()
            except ValueError:
                return "Formato de data inválido." if self.idioma == 'pt' else "Invalid date format."

            if 'plantão no dia' in entrada or 'on-call on' in entrada:
                return self._tem_plantao_na_data(data)

            if 'telefone do escalation' in entrada or 'escalation phone' in entrada:
                return self._telefone_escalation_na_data(data)

        # Comandos para ensinar contatos
        if entrada.startswith('plantonistas são') or entrada.startswith('plantonistas are'):
            return self.ensinar_plantonistas(entrada)
        if entrada.startswith('escalations são') or entrada.startswith('escalations are'):
            return self.ensinar_escalations(entrada)

        return ("Não entendi. Tente novamente." if self.idioma == 'pt' else "I didn't understand. Please try again.")

    def _proximo_plantao(self):
        hoje = datetime.now().date()
        futuras = self.plantoes[self.plantoes['Data'] >= hoje]
        futuras = futuras.sort_values('Data')

        for _, row in futuras.iterrows():
            if row['Plantonista'].lower() == self.meu_nome.lower():
                data_str = row['Data'].strftime('%d/%m/%Y')
                entrada = row['Entrada']
                saida = row['Saida']
                if self.idioma == 'pt':
                    return f"Seu próximo plantão é em {data_str}, das {entrada} às {saida}."
                else:
                    return f"Your next on-call is on {data_str}, from {entrada} to {saida}."

        if self.idioma == 'pt':
            return "Você não tem plantões futuros."
        else:
            return "You have no upcoming on-calls."

    def _tem_plantao_na_data(self, data):
        plantao = self._get_plantao_por_data(data)
        if plantao is not None and plantao['Plantonista'].lower() == self.meu_nome.lower():
            if self.idioma == 'pt':
                return f"Sim, você está de plantão em {data.strftime('%d/%m/%Y')}."
            else:
                return f"Yes, you are on-call on {data.strftime('%d/%m/%Y')}."
        else:
            if self.idioma == 'pt':
                return f"Não, você não está de plantão em {data.strftime('%d/%m/%Y')}."
            else:
                return f"No, you are not on-call on {data.strftime('%d/%m/%Y')}."

    def _telefone_escalation_na_data(self, data):
        plantao = self._get_plantao_por_data(data)
        if plantao is None:
            return ("Não há plantão nesta data." if self.idioma == 'pt' else "No on-call found for this date.")

        escalation = plantao['Escalation']
        nome_tel = escalation
        telefone = None
        for nome_salvo, tel in self.escalations_info.items():
            if nome_salvo.strip().lower() == escalation.strip().lower():
                telefone = tel
                break
        if telefone:
            nome_tel = f"{escalation} - {telefone}"

        if self.idioma == 'pt':
            return f"Escalation para {data.strftime('%d/%m/%Y')}: {nome_tel}"
        else:
            return f"Escalation for {data.strftime('%d/%m/%Y')}: {nome_tel}"

    def ensinar_plantonistas(self, texto):
        try:
            # Pega tudo depois de ':' e divide por vírgulas
            partes = texto.split(':',1)[1].split(',')
            for p in partes:
                if ':' not in p:
                    continue
                nome, tel = p.strip().split(':',1)
                self.plantonistas_info[nome.strip()] = tel.strip()
            self._salvar_json("plantonistas.json", self.plantonistas_info)
            return ("Plantonistas atualizados com sucesso." if self.idioma == 'pt' else "On-call contacts updated successfully.")
        except Exception as e:
            return ("Erro ao atualizar plantonistas." if self.idioma == 'pt' else "Error updating on-call contacts.")

    def ensinar_escalations(self, texto):
        try:
            partes = texto.split(':',1)[1].split(',')
            for p in partes:
                if ':' not in p:
                    continue
                nome, tel = p.strip().split(':',1)
                self.escalations_info[nome.strip()] = tel.strip()
            self._salvar_json("escalations.json", self.escalations_info)
            return ("Escalations atualizados com sucesso." if self.idioma == 'pt' else "Escalation contacts updated successfully.")
        except Exception as e:
            return ("Erro ao atualizar escalations." if self.idioma == 'pt' else "Error updating escalation contacts.")
