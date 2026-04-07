from typing import Any

class Scene:
    async def start(self, app):
        pass

class State:
    def get_data(self) -> dict[str, Any]: pass
    def set_data(self, data: dict[str, Any]): pass
    def update_data(self, data: dict[str, Any]): pass
    def get_scene(self) -> Scene | None: pass
    def set_scene(self, scene: Scene): pass

class MapState(State):
    def __init__(self, data: dict[str, Any], scene: Scene | None):
        self.data = data.copy()
        self.scene = scene

    def get_data(self) -> dict[str, Any]: return self.data
    def set_data(self, data: dict[str, Any]): self.data = data
    def update_data(self, data: dict[str, Any]): self.data.update(data)
    def get_scene(self) -> Scene | None: return self.scene
    def set_scene(self, scene: Scene): self.scene = scene

class MapStateManager:
    def __init__(self, init_data: dict[str, Any]):
        self.states: dict[str, State] = {}
        self.init_data = init_data
        self.start_scene: Scene | None = None

    def get_start_scene(self) -> Scene | None:
        return self.start_scene

    def set_start_scene(self, start_scene: Scene):
        self.start_scene = start_scene

    def get(self, state_id: str) -> State | None:
        return self.states.get(state_id)

    def create(self, state_id: str) -> State:
        self.states[state_id] = MapState(self.init_data, self.start_scene)
        return self.states[state_id]

    def delete(self, state_id: str):
        self.states.pop(state_id, None)

    def get_state_data(self, state_id: str) -> dict[str, Any] | None:
        state = self.get(state_id)
        return state.get_data() if state else None

    def set_state_data(self, state_id: str, new_state_data: dict[str, Any]):
        state = self.get(state_id)
        if state: state.set_data(new_state_data)

    def update_state_data(self, state_id: str, new_state_data: dict[str, Any]):
        state = self.get(state_id)
        if state: state.update_data(new_state_data)

    def activate_next_scene(self, state_id: str, scene: Scene):
        state = self.get(state_id)
        if state: state.set_scene(scene)

    def get_current_scene(self, state_id: str) -> Scene | None:
        state = self.get(state_id)
        return state.get_scene() if state else None