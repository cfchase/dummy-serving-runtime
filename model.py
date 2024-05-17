import os
import argparse

from typing import Dict, Union
from kserve import (
    Model,
    ModelServer,
    model_server,
    InferRequest,
    InferResponse,
)
from kserve.errors import InvalidInput


def ls(directory="", max_num_files=100):
    if not directory:
        raise ValueError("directory is required")
    file_list = []
    num_files = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, directory)
            file_list.append(relative_path)
            num_files += 1
            if num_files >= max_num_files:
                return file_list
    return file_list


class DummyModel(Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.ready = False
        self.load()

    def load(self):
        self.ready = True

    def preprocess(
            self, payload: Union[Dict, InferRequest], headers: Dict[str, str] = None
    ) -> Dict:
        if isinstance(payload, Dict) and "instances" in payload:
            headers["request-type"] = "v1"
        elif isinstance(payload, InferRequest):
            print("v2 protocol")
            # raise InvalidInput("v2 protocol not implemented")
        else:
            raise InvalidInput("invalid payload")

        return payload

    def predict(
            self, payload: Union[Dict, InferRequest], headers: Dict[str, str] = None
    ) -> Union[Dict, InferResponse]:

        predictions = []
        for instance in payload["instances"]:
            if "directory" in instance:
                # print(f"ls({instance['directory']}")
                predictions.append({"files": ls(**instance)})

        return {
            "payload": payload,
            "predictions": predictions}


parser = argparse.ArgumentParser(parents=[model_server.parser])
args, _ = parser.parse_known_args()

if __name__ == "__main__":
    model = DummyModel(args.model_name)
    model.load()
    ModelServer().start([model])
