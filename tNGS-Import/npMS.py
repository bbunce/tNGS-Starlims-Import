import re
import openpyxl

class MutationSurveyor:

    def __init__(self, wb, ws_ms):
        self.wb = wb
        self.ws = ws_ms

    