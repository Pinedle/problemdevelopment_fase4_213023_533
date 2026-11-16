'''
UNAD:       Universidad Nacional Abierta y a Distancia
ECBTI:      Escuela de Ciencias Básicas Tecnología e Ingeniería
Curso:      Programación
Grupo:      213023_533
Programa:   Ingeniería de Sistemas

Actividad Fase 4 - Diseño y Programación Orientada a Objetos
Autores: Lenyn Estéban Lozano, Luís Ángel Padilla Soto
Versión: 1.0
Fecha de Actualización: 14 de septiembre de 2026
'''


import logging
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
from itertools import count
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

#--------------------------------------------------------------------------------------------------------------------------------
# PUNTO 6: ARCHIVO DE LOGS - Se crea un archivo de registro en la carpeta "logs" para registrar eventos y errores del sistema. --
# Autor: Luis Ángel Padilla                                                                                                    --      
#--------------------------------------------------------------------------------------------------------------------------------


CARPETA_LOGS = Path(__file__).resolve().parent / "logs"
CARPETA_LOGS.mkdir(exist_ok=True)          # si no existe, la crea
ARCHIVO_LOG = CARPETA_LOGS / "software_fj.log"

# Un "logger" es el objeto que usaremos para escribir mensajes.
logger = logging.getLogger("SoftwareFJ")
logger.setLevel(logging.DEBUG)

if not logger.handlers:                     # evita duplicar mensajes
    # El handler decide A DÓNDE van los mensajes: aquí, a un archivo.
    # mode="a" significa "append": agrega al final, no borra lo anterior.
    manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    # El formato define cómo se ve cada línea: fecha, nivel y mensaje.
    manejador.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    )
    logger.addHandler(manejador)


def registrar_evento(mensaje):
    """Guarda un evento normal (algo que salió bien) en el log."""
    logger.info(mensaje)


def registrar_error(mensaje, excepcion=None):
    """
    Guarda un error en el log. Si recibe la excepción, también deja
    registrada la causa original (por si hubo encadenamiento).
    """
    if excepcion is not None and excepcion.__cause__ is not None:
        mensaje += f" | causa original: {excepcion.__cause__!r}"
    logger.error(mensaje)

#Se incluyen las excepciones personalizadas

# Permiten distinguir los errores del dominio de los errores generales de Python.
class SoftwareFJError(Exception):
    pass


class ClienteInvalidoError(SoftwareFJError):
    pass


class ServicioInvalidoError(SoftwareFJError):
    pass


class ParametroFaltanteError(SoftwareFJError):
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    pass


class CalculoInconsistenteError(SoftwareFJError):
    pass


class OperacionNoPermitidaError(SoftwareFJError):
    pass


class ParametroInvalidoError(SoftwareFJError):
    pass


class ReservaInvalidaError(SoftwareFJError):
    pass

def convertir_numero(valor, campo, entero=False):

    if valor is None or str(valor).strip() == "":
        raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
    try:
        n = float(str(valor).strip().replace(",", "."))
        if entero:
            if not n.is_integer():
                raise ValueError("El valor debe ser entero")
            return int(n)
        return n
    except ValueError as e:
        tipo = "Un número entero" if entero else "un número"
        raise ServicioInvalidoError(f"'{campo}' debe ser {tipo} (recibido: {valor!r})") from e
#------------------------------------------------------------------
# PUNTO 1: ENTIDAD BASE - Define la estructura común de las entidades.
# Autor: Lenyn Lozano
#------------------------------------------------------------------
#Esta es la clase abstracta de las entidades generales

# Se define la clase abstracta de la que heredan las entidades del sistema.
class EntidadBase(ABC):

# El contador compartido asigna identificadores consecutivos a todas las entidades.
    _contador_id = count(1)

    # Se inicializa el identificador y la fecha de creación de cada entidad.
    def __init__(self):
        self._id = next(EntidadBase._contador_id)
        self._fecha_creacion = datetime.now()

    # Se expone el identificador de forma controlada.
    @property
    def id(self) -> int:
        return self._id

    # Se expone la fecha de creación de forma controlada.
    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    # Se declara el método abstracto que cada entidad concreta debe describir.
    @abstractmethod
    def descripcion(self) -> str:
        """En la entidad cada una de ellas se  debe describir a sí misma, por lo que este método es abstracto y debe ser implementado en las subclases."""

    # Se genera una representación textual con el tipo, el identificador y la descripción.
    def __str__(self) -> str:
        return f"[{self.__class__.__name__} #{self._id}] {self.descripcion()}"


#Esta es la clase abstracta del cliente
# Estas expresiones regulares definen los formatos aceptados para el correo y el nombre.
_RE_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_RE_NOMBRE = re.compile(
    r"^[A-Za-zÁÉÍÓÚÜáéíóúüÑñ]+(?:[ '-][A-Za-zÁÉÍÓÚÜáéíóúüÑñ]+)*$"
)

#------------------------------------------------------------------
# PUNTO 2: CLIENTE - Valida y encapsula los datos del cliente.
# Autor: Lenyn Lozano
#------------------------------------------------------------------

