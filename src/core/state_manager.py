#Módulo de gerenciamento de estados (telas) do jogo.
import pygame

class StateManager:
    #Gerencia o registro, a troca e o ciclo de vida das telas do jogo.
    def __init__(self):
        #Inicializa o gerenciador sem estados cadastrados.
        self.states = {}
        self.current_state = None
        self.ultimo_tempo = 0  # Regista o momento exato da última troca de ecrã

    def add_state(self, name, state_instance):
        #Registra uma instância de estado associada ao nome fornecido.
        self.states[name] = state_instance

    def change_state(self, name):
        #Alterna para o estado indicado respeitando um intervalo mínimo de 250 ms.
        tempo_atual = pygame.time.get_ticks()
        
        if tempo_atual - self.ultimo_tempo > 250:
            if name in self.states:
                self.current_state = self.states[name]
                self.ultimo_tempo = tempo_atual

    def process_events(self, events):
        #Repassa a lista de eventos do Pygame para o estado ativo.
        if self.current_state:
            self.current_state.process_events(events)

    def update(self, dt):
        #Atualiza a lógica do estado ativo com base no tempo decorrido ('dt').
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, surface):
        #Renderiza o estado ativo na superfície fornecida.
        if self.current_state:
            self.current_state.draw(surface)