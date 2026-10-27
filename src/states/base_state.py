from abc import ABC, abstractmethod

class BaseState(ABC):

    def __init__(self, state_manager):
        self.state_manager = state_manager

    @abstractmethod
    def process_events(self, events):
        """Trata cliques, teclas e input especificos desta tela."""
        pass
    @abstractmethod
    def update(self, dt):
        """Atualiza a logica e fisica desta tela."""
        pass

    @abstractmethod
    def draw(self, surface):
        """Desenha os elementos desta tela."""
        pass