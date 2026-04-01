from typing import Any, Dict, Optional

class Scene:
    async def start(self, app):
        pass

class State:
    def get_data(self) -> Dict[str, Any]: pass
    def set_data(self, data: Dict[str, Any]): pass
    def update_data(self, data: Dict[str, Any]): pass
    def get_scene(self) -> Optional[Scene]: pass
    def set_scene(self, scene: Scene): pass

class MapState(State):
    def __init__(self, data: Dict[str, Any], scene: Optional[Scene]):
        self.data = data.copy()
        self.scene = scene

    def get_data(self) -> Dict[str, Any]: return self.data
    def set_data(self, data: Dict[str, Any]): self.data = data
    def update_data(self, data: Dict[str, Any]): self.data.update(data)
    def get_scene(self) -> Optional[Scene]: return self.scene
    def set_scene(self, scene: Scene): self.scene = scene

class MapStateManager:
    def __init__(self, init_data: Dict[str, Any]):
        self.states: Dict[str, State] = {}
        self.init_data = init_data
        self.start_scene: Optional[Scene] = None

    def get_start_scene(self) -> Optional[Scene]:
        """
        Returns the initial scene assigned to new states.
        """
        return self.start_scene

    def set_start_scene(self, start_scene: Scene):
        """
        Sets the default scene for all newly created states.

        Example:
            manager.set_start_scene(WelcomeScene())
        """
        self.start_scene = start_scene

    def get(self, state_id: str) -> Optional[State]:
        """
        Retrieves the state object associated with the given ID.
        """
        return self.states.get(state_id)

    def create(self, state_id: str) -> State:
        """
        Initializes a new state for the given ID using template data and the start scene.

        Example:
            state = manager.create("chat_12345")
        """
        self.states[state_id] = MapState(self.init_data, self.start_scene)
        return self.states[state_id]

    def delete(self, state_id: str):
        """
        Purges the state data for the specified ID.
        """
        self.states.pop(state_id, None)

    def get_state_data(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns the data dictionary for the specific state.

        Example:
            user_info = manager.get_state_data("chat_123")
        """
        state = self.get(state_id)
        return state.get_data() if state else None

    def set_state_data(self, state_id: str, new_state_data: Dict[str, Any]):
        """
        Completely replaces the data dictionary for the specified state.
        """
        state = self.get(state_id)
        if state: state.set_data(new_state_data)

    def update_state_data(self, state_id: str, new_state_data: Dict[str, Any]):
        """
        Updates specific keys in the state data dictionary.

        Example:
            manager.update_state_data("chat_123", {"is_authorized": True})
        """
        state = self.get(state_id)
        if state: state.update_data(new_state_data)

    def activate_next_scene(self, state_id: str, scene: Scene):
        """
        Transitions the specified state to a new scene.

        Example:
            manager.activate_next_scene("chat_123", MainMenuScene())
        """
        state = self.get(state_id)
        if state: state.set_scene(scene)

    def get_current_scene(self, state_id: str) -> Optional[Scene]:
        """
        Retrieves the currently active scene object for the given ID.
        """
        state = self.get(state_id)
        return state.get_scene() if state else None