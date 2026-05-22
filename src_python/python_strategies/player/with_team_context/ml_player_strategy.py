import json
from python_strategies.player.with_team_context.base_strategy_with_team_context import BaseStrategyPlayerWithTeamContext
import sys
import os
import subprocess
import math

current_dir = os.path.dirname(os.path.abspath(__file__))
venv_site_packages = os.path.join(current_dir, "venv", "lib", "python3.13", "site-packages")
sys.path.append(venv_site_packages)

from ml_python.feature_builder import build_features

import numpy as np
import joblib

MOVE_TYPE_MAP = {
    0: "MoveForward",
    1: "RotateLeft",
    2: "RotateRight",
    3: "Shoot",
    4: "StandStill",
    5: "None"
}

MOVE_TYPE_REVERSE = {v: k for k, v in MOVE_TYPE_MAP.items()}

class MLSupervisedPlayerStrategy(BaseStrategyPlayerWithTeamContext):
    def __init__(self):
        self.clf_type = None
        self.clf_value = None
        self.team_count = None
        self.initialized = False

    def get_name(self) -> str:
        return "ML Supervised Learning PlayerStrategy"

    def init(self, teamCount: int, staticMap: dict):
        if self.initialized:
            return

        self.team_count = teamCount

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))

        venv_python = os.path.join(project_root, "venv", "bin", "python3")
        train_script = os.path.join(
            project_root,
            "src_python",
            "ml_python",
            "train_ml_model.py"
        )

        print(f"[MLStrategy] Init mit teamCount={teamCount}")

        subprocess.run(
            [venv_python, train_script, str(teamCount)],
            check=True
        )

        model_path = os.path.join(
            project_root,
            "src_python",
            "ml_python",
            f"ml_model_{teamCount}.joblib"
        )

        print(f"[MLStrategy] Lade Modell: {model_path}")

        self.clf_type, self.clf_value = joblib.load(model_path)

        self.initialized = True
        print("[MLStrategy] Init abgeschlossen")

    def extract_features(self, game_state: dict, player_state: dict, target_position: dict) -> np.ndarray:
        sample = {
            "playerPos": player_state["position"],
            "playerRotation": player_state["rotation"],
            "targetPos": [target_position["x"], target_position["y"]],
            "canShoot": player_state["canShoot"],
            "isDead": player_state["isCurrDead"],
            "teamID" : player_state["teamID"],
            "visibleEnemies": game_state.get("enemyPositions", []),
            "visibleBullets": game_state.get("enemyBulletPositions", []),
            "zones" : game_state.get("zones", []),
            "lastCommandState" : player_state["lastCommandState"]
        }

        features = build_features(sample)

        return np.array(features).reshape(1, -1)
    

    def decide_action(self, game_state_json: str, player_state_json: str, target_position_json: str) -> dict | None:
        if not self.initialized:
            print("[MLStrategy] WARNUNG: decide_action vor init() aufgerufen")
            return {"type": "None", "value": 0.0}

        game_state = json.loads(game_state_json)
        player_state = json.loads(player_state_json)
        target_position = json.loads(target_position_json)

        features = self.extract_features(game_state, player_state, target_position)
        features = np.array(features, dtype=float).reshape(1, -1)

        move_type_idx = int(self.clf_type.predict(features)[0])
        move_value = float(self.clf_value.predict(features)[0])

        MOVE_TYPE_MAP = {
            0: "MoveForward",
            1: "RotateLeft",
            2: "RotateRight",
            3: "Shoot",
            4: "StandStill",
            5: "None"
        }

        move_type = MOVE_TYPE_MAP.get(move_type_idx, "MoveForward")

        return {
            "type": move_type,
            "value": move_value
        }


