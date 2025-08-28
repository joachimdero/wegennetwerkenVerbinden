from dataclasses import dataclass, field
from typing import Optional, Any
from events import make_event_rijstrook, make_event_wegbreedte, make_event_wegverharding

@dataclass
class WegsegmentWallonie:
    geometrie: Any
    nature_desc: Optional[str] = None
    icarrueid1: Optional[int] = None
    rue_nom1: Optional[str] = None
    commu_nom1: Optional[str] = None
    commu_ins1: Optional[str] = None
    icarrueid2: Optional[int] = None
    rue_nom2: Optional[str] = None
    commu_nom2: Optional[str] = None
    commu_ins2: Optional[str] = None
    gestion: Optional[str] = None
    voirie_nom: Optional[str] = None
    sens_bk: Optional[str] = None
    amenag: Optional[str] = None
    bron: Optional[str] = None

    ws_oidn: int = field(default_factory=lambda: WegsegmentWallonie.get_next_oidn('ws'))
    status: int = 4
    lblstatus: str = "in gebruik"

    @staticmethod
    def get_next_oidn(type_: str) -> int:
        if not hasattr(WegsegmentWallonie, "_oidn_counters"):
            WegsegmentWallonie._oidn_counters = {'ws': 0, 'nw': 0, 'rs': 0, 'wb': 0, 'wv': 0}
        oidn = WegsegmentWallonie._oidn_counters[type_]
        WegsegmentWallonie._oidn_counters[type_] += 1
        return oidn

    def export_wegsegment_as_list(self):
        return [self.geometrie, self.ws_oidn, self.status, self.lblstatus, self.bron]

    def apply_events(self):
        make_event_rijstrook(self)
        make_event_wegbreedte(self)
        make_event_wegverharding(self)