# Se define la clase Cliente, que hereda de EntidadBase y encapsula sus datos validados.
# Nota: registra eventos mediante logger, definido en el PUNTO 6.
class Cliente(EntidadBase):
    # Se validan los datos al crear el cliente y se registra el resultado.
    def __init__(self, nombre, documento, correo, telefono):
        super().__init__()
        # Se asignan los valores mediante propiedades para aplicar sus validaciones.
        try:
            # La asignación mediante propiedades centraliza la validación de cada dato.
            self.nombre = nombre
            self.documento = documento
            self.correo = correo
            self.telefono = telefono
        # Si una validación falla, se registra el error y se propaga.
        except ClienteInvalidoError as e:
            logger.error("Fallo al crear el cliente: %s", e)
            raise
        # Si todos los datos son válidos, se registra la creación del cliente.
        else:
            logger.info("Cliente creado exitosamente: %s (Doc: %s)", self.nombre, self.documento)
        
    # Se comprueba que el dato obligatorio no esté vacío.
    @staticmethod
    def _requerido(valor, campo):
        # Rechaza valores vacíos antes de aplicar las reglas específicas de cada campo.
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
        return valor

    # Se obtiene el nombre almacenado de forma encapsulada.
    @property
    def nombre(self):
        return self._nombre
        
    # Se valida el formato y la longitud antes de guardar el nombre.
    @nombre.setter
    def nombre(self, valor):
            # Se comprueba que el nombre sea obligatorio y cumpla el formato esperado.
            try:
                valor = self._requerido(valor, "nombre")
                if not isinstance(valor, str) or not _RE_NOMBRE.match(valor.strip()) or len(valor.strip()) < 3:
                    raise ValueError(f"Nombre invalido: {valor!r}")
            # Se convierte el error de validación en una excepción propia del cliente.
            except (ParametroFaltanteError, ValueError) as e:
               # Se conserva la causa original mediante el encadenamiento de excepciones.
               raise ClienteInvalidoError(f"Nombre del cliente invalido") from e
            self._nombre = valor.strip().title()

    # Se obtiene el documento almacenado de forma encapsulada.
    @property
    def documento(self):
        return self._documento
    # Se comprueba que el documento contenga entre 6 y 12 dígitos.
    @documento.setter
    def documento(self, valor):
        # Se normaliza el dato y se valida su formato antes de almacenarlo.
        try:
            valor = str(self._requerido(valor, "documento")).strip()
            if not valor.isdigit() or not 6 <= len(valor) <= 12:
                raise ValueError(f"Documento debe tener entre 6 y 12 dígitos: {valor!r}")
        # Se informa el error como una validación propia de Cliente.
        except (ParametroFaltanteError, ValueError) as e:
            # Se conserva la causa original mediante el encadenamiento de excepciones.
            raise ClienteInvalidoError(f"Documento del cliente invalido") from e
        self._documento = valor
    
    # Se obtiene el correo almacenado de forma encapsulada.
    @property
    def correo(self):
        return self._correo

    # Se valida el formato del correo antes de guardarlo en minúsculas.
    @correo.setter
    def correo(self, valor):
        # Se comprueba que el correo sea obligatorio y tenga un formato válido.
        try:
            valor = self._requerido(valor, "correo")
            if not isinstance(valor, str) or not _RE_CORREO.match(valor.strip()):
                raise ValueError(f"Formato de correo invalido: {valor!r}")
        # Se convierte el fallo de formato en una excepción del cliente.
        except (ParametroFaltanteError, ValueError) as e:
            # Se conserva la causa original mediante el encadenamiento de excepciones.
            raise ClienteInvalidoError(f"Correo del cliente invalido") from e
        self._correo = valor.lower()
    
    # Se obtiene el teléfono almacenado de forma encapsulada.
    @property
    def telefono(self):
        return self._telefono
    
    # Se comprueba que el teléfono tenga exactamente diez dígitos.
    @telefono.setter
    def telefono(self, valor):
        # Se normaliza el dato y se verifica su formato.
        try:
            valor = str(self._requerido(valor, "telefono")).strip()
            if not valor.isdigit() or len(valor) != 10:
                raise ValueError(f"Telefono debe tener 10 dígitos: {valor!r}")
        # Se convierte el error de formato en una excepción del cliente.
        except (ParametroFaltanteError, ValueError) as e:
            # Se conserva la causa original mediante el encadenamiento de excepciones.
            raise ClienteInvalidoError(f"Telefono del cliente invalido") from e
        self._telefono = valor

    # Se reúne la información principal del cliente en una descripción.
    def descripcion(self) -> str:
        return f"{self.nombre} | Doc: {self.documento} | Correo: {self.correo} | Tel: {self.telefono}"

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PUNTO 5: MÉTODOS SOBRECARGADOS - Se implementa la clase CalculadoraCostos con un método estático "calcular" que permite calcular el costo final de un servicio considerando base,     --
# impuesto, descuento y cargo extra. Se manejan errores de parámetros inválidos y cálculos inconsistentes.                                                                              --
# Autor: Luis Ángel Padilla                                                                                                                                                             --
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Python no tiene sobrecarga "real" como Java, pero se logra con
# parámetros opcionales: el MISMO método se puede llamar de varias
# formas y se comporta distinto según lo que le pases.

# Se define la clase CalculadoraCostos, que agrupa las distintas variantes para calcular un costo final.
class CalculadoraCostos:
    """Agrupa las distintas variantes para calcular un costo final."""

    @staticmethod
    def calcular(base, impuesto=None, descuento=None, cargo_extra=0.0):
        """
        Variantes de uso:
            calcular(100)                  -> solo el valor base
            calcular(100, 0.19)            -> base + IVA
            calcular(100, 0.19, 0.10)      -> base - descuento + IVA
            calcular(100, 0.19, 0.10, 20)  -> lo anterior + cargo extra
        """
        if base is None or not isinstance(base, (int, float)):
            raise ParametroInvalidoError("Falta el valor base del cálculo")
        if base < 0:
            raise CalculoInconsistenteError("El costo base no puede ser negativo")

        total = float(base)

        # Si nos dieron descuento, se aplica primero.
        if descuento is not None:
            if not 0 <= descuento <= 1:
                raise ParametroInvalidoError(
                    "El descuento debe estar entre 0 y 1 (ej: 0.10 = 10%)"
                )
            total -= total * descuento

        # Luego el impuesto, si lo pidieron.
        if impuesto is not None:
            if not 0 <= impuesto <= 1:
                raise ParametroInvalidoError(
                    "El impuesto debe estar entre 0 y 1 (ej: 0.19 = 19%)"
                )
            total += total * impuesto

        total += cargo_extra

        # Revisión final de sanidad: un total negativo no es lógico.
        if total < 0:
            raise CalculoInconsistenteError(
                f"El total quedó negativo ({total:.2f})"
            )
        return round(total, 2)

