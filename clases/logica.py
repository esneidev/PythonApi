from clases.conection import conectar
from datetime import datetime
import json
import bcrypt
import logging
import jwt
import mysql.connector

logging.basicConfig(level=logging.DEBUG)

SECRET_KEY = 'secretKeyApi'

# Funcion para crear tickets
def crear(fk_usuario, nombre, descripcion, fk_prioridad):
    connection = conectar()
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(num_ticket) FROM tbl_tickets")
    max_num_ticket = cursor.fetchone()[0]
    if max_num_ticket is None:
        num_ticket = 1
    else:
        num_ticket = max_num_ticket + 1

    query = """
    INSERT INTO tbl_tickets (fk_usuario, nombre, num_ticket, descripcion, fk_prioridad)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (fk_usuario, nombre, num_ticket, descripcion, fk_prioridad))
    
    id_ticket = cursor.lastrowid
    
    seguimiento_query = """
    INSERT INTO tbl_seguimiento (fk_ticket, fk_estado)
    VALUES (%s, 1)
    """
    cursor.execute(seguimiento_query, (id_ticket,))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return {"success": True, "message": "Ticket creado y seguimiento inicial registrado satisfactoriamente", "num_ticket": num_ticket}

# Funcion para listar los tickets creados
def listar():
    connection = conectar()   
    cursor = connection.cursor()

    query = """
    SELECT t.id_ticket, t.fk_usuario, t.nombre, t.num_ticket, t.descripcion, p.nombre AS prioridad_nombre, t.fk_prioridad, t.fecha_registro, e.nombre AS estado_nombre, s.fk_estado, s.fecha_cambio, u.nombre AS nombre_usuario 
    FROM tbl_tickets t
     JOIN tbl_estados p ON t.fk_prioridad = p.id_estado
     JOIN tbl_seguimiento s ON t.id_ticket = s.fk_ticket
     JOIN tbl_usuarios u ON t.fk_usuario = u.id_usuario
        AND s.fecha_cambio = (
            SELECT MAX(s2.fecha_cambio)
            FROM tbl_seguimiento s2
            WHERE s2.fk_ticket = t.id_ticket
        )
     JOIN tbl_estados e ON s.fk_estado = e.id_estado
    """
    cursor.execute(query)
    datos = cursor.fetchall()
    cursor.close()
    connection.close()

    resultados = []
    for row in datos:
        ticket = {
            "id_ticket": row[0],
            "fk_usuario": row[1],
            "nombre": row[2],
            "num_ticket": row[3],
            "descripcion": row[4],
            "prioridad_nombre": row[5],
            "fk_prioridad":row[6],
            "fecha_registro": row[7].isoformat() if isinstance(row[7], datetime) else row[7],
            "nombre_estado": row[8],
            "fk_estado": row[9],
            "fecha_cambio": row[10].isoformat() if isinstance(row[10], datetime) else row[10],
            "nombre_usuario": row[11]
        }
        resultados.append(ticket)

    return resultados

# Funcion parar buscar tickets por id, estado o fecha    
def listarTicketFiltro(fecha=None, estado=None, id_ticket=None):
    connection = conectar()
    cursor = connection.cursor()
    
    query = """
    SELECT t.id_ticket, t.fk_usuario, t.nombre, t.num_ticket, t.descripcion, p.nombre AS prioridad_nombre, t.fk_prioridad, t.fecha_registro, e.nombre AS estado_nombre, s.fk_estado 
    FROM tbl_tickets t
    LEFT JOIN tbl_estados p ON t.fk_prioridad = p.id_estado
    LEFT JOIN tbl_seguimiento s ON t.id_ticket = s.fk_ticket
        AND s.fecha_cambio = (
            SELECT MAX(s2.fecha_cambio)
            FROM tbl_seguimiento s2
            WHERE s2.fk_ticket = t.id_ticket
        )
    LEFT JOIN tbl_estados e ON s.fk_estado = e.id_estado
    """
    conditions = []
    params = []

    if fecha:
        conditions.append("DATE(fecha_registro) = %s")
        params.append(fecha)
    if estado:
        conditions.append("fk_estado = %s")
        params.append(estado)
    if id_ticket:
        conditions.append("id_ticket = %s")
        params.append(id_ticket)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    else:
        cursor.close()
        connection.close()
        return {'error': 'No se proporcionaron parámetros de búsqueda'}

    cursor.execute(query, params)
    tickets = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    # Convertir a json
    resultado = []
    for row in tickets:
        resultado.append({
            "id_ticket": row[0],
            "fk_usuario": row[1],
            "nombre": row[2],
            "num_ticket": row[3],
            "descripcion": row[4],
            "prioridad_nombre": row[5],
            "fk_prioridad":row[6],
            "fecha_registro": row[7].isoformat() if isinstance(row[7], datetime) else row[7],
            "nombre_estado": row[8],
            "fk_estado": row[9]
        })

    return resultado

# Funcion para actualizar los datos de los tickets
def actualizar(id_ticket, descripcion, prioridad):
    connection = conectar()
    cursor = connection.cursor()
    query = "UPDATE tbl_tickets SET descripcion = %s, fk_prioridad = %s WHERE id_ticket = %s"
    cursor.execute(query, (descripcion, prioridad, id_ticket))
    connection.commit()
    cursor.close()
    connection.close()
    return {'message': 'Ticket actualizado correctamente'}

# Funcion para actualizar el estado de los tickets (nuevo, notificado, error, realizado)
def actualizar_estado(id_ticket, nuevo_estado):
    connection = conectar()
    cursor = connection.cursor()
    
    seguimiento_query = """
    INSERT INTO tbl_seguimiento (fk_ticket, fk_estado)
    VALUES (%s, %s)
    """
    cursor.execute(seguimiento_query, (id_ticket, nuevo_estado))

    connection.commit()
    cursor.close()
    connection.close()
    
    return {"message": "Estado actualizado y seguimiento registrado satisfactoriamente"}

# def crear_usuario(nombre, password):
#     bytes = password.encode('utf-8')
#     salt = bcrypt.gensalt()
#     hash = bcrypt.hashpw(bytes, salt)

#     connection = conectar()
#     cursor = connection.cursor()
#     cursor.execute("SELECT nombre FROM tbl_usuarios")
#     nombreUsuario = cursor.fetchall()
#     if nombreUsuario == nombre:
#         query = "INSERT INTO tbl_usuarios (nombre, password) VALUES (%s, %s)"
#         cursor.execute(query, (nombre, hash))
#     else:
#         print("Este nombre de usuario ya esta siendo utilizado, por favor use otro")   

#     connection.commit()
#     cursor.close()
#     connection.close()

#     return {"success": True, "message": "Usuario registrado satisfactoriamente"}

def listarUsuarios():
    connection = conectar()
    cursor = connection.cursor()

    query = "SELECT nombre FROM tbl_usuarios"
    cursor.execute(query)
    datos = cursor.fetchall()

    return datos

def crear_usuario(nombre, password):
    response = {}
    connection = None
    cursor = None
    
    try:
        connection = conectar()
        cursor = connection.cursor()
        
        # Verificar si el nombre de usuario ya existe
        query_check = "SELECT nombre FROM tbl_usuarios WHERE nombre = %s"
        cursor.execute(query_check, (nombre,))
        nombreUsuario = cursor.fetchone()
        
        if nombreUsuario is None:  # Si no se encontró el usuario
            # Generar el hash de la contraseña
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            
            query_insert = "INSERT INTO tbl_usuarios (nombre, password) VALUES (%s, %s)"
            cursor.execute(query_insert, (nombre, hashed_password))
            connection.commit()
            response = {"success": True, "message": "Usuario registrado satisfactoriamente"}
        else:
            response = {"success": False, "message": "Este nombre de usuario ya está siendo utilizado, por favor use otro"}
    
    except mysql.connector.Error as err:
        response = {"success": False, "message": f"Error en la base de datos: {err}"}
    
    except Exception as e:
        response = {"success": False, "message": f"Error inesperado: {e}"}
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    
    return response

# Funcion para iniciar sesion
def iniciar_sesion(nombre, password):
    connection = conectar()
    cursor = connection.cursor()
    query = "SELECT id_usuario, password FROM tbl_usuarios WHERE nombre = %s"

    cursor.execute(query, (nombre,))
    usuario = cursor.fetchall()

    if usuario:
        passwordHash = usuario[0][1]  # El hash de la contraseña almacenado
        user_id = usuario[0][0]  # El id del usuario

        # Verifica la contraseña proporcionada por el usuario
        bytes = password.encode('utf-8')
        result = bcrypt.checkpw(bytes, passwordHash.encode('utf-8'))

        if result:
            token = jwt.encode({'sub': user_id}, SECRET_KEY, algorithm='HS256')
            return {"success": True, "token": token, "message": "Inicio de sesión exitoso"}
        else:
            return {"success": False, "message": "Nombre de usuario o contraseña incorrectos"}
    else:
        return {"success": False, "message": "Nombre de usuario o contraseña incorrectos"}

    

# Funcion para validar que el token sea valido    
def validarToken(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {"success": True, "id_usuario": decoded['sub']}   
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Token invalido"} 

# Funcion para desactivar el token (necesario para el cierre de sesion)    
def desactivarToken(token):
    connection = conectar()
    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO tbl_token_desactivado (token) VALUES (%s)"
            cursor.execute(query, (token,))
            connection.commit()
    finally:
            connection.close()

# Funcion para validar que el token este desactivado
def esTokenDesativado(token):
    connection = conectar()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM tbl_token_desactivado WHERE token = %s"
            cursor.execute(query, (token,))
            resultado = cursor.fetchone()
            return resultado is not None
    finally:
        connection.close()

# Funcion parar cerrar sesion
def logout(token):

    # Se llama a la funcion para verificar que el token este desactivado
    if esTokenDesativado(token):
        return {"success": True, "message": "Token desactivado"}
    
    desactivarToken(token)
    return {"success": True, "message": "Logout exitoso"}
