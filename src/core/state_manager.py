#Módulo de gerenciamento de estados (telas) do jogo.
import pygame

class StateManager:
    #Gerencia o registro, a troca e o ciclo de vida das telas do jogo.
    def __init__(self):
        #Inicializa o gerenciador sem estados cadastrados.
        self._states = {}
        self._current_state = None
        self._ultimo_tempo = 0

    @property
    def current_state(self):
       #Retorna a instância do estado atualmente ativo (somente leitura).   
        return self._current_state

    def add_state(self, name, state_instance):
        #Registra uma instância de estado associada ao nome fornecido.
        self._states[name] = state_instance

    def change_state(self, name):
        #Alterna para o estado indicado respeitando um intervalo mínimo de 250 ms.
        tempo_atual = pygame.time.get_ticks()
        
        if tempo_atual - self._ultimo_tempo > 250:
            if name in self._states:
                self._current_state = self._states[name]
                self._ultimo_tempo = tempo_atual

    def process_events(self, events):
        #Repassa a lista de eventos do Pygame para o estado ativo.
        if self._current_state:
            self._current_state.process_events(events)

    def update(self, dt):
        #Atualiza a lógica do estado ativo com base no tempo decorrido ('dt').
        if self._current_state:
            self._current_state.update(dt)

    def draw(self, surface):
        #Renderiza o estado ativo na superfície fornecida.
        if self._current_state:
            self._current_state.draw(surface)