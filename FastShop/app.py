from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
import mysql.connector

# Crear la aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar SQLAlchemy
db = SQLAlchemy(app)
app.jinja_env.globals.update(enumerate=enumerate)
# ========== FUNCIONES DE CONTROL DE PERMISOS ==========

def verificar_permiso(modulo, accion):
    """
    Verifica si el usuario tiene permiso para realizar una acción en un módulo
    modulo: 'clientes', 'productos', 'reportes'
    accion: 'crear', 'leer', 'actualizar', 'eliminar'
    """
    if 'id_rol' not in session:
        return False
    
    # Administrador tiene acceso total
    if session['id_rol'] == 1:
        return True
    
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        
        # Buscar permiso específico
        query = """SELECT puede_crear, puede_leer, puede_actualizar, puede_eliminar 
                   FROM permisos 
                   WHERE id_rol = %s AND modulo = %s"""
        cursor.execute(query, (session['id_rol'], modulo))
        permiso = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        if not permiso:
            return False
        
        # Verificar acción específica
        if accion == 'crear':
            return permiso['puede_crear']
        elif accion == 'leer':
            return permiso['puede_leer']
        elif accion == 'actualizar':
            return permiso['puede_actualizar']
        elif accion == 'eliminar':
            return permiso['puede_eliminar']
        else:
            return False
            
    except Exception as e:
        print(f"Error verificando permiso: {e}")
        return False

def requiere_permiso(modulo, accion):
    """
    Verifica permiso y redirige si no tiene acceso
    """
    if not verificar_permiso(modulo, accion):
        return redirect(url_for('sin_acceso'))
    return None

# Ruta principal - redirige al login
@app.route('/')
def index():
    return redirect(url_for('login'))

# Ruta de login - mostrar formulario
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener datos del formulario
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        try:
            # Conectar a MySQL
            conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password='fastshop#2026.',
                database='fastshop_db'
            )
            cursor = conexion.cursor(dictionary=True)
            
            # Buscar usuario en la base de datos
            query = "SELECT * FROM usuarios WHERE email = %s AND contrasena = %s"
            cursor.execute(query, (usuario, contrasena))
            user = cursor.fetchone()
            
            
            if user:
            # Verificar si está activo
                if user['estado'] == 0:
                    cursor.close()
                    conexion.close()
                    return render_template('login.html', error='Tu cuenta está inactiva. Contacte al administrador.')
    
                # Obtener nombre del rol ANTES de cerrar la conexión
                cursor.execute("SELECT nombre_rol FROM roles WHERE id_rol = %s", (user['id_rol'],))
                rol = cursor.fetchone()
    
                cursor.close()
                conexion.close()
    
                # Login exitoso - guardar en sesión
                session['user_id'] = user['id_usuario']
                session['usuario'] = user['usuario']
                session['nombre'] = user['nombre_completo']
                session['id_rol'] = user['id_rol']
                session['nombre_rol'] = rol['nombre_rol'] if rol else 'Usuario'
    
                return redirect(url_for('home'))

            else:
                cursor.close()
                conexion.close()
                return render_template('login.html', error='Correo o contraseña incorrectos')
                
        except Exception as e:
            return render_template('login.html', error=f'Error de conexión: {str(e)}')
    
    # Mostrar formulario de login (GET)
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Ruta de sin acceso
@app.route('/sin-acceso')
def sin_acceso():
    return render_template('sin_acceso.html')

# Ruta de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========== RUTAS DE CLIENTES ==========

# Ver lista de clientes
@app.route('/clientes')
def clientes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    #Verificar permiso de lectura
    if not verificar_permiso('clientes', 'leer'):
        return redirect(url_for('sin_acceso'))
    
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes ORDER BY id_cliente DESC")
        clientes = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        #Pasar permisos al template
        puede_crear = verificar_permiso('clientes', 'crear')
        puede_actualizar = verificar_permiso('clientes', 'actualizar')
        puede_eliminar = verificar_permiso('clientes', 'eliminar')

        return render_template('clientes.html', 
                               clientes=clientes,
                                puede_crear=puede_crear,
                                puede_actualizar=puede_actualizar,
                                puede_eliminar=puede_eliminar)
    except Exception as e:
        return render_template('clientes.html', error=f'Error: {str(e)}', clientes=[])

