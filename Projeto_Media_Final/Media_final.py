import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def processar_tres_tabelas():
    arquivos = filedialog.askopenfilenames(
        title="Selecione exatamente 3 arquivos de precipitação",
        filetypes=[("Arquivos CSV", "*.csv *.CSV")]
    )
    
    if not arquivos:
        return

    if len(arquivos) != 3:
        messagebox.showwarning("Atenção", f"Você selecionou {len(arquivos)} arquivos.\nPor favor, selecione EXATAMENTE 3 arquivos.")
        return

    try:
        lista_dfs = []
        
        # Lê cada um dos 3 arquivos
        for i, arquivo in enumerate(arquivos):
            df = pd.read_csv(arquivo, sep=';', decimal=',', encoding='utf-8-sig')
            
            df.columns = [col.strip().upper() for col in df.columns]
            
            if 'DATA' not in df.columns or 'PRECIPITACAO_MEDIA_MM' not in df.columns:
                raise ValueError(f"O arquivo {os.path.basename(arquivo)} não possui as colunas esperadas ('DATA', 'PRECIPITACAO_MEDIA_MM').")
            
            df['DATA'] = pd.to_datetime(df['DATA'], format='mixed', errors='coerce')
            df = df.dropna(subset=['DATA'])
            
            # Converte a precipitação para float de forma segura
            df['PRECIPITACAO_MEDIA_MM'] = pd.to_numeric(
                df['PRECIPITACAO_MEDIA_MM'].astype(str).str.replace(',', '.'), errors='coerce'
            )
            
            # Renomeia a coluna de precipitação para identificar cada estação (ex: PRECIP_0, PRECIP_1, PRECIP_2)
            df = df[['DATA', 'PRECIPITACAO_MEDIA_MM']].rename(columns={'PRECIPITACAO_MEDIA_MM': f'PRECIP_{i}'})
            lista_dfs.append(df)

        # Une as 3 tabelas usando 'outer' (junta por data mantendo todos os dias que existirem em qualquer tabela)
        df_combinado = pd.merge(lista_dfs[0], lista_dfs[1], on='DATA', how='outer')
        df_combinado = pd.merge(df_combinado, lista_dfs[2], on='DATA', how='outer')
        
        # Calcula a média diária ignorando valores vazios (NaN) caso alguma estação não tenha o dia
        df_combinado['PRECIPITACAO_MEDIA_MM'] = df_combinado[['PRECIP_0', 'PRECIP_1', 'PRECIP_2']].mean(axis=1, skipna=True)
        
        # Arredonda para 5 casas decimais
        df_combinado['PRECIPITACAO_MEDIA_MM'] = df_combinado['PRECIPITACAO_MEDIA_MM'].round(5)
        
        # Ordena cronologicamente
        df_combinado = df_combinado.sort_values(by='DATA').reset_index(drop=True)
        
        # Pega a primeira e última data formatadas para o nome do arquivo
        data_inicio = df_combinado['DATA'].min().strftime('%d-%m-%Y')
        data_fim = df_combinado['DATA'].max().strftime('%d-%m-%Y')
        
        df_combinado['DATA'] = df_combinado['DATA'].dt.strftime('%Y-%m-%d')
        
        # Seleciona apenas as colunas finais
        df_final = df_combinado[['DATA', 'PRECIPITACAO_MEDIA_MM']]
        
        # Define o caminho de salvamento na mesma pasta do primeiro arquivo
        diretorio_origem = os.path.dirname(arquivos[0])
        nome_novo_arquivo = f"MEDIA_3_ESTACOES_{data_inicio}_A_{data_fim}_media_precipitacao.csv"
        caminho_saida = os.path.join(diretorio_origem, nome_novo_arquivo)

        # Salva o arquivo final
        df_final.to_csv(
            caminho_saida, 
            index=False, 
            encoding='utf-8-sig', 
            sep=';', 
            decimal=','
        )
        
        messagebox.showinfo("Sucesso!", f"Média das 3 tabelas calculada com sucesso!\n\nSalvo em:\n{caminho_saida}")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao processar:\n{str(e)}")

# Configuração da Janela Visual
root = tk.Tk()
root.title("Média de 3 Tabelas INMET")
root.geometry("500x350")
root.config(bg="#f4f6f9")
root.resizable(False, False)

lbl_titulo = tk.Label(root, text="Média de 3 Estações", font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#333333")
lbl_titulo.pack(pady=(30, 10))

lbl_sub = tk.Label(root, text="Selecione exatamente 3 arquivos tratados\npara calcular a média diária combinada.", font=("Segoe UI", 11), bg="#f4f6f9", fg="#666666", justify="center")
lbl_sub.pack(pady=(0, 30))

btn_processar = tk.Button(
    root, 
    text="Selecionar 3 Arquivos e Calcular", 
    command=processar_tres_tabelas, 
    font=("Segoe UI", 12, "bold"), 
    bg="#17A2B8", 
    fg="white", 
    activebackground="#138496",
    activeforeground="white",
    relief="flat", 
    cursor="hand2",
    width=28, 
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
btn_sair.pack(side="bottom", pady=20)

root.mainloop()