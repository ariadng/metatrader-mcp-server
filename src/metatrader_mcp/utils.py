from typing import Any, Optional, Union
from metatrader_client import client

def init(
	login: Optional[Union[str, int]],
	password: Optional[str],
	server: Optional[str],
	path: Optional[str] = None,
	portable: Optional[str] = None
) -> Optional[client.MT5Client]:
	"""
	Initialize MT5Client

	Args:
		login (Optional[Union[str, int]]): Login ID
		password (Optional[str]): Password
		server (Optional[str]): Server name
		path (Optional[str]): Path to MT5 terminal executable (default: None for auto-detect)
		portable (Optional[bool]): MT5 in Portable Mode
	Returns:
		Optional[client.MT5Client]: MT5Client instance if all parameters are provided, None otherwise
	"""

	if login and password and server:
		config = {
			"login": int(login),
			"password": password,
			"server": server
		}

		if portable == "True":
			config["portable"] = portable

		# Add path to config if provided
		if path:
			config["path"] = path

		mt5_client = client.MT5Client(config=config)
		mt5_client.connect()
		return mt5_client

	return None
	
def get_client(ctx: Any) -> Optional[client.MT5Client]:
	return ctx.request_context.lifespan_context.client
