'''
UNAD:       Universidad Nacional Abierta y a Distancia
ECBTI:      Escuela de Ciencias Básicas Tecnología e Ingeniería
Curso:      Programación
Grupo:      213023_533
Programa:   Ingeniería de Sistemas

Actividad Fase 2 - Diseño y Programación Orientada a Objetos
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
import tkinter as tkinter
from tkinter import messagebox, tkinter


#Se incluyen las excepciones personalizadas

# Permiten distinguir los errores del dominio de los errores generales de Python.
class SoftwareFJError(Exception):


class ClienteInvalidoError(SoftwareFJError):


class ServicioInvalidoError(SoftwareFJError):


class ParametroFaltanteError(SoftwareFJError):


class ServicioNoDisponibleError(SoftwareFJError):


class CalculoInconsistenteError(SoftwareFJError):


class OperacionNoPermitidaError(SoftwareFJError):

 
#El logger que es para los archivos de logs

# El archivo de registro se configura una sola vez para evitar duplicar mensajes.
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__))),"software_fj.log"

logger = logging.getLogger("software_fj")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    _h = logging.FileHandler(RUTA_LOG, encoding="utf-8")
    _h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s" ))
    logger.addHandler(_h)

#Esta es la clase abstracta de las entidades generales

class EntidadBase(ABC):

# El contador compartido asigna identificadores consecutivos a todas las entidades.
_contador_id = count(1)

def __init__(self)
    self._id = next(EntidadBase._contador)
    self._fecha_creacion = datetime.now()

@property
def id(self) -> int:
    return self._id

@property
def fecha_creacion(self) -> datetime:
    return self._fecha_creacion

@abstractmethod
def descripcion(self) -> str:
    """En la entidad cada una de ellas se  debe describir a sí misma, por lo que este método es abstracto y debe ser implementado en las subclases."""

def __str__(self) -> str:
    return f"[{self.__class__.__name__} #{self._id}] {self.descripcion()}"


#Esta es la clase abstracta del cliente
# Estas expresiones regulares definen los formatos aceptados para el correo y el nombre.
_RE_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
_RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÚú]+([A-Za-zÁÉÍÓÚáéíóúÑñÚú]+)*$")


class Cliente(EntidadBase):
    def__init__(self, nombre, documento, correo, telefono):
        super().__init__()
        try:
            # La asignación mediante propiedades centraliza la validación de cada dato.
            self.nombre = nombre
            self.documento = documento
            self.correo = correo
            self.telefono = telefono
        except clienteInvalidoError as e:
            logger.error("Fallo al crear el cliente: %s", e)
            raise
        else:
            logger.info("Cliente creado exitosamente: %s (Doc: %s)", self.nombre, self.documento)
        
        @staticmethod
        def _requerido(valor, campo):
            # Rechaza valores vacíos antes de aplicar las reglas específicas de cada campo.
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
            return valor

        @property
        def nombre(self):
            return self._nombre
        
        @nombre.setter
        def nombre(self, valor):
           try:
                valor = self._requerido(valor, "nombre")
                if not isinstance(valor, str) or not _RE_NOMBRE.match(valor.strip()) or len(valor.strip()) < 3:
                    raise valueError(f"Nombre invalido: {valor!r}")
            except (ParametroFaltanteError, ValueError) as e:
               raise ClienteInvalidoError(f"Nombre del cliente invalido") from e
            self._nombre = valor.strip().title()

        @property
        def documento(self):
            return self._documento
        @documento.setter
        def documento(self, valor):
            try:
                valor = str(self._requerido(valor, "documento")).strip()
                if not valor.isdigit() or not 6 <= len(valor) <= 12:
                    raise ValueError(f"Documento debe tener entre 6 y 12 dígitos: {valor!r}")
            except (ParametroFaltanteError, ValueError) as e:
                raise ClienteInvalidoError(f"Documento del cliente invalido") from e
            self._documento = valor
        
        @property
        def correo(self):
            return self._correo

        @correo.setter
        def correo(self, valor):
            try:
                valor = self._requerido(valor, "correo")
                if not isinstance(valor, str) or not _RE_CORREO.match(valor.strip()):
                    raise ValueError(f"Formato de correo invalido: {valor!r}")
            except (ParametroFaltanteError, ValueError) as e:
                raise ClienteInvalidoError(f"Correo del cliente invalido") from e
            self._correo = valor.lower()
        
        @property
        def telefono(self):
            return self._telefono
        
        @telefono.setter
        def telefono(self, valor):
            try:
                valor = str(self._requerido(valor, "telefono")).strip()
                if not valor.isdigit() or len(valor) != 10:
                    raise ValueError(f"Telefono debe tener 10 dígitos: {valor!r}")
            except (ParametroFaltanteError, ValueError) as e:
                raise ClienteInvalidoError(f"Telefono del cliente invalido") from e
            self._telefono = valor

        def descripcion(self) -> str:
            return f"{self.nombre} | Doc: {self.documento} | Correo: {self.correo} | Tel: {self.telefono}"

#Esta es la clase abstracta del servicio y los tres servicio especializados

# Porcentaje de IVA usado por el método de cálculo de conveniencia.
IVA = 0.19 

# Clase base para los servicios; las subclases concretas definen sus reglas de uso
# y la forma de calcular el costo según la duración.
class Servicio(EntidadBase):
        """Abstraccion de un servicio ofrecido por softwareFJ. Cada servicio tiene un nombre, un precio base y un estado de disponibilidad."""

        def __init__(self, nombre, tarifa_base, disponible=True):
            super().__init__()
            # Se validan los datos comunes antes de guardar el servicio.
            if nombre is None or not str(nombre).strip():
                raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
            if not isinstance(tarifa_base, (int, float)) or isinstance(tarifa_base, bool) or tarifa_base <= 0:
                raise ServicioInvalidoError(f"Tarifa base invalida: {tarifa_base!r}")
            self.nombre = str(nombre).strip()
            self.tarifa_base = float(tarifa_base)
            self.disponible = bool(disponible)

            @property
            def nombre(self):
                return self._nombre
            
            @property
            def tarifa_base(self):
                return self._tarifa_base

            @property
            def disponible(self):
                return self._disponible
            
            def activar(self):
                # Habilita nuevamente el servicio para que pueda ser utilizado.
                self._disponible = True
            
            def desactivar(self):
                # Conserva el servicio, pero impide su uso mientras esté desactivado.
                self._disponible = False
            
            # Cada subclase debe proporcionar el costo antes de aplicar impuestos o descuentos.
            @abstractmethod
            def _costo_base(self, duracion: float) -> float:
                """Costo sin impuestos ni descuentos, según la duración del servicio."""
            
            # La descripción permite mostrar la información propia de cada tipo de servicio.
            @abstractmethod
            def describir(self) -> str:
                """Descripción específica del servicio."""

            # La implementación concreta decide qué duraciones son válidas para el servicio.
            @abstractmethod
            def validar_duracion(self, duracion: float) -> bool:
                """Valida los parámetros de uso; lanza ServicioNoDisponibleError si no es válido."""
            
            def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
                """variantes:
                calcular_costo(2)                                   -> Costo base
                calcular_costo(2, impuesto=0.19)                    -> con impuesto
                calcular_costo(2, impuesto=0.19, descuento=0.1)     -> con impuesto y descuento
                calcular_costo(2, descuento=0.1)                    -> solo descuento
                
                """

                try:
                    # Se comprueba disponibilidad y duración antes de calcular el importe.
                    self.verificar_disponible()
                    self.validar_parametros(duracion)
                    if not 0 <= impuesto <= 1 or not 0 <= descuento <= 1:
                        raise CalculoInsconsistenteError(f"Impuesto debe estar entre 0 y 1")
                    # El descuento reduce el costo base y luego se aplica el impuesto.
                    total = self._costo_base(duracion) * (1 - descuento) * (1 + impuesto)
                    if total < 0:
                        raise CalculoInsconsistenteError(f"El costo calculado no es valido: {total}")
                    
                except (ServicioInvalidoError, ServicioNoDisponibleError, CalculoInsconsistenteError) as e:
                    logger.error("Error al calcular el costo de'%s': %s", self.nombre, e)
                    raise
                else:
                    logger.info("Costo '%s' (%s): %.2f", self.nombre, duracion, total)
                    return round(total, 2)
                finally:
                    logger.info("Cálculo de costo finalizado para '%s'", self.nombre)
            
            def calcular_costo_con_iva(self, duracion):
                """Variante de conveniencia: se aplica el IVA estandar."""
                return self.calcular_costo(duracion, impuesto=IVA)
            
            def verificar_disponible(self):
                # Centraliza la verificación para evitar cobrar por un servicio inactivo.
                if not self.disponible:
                    raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' no está disponible actualmente.")
                
            def descripcion(self):
                # Reutiliza la descripción específica implementada por cada subclase.
                return self.describir()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PUNTO 4: CLASE RESERVA - La reserva integra cliente y servicio, y maneja su propio estado. Implementa cancelación y confirmación, y el cálculo de costos finales con manejo de errores. --
# Autor: Luis Ángel Padilla                                                                                                                                                               --
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Nota: esta clase usa registrar_evento() y registrar_error(), que se definen en el PUNTO 6 (archivo de logs). Esto permite que cada reserva deje regitros, tanto de éxito como de error.


# Se define la clase Reserva, que hereda de Entidad.
class Reserva(Entidad):
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

    # Se definen propiedades de solo lectura para cliente, servicio, horas y estado.
    @property
    def estado(self):
        return self._estado

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
            self.confirmar()
            costo = self._servicio.calcular_costo_total(
                self._horas, impuesto, descuento
            )
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