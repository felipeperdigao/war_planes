from sre_constants import JUMP
from tokenize import String
import pygame, random, time
pygame.init()

#relógios e frame rate
relogio = pygame.time.Clock()
fps = 60

#configurações da tela
largura_tela = 1280
altura_tela = 720
altura_painel = 120
tela = pygame.display.set_mode((largura_tela, altura_tela))
icone = pygame.image.load('assets/UI/iconWP.png')
pygame.display.set_caption('War Planes!')
pygame.display.set_icon(icone)

menu = pygame.image.load('assets/UI/menu.png')
fundo_img = pygame.image.load('assets/UI/background.png')
hud = pygame.image.load('assets/UI/hud.png')
icone_vida = pygame.image.load('assets/UI/icon.vida.png')
branco = (255, 255, 255)
preto = (0, 0, 0)

#textos e fontes
fonte = pygame.font.Font('assets/Perfect DOS VGA 437.ttf', 80)
fonte_peq = pygame.font.Font('assets/Perfect DOS VGA 437.ttf', 30)
game_over_bg = pygame.image.load('assets/UI/gameover.png')
fx = (pygame.mixer.Sound('assets/fx/disparo.wav'), pygame.mixer.Sound('assets/fx/explosao.wav'))

#Estado atual do jogo: 0 = menu; 1 = jogo, 2 = game over
estado_jogo = 0
iniciando = True

def nova_animacao(caminho, comprimento):
    anim = []
    for i in range(comprimento):
        img = pygame.image.load(f'{caminho}/{i}.png')
        anim.append(img)
    return anim
    

inimigo_anim = nova_animacao('assets/enemy', 4)
    
tiro_anim = []
tiro_anim.append(nova_animacao('assets/player/tiro_player', 3))
tiro_anim.append(nova_animacao('assets/player/tiro_esp1', 3))
tiro_anim.append(nova_animacao('assets/player/tiro_esp2', 3))
temp = []
for i in range(3):
    img = pygame.transform.flip(tiro_anim[2][i], False, True)
    temp.append(img)
tiro_anim.append(temp)

explosao_anim = nova_animacao('assets/misc/explosao', 3)

power_anim = nova_animacao('assets\misc\icon_pu', 5)

alerta_frame = 0
alerta_anim = nova_animacao('assets/misc/atention_level', 8)
alerta_time = [0, 0]
desenha_alerta = False


#pontuação
pontuacao = 0
nivel_atual = 1
prox_nivel = nivel_atual * 10
vidas = 3

bg_pos = 0
velocidade = 1

