import pygame

class StateManager:

    def __init__(self):
        self.states = {}
        self.current_state = None
        self.ultimo_tempo = 0  # Regista o momento exato da última troca de ecrã

    def add_state(self, name, state_instance):
        self.states[name] = state_instance

    def change_state(self, name):
        tempo_atual = pygame.time.get_ticks()
        
        # Só permite uma nova troca se tiverem passado 250 milissegundos
        if tempo_atual - self.ultimo_tempo > 250:
            if name in self.states:
                self.current_state = self.states[name]
                self.ultimo_tempo = tempo_atual

    def process_events(self, events):
        if self.current_state:
            self.current_state.process_events(events)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)