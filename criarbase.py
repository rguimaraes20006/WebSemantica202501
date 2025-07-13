import pandas as pd
import os
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal
from unidecode import unidecode

BASE_URL = "http://www.ons.org.br/ontologia/sin#"
ONS = Namespace(BASE_URL)
PASTA = "./Arquivos base"


def remover_acentos(texto):    
    return unidecode(texto)

ontology = Graph()
ontology.bind("ons", ONS)
ontology.parse("ons-ontology-ia.ttl", format="ttl")

individuals = Graph()
individuals.bind("ons", ONS)


def adicionar_agente(row):
    agent_uri = ONS[f'Agente_{row["age_id"]}']
    tipo = row['tipo'].strip().lower()
    if tipo == 'transmissao':
        individuals.add((agent_uri, RDF.type, ONS.Transmissao))
    elif tipo == 'geracao':
        individuals.add((agent_uri, RDF.type, ONS.Geracao))
    else:
        individuals.add((agent_uri, RDF.type, ONS.Agente))

    individuals.add((agent_uri, ONS.age_id, Literal(row['age_id'])))
    individuals.add((agent_uri, ONS.descricao, Literal(remover_acentos(  row['descricao']))))
    individuals.add((agent_uri, ONS.nome, Literal( remover_acentos(row['nome']))))
    individuals.add((agent_uri, ONS.tipo, Literal( remover_acentos(row['tipo']))))

def adicionar_subestacao(row) :  #ins_id,nome,descricao
    sub_uri = ONS[f'Subestacao_{row["ins_id"]}']
    individuals.add((sub_uri, RDF.type, ONS.Subestacao))
    individuals.add((sub_uri, ONS.ins_id, Literal(row['ins_id'])))
    individuals.add((sub_uri, ONS.nome, Literal( remover_acentos( row['nome']))))
    if 'descricao' in row:
        individuals.add((sub_uri, ONS.descricao, Literal( remover_acentos( row['descricao']))))

def adicionar_usina(row):  #usi_id,ins_id,nome_usina,tipo,age_id,potencianominal
    usina_uri = ONS[f'Usina_{row["usi_id"]}']
    individuals.add((usina_uri, RDF.type, ONS.Usina))
    individuals.add((usina_uri, ONS.usi_id, Literal(row['usi_id'])))
    individuals.add((usina_uri, ONS.ins_id, ONS[f'Subestacao_{row["ins_id"]}']))
    individuals.add((usina_uri, ONS.nome_usina, Literal(row['nome_usina'])))
    individuals.add((usina_uri, ONS.tipo, Literal(  remover_acentos(row['tipo']))))
    individuals.add((usina_uri, ONS.age_id,  ONS[f'Agente_{row["age_id"]}']))


    #se existir a row['potencianominal'], adiciona a propriedade convertendo para duas casas decimais em formato string
    if 'potencianominal' in row and pd.notna(row['potencianominal']):
        # Verifica se o valor é numérico e converte para float
        try:
            potencia = float(row['potencianominal'])
            # Formata para duas casas decimais
            potencia_formatada = f"{potencia:.2f}"
            individuals.add((usina_uri, ONS.potencianominal, Literal(potencia_formatada)))
        except ValueError:
            individuals.add((usina_uri, ONS.potencianominal, Literal('0.00')))
    
def adicionar_transformador(row):  #eqp_id,age_id_prop,nomelongo,ins_id
    transformador_uri = ONS[f'Transformador_{row["eqp_id"]}']
    individuals.add((transformador_uri, RDF.type, ONS.Transformador))
    individuals.add((transformador_uri, ONS.eqp_id, Literal(row['eqp_id'])))
    individuals.add((transformador_uri, ONS.age_id_prop,  ONS[f'Agente_{row["age_id_prop"]}']))
    individuals.add((transformador_uri, ONS.nomelongo, Literal(remover_acentos(row['nomelongo']))))
    individuals.add((transformador_uri, ONS.ins_id, ONS[f'Subestacao_{row["ins_id"]}']))

def adicionar_linhatransmissao(row):  #eqp_id,age_id,descricao,instalacao_de,instalacao_para
    linha_uri = ONS[f'LinhaTransmissao_{row["eqp_id"]}']
    individuals.add((linha_uri, RDF.type, ONS.LinhaTransmissao))
    individuals.add((linha_uri, ONS.eqp_id, Literal(row['eqp_id'])))
    individuals.add((linha_uri, ONS.age_id,  ONS[f'Agente_{row["age_id"]}']))
    individuals.add((linha_uri, ONS.instalacao_de, ONS[f'Subestacao_{row["instalacao_de"]}']))
    individuals.add((linha_uri, ONS.descricao, Literal(remover_acentos(row['descricao']))))
    individuals.add((linha_uri, ONS.instalacao_de, ONS[f'Subestacao_{row["instalacao_de"]}']))
    individuals.add((linha_uri, ONS.instalacao_para, ONS[f'Subestacao_{row["instalacao_para"]}']))


#AGENTE
agente_df = pd.read_csv(os.path.join(PASTA, 'Agente.csv'), encoding='windows-1252')
for _, row in agente_df.iterrows():
    adicionar_agente(row)

#SUBESTAÇÃO ins_id,nome,descricao
sub_df = pd.read_csv(os.path.join(PASTA, 'Subestacao.csv'), encoding='windows-1252')
for _, row in sub_df.iterrows():
    adicionar_subestacao(row)

#USINA - usi_id,ins_id,nome_usina,tipo,age_id,potencianominal
usi_df = pd.read_csv(os.path.join(PASTA, 'Usina.csv'), encoding='utf-8')
for _, row in usi_df.iterrows():
    adicionar_usina(row)


#TRANSFORMADOR - eqp_id,age_id_prop,nomelongo,ins_id
transformador_df = pd.read_csv(os.path.join(PASTA, 'Transformador.csv'), encoding='utf-8')
for _, row in transformador_df.iterrows():
    adicionar_transformador(row)    

#LINHA DE TRANSMISSÃO - eqp_id,age_id,descricao,instalacao_de,instalacao_para
linha_df = pd.read_csv(os.path.join(PASTA, 'LinhaTransmissao.csv'), encoding='utf-8')
for _, row in linha_df.iterrows():
    adicionar_linhatransmissao(row)


individuals.serialize(destination="ons-ontology-individuals.ttl", format="turtle")


