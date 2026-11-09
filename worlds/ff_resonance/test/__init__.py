from test.bases import WorldTestBase

from ..world import FFResonanceWorld


class FFResonanceTestBase(WorldTestBase):
    game = "Final Fantasy Resonance"
    world: FFResonanceWorld
