#%%
from fiona.core.db_builder import DB_builder
import yaml
import os 

user = 'LRinaldi'

with open('support/paths.yml', 'r') as file:
    paths = yaml.safe_load(file)

folder = paths['shared_folder'][user]
master_file_path = os.path.join(folder,paths['inventories']['master_file_path'])

db = DB_builder(
    sut_path=os.path.join(folder,paths['database']['exiobase_aggregated'],'flows'),
    sut_mode='flows',
    master_file_path=master_file_path,
    sut_format='txt',
    read_master_file=True,
)

#%% Read inventories from master file
db.read_inventories(master_file_path,check_errors=False)

#%% Add inventories to SUT
db.add_inventories(source = 'excel')

# %% check if it worked by looking at footprint of a product
db.sut.f.loc[db.sut.search('Satellite account','dioxide'),('CN','Commodity',db.new_commodities)]

# %%
