from typing import Optional, Dict, List, Any
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp")


def fetch_establishment_field(establishment_id: str, token: str, field: str) -> Optional[Any]:
    """
    Función auxiliar que obtiene un solo campo del establecimiento.
    """
    url = f"https://www.clapzy.app/api/establishments/{establishment_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        return data["establishment"].get(field)


    except requests.exceptions.RequestException as e:
        error_response = {}
        if e.response is not None:
            try:
                error_response = e.response.json()
            except ValueError:
                error_response = {"message": e.response.text}

        print(f"Error en la petición: {e}")
        return {
            "error": "No se pudo crear la reservación",
            "details": str(e),
            "response": error_response
        }

    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error inesperado", "details": str(e)}


@mcp.tool(
    name="get_establishment_name",
    description="Obtiene el nombre del establecimiento desde la API de Clapzy.",
)
def get_establishment_name(establishment_id: str, token: str) -> Optional[str]:
    """
    Obtiene el nombre del establecimiento especificado desde la API de Clapzy.

    Args:
        establishment_id (str): ID único del establecimiento que se desea consultar.
        token (str): Token de autenticación Bearer válido para la API de Clapzy.

    Returns:
        Optional[str]: El nombre del establecimiento si la consulta es exitosa; None en caso de error.

    Raises:
        SystemError: Si ocurre un error al comunicarse con la API.
    """
    return fetch_establishment_field(establishment_id, token, "name")


@mcp.tool(
    name="get_establishment_address",
    description="Obtiene la dirección del establecimiento desde la API de Clapzy.",
)
def get_establishment_address(establishment_id: str, token: str) -> Optional[str]:
    """
    Obtiene la dirección física del establecimiento especificado desde la API de Clapzy.

    Args:
        establishment_id (str): ID único del establecimiento que se desea consultar.
        token (str): Token de autenticación Bearer válido para la API de Clapzy.

    Returns:
        Optional[str]: La dirección del establecimiento si la consulta es exitosa; None en caso de error.

    Raises:
        SystemError: Si ocurre un error al comunicarse con la API.
    """
    return fetch_establishment_field(establishment_id, token, "address")


@mcp.tool(
    name="get_establishment_phone",
    description="Obtiene el número de teléfono del establecimiento desde la API de Clapzy.",
)
def get_establishment_phone(establishment_id: str, token: str) -> Optional[str]:
    """
    Obtiene el número de teléfono del establecimiento especificado desde la API de Clapzy.

    Args:
        establishment_id (str): ID único del establecimiento que se desea consultar.
        token (str): Token de autenticación Bearer válido para la API de Clapzy.

    Returns:
        Optional[str]: El número de teléfono del establecimiento si la consulta es exitosa; None en caso de error.

    Raises:
        SystemError: Si ocurre un error al comunicarse con la API.
    """
    return fetch_establishment_field(establishment_id, token, "phone")


@mcp.tool(
    name="get_establishment_dishes",
    description="Obtiene una lista de platillos del menu del establecimiento desde la API de Clapzy.",
)
def get_establishment_name(establishment_id: str, token: str) -> Optional[List[Dict]]:
    """
    Obtiene una lista de platillos del menu del establecimiento desde la API de Clapzy.

    Args:
        establishment_id (str): ID único del establecimiento que se desea consultar.
        token (str): Token de autenticación Bearer válido para la API de Clapzy.

    Returns:
        Optional[List[Dict]]: Lista de diccionarios, cada uno representando un platillo.
                              Devuelve None en caso de error o si no hay platillos disponibles.

    Raises:
        SystemError: Si ocurre un error al comunicarse con la API.
    """
    return fetch_establishment_field(establishment_id, token, "dishes")


@mcp.tool(
    name="create_reservation",
    description="Crea una nueva reservación en un establecimiento utilizando la API de Clapzy.",
)
def create_reservation(
        establishment_id: int,
        token: str,
        date: str,
        time: str,
        peoples: int
) -> str:
    """
    Crea una reservación para un establecimiento específico utilizando la API de Clapzy.

    Args:
        establishment_id (int): ID único del establecimiento donde se desea hacer la reserva.
        token (str): Token de autenticación Bearer válido para la API de Clapzy.
        date (str): Fecha de la reservación en formato 'YYYY-MM-DD'.
        time (str): Hora de la reservación en formato 'HH:MM'.
        peoples (int): Número de personas para la reservación.

    Returns:
        Optional[str]: Cadena de texto con el id de la reserva si la reserva es exitosa; None en caso de error.

    Raises:
        SystemError: Si ocurre un error al comunicarse con la API.
    """
    url = "https://www.clapzy.app/api/reservations"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "date": date,
        "time": time,
        "peoples": peoples,
        "establishment_id": establishment_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["reservation"]["uuid"]

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return {"error": "No se pudo crear la reservación", "details": str(e)}

    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error inesperado", "details": str(e)}


if __name__ == "__main__":
    mcp.run(transport="sse")
