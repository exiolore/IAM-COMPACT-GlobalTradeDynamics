#%%
import mario
import yaml
import os

user = 'LRinaldi'

with open('support/paths.yml', 'r') as file:
    paths = yaml.safe_load(file)

folder = paths['onedrive_folder'][user]
master_file_path = os.path.join(folder,paths['inventories'])  # switch this from master and master_simplified from paths.yml

#%%
db = mario.parse_from_txt(
    path=os.path.join(folder,paths['database']['exiobase']['aggregated'],'flows'),
    mode='flows',
    table='SUT',
)

#%%
# db.get_add_sectors_excel(master_file_path)

#%%
db.read_add_sectors_excel(master_file_path,read_inventories=True)

#%%
# db.read_inventory_sheets(master_file_path)

#%%
db.add_sectors()

#%% Calculate GHG footprints

# provide a dictionary with GHGs and their GWP
ghgs = {
    'Carbon dioxide, fossil (air - Emiss)':1,
    'CH4 (air - Emiss)':29.8,
    'N2O (air - Emiss)':273
    }

# isolate GHGs for new commodities (batteries) in f matrix (specific footprints)
f = db.f.loc[ghgs.keys(),(slice(None),'Commodity',db.new_commodities)]
for ghg,gwp in ghgs.items():
    f.loc[ghg,:] *= gwp # multiply each GHG by its GWP

# rearrange the shape of the resulting dataframe
f = f.sum(0) 
f = f.to_frame()    
f.reset_index(inplace=True)
f.columns = ['Region','Item','Commodity','Value']
f = f.drop('Item',axis=1)
f.set_index(['Region','Commodity'],inplace=True)
f = f.unstack()
f = f.droplevel(0,axis=1)
f = f*1000/80 # convert to kg CO2-eq/kWh
f.to_excel('footprints.xlsx')

#%%
# isolate prices for new commodities (batteries) in f matrix (specific footprints)
p = db.p.loc[(slice(None),'Commodity',db.new_commodities),:]
p = p.unstack(-1)
p = p.droplevel(1,axis=0)
p = p.droplevel(0,axis=1)

p = p*1e6/80 # convert to €/kWh
p = p/0.92 # convert from EUR to USD in 2011
p = p*1.33 # deflat from 2011 to 2024

p.to_excel('prices.xlsx')

# %% Export aggregated database to txt
db.to_txt(
    os.path.join(folder,paths['database']['exiobase']['extended']),
    flows=False,
    coefficients=True
    )

# %%
f


# %%
import pandas as pd
import numpy as np

ghgs = {
    'Carbon dioxide, fossil (air - Emiss)':1,
    'CH4 (air - Emiss)':29.8,
    'N2O (air - Emiss)':273
    }

e = db.e.loc[ghgs.keys(),:]
for ghg,gwp in ghgs.items():
    e.loc[ghg,:] *= gwp

e = e.sum(0).to_frame().T
e.index = ['GHGs']

f_exp = pd.DataFrame(
    np.diagflat(e.values) @ db.w.values,
    index = e.columns,
    columns = e.columns
)

#%%
f_exp_lfp = f_exp.loc[(slice(None),'Activity',slice(None)),('CN','Commodity','LFP batteries')]
f_exp_lfp.to_clipboard()

# %%
