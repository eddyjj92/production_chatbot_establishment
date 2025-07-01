from typing import Optional, Dict, List, Any
import requests
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("mcp")


def fetch_establishment_field(establishment_id: str, token: str, field: str) -> Optional[Any]:
    """
    Función auxiliar que obtiene un solo campo del establecimiento.
    """
    url = f"https://backend.clapzy.pro/api/establishments/{establishment_id}"

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
    name="get_establishment_schedule",
    description="Obtiene los horarios del establecimiento desde la API de Clapzy.",
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
    return fetch_establishment_field(establishment_id, token, "schedule")


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
    description="Obtiene una lista de platillos o bebidas(vinos, cervezas, referscos) del menu del establecimiento desde la API de Clapzy.",
)
def get_establishment_name(establishment_id: str, token: str) -> Optional[List[Dict]]:
    """
    Obtiene una lista de platillos o bebidas(vinos, cervezas, referscos) del menu del establecimiento desde la API de Clapzy.

    Args:
        establishment_id (str): ID único del establecimiento que se desea consultar.
        token (str): Token de autenticación Bearer válido para la API de Clapzy.

    Returns:
        Optional[List[Dict]]: Lista de diccionarios, cada uno representando un platillo o una bebida(vino, cerveza, refresco).
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
    url = "https://backend.clapzy.pro/api/reservations"

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
        print(response.json()["reservation"]["uuid"])
        return response.json()["reservation"]["uuid"]

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return {"error": "No se pudo crear la reservación", "details": str(e)}

    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error inesperado", "details": str(e)}


@mcp.tool(
    name="get_user_reservations",
    description="Obtiene todas las reservaciones del usuario autenticado en Clapzy.",
)
def get_user_reservations(establishment_id: int, token: str) -> list:
    """
    Obtiene las reservaciones del usuario autenticado utilizando la API de Clapzy.

    Args:
        establishment_id (int): ID único del establecimiento donde se desea hacer la reserva.
        token (str): Token de autenticación Bearer válido para la API de Clapzy.

    Returns:
        list: Lista de reservaciones del usuario o diccionario con error en caso de fallo.

    Raises:
        SystemError: Si ocurre un error al comunicarse con la API.
    """
    url = f"https://backend.clapzy.pro/api/reservations/auth?establishment_id={establishment_id}"  # Asegúrate que este es el endpoint correcto

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Devuelve la lista completa de reservaciones

        reservations_data = response.json().get("reservations", [])
        campos_deseados = ["uuid", "date", "time", "peoples", "state"]
        reservas_filtradas = [{campo: reserva.get(campo) for campo in campos_deseados} for reserva in reservations_data]
        return reservas_filtradas

    except requests.exceptions.RequestException as e:
        error_msg = f"Error en la petición: {e}"
        if hasattr(e, 'response') and e.response:
            error_msg += f" | Respuesta: {e.response.text}"
        print(error_msg)
        return {"error": "No se pudieron obtener las reservaciones", "details": str(e)}

    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error inesperado al obtener reservaciones", "details": str(e)}


@mcp.tool(
    name="get_current_datetime",
    description="Devuelve un string con la fecha y hora actual del sistema.",
)
def get_current_datetime() -> str:
    """
    Devuelve un string con la fecha y hora actual del sistema.

    Returns:
        str: String con la fecha y la hora, en formato 'fecha {fecha} y hora {hora}'.
    """
    now = datetime.now()
    fecha = now.date().isoformat()
    hora = now.time().strftime('%H:%M:%S')
    return f"Fecha {fecha} y hora {hora} actual"


@mcp.tool(
    name="check_business_hours",
    description="Verifica si una fecha y hora específica está dentro del horario de apertura del establecimiento.",
)
def check_business_hours(
        date: str,  # Fecha en formato YYYY-MM-DD
        time: str,  # Hora en formato HH:MM
        establishment_id: str,  # ID del establecimiento
        token: str,  # Token de autenticación
        timezone: str = "UTC"  # Zona horaria (opcional)
) -> dict:
    """
    Verifica si una fecha y hora está dentro del horario de apertura del establecimiento.

    Args:
        date (str): Fecha en formato YYYY-MM-DD.
        time (str): Hora en formato HH:MM.
        establishment_id (str): ID del establecimiento para obtener su horario.
        token (str): Token de autenticación para la API.
        timezone (str): Zona horaria (por defecto "UTC").

    Returns:
        dict: {
            "is_open": bool,
            "current_day": str,       # Nombre del día (ej. "monday")
            "opening_time": str,      # Hora de apertura (ej. "08:00")
            "closing_time": str,      # Hora de cierre (ej. "17:00")
            "current_time": str,     # Hora actual formateada (ej. "14:30")
            "message": str           # Mensaje descriptivo
        }

    Raises:
        ValueError: Si los formatos no son válidos.
    """
    import json
    from datetime import datetime
    import pytz

    try:
        # Obtener horarios del establecimiento
        business_hours = fetch_establishment_field(establishment_id, token, "schedule")
        hours = json.loads(business_hours)

        # Combinar fecha y hora
        datetime_str = f"{date}T{time}:00"
        dt = datetime.fromisoformat(datetime_str)

        # Aplicar timezone si no tiene
        if not dt.tzinfo:
            tz = pytz.timezone(timezone)
            dt = tz.localize(dt)

        # Obtener día de la semana
        weekday = dt.strftime("%A").lower()
        day_schedule = hours.get(weekday)

        if not day_schedule:
            return {
                "is_open": False,
                "message": f"No se encontró horario para {weekday}"
            }

        # Manejar días cerrados
        if day_schedule["opening"] == "closed":
            print(f"""El establecimiento está cerrado los {weekday}""")
            return {
                "is_open": False,
                "message": f"El establecimiento está cerrado los {weekday}"
            }

        # Convertir horas a minutos desde medianoche para comparación
        current_time_min = dt.hour * 60 + dt.minute

        opening_parts = day_schedule["opening"].split(":")
        opening_min = int(opening_parts[0]) * 60 + int(opening_parts[1])

        closing_parts = day_schedule["closing"].split(":")
        closing_min = int(closing_parts[0]) * 60 + int(closing_parts[1])

        # Verificar si está dentro del horario
        is_open = opening_min <= current_time_min < closing_min

        print(f"""Abierto: {is_open}""")

        return {
            "is_open": is_open,
            "message": (
                f"El establecimiento está {'abierto, se puede proceder con la reserva.' if is_open else 'cerrado, no se puede proceder con la reserva.'}. "
                f"La hora {time} {'está' if is_open else 'no está'} dentro del horario de {day_schedule['opening']} a {day_schedule['closing']} los {weekday}."
            )
        }

    except json.JSONDecodeError:
        print("Formato de horarios inválido obtenido de la API")
        raise ValueError("Formato de horarios inválido obtenido de la API")
    except ValueError as e:
        print(f"Formato de fecha/hora inválido: {str(e)}")
        raise ValueError(f"Formato de fecha/hora inválido: {str(e)}")
    except Exception as e:
        print(f"Error al verificar horario: {str(e)}")
        raise ValueError(f"Error al verificar horario: {str(e)}")


if __name__ == "__main__":
    mcp.run(transport="stdio")
