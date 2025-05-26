from PIL import Image, ImageEnhance
import numpy as np
import os
import matplotlib.pyplot as plt

def calcular_histograma(caminho_imagem, num_niveis):
    """
    Calcula o histograma de uma imagem em tons de cinza.
    """
    try:
        img = Image.open(caminho_imagem).convert('L')
        img_array = np.array(img)
        contagens_histograma, _ = np.histogram(img_array.flatten(), bins=num_niveis, range=(0, num_niveis))
        niveis_cinza = np.arange(num_niveis)
        return contagens_histograma, niveis_cinza
    except Exception as e:
        print(f"Erro em calcular_histograma: {e}")
        return None, None

def plotar_histograma(histograma, niveis_cinza, num_niveis, titulo_imagem="Imagem"):
    """
    Plota o histograma da imagem.
    """
    if histograma is not None and niveis_cinza is not None:
        plt.figure(figsize=(10, 6))
        plt.bar(niveis_cinza, histograma, width=1.0, color='dodgerblue', edgecolor='black', linewidth=0.5)
        plt.title(f"Histograma de '{titulo_imagem}' ({num_niveis} níveis)")
        plt.xlabel("Nível de Cinza ($r_k$)")
        plt.ylabel("Número de Pixels ($n_k$)")
        plt.xlim([-0.5, num_niveis - 0.5]) 
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.show()
    else:
        print("Dados do histograma ausentes para plotagem.")

def salvar_variante_imagem(imagem_pil, nome_base_arquivo, nome_variante):
    """Salva a imagem PIL, tentando PGM primeiro, depois PNG."""
    try:
        # Garante que a imagem está em modo 'L' (tons de cinza) para PGM
        if imagem_pil.mode != 'L':
            imagem_pil = imagem_pil.convert('L')
        
        nome_arquivo_pgm = f"{nome_base_arquivo}_{nome_variante}.pgm"
        imagem_pil.save(nome_arquivo_pgm)
        print(f"Imagem salva como: {nome_arquivo_pgm}")
        return nome_arquivo_pgm
    except Exception as e_pgm:
        print(f"Não foi possível salvar como PGM ({e_pgm}), tentando PNG...")
        try:
            nome_arquivo_png = f"{nome_base_arquivo}_{nome_variante}.png"
            imagem_pil.convert('L').save(nome_arquivo_png)
            print(f"Imagem salva como: {nome_arquivo_png}")
            return nome_arquivo_png
        except Exception as e_png:
            print(f"Falha ao salvar imagem {nome_variante}: {e_png}")
            return None

def mostrar_imagem(imagem_pil, titulo="Imagem"):
    """
    Mostra uma imagem usando matplotlib.
    """
    plt.figure(figsize=(8, 8))
    plt.imshow(imagem_pil, cmap='gray')
    plt.title(titulo)
    plt.axis('off')
    plt.show()

def mostrar_imagens_e_histogramas(imagens_geradas, num_niveis_histograma):
    """
    Mostra as imagens e seus histogramas em um formato de slideshow.
    """
    # Cria uma figura com dois subplots lado a lado
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Lista de nomes das variantes
    variantes = list(imagens_geradas.keys())
    current_idx = 0
    
    def update_plot(idx):
        # Limpa os subplots
        ax1.clear()
        ax2.clear()
        
        # Obtém os dados da variante atual
        nome_variante = variantes[idx]
        dados = imagens_geradas[nome_variante]
        
        # Calcula estatísticas da imagem
        img_array = np.array(dados["imagem"])
        valor_medio = np.mean(img_array)
        valor_min = np.min(img_array)
        valor_max = np.max(img_array)
        
        ax1.imshow(dados["imagem"], cmap='gray')
        ax1.set_title(f"Imagem: {nome_variante}\nMédia: {valor_medio:.1f}, Min: {valor_min}, Max: {valor_max}")
        ax1.axis('off')
        
        # Calcula e plota o histograma
        histograma, niveis = calcular_histograma(dados["caminho"], num_niveis_histograma)
        if histograma is not None:
            ax2.bar(niveis, histograma, width=1.0, color='dodgerblue', edgecolor='black', linewidth=0.5)
            ax2.set_title(f"Histograma: {nome_variante}")
            ax2.set_xlabel("Nível de Cinza ($r_k$)")
            ax2.set_ylabel("Número de Pixels ($n_k$)")
            ax2.set_xlim([-0.5, num_niveis_histograma - 0.5])
            ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        fig.canvas.draw()
    
    def on_key(event):
        nonlocal current_idx
        if event.key == 'right' or event.key == 'down':
            current_idx = (current_idx + 1) % len(variantes)
        elif event.key == 'left' or event.key == 'up':
            current_idx = (current_idx - 1) % len(variantes)
        update_plot(current_idx)
    
    # Conecta o evento de teclado
    fig.canvas.mpl_connect('key_press_event', on_key)
    
    update_plot(current_idx)
    
    print("\nUse as setas do teclado para navegar:")
    print("→ ou ↓ : Próxima imagem")
    print("← ou ↑ : Imagem anterior")
    
    plt.show()

