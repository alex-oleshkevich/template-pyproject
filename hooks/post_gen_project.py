import os
import shutil

shutil.copy('.env.example', '.env')
os.makedirs('_private')