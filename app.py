import pandas as pd
import numpy as np
from datetime import datetime

#criando segmentos
def recencia_class(x,r,q_dict):
    """Classifica como melhor o menor quartil
     x = valor da linha,
     r = recencia,
     q_dict = quartil dicionario"""
    
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'
    
def freq_val_class(x, fv, q_dict):
    """Classifica como melhoro maior quartil
    x = valor da linha,
    fv = frequencia ou valor,
    q_dict = quartil dicionario
    """

    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'
    
df_compras = pd.read_csv("dados.csv", infer_datetime_format=True, parse_dates=['DiaCompra'])

# Recencia

## Quantos dias fas que o cliente fez a última compra ?

df_recencia = df_compras.groupby(by='ID_cliente', as_index=False)['DiaCompra'].max()
df_recencia.columns = ['ID_cliente', 'DiaUltimaCompra']
print(df_recencia.head())

# Dia atual

dia_atual = df_compras['DiaCompra'].max()
print(dia_atual)

df_recencia['Recencia'] = df_recencia['DiaUltimaCompra'].apply(lambda x: (dia_atual - x).days)

print(df_recencia.head())

df_recencia.drop('DiaUltimaCompra', axis=1, inplace=True)

# Frequancia

## Quantas vezes cada cliente comprou ?

df_frequencia = df_compras[['ID_cliente','CodigoCompra']].groupby('ID_cliente').count().reset_index()
df_frequencia.columns = ['ID_cliente','Frequencia']
print(df_frequencia.head())

# Valor

## Quanto cada cliente gastou no periodo ?

df_valor = df_compras[['ID_cliente','ValorTotal']].groupby('ID_cliente').sum().reset_index()
df_valor.columns = ['ID_cliente','Valor']
print(df_valor.head())

# Criando a tabela RFV

df_RF = df_recencia.merge(df_frequencia, on='ID_cliente')
print(df_RF.head())

df_RFV = df_RF.merge(df_valor, on='ID_cliente')
df_RFV.set_index('ID_cliente', inplace=True)
print(df_RFV.head())

# Quatis para o RFV

quartis = df_RFV.quantile(q=[0.25,0.5,0.75])
print(quartis)

df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class,
                                                args=('Recencia',quartis))
df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class,
                                                  args=('Frequencia',quartis))
df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class,
                                             args=('Valor',quartis))
print(df_RFV.head)

df_RFV['RFV_Score'] = (df_RFV.R_quartil
                       + df_RFV.F_quartil
                       + df_RFV.V_quartil)
print(df_RFV.head)

df_RFV['RFV_Score'].value_counts()

df_RFV[df_RFV['RFV_Score']=='AAA'].sort_values('Valor', ascending=False).head(10)

# Ações de marketing/CRM

dict_acoes = {'AAA': 'Enviar cupons de desconto, Pedir para indicar nosso produto para algum amigo, Ao lançar um novo produto, enviar amostras grátis para esses.',
              'DDD': 'Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
              'DAA': 'Clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
              'CAA': 'Clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar'}

df_RFV['acoes de marketing/crm'] = df_RFV['RFV_Score'].map(dict_acoes)

print(df_RFV.head())

df_RFV.to_excel('./output/RFV.xlsx')