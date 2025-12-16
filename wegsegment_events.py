
from wegsegment_utils import OidnManager

def make_event_rijstrook(obj):
    obj.rsoidn = OidnManager.rs_oidn
    OidnManager.rs_oidn += 1
    obj.rijstroken_aantal = 1
    if obj.bron == "WAL":
        if obj.sens_bk in ("C", "D"):
            obj.rijstroken_richting, obj.rijstroken_lblricht = 1, "gelijklopend met de digitalisatiezin"
        else:
            obj.rijstroken_richting, obj.rijstroken_lblricht = 3, "onafhankelijk van de digitalisatiezin"

def make_event_wegbreedte(obj):
    obj.wboidn = OidnManager.wb_oidn
    OidnManager.wb_oidn += 1
    obj.breedte = -8

def make_event_wegverharding(obj):
    obj.wvoidn = OidnManager.wv_oidn
    OidnManager.wv_oidn += 1
    obj.type_wegverharding, obj.lbltype_wegverharding = 1, "weg met vaste verharding"

