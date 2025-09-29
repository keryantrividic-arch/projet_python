import random
import time
from threading import Thread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext


def sim_centrale_nuc (context, slave_id=0x00) :
    temperature = 500
    besoin_production_MW = 1000
    while(True):
        temperature += random.randint(-50, 50)
        besoin_production_MW += random.randint(-250, 250)
        if temperature > 1000 : temperature = 1000
        if temperature < 250 : temperature= 250
        if besoin_production_MW > 2000 : besoin_production_MW = 2000
        if besoin_production_MW < 250 : besoin_production_MW= 250
        context[slave_id].setValues(3, 0, [temperature])
        context[slave_id].setValues(3, 1, [besoin_production_MW])
        time.sleep(1)





if __name__ =='__main__' :
    device = ModbusDeviceContext(hr=ModbusSequentialDataBlock(0, [500]))
# Contexte du serveur (1 slave par défaut, unit_id=1)
    context = ModbusServerContext(devices = device, single=True)

sim_thread = Thread(target=sim_centrale_nuc, args=(context,))
sim_thread.daemon=True
sim_thread.start()

# Démarrer le serveur sur le port 5020
StartTcpServer(context=context, address=("0.0.0.0", 502))