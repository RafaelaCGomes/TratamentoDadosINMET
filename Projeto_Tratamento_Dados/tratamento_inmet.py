import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def processar_arquivo():
    arquivo_entrada = filedialog.askopenfilename(
        title="Selecione o arquivo CSV do INMET",
        filetypes=[("Arquivos CSV", "*.csv *.CSV")]
    )
    
    if not arquivo_entrada:
        return

    try:
        # Processamento dos dados
        df = pd.read_csv(arquivo_entrada, skiprows=8, sep=';', encoding='latin1', decimal=',')
        coluna_data = 'DATA (YYYY-MM-DD)'
        coluna_precipitacao = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'
        
        df_filtrado = df[df[coluna_precipitacao] != -9999].copy()
        df_agrupado = df_filtrado.groupby(df_filtrado[coluna_data])[coluna_precipitacao].mean().reset_index()
        df_agrupado.columns = ['DATA', 'PRECIPITACAO_MEDIA_MM']
        
        # Arredondar para 5 casas decimais
        df_agrupado['PRECIPITACAO_MEDIA_MM'] = df_agrupado['PRECIPITACAO_MEDIA_MM'].round(5)
        
        # Nome dinâmico do arquivo de saída
        diretorio_origem = os.path.dirname(arquivo_entrada)
        nome_arquivo_completo = os.path.basename(arquivo_entrada)
        nome_base, _ = os.path.splitext(nome_arquivo_completo)
        nome_novo_arquivo = f"{nome_base}_media_precipitacao.csv"
        caminho_saida = os.path.join(diretorio_origem, nome_novo_arquivo)

        # Salvar o novo CSV com delimitador ';' e vírgula para decimais
        df_agrupado.to_csv(
            caminho_saida, 
            index=False, 
            encoding='utf-8-sig', 
            sep=';', 
            decimal=','
        )
        
        messagebox.showinfo("Sucesso", f"Processamento concluído!\n\nSalvo como:\n{nome_novo_arquivo}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Configuração da Janela Principal
root = tk.Tk()
root.title("Processador de Dados INMET")
root.geometry("500x350")
root.config(bg="#f4f6f9")
root.resizable(False, False)

lbl_titulo = tk.Label(root, text="Processador INMET", font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#333333")
lbl_titulo.pack(pady=(30, 10))

lbl_sub = tk.Label(root, text="Selecione o arquivo CSV para gerar\na média diária de precipitação.", font=("Segoe UI", 11), bg="#f4f6f9", fg="#666666", justify="center")
lbl_sub.pack(pady=(0, 30))

btn_processar = tk.Button(
    root, 
    text="Selecionar arquivo CSV", 
    command=processar_arquivo, 
    font=("Segoe UI", 12, "bold"), 
    bg="#007ACC", 
    fg="white", 
    activebackground="#005999",
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