#------------------------------------------------------------------
# PUNTO 3: SERVICIOS - Define el servicio abstracto y sus especializaciones.
# Autor: Lenyn Lozano
#------------------------------------------------------------------
#Esta es la clase abstracta del servicio y los tres servicio especializados

# Porcentaje de IVA usado por el método de cálculo de conveniencia.
IVA = 0.19 

# Clase base para los servicios; las subclases concretas definen sus reglas de uso
# y la forma de calcular el costo según la duración.
# Se define una clase abstracta para centralizar las reglas comunes de los servicios.
# Nota: registra eventos mediante logger, definido en el PUNTO 6.
class Servicio(EntidadBase):
    """Abstraccion de un servicio ofrecido por softwareFJ. Cada servicio tiene un nombre, un precio base y un estado de disponibilidad."""

    # Se inicializan los datos comunes del servicio después de validar sus valores.
    def __init__(self, nombre, tarifa_base, disponible=True):
        """Variantes de uso:
            super().__init__(nombre, tarifa)
            super().__init__(nombre, tarifa, disponible=False)
        """
        super().__init__()
        # Se validan los datos comunes antes de guardar el servicio.
        if nombre is None or not str(nombre).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or isinstance(tarifa_base, bool) or tarifa_base <= 0:
            raise ServicioInvalidoError(f"Tarifa base invalida: {tarifa_base!r}")
        self._nombre = str(nombre).strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    # Se obtiene el nombre mediante una propiedad de solo lectura.
    @property
    def nombre(self):
        return self._nombre

    # Se obtiene la tarifa base mediante una propiedad de solo lectura.
    @property
    def tarifa_base(self):
        return self._tarifa_base

    # Se consulta si el servicio está disponible.
    @property
    def disponible(self):
        return self._disponible

    # Se vuelve a habilitar el servicio.
    def activar(self):
        self._disponible = True

    # Se deshabilita el servicio para impedir que sea utilizado.
    def desactivar(self):
        self._disponible = False

    # Se declara el cálculo base que cada servicio especializado debe implementar.
    @abstractmethod
    def _costo_base(self, duracion: float) -> float:
        """Costo sin impuestos ni descuentos, según la duración del servicio."""

    # Se declara la descripción que cada servicio especializado debe implementar.
    @abstractmethod
    def describir(self) -> str:
        """Descripción específica del servicio."""

    # Se declara la validación de duración que cada servicio especializado debe implementar.
    @abstractmethod
    def validar_parametros(self, duracion: float) -> bool:
        """Valida los parámetros de uso del servicio."""

    # Se calcula el costo después de validar disponibilidad, duración y porcentajes.
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        """Calcula el costo, aplicando primero el descuento y luego el impuesto.

        Variantes de uso:
            calcular_costo(2) -> costo base
            calcular_costo(2, 0.19) -> costo con impuesto
            calcular_costo(2, 0.19, 0.10) -> costo con impuesto y descuento
        """
        try:
            # Se verifica que el servicio esté disponible y que la duración sea válida.
            self.verificar_disponible()
            self.validar_parametros(duracion)
            if (not isinstance(impuesto, (int, float)) or isinstance(impuesto, bool)
                    or not 0 <= impuesto <= 1):
                raise CalculoInconsistenteError("El impuesto debe estar entre 0 y 1")
            if (not isinstance(descuento, (int, float)) or isinstance(descuento, bool)
                    or not 0 <= descuento <= 1):
                raise CalculoInconsistenteError("El descuento debe estar entre 0 y 1")
            total = self._costo_base(duracion) * (1 - descuento) * (1 + impuesto)
            if total < 0:
                raise CalculoInconsistenteError(
                    f"El costo calculado no es válido: {total}"
                )
        # Si alguna validación falla, se registra el error y se propaga.
        except (ServicioInvalidoError, ServicioNoDisponibleError,
                CalculoInconsistenteError) as e:
            logger.error("Error al calcular el costo de '%s': %s", self.nombre, e)
            raise
        # Si el cálculo termina correctamente, se registra y se devuelve el total.
        else:
            logger.info("Costo '%s' (%s): %.2f", self.nombre, duracion, total)
            return round(total, 2)
        # Se registra el cierre del cálculo tanto si termina bien como si falla.
        finally:
            logger.info("Cálculo de costo finalizado para '%s'", self.nombre)

    # Se calcula el costo aplicando la tasa de IVA definida para el sistema.
    def calcular_costo_con_iva(self, duracion):
        return self.calcular_costo(duracion, impuesto=IVA)

    # Se rechaza el cálculo cuando el servicio está deshabilitado.
    def verificar_disponible(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible actualmente."
            )

    # Se delega la descripción a la especialización concreta.
    def descripcion(self):
        return self.describir()

