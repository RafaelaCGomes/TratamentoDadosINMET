import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import glob
import os

def selecionar_pasta():
    pasta_escolhida = filedialog.askdirectory(title="Selecione a pasta com os arquivos tratados")
    
    if not pasta_escolhida:
        return

    try:
        caminho_padrao = os.path.join(pasta_escolhida, "*_media_precipitacao.csv")
        arquivos = glob.glob(caminho_padrao)

        if not arquivos:
            messagebox.showwarning("Aviso", "Nenhum arquivo '_media_precipitacao.csv' encontrado nesta pasta!")
            return

        lista_dfs = []
        prefixo_estacao = None

        for arquivo in arquivos:
            # Lê o arquivo ignorando possíveis problemas de codificação
            df = pd.read_csv(arquivo, sep=';', decimal=',', encoding='utf-8-sig')
            lista_dfs.append(df)
            
            if not prefixo_estacao:
                nome_base = os.path.basename(arquivo)
                partes = nome_base.split("_")
                for i, parte in enumerate(partes):
                    if ("-" in parte or "/" in parte) and len(parte) == 10:
                        prefixo_estacao = "_".join(partes[:i]) + "_"
                        break
                if not prefixo_estacao:
                    prefixo_estacao = nome_base.rsplit("_media_precipitacao", 1)[0].rsplit("_", 4)[0] + "_"

        # Une todos os dataframes
        df_final = pd.concat(lista_dfs, ignore_index=True)
        
        # CORREÇÃO: Usa format='mixed' para aceitar tanto hífen quanto barra nas datas
        df_final['DATA'] = pd.to_datetime(df_final['DATA'], format='mixed', errors='coerce')
        
        # Remove linhas com datas inválidas por segurança
        df_final = df_final.dropna(subset=['DATA'])
        
        # Ordena cronologicamente
        df_final = df_final.sort_values(by='DATA').reset_index(drop=True)
        
        # Pega a primeira e a última data formatadas corretamente com hífen
        data_inicio = df_final['DATA'].min().strftime('%d-%m-%Y')
        data_fim = df_final['DATA'].max().strftime('%d-%m-%Y')
        
        df_final['DATA'] = df_final['DATA'].dt.strftime('%Y-%m-%d')
        
        if prefixo_estacao:
            nome_final = f"{prefixo_estacao}{data_inicio}_A_{data_fim}_media_precipitacao.csv"
        else:
            nome_final = f"CONSOLIDADO_{data_inicio}_A_{data_fim}_media_precipitacao.csv"
            
        caminho_saida = os.path.join(pasta_escolhida, nome_final)

        # Salva o arquivo consolidado
        df_final.to_csv(caminho_saida, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        
        messagebox.showinfo("Sucesso!", f"Arquivos unidos com sucesso!\n\nSalvo em:\n{caminho_saida}")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao juntar os arquivos:\n{str(e)}")

# Configuração da Janela
root = tk.Tk()
root.title("Unificador de Tabelas INMET")
root.geometry("500x350")
root.config(bg="#f4f6f9")
root.resizable(False, False)

lbl_titulo = tk.Label(root, text="Unificador INMET", font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#333333")
lbl_titulo.pack(pady=(30, 10))

lbl_sub = tk.Label(root, text="Selecione a pasta onde estão os arquivos\npara juntá-los em uma única tabela.", font=("Segoe UI", 11), bg="#f4f6f9", fg="#666666", justify="center")
lbl_sub.pack(pady=(0, 30))

btn_processar = tk.Button(
    root, 
    text="Selecionar Pasta e Juntar", 
    command=selecionar_pasta, 
    font=("Segoe UI", 12, "bold"), 
    bg="#28A745", 
    fg="white", 
    activebackground="#218838",
    activeforeground="white",
    relief="flat", 
    cursor="hand2",
    width=25, 
    height=2
)
btn_processar.pack(pady=10)

btn_sair = tk.Button(
    root, 
    text="Sair", 
    command=root.destroy, 
    font=("Segoe UI", 10), 
    bg="#f4f6f9", 
    fg="#d9534f", 
    activebackground="#f4f6f9",
    activeforeground="#c9302c",
    relief="flat", 
    cursor="hand2"
)
btn_sair.pack(pady=(20, 0))

root.mainloop()