#Classe o Jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        #importção e animações e configurando-as
        self.anim_lista = []
        self.frame_id = 0
        self.anim_id = 0     #indice de animações| 0 = neutro | 1 = explosão
        self.anim_lista.append(nova_animacao('assets/player', 4))
        self.anim_lista.append(explosao_anim)
        self.temp_atualizar = pygame.time.get_ticks()
        
        
        #hitbox
        self.rect = self.anim_lista[self.anim_id][self.frame_id].get_rect()
        
        #posição inicial
        self.rect.center = (100, (altura_tela - altura_painel) // 2 - 32)
        #velociadade (de movimento e de tiro)
        self.velocidade = 9
        self.cooldown = pygame.time.get_ticks() - 300
        
        #power ups
        # [0] = velocidade extra
        # [1] tipo  tiros (0 = normal | 1 = penetrar | 2 = espalhado)
        # [2] = dobrar pontuação
        self.power_ups = [False, 0, False]
        self.temporizadores = [0, 0, 0]
        
        self.vivo = True
    
    #controle de animações
    def atualizar(self):
        if self.vivo: cooldown_animação = 100 // (self.velocidade + self.power_ups[0])
        else: cooldown_animação = 100
        self.imagem = self.anim_lista[0][self.frame_id]
        if pygame.time.get_ticks() - self.temp_atualizar > cooldown_animação:
            self.temp_atualizar = pygame.time.get_ticks()
            self.frame_id += 1
            if self.frame_id >= 4:
                self.frame_id = 0
    
    def aprimorar(self, power_up):
        if power_up == 0: 
            global vidas
            vidas = min(9, vidas + 1)
        elif power_up == 1:
            self.power_ups[2] = True
            self.temporizadores[2] = pygame.time.get_ticks()
        elif power_up == 2: 
            self.power_ups[0] = True
            self.temporizadores[0] = pygame.time.get_ticks()
        elif power_up == 3: 
            self.power_ups[1] = 1
            self.temporizadores[1] = pygame.time.get_ticks()
        elif power_up == 4: 
            self.power_ups[1] = 2
            self.temporizadores[1] = pygame.time.get_ticks()
    
    def controle_powerups(self):
        if self.power_ups[0] and pygame.time.get_ticks() - self.temporizadores[0] > 20000:
            self.power_ups[0] = False
        if self.power_ups[1] == 1 and pygame.time.get_ticks() - self.temporizadores[1] > 15000:
            self.power_ups[1] = 0
        if self.power_ups[1] == 2 and pygame.time.get_ticks() - self.temporizadores[1] > 10000:
            self.power_ups[1] = 0
        if self.power_ups[2] and pygame.time.get_ticks() - self.temporizadores[2] > 15000:
            self.power_ups[1] = False
    
    #movimentações e outros controles do jogador
    def controle(self):
        cooldown_tiro = 175
        if self.power_ups[0]: velocidade = self.velocidade + 6
        else: velocidade = self.velocidade
        teclas_pressionadas = pygame.key.get_pressed()
        if self.rect.top > 0:
              if teclas_pressionadas[pygame.K_w] or teclas_pressionadas[pygame.K_UP]:
                  self.rect.move_ip(0, -velocidade)
        if self.rect.bottom < altura_tela - altura_painel:        
              if teclas_pressionadas[pygame.K_s] or teclas_pressionadas[pygame.K_DOWN]:
                  self.rect.move_ip(0, velocidade)
        if self.rect.left > 0:
              if teclas_pressionadas[pygame.K_a] or teclas_pressionadas[pygame.K_LEFT]:
                  self.rect.move_ip(-(velocidade - 3), 0)
        if self.rect.right < largura_tela:        
              if teclas_pressionadas[pygame.K_d] or teclas_pressionadas[pygame.K_RIGHT]:
                  self.rect.move_ip((velocidade - 3), 0) 
        if teclas_pressionadas[pygame.K_SPACE] or teclas_pressionadas[pygame.K_RETURN]:
                if (len(disparos) < 8 or (self.power_ups[1] == 2 and len(disparos) < 10))and pygame.time.get_ticks() - self.cooldown > cooldown_tiro:
                    if self.power_ups[1] == 2:
                        disparos.add(Projetil(jogador.rect.right - 4, jogador.rect.bottom - 8, 2, self.power_ups[0]))
                        disparos.add(Projetil(jogador.rect.right - 4, jogador.rect.bottom - 10, 0, self.power_ups[0]))
                        disparos.add(Projetil(jogador.rect.right - 4, jogador.rect.bottom - 12, 3, self.power_ups[0]))
                    else: disparos.add(Projetil(jogador.rect.right - 4, jogador.rect.bottom - 10, self.power_ups[1], self.power_ups[0]))
                    self.cooldown = pygame.time.get_ticks()
                    fx[0].play()
                  
#Classe dos projéteis
class Projetil(pygame.sprite.Sprite):
    def __init__(self,x,y, tipo, vel):
        super().__init__()
        
        #carrega a imagem
        self.frame_id = 0
        self.anim_lista = tiro_anim[tipo]
        self.rect = self.anim_lista[0].get_rect()
        self.temp_atualizar = pygame.time.get_ticks()
        
        #posição inicial
        self.rect.center = (x, y - 6)
        #velocidade
        self.vel = 10 + vel * 2
        
        self.tipo = tipo
        
    
    #controle de animações
    def atualizar(self):
        cooldown_animação = 100
        self.imagem = self.anim_lista[self.frame_id]
        if pygame.time.get_ticks() - self.temp_atualizar > cooldown_animação:
            self.temp_atualizar = pygame.time.get_ticks()
            self.frame_id += 1
            if self.frame_id >= 3:
                self.frame_id = 0
    
    def desenhar(self):
        if self.tipo == 2: self.rect.move_ip(disparo.vel / 2, -disparo.vel / 2)
        elif self.tipo == 3: self.rect.move_ip(disparo.vel / 2, disparo.vel / 2)
        else: self.rect.move_ip(disparo.vel, 0)
        tela.blit(self.imagem, self.rect)

#Classe do inimigo
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, i):
        super().__init__()
        
        #animações do inimigo
        self.anim_lista = []
        self.anim_id = 0     #indice de animações| 0 = neutro | 1 = explosão
        self.frame_id = 0
        self.anim_lista.append(inimigo_anim)
        self.anim_lista.append(explosao_anim)
        self.temp_atualizar = pygame.time.get_ticks()
        
        #hitbox do inimigo
        self.rect = self.anim_lista[self.anim_id][self.frame_id].get_rect()
        self.rect.center = (largura_tela * i + 256, random.randint(32, altura_tela - altura_painel - 64))
        self.vivo = True
    
    #controle de animações
    def atualizar(self):
        if self.vivo: cooldown_animação = 100 // velocidade
        else: cooldown_animação = 100
        if pygame.time.get_ticks() - self.temp_atualizar > cooldown_animação:
            self.temp_atualizar = pygame.time.get_ticks()
            self.frame_id += 1
            if self.anim_id == 0 and self.frame_id >= 4:
                self.frame_id = 0
            elif self.anim_id == 1 and self.frame_id >= 3:
                self.frame_id = 0
                self.anim_id = 0
                self.rect.right = -150
                self.vivo = True
    
    #movimentação do inimgo
    def mover(self):
        self.rect.move_ip(-(2 * velocidade), 0)
        if (self.rect.right < 0):
            self.rect.left = largura_tela
            self.rect.center = (largura_tela, random.randint(32, altura_tela - altura_painel - 32))
            
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        self.frame_id = random.choices(range(5), [1, 3, 5, 4, 3], k = 1)[0]
        self.anim_lista = power_anim
        self.rect = self.anim_lista[0].get_rect()
        self.temp_atualizar = pygame.time.get_ticks()
        
        #posição inicial
        self.rect.center = pos
        
    def atualizar(self):
        cooldown_animação = 1500
        self.imagem = self.anim_lista[self.frame_id]
        if pygame.time.get_ticks() - self.temp_atualizar > cooldown_animação:
            self.temp_atualizar = pygame.time.get_ticks()
            self.frame_id = random.choices(range(5), [1, 3, 5, 4, 3], k = 1)[0]
                
    def desenhar(self):
        self.rect.move_ip(- 3, 0)
        tela.blit(self.imagem, self.rect)
        
        
        