def gerar_e_analisar_variantes(caminho_imagem_base, num_niveis_histograma=256):
    """
    Carrega uma imagem base, gera variações de contraste/brilho,
    salva-as e calcula/plota seus histogramas.
    """
    try:
        img_pil_base = Image.open(caminho_imagem_base).convert('L')
        print(f"Imagem base '{caminho_imagem_base}' carregada com sucesso.")
    except FileNotFoundError:
        print(f"Erro: Imagem base '{caminho_imagem_base}' não encontrada.")
        return
    except Exception as e:
        print(f"Erro ao carregar a imagem base: {e}")
        return

    nome_base_sem_ext = os.path.splitext(caminho_imagem_base)[0]
    
    imagens_geradas = {}
    
    # Imagem Original
    imagens_geradas["original"] = {"caminho": caminho_imagem_base, "imagem": img_pil_base}
    
    # Imagem Escura 
    realcador_brilho = ImageEnhance.Brightness(img_pil_base)
    img_escura = realcador_brilho.enhance(0.5)  
    
    # Correção gamma para tornar a diferença mais perceptível
    img_array = np.array(img_escura)
    gamma = 2.0  # Fator gamma > 1 escurece mais os tons médios
    img_array = np.power(img_array / 255.0, gamma) * 255.0
    img_escura = Image.fromarray(img_array.astype(np.uint8))
    
    caminho_escura = salvar_variante_imagem(img_escura, nome_base_sem_ext, "escura")
    if caminho_escura:
        imagens_geradas["escura"] = {"caminho": caminho_escura, "imagem": img_escura}
    
    # Imagem Clara 
    img_clara = realcador_brilho.enhance(2.0)
    caminho_clara = salvar_variante_imagem(img_clara, nome_base_sem_ext, "clara")
    if caminho_clara:
        imagens_geradas["clara"] = {"caminho": caminho_clara, "imagem": img_clara}
    
    # Imagem com Baixo Contraste 
    realcador_contraste = ImageEnhance.Contrast(img_pil_base)
    img_baixo_contraste = realcador_contraste.enhance(0.1)
    caminho_baixo_contraste = salvar_variante_imagem(img_baixo_contraste, nome_base_sem_ext, "baixo_contraste")
    if caminho_baixo_contraste:
        imagens_geradas["baixo_contraste"] = {"caminho": caminho_baixo_contraste, "imagem": img_baixo_contraste}
    
    # Imagem com Alto Contraste
    img_alto_contraste = realcador_contraste.enhance(3.0)
    caminho_alto_contraste = salvar_variante_imagem(img_alto_contraste, nome_base_sem_ext, "alto_contraste")
    if caminho_alto_contraste:
        imagens_geradas["alto_contraste"] = {"caminho": caminho_alto_contraste, "imagem": img_alto_contraste}

    mostrar_imagens_e_histogramas(imagens_geradas, num_niveis_histograma)

if __name__ == "__main__":
    caminho_imagem_base = "lena.pgm"
    gerar_e_analisar_variantes(caminho_imagem_base, num_niveis_histograma=256)