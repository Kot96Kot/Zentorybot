def build_mock_action_payload(action_type: str, payload: dict) -> dict:
    return {"mock": True, "action_type": action_type, "payload": payload}
