from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Constants.Fields import XMRIG_FIELD

depl_mgr = DeploymentMgr()

xmrig = depl_mgr.get_deployment(XMRIG_FIELD, 'Bill')

print(f"xmrig: {xmrig.to_rec()}")