# Guardar cliente (crear o editar)
@app.route('/clientes/guardar', methods=['POST'])
def guardar_cliente():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar si es creación o actualización
    id_cliente = request.form.get('id_cliente')
    accion = 'actualizar' if id_cliente else 'crear'
    
    # Verificar permiso
    if not verificar_permiso('clientes', accion):
        return redirect(url_for('sin_acceso'))
    
    try:
        nombre = request.form['nombre']
        nit = request.form.get('nit')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        direccion = request.form.get('direccion')
        estado = 1 if request.form.get('estado') else 0
        
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor()
        
        if id_cliente:
            # Actualizar cliente existente
            query = """UPDATE clientes SET nombre=%s, nit=%s, telefono=%s, 
                      email=%s, direccion=%s, estado=%s WHERE id_cliente=%s"""
            cursor.execute(query, (nombre, nit, telefono, email, direccion, estado, id_cliente))
        else:
            # Crear nuevo cliente
            query = """INSERT INTO clientes (nombre, nit, telefono, email, direccion, estado) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (nombre, nit, telefono, email, direccion, estado))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return redirect(url_for('clientes'))
        
    except Exception as e:
        return redirect(url_for('clientes'))
    
# Eliminar cliente
@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar permiso de eliminación
    if not verificar_permiso('clientes', 'eliminar'):
        return redirect(url_for('sin_acceso'))
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return redirect(url_for('clientes'))
    
    except Exception as e:
        return redirect(url_for('clientes'))
    
    #  RUTAS DE PRODUCTOS 

# Ver lista de productos
@app.route('/productos')
def productos():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar permiso de lectura
    if not verificar_permiso('productos', 'leer'):
        return redirect(url_for('sin_acceso'))
    
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos ORDER BY id_producto DESC")
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        # Pasar permisos al template
        puede_crear = verificar_permiso('productos', 'crear')
        puede_editar = verificar_permiso('productos', 'actualizar')
        puede_eliminar = verificar_permiso('productos', 'eliminar')

        return render_template('productos.html', 
                               productos=productos,
                               puede_crear=puede_crear,
                               puede_editar=puede_editar,
                               puede_eliminar=puede_eliminar)
    except Exception as e:
        return render_template('productos.html', error=f'Error: {str(e)}', productos=[])

# Guardar producto (crear o editar)
@app.route('/productos/guardar', methods=['POST'])
def guardar_producto():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar si es creación o actualización
    id_producto = request.form.get('id_producto')
    accion = 'actualizar' if id_producto else 'crear'
    
    # Verificar permiso
    if not verificar_permiso('productos', accion):
        return redirect(url_for('sin_acceso'))
    
    try:
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion')
        categoria = request.form['categoria']
        precio = request.form['precio']
        stock = request.form['stock']
        marca = request.form.get('marca')
        talla = request.form.get('talla', '')[:50]
        color = request.form.get('color', '')[:50]
        estado = 1 if request.form.get('estado') else 0
        
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor()
        
        if id_producto:
            # Actualizar producto existente
            query = """UPDATE productos SET nombre=%s, descripcion=%s, categoria=%s, 
                      precio=%s, stock=%s, marca=%s, talla=%s, color=%s, estado=%s 
                      WHERE id_producto=%s"""
            cursor.execute(query, (nombre, descripcion, categoria, precio, stock, 
                                  marca, talla, color, estado, id_producto))
        else:
            # Crear nuevo producto
            query = """INSERT INTO productos (nombre, descripcion, categoria, precio, 
                      stock, marca, talla, color, estado) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (nombre, descripcion, categoria, precio, stock, 
                                  marca, talla, color, estado))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return redirect(url_for('productos'))
        
    except Exception as e:
        print(f"Error guardando producto: {e}")
        return redirect(url_for('productos'))

# Eliminar producto
@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
     # Verificar permiso de eliminación
    if not verificar_permiso('productos', 'eliminar'):
        return redirect(url_for('sin_acceso'))
    
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return redirect(url_for('productos'))
    except Exception as e:
        return redirect(url_for('productos'))
    
# ========== RUTAS DE REPORTES ==========

