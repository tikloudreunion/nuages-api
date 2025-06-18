from os import getenv
from contextlib import contextmanager

from proxmoxer import ProxmoxAPI  # type: ignore


class ProxmoxExecption(Exception):
    pass


class ProxmoxSession(ProxmoxAPI):
    def __init__(self):
        host = getenv("PROXMOX_HOST")
        if host is None:
            raise ProxmoxExecption("PROXMOX_HOST environment variable is not set")
        user = getenv("PROXMOX_USER")
        if user is None:
            raise ProxmoxExecption("PROXMOX_USER environment variable is not set")
        token_name = getenv("PROXMOX_TOKEN_NAME")
        if token_name is None:
            raise ProxmoxExecption("PROXMOX_TOKEN_NAME environment variable is not set")
        token_value = getenv("PROXMOX_TOKEN_VALUE")
        if token_value is None:
            raise ProxmoxExecption(
                "PROXMOX_TOKEN_VALUE environment variable is not set"
            )

        super().__init__(  # type: ignore
            host=host,
            backend="https",
            service="PVE",
            user=user,
            token_name=token_name,
            token_value=token_value,
            verify_ssl=False,
        )


@contextmanager
def get_proxmox():
    """Context manager for Proxmox API."""
    proxmox = ProxmoxSession()
    try:
        yield proxmox
    finally:
        pass


def get_proxmox_session():
    """Dependency for FastAPI to get Proxmox instance."""
    with get_proxmox() as proxmox:
        yield proxmox
