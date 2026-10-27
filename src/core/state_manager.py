class StateManager:

    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, name, state_instance):
        self.states[name] = state_instance

    def change_state(self, name):
        if name in self.states:
            self.current_state = self.states[name]

    def process_events(self, events):
        if self.current_state:
            self.current_state.process_events(events)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)