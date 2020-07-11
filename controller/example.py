from pox.core import core
import pox.openflow.discovery
import pox.openflow.spanning_tree
import pox.forwarding.l2_learning
from pox.lib.util import dpid_to_str
from extensions.switch import SwitchController
from extensions.graph import Graph
from extensions.dijkstra import shortest_path

log = core.getLogger()

class Controller:

    def __init__(self):
        self.connections = set()
        self.switches = []
        self.g = Graph()

        # Esperando que los modulos openflow y openflow_discovery esten listos
        core.call_when_ready(self.startup, ('openflow', 'openflow_discovery'))

    def startup(self):
        """
    Esta funcion se encarga de inicializar el controller
    Agrega el controller como event handler para los eventos de
    openflow y openflow_discovery
    """
        core.openflow.addListeners(self)
        core.openflow_discovery.addListeners(self)
        log.info('Controller initialized')

    def _handle_ConnectionUp(self, event):
        """
    Esta funcion es llamada cada vez que un nuevo switch establece conexion
    Se encarga de crear un nuevo switch controller para manejar los eventos de cada switch
    """
        log.info("Switch %s has come up.", dpid_to_str(event.dpid))
        self.g.add_node(dpid_to_str(event.dpid))

        if (event.connection not in self.connections):
            self.connections.add(event.connection)
            sw = SwitchController(event.dpid, event.connection)
            self.switches.append(sw)

    def _handle_ConnectionDown(self, event):
        self.g.remove_node(dpid_to_str(event.dpid))

    def _handle_LinkEvent(self, event):
        """
    Esta funcion es llamada cada vez que openflow_discovery descubre un nuevo enlace
    """
        link = event.link
        sw1 = dpid_to_str(link.dpid1)
        sw2 = dpid_to_str(link.dpid2)
        pt1 = link.port1
        pt2 = link.port2
        if event.added:
            try:
                self.g.add_edge(sw1, sw2)
                # ya lo logea el discover pero para testear
                log.info('link added: [%s:%s] -> [%s:%s]', sw1, pt1, sw2, pt2)
            except:
                log.error("add edge error")
        elif event.removed:
            try:
                self.g.remove_edge(sw1, sw2)
                log.info('link removed [%s:%s] -> [%s:%s]', sw1, pt1, sw2, pt2)
            except:
                log.error("remove edge error")
        #
        # try:
        #     shortest_path(self.g, 1, 6)
        # except:
        #     log.error("no such Graph")


def launch():
    # Inicializando el modulo openflow_discovery
    pox.openflow.discovery.launch()

    # Registrando el Controller en pox.core para que sea ejecutado
    core.registerNew(Controller)

    """
  Corriendo Spanning Tree Protocol y el modulo l2_learning.
  No queremos correrlos para la resolucion del TP.
  Aqui lo hacemos a modo de ejemplo
  """
    # pox.openflow.spanning_tree.launch()
    # pox.forwarding.l2_learning.launch()
