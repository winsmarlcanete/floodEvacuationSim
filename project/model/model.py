from mesa import Model
from mesa.time import RandomActivation
import geopandas as gpd
import random
from agent import EvacueeAgent

class FloodEvacuationModel(Model):
    def __init__(self, num_agents):
        self.schedule = RandomActivation(self)

        # Load road network
        self.roads = gpd.read_file("data/final_data/RoadMapWithHazard.geojson")

        # Filter only usable roads
        self.roads = self.roads[self.roads["Var_max"].notnull()]

        # Spawn agents at random low-hazard locations
        for i in range(num_agents):
            start = self.roads[self.roads["hazard_level"] == "low"].sample(1).geometry.values[0]
            agent = EvacueeAgent(i, self, start)
            self.schedule.add(agent)

    def get_next_segment(self, current_pos):
        # Simplified logic: pick a nearby connected low/medium hazard road
        candidates = self.roads[self.roads["hazard_level"].isin(["low", "medium"])]
        return candidates.sample(1).geometry.values[0]

    def is_safe_zone(self, pos):
        # Example: rightmost or northernmost roads
        return pos.bounds[0] > 121.12 or pos.bounds[3] > 14.72

    def step(self):
        self.schedule.step()