class ReversaSala(Servicio):

    def __init__(self, nombre, tarifa_hora, capacidad, proyector=False, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if (not isinstance(capacidad, int) or isinstance(capacidad, bool)
                or not 1 <= capacidad <= 200):
            raise ServicioInvalidoError(f"Capacidad invalida (1-200): {capacidad!r}")
        self.capacidad = capacidad
        self.proyector = bool(proyector)
    
    def _costo_base(self, duracion):
        recargo = 0.10 if self.capacidad > 20 else 0.0
        extra = 15000 * duracion if self.proyector else 0
        return self.tarifa_base * duracion * (1 + recargo) + extra

    def describir(self):
        return (f"Sala '{self.nombre}' - capacidad {self.capacidad} personas, "
                f"Proyector: {'Sí' if self.proyector else 'No'}, "
                f"${self.tarifa_base:,.0f}/hora")

    def validar_parametros(self, duracion):
        if (not isinstance(duracion, (int, float)) or isinstance(duracion, bool)
                or not 1 <= duracion <= 12):
            raise ServicioInvalidoError(f"La sala se reserva entre 1 y 12 horas (recibido: {duracion!r})")
        return True
    
# Se define el alquiler de equipo como una especialización de Servicio.
class AlquilerEquipo(Servicio):
    # Se construye el alquiler con equipo y opciones de seguro.
    def __init__(self, nombre, tarifa_dia, tipo_equipo, con_seguro=False, disponible=True):
        """Variantes de uso:
            AlquilerEquipo(nombre, tarifa, tipo_equipo)
            AlquilerEquipo(nombre, tarifa, tipo_equipo, con_seguro=True)
        """
        super().__init__(nombre, tarifa_dia, disponible)
        if not tipo_equipo or not str (tipo_equipo).strip():
            raise ParametroFaltanteError("El tipo de equipo es obligatorio")
        self.tipo_equipo = str(tipo_equipo).strip()
        self._con_seguro = bool(con_seguro)

    # Se calcula el costo por días y se aplica el recargo del seguro, si corresponde.
    def _costo_base(self, duracion):
        seguro = 0.05 if self._con_seguro else 0.0
        return self.tarifa_base * duracion * (1 + seguro)

    # Se presenta el tipo de equipo, la tarifa y la condición del seguro.
    def describir(self):
        return (f"Equipo '{self.nombre}' ({self.tipo_equipo}) - "
                f"${self.tarifa_base:,.0f}/día, seguro: "
                f"{'Sí' if self._con_seguro else 'No'}")


    # Se limita el periodo del alquiler a un máximo de treinta días.
    def validar_parametros(self, duracion):
        if (not isinstance(duracion, int) or isinstance(duracion, bool)
                or not 1 <= duracion <= 30):
            raise ServicioInvalidoError(f"El alquiler es de 1 a 30 días (recibido: {duracion!r})")
        return True
           

# Se define la asesoría especializada como una especialización de Servicio.
class AsesoriaEspecializada(Servicio):

    _NIVELES = {"junior": 1.0, "senior": 1.5, "expert": 2.0, "experto": 2.0}

    # Se crea la asesoría con una especialidad y un nivel válidos.
    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        """Variantes de uso:
            AsesoriaEspecializada(nombre, tarifa, especialidad)
            AsesoriaEspecializada(nombre, tarifa, especialidad, nivel="senior")
        """
        super().__init__(nombre, tarifa_hora, disponible)
        if not especialidad or not str(especialidad).strip():
            raise ParametroFaltanteError("La especialidad es obligatoria")
        nivel = str(nivel).lower()
        if nivel not in self._NIVELES:
            raise ServicioInvalidoError(
                f"Nivel inválido: '{nivel}'. Use: {', '.join(self._NIVELES)}"
            )
        self.especialidad = str(especialidad).strip()
        self.nivel = nivel

    # Se calcula el costo según las horas y el multiplicador del nivel.
    def _costo_base(self, duracion):
        return self.tarifa_base * duracion * self._NIVELES[self.nivel]

    # Se describe la especialidad, el nivel y la tarifa de la asesoría.
    def describir(self):
        return (f"Asesoría '{self.nombre}' en {self.especialidad} - "
                f"nivel {self.nivel}, ${self.tarifa_base:,.0f}/hora")

    # Se valida que la duración de la asesoría esté dentro del rango permitido.
    def validar_parametros(self, duracion):
        if (not isinstance(duracion, (int, float)) or isinstance(duracion, bool)
                or not 0.5 <= duracion <= 8):
            raise ServicioInvalidoError(
                f"La asesoría es de 0.5 a 8 horas (recibido: {duracion!r})"
            )
        return True


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PUNTO 4: CLASE RESERVA - La reserva integra cliente y servicio, y maneja su propio estado. Implementa cancelación y confirmación, y el cálculo de costos finales con manejo de errores. --
# Autor: Luis Ángel Padilla                                                                                                                                                               --
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Nota: esta clase usa registrar_evento() y registrar_error(), que se definen en el PUNTO 6 (archivo de logs). Esto permite que cada reserva deje regitros, tanto de éxito como de error.


# Se define la clase Reserva, que hereda de Entidad.
class Reserva(EntidadBase):
    
    """
    Une a un cliente con un servicio durante cierta cantidad de horas.
    Maneja su propio estado: PENDIENTE -> CONFIRMADA o CANCELADA.
    """

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    # El constructor recibe un cliente, un servicio y la cantidad de horas.
    def __init__(self, cliente, servicio, horas):
        super().__init__()
        # Validar que lo recibido sea del tipo correcto.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva necesita un cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva necesita un servicio válido")
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = self.PENDIENTE
        self._costo = None

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    # Se define el método confirmar(), que pasa la reserva a CONFIRMADA si todo está en orden. Si la reserva no está en estado PENDIENTE, o si el servicio no está disponible, o si los parámetros de horas no son válidos, se lanza una excepción.
    def confirmar(self):
        """Pasa la reserva a CONFIRMADA si todo está en orden."""
        if self._estado != self.PENDIENTE:
            raise ReservaInvalidaError(
                f"No se puede confirmar una reserva en estado {self._estado}"
            )
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' no está disponible"
            )
        self._servicio.validar_parametros(self._horas)
        self._estado = self.CONFIRMADA

    # Se define el método cancelar(), que pasa la reserva a CANCELADA si no estaba ya cancelada. Si la reserva ya estaba en estado CANCELADA, se lanza una excepción.
    def cancelar(self):
        """Cancela la reserva (solo si no estaba ya cancelada)."""
        if self._estado == self.CANCELADA:
            raise ReservaInvalidaError("La reserva ya estaba cancelada")
        self._estado = self.CANCELADA

    # Se define el método procesar(), que confirma la reserva y calcula su costo final. Este método maneja errores usando try-except-else-finally, registrando eventos y errores en un archivo de log.
    def procesar(self, impuesto=0.19, descuento=None):
        """
        Confirma la reserva y calcula su costo final. Aquí se muestran
        los bloques de manejo de errores que pide la guía:
            try      -> lo que intentamos hacer
            except   -> qué hacemos si algo falla
            else     -> qué hacemos si TODO salió bien
            finally  -> lo que pase lo que pase siempre se ejecuta
        """
        costo = None
        try:
            if self._estado == self.CANCELADA:
                raise ReservaInvalidaError("No se puede procesar una reserva cancelada")
            costo = self._servicio.calcular_costo(
                self._horas, impuesto, descuento if descuento is not None else 0.0
            )
            if self._estado == self.PENDIENTE:
                self.confirmar()
            self._costo = costo
        except SoftwareFJError as error:
            # Encadenamiento: envolvemos el error original en uno de
            # reserva, pero "from error" conserva la causa real.
            registrar_error(
                f"Reserva #{self.id} falló al procesarse: {error}", error
            )
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva #{self.id}"
            ) from error
        else:
            registrar_evento(
                f"Reserva #{self.id} confirmada para {self._cliente.nombre} "
                f"| {self._servicio.nombre} | {self._horas}h | total ${costo:,.2f}"
            )
            return costo
        finally:
            # Se ejecuta siempre: éxito o error.
            registrar_evento(
                f"Fin del procesamiento de la reserva #{self.id} "
                f"(estado: {self._estado})"
            )
    # Se define el método describir(), que devuelve una cadena con la información de la reserva, incluyendo su id, cliente, servicio, horas y estado.
    def describir(self):
        return (f"Reserva #{self.id} | {self._cliente.nombre} -> "
                f"{self._servicio.nombre} | {self._horas}h | {self._estado}")

    def descripcion(self):
        return self.describir()


