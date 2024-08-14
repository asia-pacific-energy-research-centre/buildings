import os
import re
import datetime
import pandas as pd
import plotly.express as px

class Config:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.BASE_YEAR = 2022