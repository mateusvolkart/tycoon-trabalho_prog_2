import pygame
from config import LOTES_CONFIG

class Lote:
    def __init__(self, x, y, largura, altura, imagem_superficie, custo_inicial):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        
        self.imagem = pygame.transform.scale(imagem_superficie, (largura, altura))
        
        self.rect_lote = self.imagem.get_rect()
        self.rect_lote.topleft = (x, y)
        
        self.nivel = 0
        self.nivel_maximo = max(int(nivel) for nivel in LOTES_CONFIG)

        custo_proximo_nivel = str(self.nivel + 1)

        if custo_proximo_nivel in LOTES_CONFIG:
            self.custo = LOTES_CONFIG[custo_proximo_nivel]["custo"]
        else:
            self.custo = 0

        # level 1 não tem ganho por segundo, apenas ganho por clique
        if "ganho_clique" in LOTES_CONFIG[str(self.nivel)]:
            self.ganho = LOTES_CONFIG[str(self.nivel)]["ganho_clique"]
        else:
            self.ganho = LOTES_CONFIG[str(self.nivel)]["ganho_por_segundo"]

        self.rect_botao = pygame.Rect(x, y + altura + 8, largura, 45)

    def evoluir(self, lote_num):
        if self.nivel < self.nivel_maximo:
            self.nivel += 1
            dados = LOTES_CONFIG[str(self.nivel)]
            proximo_nivel = str(self.nivel + 1)

            # Atualiza o custo
            if proximo_nivel in LOTES_CONFIG:
                self.custo = LOTES_CONFIG[proximo_nivel]["custo"] * lote_num
            else:
                self.custo = 0
                
            # Atualiza o ganho
            self.ganho = int(dados["ganho_por_segundo"] * lote_num)
            
            # Atualiza a imagem
            nova_imagem = pygame.image.load(dados["image_path"])
            self.imagem = pygame.transform.scale(nova_imagem, (self.largura, self.altura))

    def desenhar(self, superficie, fonte):
        superficie.blit(self.imagem, (self.rect_lote.x, self.rect_lote.y))
        
        pygame.draw.rect(superficie, (0, 150, 0), self.rect_botao)
        pygame.draw.rect(superficie, (0, 0, 0), self.rect_botao, 2)
        
        texto_botao = fonte.render(f"Upgrade ${self.custo}", True, (255, 255, 255))
        if self.nivel == self.nivel_maximo:
            texto_botao = fonte.render("Max Level", True, (255, 255, 255))
            
        texto_rect = texto_botao.get_rect(center=self.rect_botao.center)
        superficie.blit(texto_botao, texto_rect)

    def verificar_clique_botao(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if self.rect_botao.collidepoint(evento.pos):
                    return True
        return False

    def verifica_clique_lote(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if self.rect_lote.collidepoint(evento.pos):
                    return True
        return False