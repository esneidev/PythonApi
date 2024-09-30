from clases.logica import crear, listar, actualizar, actualizar_estado, listarUsuarios, crear_usuario, iniciar_sesion, listarTicketFiltro, validarToken, logout
import json
import logging
from functools import wraps

logging.basicConfig(level=logging.DEBUG)

# Crear ticket
def crearTicket(event, context):
    body = json.loads(event['body'])
    
    # Se obtiene el token (necesario para saber que usuario creo el ticket)
    token = event.get('headers', {}).get('authorization', '').replace('Bearer ', '')
    
    if not token:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Token requerido'})
        }
    
    token_result = validarToken(token)

    if not token_result['success']:
        return {
            'statusCode': 401,
            'body': json.dumps(token_result)
        }
    
    userId = token_result['id_usuario'] # Se obtiene el id del usuario en el payload del token
    nombre = body.get('nombre')
    descripcion = body.get('descripcion')
    fk_prioridad = body.get('fk_prioridad')

    if not nombre or not descripcion or not fk_prioridad:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Nombre, descripcion y prioridad son requeridos'})
        }
    
    result = crear(userId, nombre, descripcion, fk_prioridad)
    
    status = 200 if result['success'] else 400
    return {
        'statusCode': status,
        'body': json.dumps(result)
    }

# Obtener los datos del ticket
def getDatos(event, context):
    result = listar()
    return{
        "statusCode": 200,
        "body": json.dumps(result)
    }

# Buscar ticket por id, estado o fecha
def buscarTickets(event, context):
    params = event.get('queryStringParameters', {})
    fecha = params.get('fecha_registro')
    estado = params.get('fk_estado')
    id_ticket = params.get('id_ticket')
    
    result = listarTicketFiltro(
        fecha=fecha if fecha else None, 
        estado=estado if estado else None, 
        id_ticket=id_ticket if id_ticket else None
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(result, indent=4)  # Añadido indent=4 para mejor legibilidad
    }

# Actualizar datos del ticket
def actualizarDatos(event, context):
    id_ticket = event['pathParameters']['id_ticket']
    body = json.loads(event['body'])
    result = actualizar(id_ticket, body['descripcion'], body['fk_prioridad'])
    return{
        'statusCode': 200,
        'body': json.dumps(result)
    } 

# Actualizar el estado del token (nuevo, notificado, error, realizado)
def finalizarTicket(event, context):    
    id_ticket = event['pathParameters']['id_ticket']
    body = json.loads(event['body'])
    result = actualizar_estado(id_ticket, body['fk_estado'],)
    return{
        'statusCode': 200,
        'body': json.dumps(result)
    }

# Funcion decoradora
def require_auth(func):
    @wraps(func)
    def wrapper(event, context):
        token = event.get('headers', {}).get('authorization', '').replace('Bearer ', '')
        if not token:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Token requerido'})
            }
        
        result = validarToken(token)
        if not result['success']:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': result['message']})
            }
        
        return func(event, context, result['id_usuario'])
    
    return wrapper

# Verificar que el token exista
@require_auth
def validarTokenHandler(event, context, id_usuario):
    return {
        'statusCode': 200,
        'body': json.dumps({'success': True, 'id_usuario': id_usuario})
    }

def listarUsuarios(event, context):
    result = listarUsuarios()
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def crearUsuario(event, context):
    body = json.loads(event['body'])

    nombre = body.get('nombre')
    password = body.get('password')

    if not nombre or not password:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Nombre y contraseña son requeridos'})
        }
    
    result = crear_usuario(nombre, password)

    status = 200 if result['success'] else 400
    return {
        'statusCode': status,
        'body': json.dumps(result)
    }

# Iniciar sesion
def IniciarSesion(event, context):
    try:
        body = json.loads(event['body'])
        nombre = body.get('nombre')
        password = body.get('password')

        result = iniciar_sesion(nombre, password)
        status = 200 if result['success'] else 401

        return {
            'statusCode': status,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
            },
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': 'Error interno del servidor'}),
            'headers': {
                'Content-Type': 'application/json',
            },
        }

# cerrar sesion
@require_auth
def logoutUsuario(event, context, id_usuario):
    
    authorization_header = event.get('headers', {}).get('authorization')
    
    if not authorization_header or not authorization_header.startswith('Bearer '):
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Token requerido'})
        }

    token = authorization_header.replace('Bearer ', '').strip()

    if not token:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Token requerido'})
        }
    
    # Llamar a la función de logout
    result = logout(token)

    status = 200 if result['success'] else 400
    return {
        'statusCode': status,
        'body': json.dumps(result)
    }

            