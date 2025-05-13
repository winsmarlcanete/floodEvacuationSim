from mesa import Agent
import random

class EvacueeAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.evacuated = False

    def step(self):
        if self.evacuated:
            return

        # Find nearest low-hazard road segment
        next_segment = self.model.get_next_segment(self.pos)
        if next_segment is None:
            return

        # Move to next position
        self.pos = next_segment

        if self.model.is_safe_zone(self.pos):
            self.evacuated = True
