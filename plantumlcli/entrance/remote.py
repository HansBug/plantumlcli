from ..models.remote import RemotePlantuml
from ..utils import check_func


def _check_remote(host: str):
    RemotePlantuml(host).check()


_if_remote_ok = check_func(keep_return=False)(_check_remote)
