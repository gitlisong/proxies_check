import logging
import importlib.util

from ..errors.error import loadConfigError
from ..models.script import Script


class Config:
    @staticmethod
    def init_log(log: logging.Logger) -> logging.Logger:
        log.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(filename="app.log", mode="w")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

        log.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        log.addHandler(stream_handler)
        return log

    @staticmethod
    def load_script(path: str, variable_name: str) -> Script:
        try:
            spec = importlib.util.spec_from_file_location(
                f"external_{variable_name}", path
            )
            if spec is None:
                raise loadConfigError("无法创建模块说明")
            module = importlib.util.module_from_spec(spec)
            loader = spec.loader
            if loader is None:
                raise loadConfigError(f"{path} 无法被加载")
            loader.exec_module(module)
        except FileNotFoundError:
            raise loadConfigError(f"找不到 {path} 文件")
        except Exception as e:
            raise loadConfigError(f"加载 {path} 失败: {e}")

        if not hasattr(module, variable_name):
            raise loadConfigError(f"{path} 中未定义 {variable_name} 变量")

        module_obj = getattr(module, variable_name)

        if not isinstance(module_obj, Script):
            raise loadConfigError(f"{variable_name} 变量不是 {Script.__name__} 类型")

        return module_obj