# Ver reportes
@app.route('/reportes')
def reportes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar permiso de lectura en reportes
    if not verificar_permiso('reportes', 'leer'):
        return redirect(url_for('sin_acceso'))
    
    tipo = request.args.get('tipo', 'clientes')

    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        
        # Obtener todos los clientes
        cursor.execute("SELECT * FROM clientes WHERE estado = 1 ORDER BY nombre")
        clientes = cursor.fetchall()
        
        # Obtener todos los productos
        cursor.execute("SELECT * FROM productos WHERE estado = 1 ORDER BY nombre")
        productos = cursor.fetchall()
        
        # Calcular estadísticas
        total_clientes = len(clientes)
        total_productos = len(productos)
        
        # Calcular valor del inventario
        valor_inventario = 0
        for producto in productos:
            valor_inventario += producto['precio'] * producto['stock']
        
        cursor.close()
        conexion.close()
        
        return render_template('reportes.html', 
                             clientes=clientes, 
                             productos=productos,
                             total_clientes=total_clientes,
                             total_productos=total_productos,
                             valor_inventario=valor_inventario,
                             tipo=tipo)
    except Exception as e:
        return render_template('reportes.html', 
                             error=f'Error: {str(e)}', 
                             clientes=[], 
                             productos=[],
                             total_clientes=0,
                             total_productos=0,
                             valor_inventario=0)

# Ruta de prueba para verificar conexión con MySQL
@app.route('/test-db')
def test_db():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='fastshop#2026.',
            database='fastshop_db'
        )
        if conexion.is_connected():
            return '<h1>¡Conexión a MySQL exitosa!</h1>'
    except Exception as e:
        return f'<h1>ERROR de conexión</h1><p>{str(e)}</p>'
## ========== RUTAS DE FACTURACIÓN ==========

@app.route('/facturacion')
def facturacion():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if not verificar_permiso('facturacion', 'leer'):
        return redirect(url_for('sin_acceso'))
    try:
        conexion = mysql.connector.connect(
            host='localhost', user='root',
            password='fastshop#2026.', database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.id_factura, f.fecha, f.total, f.estado,
                   c.nombre AS cliente, u.nombre_completo AS usuario
            FROM factura f
            JOIN clientes c ON f.id_cliente = c.id_cliente
            JOIN usuarios u ON f.id_usuario = u.id_usuario
            ORDER BY f.id_factura DESC
        """)
        facturas = cursor.fetchall()
        cursor.close()
        conexion.close()
        puede_crear   = verificar_permiso('facturacion', 'crear')
        puede_eliminar = verificar_permiso('facturacion', 'eliminar')
        return render_template('facturacion.html',
                               facturas=facturas,
                               puede_crear=puede_crear,
                               puede_eliminar=puede_eliminar)
    except Exception as e:
        return render_template('facturacion.html', error=f'Error: {str(e)}',
                               facturas=[], puede_crear=False, puede_eliminar=False)


@app.route('/facturacion/nueva')
def nueva_factura():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if not verificar_permiso('facturacion', 'crear'):
        return redirect(url_for('sin_acceso'))
    try:
        conexion = mysql.connector.connect(
            host='localhost', user='root',
            password='fastshop#2026.', database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_cliente, nombre FROM clientes WHERE estado=1 ORDER BY nombre")
        clientes = cursor.fetchall()
        cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos WHERE estado=1 ORDER BY nombre")
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template('nueva_factura.html', clientes=clientes, productos=productos)
    except Exception as e:
        return render_template('nueva_factura.html', error=f'Error: {str(e)}',
                               clientes=[], productos=[])


@app.route('/facturacion/guardar', methods=['POST'])
def guardar_factura():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if not verificar_permiso('facturacion', 'crear'):
        return redirect(url_for('sin_acceso'))
    try:
        id_cliente    = request.form['id_cliente']
        productos_ids = request.form.getlist('producto_id[]')
        cantidades    = request.form.getlist('cantidad[]')

        conexion = mysql.connector.connect(
            host='localhost', user='root',
            password='fastshop#2026.', database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)

        total = 0
        detalles = []
        for pid, cant in zip(productos_ids, cantidades):
            cant = int(cant)
            if cant <= 0:
                continue
            cursor.execute("SELECT precio, nombre FROM productos WHERE id_producto=%s", (pid,))
            prod = cursor.fetchone()
            subtotal = prod['precio'] * cant
            total += subtotal
            detalles.append({'id_producto': pid, 'cantidad': cant,
                             'precio_unitario': prod['precio'], 'subtotal': subtotal})

        # Insertar factura
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO factura (id_cliente, id_usuario, total, estado)
            VALUES (%s, %s, %s, 1)
        """, (id_cliente, session['user_id'], total))
        id_factura = cursor.lastrowid

        # Insertar detalles y actualizar stock
        for d in detalles:
            cursor.execute("""
                INSERT INTO factura_detalle
                (id_factura, id_producto, cantidad, precio_unitario, subtotal, total)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_factura, d['id_producto'], d['cantidad'],
                  d['precio_unitario'], d['subtotal'], d['subtotal']))
            cursor.execute("""
                UPDATE productos SET stock = stock - %s WHERE id_producto = %s
            """, (d['cantidad'], d['id_producto']))

        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('detalle_factura', id=id_factura))

    except Exception as e:
        return redirect(url_for('facturacion'))


@app.route('/facturacion/detalle/<int:id>')
def detalle_factura(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if not verificar_permiso('facturacion', 'leer'):
        return redirect(url_for('sin_acceso'))
    try:
        conexion = mysql.connector.connect(
            host='localhost', user='root',
            password='fastshop#2026.', database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.*, c.nombre AS cliente, c.nit,
                   u.nombre_completo AS usuario
            FROM factura f
            JOIN clientes c ON f.id_cliente = c.id_cliente
            JOIN usuarios u ON f.id_usuario = u.id_usuario
            WHERE f.id_factura = %s
        """, (id,))
        factura = cursor.fetchone()
        cursor.execute("""
            SELECT fd.*, p.nombre AS producto
            FROM factura_detalle fd
            JOIN productos p ON fd.id_producto = p.id_producto
            WHERE fd.id_factura = %s
        """, (id,))
        detalles = cursor.fetchall()
        cursor.close()
        conexion.close()
        puede_eliminar = verificar_permiso('facturacion', 'eliminar')
        return render_template('detalle_factura.html',
                               factura=factura, detalles=detalles,
                               puede_eliminar=puede_eliminar)
    except Exception as e:
        return redirect(url_for('facturacion'))