# Se definen los tipos de servicio que se ofrecen y se seleccionan desde la interfaz.
# Autor: Lenyn Lozano
TIPOS_SERVICIOS = ("Room booking", "Equipment rental", "Specialized consulting")

class GestorFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, nombre, documento, correo, telefono):
        doc = str(documento).strip()
        if any(c.documento == doc for c in self.clientes):
            raise OperacionNoPermitidaError(f"A customer with document with ID number '{doc}' already exists.")
        cliente = Cliente(nombre, documento, correo, telefono)
        self.clientes.append(cliente)
        return cliente

    def agregar_servicio(self, tipo, **p):
        tarifa = convertir_numero(p.get("tarifa"), "rate")
        if tipo == "Room booking":
            servicio = ReversaSala(p.get("nombre"), tarifa, convertir_numero(p.get("capacidad"), "capacity", entero=True), bool(p.get("proyector")))
        elif tipo == "Equipment rental":
            servicio = AlquilerEquipo(p.get("nombre"), tarifa, p.get("tipo_equipo"), bool(p.get("seguro")))
        elif tipo == "Specialized consulting":
            servicio = AsesoriaEspecializada(p.get("nombre"), tarifa, p.get("especialidad"), p.get("nivel", "junior"))

        else:
            raise ServicioInvalidoError(f"Unknown service type: {tipo!r}")
        self.servicios.append(servicio)
        registrar_evento(f"Service created: {servicio.describir()}")
        return servicio

    def crear_reserva(self, cliente, servicio, horas):
        try:
            reserva = Reserva(cliente, servicio, horas)
        except ReservaInvalidaError as e:
            registrar_error(f"Could not create reservation for client: {e}")
            raise

        self.reservas.append(reserva)
        return reserva

