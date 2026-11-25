import pygame
import sys
import json
from pathlib import Path
from lote import Lote
from config import LOTES_CONFIG

ARQUIVO_ESTADO = Path(__file__).resolve().parent / "savegame.json"

def carregar_estado():
    if not ARQUIVO_ESTADO.exists():
        return None

    try:
        with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as _arquivo:
            return json.load(_arquivo)
    except (json.JSONDecodeError, OSError):
        return None

def salvar_estado(dinheiro, lotes, tempo_jogo, ganhou):
    estado = {
        "dinheiro": dinheiro,
        "niveis": [lote.nivel for lote in lotes],
        "tempo_jogo": tempo_jogo,
        "ganhou": ganhou,
    }

    try:
        with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as arquivo:
            json.dump(estado, arquivo, indent=4, ensure_ascii=False)
    except OSError:
        pass

def verifica_fim(lotes):
    for lote in lotes:
        if lote.nivel < lote.nivel_maximo:
            return False
    return True

pygame.init()

LARGURA, ALTURA = 1200, 900
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("tycoon")

imagem_fundo = pygame.image.load("images/fundo.png").convert()
imagem_fundo = pygame.transform.scale_by(imagem_fundo, 1.5)

fonte_dinheiro = pygame.font.Font(None, 36)
fonte_botao = pygame.font.Font(None, 30)

BRANCO = (255, 0, 255)
CINZA_CLARO = (200, 200, 200)

# tamanho dos lotes
largura_botao = 262
altura_botao = 187

# espaçamento lote
espacamento_x = 60
espacamento_y = 60

largura_total = (2 * largura_botao) + espacamento_x
altura_total = (2 * altura_botao) + espacamento_y

inicio_x = (LARGURA - largura_total) // 2
inicio_y = (ALTURA - altura_total) // 2

lotes = []

for i in range(4):
    image = pygame.image.load(LOTES_CONFIG["0"]["image_path"])
    custo_inicial = LOTES_CONFIG["0"]["custo"]
    
    linha = i // 2  
    coluna = i % 2
    
    x = inicio_x + coluna * (largura_botao + espacamento_x)
    y = inicio_y + linha * (altura_botao + espacamento_y)
    
    lote = Lote(x, y, largura_botao, altura_botao, image, custo_inicial)
    lote.nivel = 0
    lotes.append(lote)

estado = carregar_estado()

# continuar só aparece quando existe um estado de jogo que nao esta na pontuacao maxima
pode_continuar = False

if isinstance(estado, dict):
    niveis_salvos = estado.get("niveis", [])

    # valida a estrutura
    if len(niveis_salvos) == len(lotes) and not estado.get("ganhou", False):
        pode_continuar = all(
            isinstance(nivel, int) and nivel < lotes[i].nivel_maximo
            for i, nivel in enumerate(niveis_salvos)
        )

fonte_menu_titulo = pygame.font.Font(None, 72)
fonte_menu = pygame.font.Font(None, 50)

botao_continuar = pygame.Rect(420, 350, 360, 70)
botao_novo = pygame.Rect(420, 450, 360, 70)

jogo_iniciado = False
rodando = True
clock = pygame.time.Clock()

while rodando and not jogo_iniciado:
    tela.fill((0, 0, 0))

    titulo = fonte_menu.render("Fazendinha Click Click", True, (255, 255, 255))
    tela.blit(titulo, titulo.get_rect(center=(600, 220)))

    if pode_continuar:
        pygame.draw.rect(tela, (0, 100, 200), botao_continuar)
        texto = fonte_menu.render("Continuar", True, (255, 255, 255))
        tela.blit(texto, texto.get_rect(center=botao_continuar.center))

    pygame.draw.rect(tela, (0, 150, 0), botao_novo)
    texto = fonte_menu.render("Novo jogo", True, (255, 255, 255))
    tela.blit(texto, texto.get_rect(center=botao_novo.center))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if pode_continuar and botao_continuar.collidepoint(evento.pos):
                # carrega o estado salvo
                dinheiro_salvo = estado["dinheiro"]
                niveis_salvos = estado["niveis"]

                dinheiro = dinheiro_salvo
                tempo_jogo = estado["tempo_jogo"]

                # atualiza os níveis dos lotes com base nos dados salvos
                for i in range(4):
                    nivel = niveis_salvos[i]
                    for x in range(nivel):
                        lotes[i].evoluir(i + 1)

                ganhou = estado["ganhou"]
                jogo_iniciado = True

            # novo jogo
            if botao_novo.collidepoint(evento.pos):
                if ARQUIVO_ESTADO.exists():
                    ARQUIVO_ESTADO.unlink()

                dinheiro = 5
                tempo_jogo = 0
                ganhou = False
                jogo_iniciado = True

    pygame.display.flip()
    clock.tick(60)

contador_frames = 0
sinais_ganho = []

while rodando:
    contador_frames += 1
    if contador_frames >= 60:
        for lote in lotes:
            if lote.nivel > 0:
                dinheiro += lote.ganho
        contador_frames = 0
        if not ganhou:
            tempo_jogo += 1
        salvar_estado(dinheiro, lotes, tempo_jogo, ganhou)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            salvar_estado(dinheiro, lotes, tempo_jogo, ganhou)
            rodando = False

        for i, lote in enumerate(lotes):
            lote_num = i + 1
          
            # botão de Upgrade
            if lote.verificar_clique_botao(evento):
                print(f"botao lote {lote_num} clicado")
                
                if lote.nivel < lote.nivel_maximo and dinheiro >= lote.custo:
                    dinheiro -= lote.custo
                    lote.evoluir(lote_num)
                    
                    if verifica_fim(lotes):
                        ganhou = True
                    salvar_estado(dinheiro, lotes, tempo_jogo, ganhou)
            
            if lote.verifica_clique_lote(evento):
                if lote.ganho > 0:
                    dinheiro += lote.ganho

                    # Adiciona sinal de ganho visual
                    sinais_ganho.append({
                        'x': evento.pos[0] - 10,
                        'y': evento.pos[1] - 10,
                        'texto': f"+{lote.ganho}",
                        'tempo_vida': 45
                    })
                    salvar_estado(dinheiro, lotes, tempo_jogo, ganhou)

    if not ganhou:
        tela.blit(imagem_fundo, (0, 0))
        
        texto_dinheiro = fonte_dinheiro.render(f"Dinheiro: ${dinheiro}", True, (0, 0, 0))
        tela.blit(texto_dinheiro, (10, 10))
        
        for lote in lotes:
            lote.desenhar(tela, fonte_botao)

        # Desenhar +1 quando clicar no lote
        for sinal in sinais_ganho:
            texto_surf = fonte_dinheiro.render(sinal['texto'], True, (0, 200, 0))
            tela.blit(texto_surf, (sinal['x'], sinal['y']))
            
            sinal['y'] -= 2
            sinal['tempo_vida'] -= 1

        sinais_ganho = [f for f in sinais_ganho if f['tempo_vida'] > 0]

    else:
        # tela de Vitória
        tela.fill((0, 0, 0))
        texto_vitoria = f"Parabéns! Você ganhou em {tempo_jogo} segundos!"
        texto_ganhou = fonte_dinheiro.render(texto_vitoria, True, (255, 255, 255))
        texto_rect = texto_ganhou.get_rect(center=(LARGURA // 2, ALTURA // 2))
        tela.blit(texto_ganhou, texto_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()