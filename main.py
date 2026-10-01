import pygame
import sys
from lote import Lote
from config import LOTES_CONFIG

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

dinheiro = 5 
contador_frames = 0

clock = pygame.time.Clock()

sinais_ganho = []

rodando = True
ganhou = False

tempo_jogo = 0

while rodando:
    contador_frames += 1
    if contador_frames >= 60:
        for lote in lotes:
            if lote.nivel > 0:
                dinheiro += lote.ganho
        contador_frames = 0
        if not ganhou:
            tempo_jogo += 1

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
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