#------------------------------------------------------------------
# PUNTO 7: INTERFAZ GRÁFICA - Permite administrar clientes, servicios y reservas.
# Autor: Lenyn Lozano
#------------------------------------------------------------------
# Se define la ventana principal, que hereda de Tk para construir la interfaz gráfica.
# Nota: utiliza GestorFJ y registra eventos con funciones definidas en otros puntos.
class App(tk.Tk):
    ENCABEZADOS = {"id": "ID", "nombre": "Name", "documento": "ID number", "correo": "Email",
                   "telefono": "Phone", "tipo": "Type", "tarifa": "Rate", "estado": "Status",
                   "descripcion": "Description", "cliente": "Customer", "servicio": "Service",
                   "horas": "Duration", "total": "Total"}

    CAMPOS = {
        "Room booking": [("nombre", "Name", "texto", None),
                            ("tarifa", "Rate per hour ($)", "texto", None),
                            ("capacidad", "Capacity (people)", "texto", None),
                            ("proyector", "Includes projector", "check", None)],
        "Equipment rental": [("nombre", "Name", "texto", None),
                               ("tarifa", "Rate per day ($)", "texto", None),
                               ("tipo_equipo", "Equipment type", "texto", None),
                               ("seguro", "Includes insurance", "check", None)],
        "Specialized consulting": [("nombre", "Name", "texto", None),
                                   ("tarifa", "Rate per hour ($)", "texto", None),
                                   ("especialidad", "Specialty", "texto", None),
                                   ("nivel", "Advisor level", "combo",
                                    ["junior", "senior", "expert"])],
    }

    # Se inicializa la ventana, el gestor y las pestañas principales de la aplicación.
    def __init__(self):
        super().__init__()
        self.title("Software FJ - Customers, Services and Reservations")
        self.geometry("1020x680")
        self.minsize(940, 600)
        ttk.Style(self).theme_use("clam")
        self.gestor = GestorFJ()
        self.estado = tk.StringVar(value="Ready")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=(8, 0))
        self._tab_clientes(nb)
        self._tab_servicios(nb)
        self._tab_costos(nb)
        self._tab_reservas(nb)
        self._tab_log(nb)
        ttk.Label(self, textvariable=self.estado, relief="sunken", anchor="w").pack(
            fill="x", padx=8, pady=6)
        registrar_evento("Application started")
        self._refrescar_log()

    # Se registran y muestran los errores no controlados que ocurren en la interfaz.
    def report_callback_exception(self, exc, val, tb):
        logger.error("Unhandled error in the interface: %s", val, exc_info=(exc, val, tb))
        messagebox.showerror("Unexpected error", f"{val}\n\nThe application is still running.")
        self._refrescar_log()

    # Se ejecuta una acción y se actualizan los mensajes, tablas y registros.
    def _ejecutar(self, accion, exito=None):
        """Variantes de uso:
            _ejecutar(accion)
            _ejecutar(accion, exito="Mensaje de confirmación")
        """
        try:
            # Se intenta realizar la operación solicitada.
            resultado = accion()
        # Si ocurre un error esperado, se muestra y se refleja en el estado.
        except SoftwareFJError as e:
            causa = f"\n\nCause: {e.__cause__}" if e.__cause__ else ""
            messagebox.showerror("Operation rejected", f"{e}{causa}")
            self.estado.set(f"Error: {e}")
            return None
        # Si ocurre otro error, se registra y se informa al usuario.
        except Exception as e:
            registrar_error(f"Unexpected error: {e}")
            messagebox.showerror("Unexpected error", f"{e}\n\nThe application is still running.")
            self.estado.set(f"Unexpected error: {e}")
            return None
        # Si la operación termina correctamente, se muestra el mensaje de éxito opcional.
        else:
            if exito:
                texto = exito(resultado) if callable(exito) else exito
                self.estado.set(texto)
                messagebox.showinfo("Success", texto)
            return resultado
        # Se actualizan las tablas y el registro tanto si hubo éxito como si hubo error.
        finally:
            self._recargar_tablas()
            self._refrescar_log()
    
    # Se construye una tabla con las columnas y anchos indicados.
    def _construir_tabla(self, padre, columnas, anchos, alto=10):
        """Variantes de uso:
            _construir_tabla(padre, columnas, anchos)
            _construir_tabla(padre, columnas, anchos, alto=12)
        """
        tabla = ttk.Treeview(padre, columns=columnas, show="headings", height=alto)
        for c, w in zip(columnas, anchos):
            tabla.heading(c, text=self.ENCABEZADOS.get(c, c.capitalize()))
            tabla.column(c, width=w, anchor="w")
        tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        return tabla

    # Se actualizan las tablas y listas desplegables con los datos del gestor.
    def _recargar_tablas(self):
        g = self.gestor
        tablas = (self.tree_cli, self.tree_srv, self.tree_res)
        seleccion = [t.selection() for t in tablas]

        for tabla in tablas:
            tabla.delete(*tabla.get_children())
        for c in g.clientes:
            self.tree_cli.insert("", "end", iid=str(c.id),
                                 values=(c.id, c.nombre, c.documento, c.correo, c.telefono))
        for s in g.servicios:
            self.tree_srv.insert("", "end", iid=str(s.id), values=(
                s.id, type(s).__name__, s.nombre, f"${s.tarifa_base:,.0f}",
                "Available" if s.disponible else "Unavailable", s.describir()))
        for r in g.reservas:
            self.tree_res.insert("", "end", iid=str(r.id), values=(
                r.id, r.cliente.nombre, r.servicio.nombre, r.horas, r.estado,
                f"${r.costo:,.2f}" if r.costo is not None else "-"))
        for tabla, sel in zip(tablas, seleccion):
            existentes = [i for i in sel if tabla.exists(i)]
            if existentes:
                tabla.selection_set(existentes)
        self.cmb_srv["values"] = [f"#{s.id} - {s.nombre}" for s in g.servicios]
        self.cmb_res_cli["values"] = [f"#{c.id} - {c.nombre}" for c in g.clientes]
        self.cmb_res_srv["values"] = [f"#{s.id} - {s.nombre}" for s in g.servicios]

    # Se crea la pestaña para registrar y consultar clientes.
    def _tab_clientes(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Customers")
        frm = ttk.LabelFrame(tab, text="Register customer")
        frm.pack(fill="x", padx=10, pady=10)
        self.cli_vars = {}
        campos = [("nombre", "Full name"), ("documento", "ID number"),
                  ("correo", "Email"), ("telefono", "Phone (10 digits)")]
        for i, (k, etiqueta) in enumerate(campos):
            ttk.Label(frm, text=etiqueta).grid(row=i // 2, column=(i % 2) * 2,
                                               sticky="w", padx=6, pady=4)
            self.cli_vars[k] = tk.StringVar()
            ttk.Entry(frm, textvariable=self.cli_vars[k], width=32).grid(
                row=i // 2, column=(i % 2) * 2 + 1, padx=6, pady=4)
        bt = ttk.Frame(frm)
        bt.grid(row=2, column=0, columnspan=4, pady=6)
        ttk.Button(bt, text="Register customer", command=self._registrar_cliente).pack(side="left", padx=4)
        ttk.Button(bt, text="Clear", command=self._limpiar_cliente).pack(side="left", padx=4)
        self.tree_cli = self._construir_tabla(
            tab, ("id", "nombre", "documento", "correo", "telefono"), (50, 220, 120, 250, 110), 12)

    # Se recogen los datos del formulario y se solicita el registro del cliente.
    def _registrar_cliente(self):
        datos = {k: v.get() for k, v in self.cli_vars.items()}
        c = self._ejecutar(lambda: self.gestor.agregar_cliente(**datos),
                           lambda c: f"Customer registered: {c.nombre}")
        if c:
            self._limpiar_cliente()

    # Se vacían los campos del formulario de clientes.
    def _limpiar_cliente(self):
        for v in self.cli_vars.values():
            v.set("")
        
    # Se crea la pestaña para registrar y administrar servicios.
    def _tab_servicios(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Services")
        frm = ttk.LabelFrame(tab, text="Create service")
        frm.pack(fill="x", padx=10, pady=10)
        ttk.Label(frm, text="Service type").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.tipo_var = tk.StringVar(value=TIPOS_SERVICIOS[0])
        cmb = ttk.Combobox(frm, textvariable=self.tipo_var, values=list(TIPOS_SERVICIOS),
                           state="readonly", width=30)
        cmb.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        cmb.bind("<<ComboboxSelected>>", self._construir_campos)
        self.frm_campos = ttk.Frame(frm)
        self.frm_campos.grid(row=1, column=0, columnspan=2, sticky="w")
        bt = ttk.Frame(frm)
        bt.grid(row=2, column=0, columnspan=2, pady=6)
        ttk.Button(bt, text="Create service", command=self._crear_servicio).pack(side="left", padx=4)
        ttk.Button(bt, text="Enable / Disable selected",
                   command=self._alternar_disponibilidad).pack(side="left", padx=4)
        self._construir_campos()
        self.tree_srv = self._construir_tabla(
            tab, ("id", "tipo", "nombre", "tarifa", "estado", "descripcion"),
            (40, 150, 150, 90, 100, 420))

    # Se muestran los campos correspondientes al tipo de servicio elegido.
    def _construir_campos(self, *_):
        for w in self.frm_campos.winfo_children():
            w.destroy()
        self.srv_vars = {}
        for i, (k, etiqueta, tipo, opc) in enumerate(self.CAMPOS[self.tipo_var.get()]):
            ttk.Label(self.frm_campos, text=etiqueta).grid(row=i, column=0, sticky="w", padx=6, pady=3)
            if tipo == "check":
                var = tk.BooleanVar()
                w = ttk.Checkbutton(self.frm_campos, variable=var)
            elif tipo == "combo":
                var = tk.StringVar(value=opc[0])
                w = ttk.Combobox(self.frm_campos, textvariable=var, values=opc,
                                 state="readonly", width=28)
            else:
                var = tk.StringVar()
                w = ttk.Entry(self.frm_campos, textvariable=var, width=32)
            w.grid(row=i, column=1, padx=6, pady=3, sticky="w")
            self.srv_vars[k] = var

    # Se recogen los datos del formulario y se solicita la creación del servicio.
    def _crear_servicio(self):
        datos = {k: v.get() for k, v in self.srv_vars.items()}
        s = self._ejecutar(lambda: self.gestor.agregar_servicio(self.tipo_var.get(), **datos),
                           lambda s: f"Service created: {s.nombre}")
        if s:
            self._construir_campos()

    # Se activa o desactiva el servicio que esté seleccionado en la tabla.
    def _alternar_disponibilidad(self):
        # Se comprueba la selección y se cambia la disponibilidad del servicio.
        def accion():
            sel = self.tree_srv.selection()
            if not sel:
                raise ParametroFaltanteError("Select a service from the table")
            s = next(x for x in self.gestor.servicios if str(x.id) == sel[0])
            s.desactivar() if s.disponible else s.activar()
            registrar_evento(f"Service '{s.nombre}' is now: "
                             f"{'available' if s.disponible else 'unavailable'}")
            return s
        self._ejecutar(accion)

    # Se crea la pestaña para calcular el costo de un servicio.
    def _tab_costos(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Cost calculation")
        frm = ttk.LabelFrame(tab, text="Calculate cost (polymorphism + method variants)")
        frm.pack(fill="x", padx=10, pady=10)
        ttk.Label(frm, text="Service").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cmb_srv = ttk.Combobox(frm, state="readonly", width=40)
        self.cmb_srv.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        self.dur_var, self.imp_var, self.desc_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for i, (etiqueta, v) in enumerate([("Duration (hours or days)", self.dur_var),
                                           ("Tax % (optional)", self.imp_var),
                                           ("Discount % (optional)", self.desc_var)], start=1):
            ttk.Label(frm, text=etiqueta).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            ttk.Entry(frm, textvariable=v, width=14).grid(row=i, column=1, padx=6, pady=4, sticky="w")
        ttk.Button(frm, text="VAT 19%", command=lambda: self.imp_var.set("19")).grid(
            row=2, column=1, padx=(120, 0), sticky="w")
        ttk.Button(frm, text="Calculate cost", command=self._calcular).grid(
            row=4, column=0, columnspan=2, pady=8)
        self.lbl_res = ttk.Label(tab, text="", font=("Segoe UI", 12, "bold"), justify="left")
        self.lbl_res.pack(anchor="w", padx=14, pady=10)

    # Se convierte un porcentaje escrito en el formulario a un valor decimal.
    @staticmethod
    def _porcentaje(txt, campo):
        if str(txt).strip() == "":
            return None
        # Se interpreta el valor y se informa si no representa un número válido.
        try:
            return float(str(txt).replace(",", ".")) / 100
        except ValueError as e:
            # Se conserva la causa original mediante el encadenamiento de excepciones.
            raise CalculoInconsistenteError(
                f"'{campo}' must be a number (received: {txt!r})") from e

    # Se valida la selección y se muestra el costo base y el costo final.
    def _calcular(self):
        # Se reúnen las entradas y se realizan los cálculos solicitados.
        def accion():
            i = self.cmb_srv.current()
            if i < 0:
                raise ParametroFaltanteError("Select a service")
            s = self.gestor.servicios[i]
            dur = convertir_numero(self.dur_var.get(), "duration")
            if float(dur).is_integer():
                dur = int(dur)
            imp = self._porcentaje(self.imp_var.get(), "tax")
            desc = self._porcentaje(self.desc_var.get(), "discount")
            base = s.calcular_costo(dur)
            total = s.calcular_costo(
                dur, imp if imp is not None else 0.0,
                desc if desc is not None else 0.0,
            )
            return s, base, total
        r = self._ejecutar(accion)
        if r:
            s, base, total = r
            self.lbl_res.config(text=f"{s.describir()}\n\nBase cost: ${base:,.2f}\n"
                                     f"Final total: ${total:,.2f}")
            self.estado.set(f"Cost calculated for '{s.nombre}'")
        else:
            self.lbl_res.config(text="")
        
    # Se crea la pestaña para registrar, confirmar, procesar y cancelar reservas.
    def _tab_reservas(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Reservations")
        frm = ttk.LabelFrame(tab, text="New reservation")
        frm.pack(fill="x", padx=10, pady=10)
        ttk.Label(frm, text="Customer").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.cmb_res_cli = ttk.Combobox(frm, state="readonly", width=34)
        self.cmb_res_cli.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        ttk.Label(frm, text="Service").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.cmb_res_srv = ttk.Combobox(frm, state="readonly", width=34)
        self.cmb_res_srv.grid(row=0, column=3, padx=6, pady=4, sticky="w")
        self.res_dur = tk.StringVar()
        self.res_imp = tk.StringVar(value="19")
        self.res_desc = tk.StringVar()
        ttk.Label(frm, text="Duration").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(frm, textvariable=self.res_dur, width=12).grid(row=1, column=1, sticky="w", padx=6)
        ttk.Label(frm, text="Tax % / Discount %").grid(row=1, column=2, sticky="w", padx=6)
        caja = ttk.Frame(frm)
        caja.grid(row=1, column=3, sticky="w")
        ttk.Entry(caja, textvariable=self.res_imp, width=8).pack(side="left", padx=(6, 4))
        ttk.Entry(caja, textvariable=self.res_desc, width=8).pack(side="left")
        bt = ttk.Frame(frm)
        bt.grid(row=2, column=0, columnspan=4, pady=6)
        ttk.Button(bt, text="Create reservation", command=self._crear_reserva).pack(side="left", padx=4)
        ttk.Button(bt, text="Confirm", command=self._confirmar_reserva).pack(side="left", padx=4)
        ttk.Button(bt, text="Process (confirm + cost)",
                   command=self._procesar_reserva).pack(side="left", padx=4)
        ttk.Button(bt, text="Cancel", command=self._cancelar_reserva).pack(side="left", padx=4)
        self.tree_res = self._construir_tabla(
            tab, ("id", "cliente", "servicio", "horas", "estado", "total"),
            (50, 200, 200, 80, 110, 130), 12)

    # Se obtiene la reserva seleccionada o se informa que falta la selección.
    def _reserva_seleccionada(self):
        sel = self.tree_res.selection()
        if not sel:
            raise ParametroFaltanteError("Select a reservation from the table")
        return next(r for r in self.gestor.reservas if str(r.id) == sel[0])

    # Se validan las selecciones y duración antes de crear una reserva.
    def _crear_reserva(self):
        # Se convierten los datos del formulario y se solicita la creación.
        def accion():
            ic, isv = self.cmb_res_cli.current(), self.cmb_res_srv.current()
            if ic < 0 or isv < 0:
                raise ParametroFaltanteError("Select a customer and a service")
            horas = convertir_numero(self.res_dur.get(), "duration")
            if float(horas).is_integer():
                horas = int(horas)
            return self.gestor.crear_reserva(self.gestor.clientes[ic],
                                             self.gestor.servicios[isv], horas)
        self._ejecutar(accion, lambda r: f"Reservation #{r.id} created (PENDING)")

    # Se solicita la confirmación de la reserva seleccionada.
    def _confirmar_reserva(self):
        self._ejecutar(lambda: self._reservar_y_confirmar(),
                       lambda r: f"Reservation #{r.id} confirmed")

    # Se obtiene y confirma la reserva seleccionada.
    def _reservar_y_confirmar(self):
        reserva = self._reserva_seleccionada()
        reserva.confirmar()
        return reserva

    # Se procesan la reserva y sus porcentajes de impuesto y descuento.
    def _procesar_reserva(self):
        # Se obtienen los datos de la reserva y se calcula su costo final.
        def accion():
            reserva = self._reserva_seleccionada()
            impuesto = self._porcentaje(self.res_imp.get(), "tax")
            descuento = self._porcentaje(self.res_desc.get(), "discount")
            total = reserva.procesar(
                impuesto=impuesto if impuesto is not None else 0.19,
                descuento=descuento,
            )
            return reserva, total

        resultado = self._ejecutar(
            accion, lambda r: f"Reservation #{r[0].id} processed: ${r[1]:,.2f}"
        )
        if resultado:
            reserva, total = resultado
            self.estado.set(f"Reservation #{reserva.id} total: ${total:,.2f}")

    # Se solicita la cancelación de la reserva seleccionada.
    def _cancelar_reserva(self):
        self._ejecutar(
            lambda: self._cancelar_reserva_seleccionada(),
            lambda r: f"Reservation #{r.id} cancelled",
        )

    # Se obtiene la reserva elegida y se cambia su estado a cancelada.
    def _cancelar_reserva_seleccionada(self):
        reserva = self._reserva_seleccionada()
        reserva.cancelar()
        return reserva

    # Se crea la pestaña donde se muestran los eventos registrados.
    def _tab_log(self, nb):
        tab = ttk.Frame(nb)
        nb.add(tab, text="Log")
        self.txt_log = tk.Text(tab, wrap="word", state="disabled", height=20)
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=10)

    # Se vuelve a leer el archivo de registro y se actualiza el texto de la pestaña.
    def _refrescar_log(self):
        if not hasattr(self, "txt_log"):
            return
        contenido = ARCHIVO_LOG.read_text(encoding="utf-8")
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.insert("end", contenido)
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")



if __name__ == "__main__":
    App().mainloop()
