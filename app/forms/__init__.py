from .veicoli import VeicoloForm
from .fornitori import FornitoreForm
from .manutenzioni import ManutenzioneForm
from .scadenze import ScadenzaForm
from .auth import LoginForm, ChangePasswordForm
from .manutenzione_preventiva import ManutenzionePreventivaForm
from .allegati import AllegatoForm
from .sinistri import SinistroForm, AllegatoSinistroForm

__all__ = [
    'VeicoloForm',
    'FornitoreForm',
    'ManutenzioneForm',
    'ScadenzaForm',
    'LoginForm',
    'ChangePasswordForm',
    'ManutenzionePreventivaForm',
    'AllegatoForm',
    'SinistroForm',
    'AllegatoSinistroForm',
]