@app.route('/facturacion/anular/<int:id>')
def anular_factura(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if not verificar_permiso('facturacion', 'eliminar'):
        return redirect(url_for('sin_acceso'))
    try:
        conexion = mysql.connector.connect(
            host='localhost', user='root',
            password='fastshop#2026.', database='fastshop_db'
        )
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_producto, cantidad FROM factura_detalle WHERE id_factura=%s", (id,))
        detalles = cursor.fetchall()
        cursor.close()

        cursor = conexion.cursor()
        for d in detalles:
            cursor.execute("UPDATE productos SET stock = stock + %s WHERE id_producto = %s",
                           (d['cantidad'], d['id_producto']))
        cursor.execute("UPDATE factura SET estado=0 WHERE id_factura=%s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('facturacion'))
    except Exception as e:
        return redirect(url_for('facturacion'))
    
#  RUTAS DE USUARIOS 

@app.route('/usuarios')
def usuarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['id_rol'] != 1:
        return redirect(url_for('sin_acceso'))
    try:
        conexion = mysql.connector.connect(host='localhost', user='root', password='fastshop#2026.', database='fastshop_db')
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios ORDER BY id_usuario")
        usuarios = cursor.fetchall()
        cursor.execute("SELECT * FROM roles ORDER BY id_rol")
        roles = cursor.fetchall()
        cursor.close(); conexion.close()
        return render_template('usuarios.html', usuarios=usuarios, roles=roles)
    except Exception as e:
        return render_template('usuarios.html', error=str(e), usuarios=[], roles=[])

@app.route('/usuarios/guardar', methods=['POST'])
def guardar_usuario():
    if 'user_id' not in session or session['id_rol'] != 1:
        return redirect(url_for('sin_acceso'))
    try:
        id_usuario      = request.form.get('id_usuario')
        usuario         = request.form['usuario']
        nombre_completo = request.form['usuario']
        email           = request.form.get('email')
        contrasena      = request.form.get('contrasena')
        id_rol          = request.form['id_rol']
        estado          = request.form.get('estado', 1)

        conexion = mysql.connector.connect(host='localhost', user='root', password='fastshop#2026.', database='fastshop_db')
        cursor = conexion.cursor(dictionary=True)

        # Validar: solo puede existir 1 administrador (al crear)
        if str(id_rol) == '1' and not id_usuario:
            cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE id_rol = 1")
            resultado = cursor.fetchone()
            if resultado['total'] >= 1:
                cursor.execute("SELECT * FROM usuarios ORDER BY id_usuario")
                usuarios = cursor.fetchall()
                cursor.execute("SELECT * FROM roles ORDER BY id_rol")
                roles = cursor.fetchall()
                cursor.close(); conexion.close()
                return render_template('usuarios.html', usuarios=usuarios, roles=roles,
                                       error='Ya existe un Administrador. No se puede crear otro perfil con ese rol.')

        if id_usuario:
            # Validar: no cambiar rol al único administrador
            cursor.execute("SELECT id_rol FROM usuarios WHERE id_usuario=%s", (id_usuario,))
            usuario_actual = cursor.fetchone()
            if usuario_actual and str(usuario_actual['id_rol']) == '1' and str(id_rol) != '1':
                cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE id_rol = 1")
                total_admins = cursor.fetchone()
                if total_admins['total'] <= 1:
                    cursor.execute("SELECT * FROM usuarios ORDER BY id_usuario")
                    usuarios = cursor.fetchall()
                    cursor.execute("SELECT * FROM roles ORDER BY id_rol")
                    roles = cursor.fetchall()
                    cursor.close(); conexion.close()
                    return render_template('usuarios.html', usuarios=usuarios, roles=roles,
                                           error='No se puede cambiar de rol ya que es el único Administrador existente.')

            if str(id_rol) == '1':
                cursor.execute(
                    "SELECT COUNT(*) as total FROM usuarios WHERE id_rol = 1 AND id_usuario != %s",
                    (id_usuario,)
                )
                resultado = cursor.fetchone()
                if resultado['total'] >= 1:
                    cursor.execute("SELECT * FROM usuarios ORDER BY id_usuario")
                    usuarios = cursor.fetchall()
                    cursor.execute("SELECT * FROM roles ORDER BY id_rol")
                    roles = cursor.fetchall()
                    cursor.close(); conexion.close()
                    return render_template('usuarios.html', usuarios=usuarios, roles=roles,
                                           error='Ya existe un Administrador. No se puede asignar ese rol a otro usuario.')

            # Validar: no inactivar al único administrador
            if str(estado) == '0':
                cursor.execute("SELECT id_rol FROM usuarios WHERE id_usuario=%s", (id_usuario,))
                usuario_actual = cursor.fetchone()
                if usuario_actual and str(usuario_actual['id_rol']) == '1':
                    cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE id_rol = 1 AND estado = 1")
                    admins_activos = cursor.fetchone()
                    if admins_activos['total'] <= 1:
                        cursor.execute("SELECT * FROM usuarios ORDER BY id_usuario")
                        usuarios = cursor.fetchall()
                        cursor.execute("SELECT * FROM roles ORDER BY id_rol")
                        roles = cursor.fetchall()
                        cursor.close(); conexion.close()
                        return render_template('usuarios.html', usuarios=usuarios, roles=roles,
                                               error='No puede inactivar al único Administrador del sistema.')

            if contrasena:
                cursor.execute("UPDATE usuarios SET usuario=%s, nombre_completo=%s, email=%s, contrasena=%s, id_rol=%s, estado=%s WHERE id_usuario=%s",
                               (usuario, nombre_completo, email, contrasena, id_rol, estado, id_usuario))
            else:
                cursor.execute("UPDATE usuarios SET usuario=%s, nombre_completo=%s, email=%s, id_rol=%s, estado=%s WHERE id_usuario=%s",
                               (usuario, nombre_completo, email, id_rol, estado, id_usuario))
        else:
            cursor.execute("INSERT INTO usuarios (usuario, nombre_completo, email, contrasena, id_rol, estado) VALUES (%s,%s,%s,%s,%s,%s)",
                           (usuario, nombre_completo, email, contrasena, id_rol, estado))

        conexion.commit(); cursor.close(); conexion.close()
        return redirect(url_for('usuarios'))
    except Exception as e:
        return render_template('usuarios.html', error=str(e), usuarios=[], roles=[])

@app.route('/usuarios/eliminar/<int:id>')
def eliminar_usuario(id):
    if 'user_id' not in session or session['id_rol'] != 1:
        return redirect(url_for('sin_acceso'))
    try:
        conexion = mysql.connector.connect(host='localhost', user='root', password='fastshop#2026.', database='fastshop_db')
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id,))
        conexion.commit(); cursor.close(); conexion.close()
        return redirect(url_for('usuarios'))
    
    except Exception as e:
        return render_template('usuarios.html', error=str(e), usuarios=[], roles=[])


@app.route('/mantenimiento')
def mantenimiento():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    puede_ver_clientes = verificar_permiso('clientes', 'leer')
    puede_ver_productos = verificar_permiso('productos', 'leer')
    
    # Redirigir según lo que pueda ver
    if puede_ver_clientes:
        return redirect(url_for('clientes'))
    elif puede_ver_productos:
        return redirect(url_for('productos'))
    else:
        return redirect(url_for('sin_acceso'))

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)