jogador = Jogador()
inimigo = Inimigo(1)
inimigos = pygame.sprite.Group()
inimigos.add(inimigo)
disparos = pygame.sprite.Group()
power_ups = pygame.sprite.Group()

#Game Loop
rodar = True
while rodar:
    #controle de frame
    relogio.tick(fps)
    pygame.display.update()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodar = False
            
    if estado_jogo == 0:
        tela.blit(menu, (0, 0))
        for evento in pygame.event.get():
            teclas_pressionadas = pygame.key.get_pressed()
            if teclas_pressionadas[pygame.K_r]:
                estado_jogo = 1
                iniciar = pygame.time.get_ticks()
            if teclas_pressionadas[pygame.K_s]:
                rodar = False
            
    elif estado_jogo == 1:
        
        #desenha e faz ele andar o fundo
        tela.blit(fundo_img, (bg_pos, 0))
        bg_pos -= velocidade
        if bg_pos <= -largura_tela:
            bg_pos += largura_tela
        
        
        if iniciando:
            pronto = fonte_peq.render('PRONTO!', True, preto)
            tela.blit(pronto, (largura_tela // 2 - 40, altura_tela // 2 - 40))
            if pygame.time.get_ticks() - iniciar > 3000:
                iniciando = False
        else:
               
            #desenha o jogador
            tela.blit(jogador.anim_lista[jogador.anim_id][jogador.frame_id], jogador.rect)
            if jogador.vivo:
                jogador.controle()
            jogador.atualizar()
            jogador.controle_powerups()
            
            #desenha o inimigo
            for inimigo in inimigos:
                tela.blit(inimigo.anim_lista[inimigo.anim_id][inimigo.frame_id], inimigo.rect)
                inimigo.mover()
                inimigo.atualizar()
            
            #desenha os tiros
            for disparo in disparos:
                if disparo.rect.left < largura_tela and disparo.rect.bottom > 0 and disparo.rect.top < altura_tela - altura_painel:
                    disparo.atualizar()
                    disparo.desenhar()
                else:
                    disparos.remove(disparo)
                    
            for power_up in power_ups:
                if power_up.rect.left < largura_tela:
                    power_up.atualizar()
                    power_up.desenhar()
                else:
                    power_ups.remove(power_up)
            
            #checa a colisão dos inimigos com os tiros    
            for inimigo in inimigos:
                disparo = pygame.sprite.spritecollideany(inimigo, disparos)
                if disparo and inimigo.vivo:
                    inimigo.vivo = False
                    inimigo.anim_id = 1
                    inimigo.frame_id = 0
                    if jogador.power_ups[1] != 1: disparo.kill()
                    if jogador.power_ups[2]: pontuacao += 2
                    else: pontuacao += 1
                    prox_nivel -= 1
                    fx[1].play()
                    if len(power_ups) < 5 and random.randint(1, 8) == 1:
                        new_power = PowerUp(inimigo.rect.center)
                        power_ups.add(new_power)
                    
            if prox_nivel <= 0:
                nivel_atual += 1
                prox_nivel += nivel_atual * 10
                desenha_alerta = True
                alerta_time[0] = pygame.time.get_ticks()
                alerta_time[1] = pygame.time.get_ticks()
                if velocidade <= 9:
                    velocidade += 1
                if nivel_atual % 3 == 0 and len(inimigos) < 4:
                    new_enemy = Inimigo(len(inimigos) + 1)
                    inimigos.add(new_enemy)
                
            
            if jogador.vivo:
                power_up_coletado = pygame.sprite.spritecollideany(jogador, power_ups)
                if power_up_coletado:
                    jogador.aprimorar(power_up_coletado.frame_id)
                    power_ups.remove(power_up_coletado)
                    
                
                #checa se houve colisão entre o jogador e os inimigos e fecha o jogo
                inimigo_colidido = pygame.sprite.spritecollideany(jogador, inimigos)
                if inimigo_colidido and inimigo_colidido.vivo:
                    desenha_alerta = False
                    vidas -= 1
                    inimigo_colidido.anim_id = 1
                    inimigo_colidido.frame_id = 0
                    iniciando = True
                    fx[1].play()
                    for i, inimigo in enumerate(inimigos):
                        inimigo = Inimigo(i + 1)
                    if vidas == 0:
                        estado_jogo = 2
                    else:
                        #Vidas Extras
                        jogador.anim_id = 1
                        jogador.frame_id = 0
                        jogador.vivo = False
            else:
                if jogador.frame_id >= 3:
                    jogador = Jogador()
                    for i, inimigo in enumerate(inimigos):
                        inimigo = Inimigo(i + 1)
                    for disparo in disparos:
                        disparo.kill()
                    for power_up in power_ups:
                        power_up.kill()
                    prox_nivel = nivel_atual * 10
                    iniciando = True
                    iniciar = pygame.time.get_ticks()
                    
        #HUD
        tela.blit(hud, (0, altura_tela - altura_painel))
            
        #pontuação
        pontuacoes = fonte_peq.render(f'MORTES: ' + str(pontuacao).zfill(5), True, preto)
        tela.blit(pontuacoes, (100, altura_tela - altura_painel + 30))
            
        #fase atual
        nivel = fonte_peq.render(f'ALERTA: {nivel_atual:2}', True, preto)
        tela.blit(nivel, (largura_tela - 250, altura_tela - altura_painel + 30))
            
        #contador de vidas
        vida = fonte_peq.render(f'VIDAS: ', True, preto)
        tela.blit(vida, (100, altura_tela - altura_painel + 70))
        for i in range(vidas):
            tela.blit(icone_vida, (210 + i * 40, altura_tela - altura_painel + 65))
            
        if desenha_alerta:
            if pygame.time.get_ticks() - alerta_time[0] > 50:
                alerta_frame += 1
                alerta_time [0] = pygame.time.get_ticks()
                if alerta_frame >= 8:
                    alerta_frame = 0
            tela.blit(alerta_anim[alerta_frame], (largura_tela // 2 - 32, altura_tela - altura_painel + 24))
            if pygame.time.get_ticks() - alerta_time[1] > 3000: 
                desenha_alerta = False
                alerta_frame = 0
    
    elif estado_jogo == 2:
        #Game Over
        tela.blit(game_over_bg, (0, 0))
        pont_tot = fonte.render(str(pontuacao).zfill(5), True, preto)
        tela.blit(pont_tot, (largura_tela // 3 + 100, altura_tela // 3))
        pygame.display.update()
        
        for evento in pygame.event.get():
            teclas_pressionadas = pygame.key.get_pressed()
            if teclas_pressionadas[pygame.K_r]:
                estado_jogo = 1
                jogador = Jogador()
                for inimigo in inimigos:
                    inimigo.kill()
                new_enemy = Inimigo(0)
                inimigos.add(new_enemy)
                for disparo in disparos:
                    disparo.kill()
                for power_up in power_ups:
                    power_up.kill()
                pontuacao = 0
                nivel_atual = 1
                prox_nivel = nivel_atual * 10
                velocidade = 1
                vidas = 3
                iniciando = True
                iniciar = pygame.time.get_ticks()
            if teclas_pressionadas[pygame.K_s]:
                rodar = False
            
    
pygame.quit()