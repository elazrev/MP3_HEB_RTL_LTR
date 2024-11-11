import flet as ft
import uuid


class BaseControl(ft.UserControl):
    def __init__(self):
        super().__init__()
        self._uid = str(uuid.uuid4())