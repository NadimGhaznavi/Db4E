from textual.widgets import RadioButton, RadioSet
from textual.containers import Vertical

from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.ConfigMgr import ConfigMgr
from db4e.Constants.Fields import P2POOL_FIELD
from db4e.Constants.Labels import P2POOL_LABEL
"""
def build_radioset(i_list):
    i_map = {}

    md = Vertical(
        RadioSet(
            for (instance, id) in i_list:
                print(f"{instance}/{id}")
                i_map[instance] = id 
                rb_list.append(RadioButton(instance, id=instance))

        ), id="p2pool_widget")
"""
    #widget = Vertical(
    #    RadioSet(
    #        id="xmrig_p2pool_radioset",
    #        RadioButton(P2POOL_LABEL, id=instance)
    #             
    #)

cm = ConfigMgr('0.1.0')
config = cm.get_config()

dm = DeploymentMgr(config)
print(dm.get_deployment_ids_and_instances(P2POOL_FIELD))

#print(i_list)
#build_radioset(i_list)

