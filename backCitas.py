from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date, time, datetime
import pyodbc

app = Flask(__name__)
CORS(app)

# Configuración de la conexión a SQL Server
DB_CONFIG = {
    'server': 'host.docker.internal',
    'database': 'proyCitas',
    'username': 'sa',
    'password': '123',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

def get_db_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return pyodbc.connect(conn_str)

# Validaciones
def validar_paciente(data):
    required = ['nombre', 'apellido', 'fecha_nacimiento', 'email']
    if not all(field in data for field in required):
        return False, "Datos incompletos"
    
    valido, mensaje = validar_fecha_nacimiento(data['fecha_nacimiento'])
    if not valido:
        return False, mensaje
    
    return True, ""

def validar_medico(data):
    required = ['nombre', 'apellido', 'especialidad', 'email']
    return all(field in data for field in required)

def validar_consultorio(data):
    required = ['numero', 'ubicacion', 'descripcion']
    return all(field in data for field in required)

def validar_cita(data):
    required = ['paciente_id', 'medico_id', 'consultorio_id', 'fecha', 'hora']
    if not all(field in data for field in required):
        return False, "Datos incompletos"
    
    # Validar hora
    valido, mensaje = validar_hora(data['hora'])
    if not valido:
        return False, mensaje
    
    # Validar fecha no pasada (opcional)
    try:
        fecha_cita = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        if fecha_cita < date.today():
            return False, "No se pueden crear citas en fechas pasadas"
    except ValueError:
        return False, "Formato de fecha inválido"
    
    return True, ""

def validar_fecha_nacimiento(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        if fecha > date.today():
            return False, "La fecha de nacimiento no puede ser futura"
        if fecha < date(1900, 1, 1):
            return False, "Fecha de nacimiento demasiado antigua (mínimo 1900-01-01)"
        return True, ""
    except ValueError:
        return False, "Formato de fecha inválido (YYYY-MM-DD)"

def validar_hora(hora_str):
    try:
        hora = datetime.strptime(hora_str, '%H:%M').time()
        return True, ""
    except ValueError:
        return False, "Formato de hora inválido (HH:MM)"

# CRUD Pacientes
@app.route('/pacientes', methods=['GET'])
def get_pacientes():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, fecha_nacimiento, email FROM Pacientes")
        pacientes = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(pacientes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
         conn.close()

@app.route('/pacientes/<int:id>', methods=['GET'])
def get_paciente(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, fecha_nacimiento, email FROM Pacientes WHERE id = ?", (id,))
        row = cursor.fetchone()
        return jsonify(dict(zip([col[0] for col in cursor.description], row))) if row else ('', 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/pacientes', methods=['POST'])
def add_paciente():
    data = request.get_json()
    valido, mensaje = validar_paciente(data)
    if not valido:
        return jsonify({'error': mensaje}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (nombre, apellido, fecha_nacimiento, email)
            VALUES (?, ?, ?, ?)
        """, (data['nombre'], data['apellido'], data['fecha_nacimiento'], data['email']))
        conn.commit()
        return jsonify({'message': 'Paciente creado'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/pacientes/<int:id>', methods=['PUT'])
def update_paciente(id):
    data = request.get_json()
    if not validar_paciente(data):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Pacientes 
            SET nombre = ?, apellido = ?, fecha_nacimiento = ?, email = ?
            WHERE id = ?
        """, (data['nombre'], data['apellido'], data['fecha_nacimiento'], data['email'], id))
        conn.commit()
        return jsonify({'message': 'Paciente actualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/pacientes/<int:id>', methods=['DELETE'])
def delete_paciente(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Pacientes WHERE id = ?", (id,))
        conn.commit()
        return jsonify({'message': 'Paciente eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# CRUD Médicos
@app.route('/medicos', methods=['GET'])
def get_medicos():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, especialidad, email FROM Medicos")
        medicos = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(medicos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
         conn.close()

@app.route('/medicos/<int:id>', methods=['GET'])
def get_medico(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, especialidad, email FROM Medicos WHERE id = ?", (id,))
        row = cursor.fetchone()
        return jsonify(dict(zip([col[0] for col in cursor.description], row))) if row else ('', 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/medicos', methods=['POST'])
def add_medico():
    data = request.get_json()
    if not validar_medico(data):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Medicos (nombre, apellido, especialidad, email)
            VALUES (?, ?, ?, ?)
        """, (data['nombre'], data['apellido'], data['especialidad'], data['email']))
        conn.commit()
        return jsonify({'message': 'Médico creado'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/medicos/<int:id>', methods=['PUT'])
def update_medico(id):
    data = request.get_json()
    if not validar_medico(data):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Medicos 
            SET nombre = ?, apellido = ?, especialidad = ?, email = ?
            WHERE id = ?
        """, (data['nombre'], data['apellido'], data['especialidad'], data['email'], id))
        conn.commit()
        return jsonify({'message': 'Médico actualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/medicos/<int:id>', methods=['DELETE'])
def delete_medico(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Medicos WHERE id = ?", (id,))
        conn.commit()
        return jsonify({'message': 'Médico eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# CRUD Consultorios
@app.route('/consultorios', methods=['GET'])
def get_consultorios():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero, ubicacion, descripcion FROM Consultorios")
        consultorios = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(consultorios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
         conn.close()

@app.route('/consultorios/<int:id>', methods=['GET'])
def get_consultorio(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero, ubicacion, descripcion FROM Consultorios WHERE id = ?", (id,))
        row = cursor.fetchone()
        return jsonify(dict(zip([col[0] for col in cursor.description], row))) if row else ('', 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/consultorios', methods=['POST'])
def add_consultorio():
    data = request.get_json()
    if not validar_consultorio(data):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Consultorios (numero, ubicacion, descripcion)
            VALUES (?, ?, ?)
        """, (data['numero'], data['ubicacion'], data['descripcion']))
        conn.commit()
        return jsonify({'message': 'Consultorio creado'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/consultorios/<int:id>', methods=['PUT'])
def update_consultorio(id):
    data = request.get_json()
    if not validar_consultorio(data):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Consultorios 
            SET numero = ?, ubicacion = ?, descripcion = ?
            WHERE id = ?
        """, (data['numero'], data['ubicacion'], data['descripcion'], id))
        conn.commit()
        return jsonify({'message': 'Consultorio actualizado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/consultorios/<int:id>', methods=['DELETE'])
def delete_consultorio(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Consultorios WHERE id = ?", (id,))
        conn.commit()
        return jsonify({'message': 'Consultorio eliminado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# CRUD Citas
@app.route('/citas', methods=['GET'])
def get_citas():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, paciente_id, medico_id, consultorio_id, fecha, hora FROM Citas")
        citas = []
        for row in cursor.fetchall():
            cita = dict(zip([col[0] for col in cursor.description], row))
            cita['hora'] = str(cita['hora'])  # Convertir tiempo a string
            citas.append(cita)
        return jsonify(citas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
         conn.close()

@app.route('/citas/<int:id>', methods=['GET'])
def get_cita(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, paciente_id, medico_id, consultorio_id, fecha, hora FROM Citas WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            cita = dict(zip([col[0] for col in cursor.description], row))
            cita['hora'] = str(cita['hora'])
            return jsonify(cita)
        return jsonify({'message': 'Cita no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/citas', methods=['POST'])
def add_cita():
    data = request.get_json()
    if not validar_cita(data):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Citas (paciente_id, medico_id, consultorio_id, fecha, hora)
            VALUES (?, ?, ?, ?, ?)
        """, (data['paciente_id'], data['medico_id'], data['consultorio_id'], data['fecha'], data['hora']))
        conn.commit()
        return jsonify({'message': 'Cita creada'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/citas/<int:id>', methods=['PUT'])
def update_cita(id):
    data = request.get_json()
    if not validar_cita(data):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Citas 
            SET paciente_id = ?, medico_id = ?, consultorio_id = ?, fecha = ?, hora = ?
            WHERE id = ?
        """, (data['paciente_id'], data['medico_id'], data['consultorio_id'], data['fecha'], data['hora'], id))
        conn.commit()
        return jsonify({'message': 'Cita actualizada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/citas/<int:id>', methods=['DELETE'])
def delete_cita(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Citas WHERE id = ?", (id,))
        conn.commit()
        return jsonify({'message': 'Cita eliminada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)