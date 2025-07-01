from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
import json # Added
from datetime import datetime
import pytz # Added
import os # Added
from werkzeug.utils import secure_filename
from sqlalchemy import Enum as SqlEnum, text

from PIL import Image, ExifTags

import mysql.connector # Added
import unicodedata

def test_mysql_connector():
    try:
        cnx = mysql.connector.connect(
            user="ADmin296",
            password="prac_seg296",
            host="gestion-sso.mysql.database.azure.com",
            port=3306,
            database="gestion_empresas",
            ssl_ca="DigiCertGlobalRootCA.crt.pem",
            ssl_disabled=False
        )
        print("MySQL direct connection successful!")
        cnx.close()
    except Exception as e:
        print("MySQL direct connection failed:", e)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://ADmin296:prac_seg296@gestion-sso.mysql.database.azure.com/gestion_empresas'
    '?charset=utf8mb4'
    '&ssl_ca=DigiCertGlobalRootCA.crt.pem'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB máximo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

import platform

# Modelos para empresas y trabajadores
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    workers = db.relationship('Worker', backref='company', lazy=True)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('America/Lima')))

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    company = db.relationship('Company', backref='assets')

class GroupCompliance(db.Model):
    __tablename__ = 'group_compliance'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    group_name = db.Column(db.String(100), nullable=False)
    compliance_status = db.Column(SqlEnum('Cumple', 'No cumple', 'No aplica'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('America/Lima')))

class DailyChecklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    prox_mantto = db.Column(db.Date)
    km_inicial = db.Column(db.Integer)
    km_final = db.Column(db.Integer)
    item0 = db.Column(db.String(5))
    item1 = db.Column(db.String(5))
    item2 = db.Column(db.String(5))
    item3 = db.Column(db.String(5))
    item4 = db.Column(db.String(5))
    item5 = db.Column(db.String(5))
    item6 = db.Column(db.String(5))
    item7 = db.Column(db.String(5))
    item8 = db.Column(db.String(5))
    item9 = db.Column(db.String(5))
    item10 = db.Column(db.String(5))
    item11 = db.Column(db.String(5))
    item12 = db.Column(db.String(5))
    item13 = db.Column(db.String(5))
    item14 = db.Column(db.String(5))
    item15 = db.Column(db.String(5))
    item16 = db.Column(db.String(5))
    item17 = db.Column(db.String(5))
    item18 = db.Column(db.String(5))
    item19 = db.Column(db.String(5))
    item100 = db.Column(db.String(5))
    item101 = db.Column(db.String(5))
    item102 = db.Column(db.String(5))
    item103 = db.Column(db.String(5))
    item104 = db.Column(db.String(5))
    item105 = db.Column(db.String(5))
    item106 = db.Column(db.String(5))
    item107 = db.Column(db.String(5))
    item108 = db.Column(db.String(5))
    item200 = db.Column(db.String(5))
    item201 = db.Column(db.String(5))
    item202 = db.Column(db.String(5))
    item203 = db.Column(db.String(5))
    item204 = db.Column(db.String(5))
    item205 = db.Column(db.String(5))
    item300 = db.Column(db.String(5))
    item301 = db.Column(db.String(5))
    item400 = db.Column(db.String(5))
    item401 = db.Column(db.String(5))
    item402 = db.Column(db.String(5))
    item403 = db.Column(db.String(5))
    item404 = db.Column(db.String(5))
    item405 = db.Column(db.String(5))
    item500 = db.Column(db.String(5))
    item501 = db.Column(db.String(5))
    item600 = db.Column(db.String(5))
    item601 = db.Column(db.String(5))
    observaciones = db.Column(db.Text)
    foto = db.Column(db.String(255))

    def to_dict(self):
        d = {col: getattr(self, col) for col in self.__table__.columns.keys()}
        # Formatear fechas a string para Jinja2 si es necesario
        if d.get('prox_mantto') and isinstance(d['prox_mantto'], (datetime,)):
            d['prox_mantto'] = d['prox_mantto'].strftime('%Y-%m-%d')
        return d

class ToolsCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    herr_item1 = db.Column(db.String(5))
    herr_item2 = db.Column(db.String(5))
    herr_item3 = db.Column(db.String(5))
    herr_extintor_fecha = db.Column(db.Date)
    herr_item4 = db.Column(db.String(5))
    herr_item5 = db.Column(db.String(5))
    herr_item6 = db.Column(db.String(5))
    herr_item7 = db.Column(db.String(5))
    herr_item8 = db.Column(db.String(5))
    kit_panos = db.Column(db.String(5))
    kit_pico = db.Column(db.String(5))
    kit_lampa = db.Column(db.String(5))
    kit_costales = db.Column(db.String(5))
    kit_salchicha = db.Column(db.String(5))
    kit_bandeja = db.Column(db.String(5))
    kit_tacos = db.Column(db.String(5))
    kit_trajes = db.Column(db.String(5))
    kit_guantes = db.Column(db.String(5))
    otros_soat = db.Column(db.String(5))
    otros_soat_fecha = db.Column(db.Date)
    otros_propiedad = db.Column(db.String(5))
    otros_circulacion = db.Column(db.String(5))
    otros_licencia = db.Column(db.String(5))
    observaciones = db.Column(db.Text)
    foto = db.Column(db.String(255))

    def to_dict(self):
        d = {col: getattr(self, col) for col in self.__table__.columns.keys()}
        # Formatear fechas a string para Jinja2 si es necesario
        if d.get('herr_extintor_fecha') and isinstance(d['herr_extintor_fecha'], (datetime,)):
            d['herr_extintor_fecha'] = d['herr_extintor_fecha'].strftime('%Y-%m-%d')
        if d.get('otros_soat_fecha') and isinstance(d['otros_soat_fecha'], (datetime,)):
            d['otros_soat_fecha'] = d['otros_soat_fecha'].strftime('%Y-%m-%d')
        return d

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calcular_cumplimiento_grupo(respuestas, items):
    valores = [respuestas.get(item) for item in items]
    # Filtra los que no tienen respuesta (None o '')
    valores_validos = [v for v in valores if v not in (None, '', 'None')]
    if not valores_validos:
        return 'No aplica'
    if all(v == 'NA' for v in valores_validos):
        return 'No aplica'
    if any(v == 'NC' for v in valores_validos):
        return 'No cumple'
    if all(v == 'C' for v in valores_validos):
        return 'Cumple'
    # Si hay mezcla de 'C' y 'NA', pero ningún 'NC'
    if all(v in ('C', 'NA') for v in valores_validos):
        return 'Cumple'
    return 'No aplica'

@app.route('/get_workers', methods=['POST'])
def get_workers():
    company_id = request.json.get('company')
    workers = Worker.query.filter_by(company_id=company_id).all()
    worker_list = [w.name for w in workers]
    return {"workers": worker_list}

@app.route('/get_assets', methods=['POST'])
def get_assets():
    company_id = request.json.get('company_id')
    assets = Asset.query.filter_by(company_id=company_id).all()
    asset_list = [{'id': a.id, 'type': a.type, 'code': a.code} for a in assets]
    return {"assets": asset_list}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company_id = request.form.get('company')
        worker_name = request.form.get('worker_name')
        asset_type = request.form.get('asset_type')
        asset_code = request.form.get('asset_code')
        if not (company_id and worker_name and asset_type and asset_code):
            flash('Debe seleccionar empresa, trabajador, tipo de equipo y placa/código.', 'error')
            companies = Company.query.all()
            return render_template('form.html', companies=companies)
        worker = Worker.query.filter_by(name=worker_name, company_id=company_id).first()
        asset = Asset.query.filter_by(type=asset_type, code=asset_code, company_id=company_id).first()
        if not worker:
            flash('Trabajador no encontrado para la empresa seleccionada.', 'error')
            companies = Company.query.all()
            return render_template('form.html', companies=companies)
        if not asset:
            flash('Equipo no encontrado para la empresa y tipo/código seleccionados.', 'error')
            companies = Company.query.all()
            return render_template('form.html', companies=companies)
        # Guardar la fecha y hora de creación en horario de Perú
        now = datetime.now(pytz.timezone('America/Lima'))
        new_submission = Submission(company_id=company_id, worker_id=worker.id, asset_id=asset.id, created_at=now)
        db.session.add(new_submission)
        db.session.commit()
        return redirect(url_for('checklist', submission_id=new_submission.id))
    companies = Company.query.all()
    return render_template('form.html', companies=companies)

@app.route('/checklist/<int:submission_id>', methods=['GET', 'POST'])
def checklist(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    company = Company.query.get(submission.company_id)
    worker = Worker.query.get(submission.worker_id)
    asset = Asset.query.get(submission.asset_id)

    # Definir función y diccionarios al inicio para ambos métodos
    def normalize_equipo(s):
        if not s:
            return ''
        s = s.strip().lower()
        s = unicodedata.normalize('NFD', s)
        s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
        s = ' '.join(s.split())
        return s

    # --- Selección de plantilla según tipo de equipo ---
    plantilla = 'checklist.html'
    tipo_equipo_norm = normalize_equipo(asset.type) if asset and asset.type else ''
    plantilla_asignada = False
    if tipo_equipo_norm == 'camioneta':
        plantilla = 'checklist_camioneta.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'ambulancia':
        plantilla = 'checklist_ambulancia.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'volquete':
        plantilla = 'checklist_volquete.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'grua':
        plantilla = 'checklist_grua.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'cisterna':
        plantilla = 'checklist_cisterna.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'utilitario':
        plantilla = 'checklist_utilitario.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'retroexcavadora':
        plantilla = 'checklist_retroexcavadora.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'excavadora':
        plantilla = 'checklist_excavadora.html'
        plantilla_asignada = True
    elif tipo_equipo_norm == 'cargador frontal':
        plantilla = 'checklist_cargador_frontal.html'
        plantilla_asignada = True
    # Puedes agregar más elif para otros tipos de equipo

    grupos_por_equipo = {
        normalize_equipo('camioneta'): ['general_apagado', 'general_encendido'],
        normalize_equipo('ambulancia'): ['general_apagado', 'general_encendido'],
        normalize_equipo('cargador frontal'): ['general_apagado', 'general_encendido', 'cargador'],
        normalize_equipo('retroexcavadora'): ['general_apagado', 'general_encendido', 'cargador'],
        normalize_equipo('excavadora'): ['general_apagado', 'general_encendido', 'cargador'],
        normalize_equipo('montacarga'): ['general_apagado', 'general_encendido', 'cargador'],
        normalize_equipo('minicargador'): ['general_apagado', 'general_encendido', 'cargador'],
        normalize_equipo('tractor'): ['general_apagado', 'general_encendido', 'cargador'],
        normalize_equipo('grua'): ['general_apagado', 'general_encendido', 'grua'],
        normalize_equipo('cisterna'): ['general_apagado', 'general_encendido', 'cisterna'],
        normalize_equipo('utilitario'): ['general_apagado', 'general_encendido', 'cisterna'],
        normalize_equipo('volquete'): ['general_apagado', 'general_encendido', 'volquete'],
    }
    grupos_items = {
        'general_apagado': [f'item{i}' for i in range(0,20)],
        'general_encendido': [f'item{100+i}' for i in range(1,10)],
        'cargador': [f'item{200+i}' for i in range(1,7)],
        'rodillo': [f'item{300+i}' for i in range(1,3)],
        'volquete': [f'item{400+i}' for i in range(1,7)],
        'grua': [f'item{500+i}' for i in range(1,3)],
        'cisterna': [f'item{600+i}' for i in range(1,3)]
    }
    if request.method == 'POST':
        checklist = dict(request.form)
        # DEBUG: Mostrar en consola los datos recibidos
        print('--- CHECKLIST SUBMIT DEBUG ---')
        print('Checklist recibido:', checklist)
        print('Campos requeridos:')
        for i in range(0, 20):
            print(f'item{i}:', checklist.get(f'item{i}'))
        for i in range(1, 10):
            print(f'item{100+i}:', checklist.get(f'item{100+i}'))
        for i in range(1, 7):
            print(f'item{200+i}:', checklist.get(f'item{200+i}'))
        for i in range(1, 3):
            print(f'item{300+i}:', checklist.get(f'item{300+i}'))
        for i in range(1, 7):
            print(f'item{400+i}:', checklist.get(f'item{400+i}'))
        for i in range(1, 3):
            print(f'item{500+i}:', checklist.get(f'item{500+i}'))
        for i in range(1, 3):
            print(f'item{600+i}:', checklist.get(f'item{600+i}'))
        # Validar que todos los campos requeridos estén presentes (ejemplo para los primeros 20)
        missing = []
        for i in range(0, 20):
            if f'item{i}' not in checklist or checklist.get(f'item{i}') in (None, '', 'None'):
                missing.append(f'item{i}')
        if missing:
            flash(f'Faltan respuestas en: {", ".join(missing)}. Revisa el autocompletado de NA.', 'error')
            print('FALTAN CAMPOS:', missing)
            return render_template(plantilla, submission=submission, company=company, worker=worker, asset=asset)
        # --- VALIDACIÓN DE TODOS LOS CAMPOS REQUERIDOS SEGÚN EL TIPO DE EQUIPO ---
        # Determinar los grupos relevantes para el equipo actual
        tipo_equipo = normalize_equipo(asset.type) if asset and asset.type else ''
        grupos_relevantes = grupos_por_equipo.get(tipo_equipo, [])
        # Obtener todos los campos requeridos para este equipo
        requeridos = set()
        for grupo in grupos_relevantes:
            requeridos.update(grupos_items[grupo])
        # Validar que todos los campos requeridos estén presentes y respondidos
        missing = []
        for key in requeridos:
            if key not in checklist or checklist.get(key) in (None, '', 'None'):
                missing.append(key)
        if missing:
            flash(f'Faltan respuestas en: {", ".join(missing)}. Revisa el autocompletado de NA.', 'error')
            print('FALTAN CAMPOS:', missing)
            return render_template(plantilla, submission=submission, company=company, worker=worker, asset=asset)
        # Guardar observaciones
        observaciones = request.form.get('observaciones', '')
        # Guardar foto si se adjunta
        foto_filename = None
        if 'foto' in request.files and request.files['foto'].filename != '':
            file = request.files['foto']
            if allowed_file(file.filename):
                foto_filename = secure_filename(f"submission_{submission.id}_" + file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename)
                file.save(filepath)
                corregir_orientacion_imagen(filepath)
            else:
                flash('Formato de imagen no permitido.', 'error')
        # --- AUTOCOMPLETAR CON NA SEGÚN EL TIPO DE EQUIPO ---
        def normalize_equipo(s):
            """
            Normaliza el nombre de equipo para comparación robusta:
            - Minúsculas
            - Sin tildes
            - Sin espacios extra
            - Sin caracteres especiales
            """
            if not s:
                return ''
            s = s.strip().lower()
            s = unicodedata.normalize('NFD', s)
            s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
            s = ' '.join(s.split())
            return s

        # Definir los grupos relevantes por tipo de equipo (todas las claves ya normalizadas)
        grupos_por_equipo = {
            normalize_equipo('camioneta'): ['general_apagado', 'general_encendido'],
            normalize_equipo('ambulancia'): ['general_apagado', 'general_encendido'],
            normalize_equipo('cargador frontal'): ['general_apagado', 'general_encendido', 'cargador'],
            normalize_equipo('retroexcavadora'): ['general_apagado', 'general_encendido', 'cargador'],
            normalize_equipo('excavadora'): ['general_apagado', 'general_encendido', 'cargador'],
            normalize_equipo('montacarga'): ['general_apagado', 'general_encendido', 'cargador'],
            normalize_equipo('minicargador'): ['general_apagado', 'general_encendido', 'cargador'],
            normalize_equipo('tractor'): ['general_apagado', 'general_encendido', 'cargador'],
            normalize_equipo('grua'): ['general_apagado', 'general_encendido', 'grua'],
            normalize_equipo('cisterna'): ['general_apagado', 'general_encendido', 'cisterna'],
            normalize_equipo('utilitario'): ['general_apagado', 'general_encendido', 'cisterna'],
            normalize_equipo('volquete'): ['general_apagado', 'general_encendido', 'volquete'],
        }
        # Mapear los grupos a los campos del checklist
        grupos_items = {
            'general_apagado': [f'item{i}' for i in range(0,20)],
            'general_encendido': [f'item{100+i}' for i in range(1,10)],
            'cargador': [f'item{200+i}' for i in range(1,7)],
            'rodillo': [f'item{300+i}' for i in range(1,3)],
            'volquete': [f'item{400+i}' for i in range(1,7)],
            'grua': [f'item{500+i}' for i in range(1,3)],
            'cisterna': [f'item{600+i}' for i in range(1,3)]
        }
        # Determinar los grupos relevantes para el equipo actual
        tipo_equipo = normalize_equipo(asset.type) if asset and asset.type else ''
        # Busca coincidencia exacta
        grupos_relevantes = grupos_por_equipo.get(tipo_equipo, [])
        # Si hay grupos relevantes, autocompletar el resto con NA
        if grupos_relevantes:
            # Todos los posibles campos del checklist diario
            all_items = set()
            for items in grupos_items.values():
                all_items.update(items)
            # Los campos requeridos para este equipo
            requeridos = set()
            for grupo in grupos_relevantes:
                requeridos.update(grupos_items[grupo])
            # Autocompletar con NA los que no son requeridos
            for key in all_items:
                if key not in requeridos and key not in checklist:
                    checklist[key] = 'NA'
        # Crear registro en DailyChecklist
        daily = DailyChecklist(
            submission_id=submission.id,
            prox_mantto=request.form.get('prox_mantto'),
            km_inicial=request.form.get('km_inicial'),
            item0=request.form.get('item0'),
            item1=request.form.get('item1'),
            item2=request.form.get('item2'),
            item3=request.form.get('item3'),
            item4=request.form.get('item4'),
            item5=request.form.get('item5'),
            item6=request.form.get('item6'),
            item7=request.form.get('item7'),
            item8=request.form.get('item8'),
            item9=request.form.get('item9'),
            item10=request.form.get('item10'),
            item11=request.form.get('item11'),
            item12=request.form.get('item12'),
            item13=request.form.get('item13'),
            item14=request.form.get('item14'),
            item15=request.form.get('item15'),
            item16=request.form.get('item16'),
            item17=request.form.get('item17'),
            item18=request.form.get('item18'),
            item19=request.form.get('item19'),
            item100=request.form.get('item100'),
            item101=request.form.get('item101'),
            item102=request.form.get('item102'),
            item103=request.form.get('item103'),
            item104=request.form.get('item104'),
            item105=request.form.get('item105'),
            item106=request.form.get('item106'),
            item107=request.form.get('item107'),
            item108=request.form.get('item108'),
            item200=request.form.get('item200'),
            item201=request.form.get('item201'),
            item202=request.form.get('item202'),
            item203=request.form.get('item203'),
            item204=request.form.get('item204'),
            item205=request.form.get('item205'),
            item300=request.form.get('item300'),
            item301=request.form.get('item301'),
            item400=request.form.get('item400'),
            item401=request.form.get('item401'),
            item402=request.form.get('item402'),
            item403=request.form.get('item403'),
            item404=request.form.get('item404'),
            item405=request.form.get('item405'),
            item500=request.form.get('item500'),
            item501=request.form.get('item501'),
            item600=request.form.get('item600'),
            item601=request.form.get('item601'),
            observaciones=observaciones,
            foto=foto_filename
        )
@app.route('/add_km_final/<int:checklist_id>', methods=['POST'])
def add_km_final(checklist_id):
    daily = DailyChecklist.query.get_or_404(checklist_id)
    if daily.km_final is None:
        km_final = request.form.get('km_final')
        if km_final and km_final.isdigit():
            daily.km_final = int(km_final)
            db.session.commit()
            flash('Kilometraje final guardado correctamente.', 'success')
        else:
            flash('Ingrese un valor válido para el kilometraje final.', 'error')
    else:
        flash('El kilometraje final ya fue registrado.', 'info')
    return redirect(request.referrer or url_for('report', submission_id=daily.submission_id))
        db.session.add(daily)
        db.session.commit()
        # Eliminar registros previos de cumplimiento por grupo para este submission
        GroupCompliance.query.filter_by(submission_id=submission.id).delete()
        db.session.commit()
        daily_dict = {col: getattr(daily, col) for col in daily.__table__.columns.keys()}
        # Calcular cumplimiento por grupo para checklist diario
        grupos = {
            'CHECKEO DIARIO': [f'item{i}' for i in range(0, 20)],
            'GENERAL (EQUIPO APAGADO)': [f'item{i}' for i in range(1, 20)],
            'GENERAL (MOTOR ENCENDIDO)': [f'item{100+i}' for i in range(1, 10)],
            'CARGADOR FRONTAL, RETROEXCAVADORA, EXCAVADORA, MONTACARGA, MINICARGADOR Y TRACTOR': [f'item{200+i}' for i in range(1, 7)],
            'RODILLO COMPACTADOR': [f'item{300+i}' for i in range(1, 3)],
            'VOLQUETE': [f'item{400+i}' for i in range(1, 7)],
            'GRÚA': [f'item{500+i}' for i in range(1, 3)],
            'CISTERNA Y UTILITARIO': [f'item{600+i}' for i in range(1, 3)]
        }
        resumen = 'Cumple'
        grupos_no_cumple = []
        for nombre, items in grupos.items():
            estado = calcular_cumplimiento_grupo(daily_dict, items)
            gc = GroupCompliance(submission_id=submission.id, group_name=nombre, compliance_status=estado)
            db.session.add(gc)
            if estado == 'No cumple':
                resumen = 'No cumple'
                grupos_no_cumple.append(nombre)
        db.session.commit()
        return redirect(url_for('tools_check', submission_id=submission.id))
    return render_template(plantilla, submission=submission, company=company, worker=worker, asset=asset)

@app.route('/tools_check/<int:submission_id>', methods=['GET', 'POST'])
def tools_check(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    company = Company.query.get(submission.company_id)
    worker = Worker.query.get(submission.worker_id)
    asset = Asset.query.get(submission.asset_id)
    if request.method == 'POST':
        tools_check = dict(request.form)
        # Guardar observaciones
        observaciones = request.form.get('observaciones', '')
        # Guardar foto si se adjunta
        foto_filename = None
        if 'foto' in request.files and request.files['foto'].filename != '':
            file = request.files['foto']
            if allowed_file(file.filename):
                foto_filename = secure_filename(f"submission_{submission.id}_" + file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename)
                file.save(filepath)
                corregir_orientacion_imagen(filepath)
            else:
                flash('Formato de imagen no permitido.', 'error')
        # Crear registro en ToolsCheck
        def parse_date_field(val):
            if val in (None, '', 'None'):
                return None
            try:
                return datetime.strptime(val, '%Y-%m-%d').date()
            except Exception:
                return None
        tools = ToolsCheck(
            submission_id=submission.id,
            herr_item1=request.form.get('herr_item1'),
            herr_item2=request.form.get('herr_item2'),
            herr_item3=request.form.get('herr_item3'),
            herr_extintor_fecha=parse_date_field(request.form.get('herr_extintor_fecha')),
            herr_item4=request.form.get('herr_item4'),
            herr_item5=request.form.get('herr_item5'),
            herr_item6=request.form.get('herr_item6'),
            herr_item7=request.form.get('herr_item7'),
            herr_item8=request.form.get('herr_item8'),
            kit_panos=request.form.get('kit_panos'),
            kit_pico=request.form.get('kit_pico'),
            kit_lampa=request.form.get('kit_lampa'),
            kit_costales=request.form.get('kit_costales'),
            kit_salchicha=request.form.get('kit_salchicha'),
            kit_bandeja=request.form.get('kit_bandeja'),
            kit_tacos=request.form.get('kit_tacos'),
            kit_trajes=request.form.get('kit_trajes'),
            kit_guantes=request.form.get('kit_guantes'),
            otros_soat=request.form.get('otros_soat'),
            otros_soat_fecha=parse_date_field(request.form.get('otros_soat_fecha')),
            otros_propiedad=request.form.get('otros_propiedad'),
            otros_circulacion=request.form.get('otros_circulacion'),
            otros_licencia=request.form.get('otros_licencia'),
            observaciones=observaciones,
            foto=foto_filename
        )
        db.session.add(tools)
        db.session.commit()
        # Eliminar registros previos de cumplimiento por grupo para este submission
        GroupCompliance.query.filter_by(submission_id=submission.id).delete()
        db.session.commit()
        # Calcular cumplimiento por grupo para herramientas
        grupos = {
            'Herramientas y Equipos de Seguridad': [f'herr_item{i}' for i in range(1, 9)],
            'Chequeo de Kit Antiderrames': ['kit_panos','kit_pico','kit_lampa','kit_costales','kit_salchicha','kit_bandeja','kit_tacos','kit_trajes','kit_guantes'],
            'Otros': ['otros_soat','otros_propiedad','otros_circulacion','otros_licencia']
        }
        tools_dict = {col: getattr(tools, col) for col in tools.__table__.columns.keys()}
        for nombre, items in grupos.items():
            estado = calcular_cumplimiento_grupo(tools_dict, items)
            gc = GroupCompliance(submission_id=submission.id, group_name=nombre, compliance_status=estado)
            db.session.add(gc)
        db.session.commit()
        return redirect(url_for('report', submission_id=submission.id))
    return render_template('tools_check.html', submission=submission, company=company, worker=worker, asset=asset)

# --- Utilidad para corregir orientación de imagen ---
def corregir_orientacion_imagen(filepath):
    try:
        image = Image.open(filepath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
            image.save(filepath)
            image.close()
    except Exception as e:
        pass  # Si falla, no interrumpe el flujo

def get_nc_items_with_description(daily_checklist, tools_check):
    """
    Devuelve dos listas de descripciones para los ítems 'NC' del checklist diario y de herramientas.
    """
    nc_daily = []
    nc_tools = []
    if daily_checklist:
        daily_dict = daily_checklist.to_dict()
        nc_keys = [k for k, v in daily_dict.items() if k.startswith('item') and v == 'NC']
        if nc_keys:
            sql = text(f"SELECT item_label FROM checklist_items WHERE item_key IN ({','.join([':k'+str(i) for i in range(len(nc_keys))])})")
            params = {f'k{i}': key for i, key in enumerate(nc_keys)}
            rows = db.session.execute(sql, params).fetchall()
            nc_daily = [row[0] for row in rows]
    if tools_check:
        tools_dict = tools_check.to_dict()
        nc_keys = [k for k, v in tools_dict.items() if (k.startswith('herr_item') or k.startswith('kit_') or k.startswith('otros_')) and v == 'NC']
        if nc_keys:
            sql = text(f"SELECT item_label FROM tools_check_items WHERE item_key IN ({','.join([':k'+str(i) for i in range(len(nc_keys))])})")
            params = {f'k{i}': key for i, key in enumerate(nc_keys)}
            rows = db.session.execute(sql, params).fetchall()
            nc_tools = [row[0] for row in rows]
    return nc_daily, nc_tools

@app.route('/report/<int:submission_id>')
def report(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    company = Company.query.get(submission.company_id)
    worker = Worker.query.get(submission.worker_id)
    asset = Asset.query.get(submission.asset_id)
    # Validar existencia de datos críticos
    if not all([company, worker, asset]):
        return render_template('error.html', mensaje='Faltan datos para generar el reporte. Verifique que la empresa, trabajador y equipo existan.'), 404
    daily_checklist = DailyChecklist.query.filter_by(submission_id=submission.id).first()
    tools_check = ToolsCheck.query.filter_by(submission_id=submission.id).first()
    group_compliance = GroupCompliance.query.filter_by(submission_id=submission.id).all()
    resumen = 'Cumple'
    grupos_no_cumple = []
    diario_no_cumple = False
    for gc in group_compliance:
        if gc.compliance_status == 'No cumple':
            resumen = 'No cumple'
            grupos_no_cumple.append(gc.group_name)
    if daily_checklist:
        daily_dict = daily_checklist.to_dict()
        for k, v in daily_dict.items():
            if k.startswith('item') and v == 'NC':
                resumen = 'No cumple'
                diario_no_cumple = True
                break
    if tools_check:
        tools_dict = tools_check.to_dict()
        for k, v in tools_dict.items():
            if (k.startswith('herr_item') or k.startswith('kit_') or k.startswith('otros_')) and v == 'NC':
                resumen = 'No cumple'
                break
    nc_daily, nc_tools = get_nc_items_with_description(daily_checklist, tools_check)

    # --- Generar checklist_rows serializable para el PDF ---
    checklist_desc = {
        'item0': 'CHEQUEO EL STICKER SI LLEGA AL KILOMETRAJE DE MANTTO LLEVE AL TALLER',
        'prox_mantto': 'PROX MANTTO',
        'item1': 'CHEQUEE SI LA UNIDAD TIENE ALGÚN ROCE, ABOLLADURA, ETC.',
        'item2': 'VERIFIQUE QUE NO EXISTAN FUGAS DE ACEITE, AGUA, COMBUSTIBLE*',
        'item3': 'PURGAR EL AGUA DEL FILTRO DE PETRÓLEO*',
        'item4': 'REVISE EL NIVEL DE ACEITE DE MOTOR*',
        'item5': 'REVISE EL NIVEL DE ACEITE HIDRÁULICO',
        'item6': 'REVISE EL NIVEL DE LÍQUIDO DE FRENO*',
        'item7': 'REVISE EL NIVEL DE LÍQUIDO DE EMBRAGUE*',
        'item8': 'REVISE EL NIVEL DE AGUA DEL LIMPIAPARABRISAS',
        'item9': 'REVISE CONEXIONES DE BATERÍA Y NIVEL DE ELECTROLITO*',
        'item10': 'REVISE TENSIÓN DE LAS FAJAS DE ALTERNADOR*',
        'item11': 'VERIFIQUE EL AJUSTE DE TUERCAS DE LAS RUEDAS*',
        'item12': 'REVISE ESPEJOS RETROVISORES *',
        'item13': 'CINTURÓN DE SEGURIDAD *',
        'item14': 'COMPROBAR ALARMA DE RETROCESO *',
        'item15': 'COMPROBAR NIVEL DEL REFRIGERANTE',
        'item16': 'TAPA DE TANQUE DE COMBUSTIBLE',
        'item17': 'VERIFIQUE PROFUNDIDAD DE NEUMÁTICOS',
        'item18': 'COMPUERTAS TRASERAS EN CASO DE FURGÓN *',
        'item19': 'CABLE PARA PASAR CORRIENTE DE BATERÍA',
        'item100': 'VERIFIQUE QUE NO EXISTAN FUGAS DE ACEITE, AGUA, COMBUSTIBLE O LIQUIDO DE FRENO QUE MOJE LOS NEUMÁTICOS*',
        'item101': 'REVISE LUCES ( BAJA Y ALTA - RUTA ) *',
        'item102': 'VERIFIQUE FUNCIONAMIENTO NORMAL DEL TABLERO DE INSTRUMENTOS',
        'item103': 'NIVEL DE COMBUSTIBLE MAYOR DE 1/4 DE TANQUE',
        'item104': 'COMPROBAR FUNCIONAMIENTO DE CLAXON *',
        'item105': 'FRENO DE MANO Y PARQUEO *',
        'item106': 'PRESIÓN DE ACEITE DE MOTOR',
        'item107': 'CARGA DE ALTERNADOR',
        'item108': 'TABLERO DE CONTROL',
        'item200': 'NIVEL DE ACEITE DE TRANSMISIÓN Y HIDRÁULICO',
        'item201': 'UÑAS Y CADENA DE LEVANTE',
        'item202': 'BRAZO DE SOPORTE',
        'item203': '---',
        'item204': 'ESTADO DE RUEDA GUÍA Y SPROCKET',
        'item205': 'ESTADO DE CONTROL DE MANDOS ',
        'item300': 'ESTADO DE ROLA',
        'item301': 'LAS GOMAS DE LA ROLA',
        'item400': 'TOLDERA ',
        'item401': 'CINTA REFLECTIVA VISIBLE',
        'item402': 'GANCHOS DE COMPUERTA TRASERA',
        'item403': 'TEMPLADORES DE LA COMPUERTA',
        'item404': 'REVISIÓN DE LA TOLVA (BASE, PINES DE COMPUERTA)',
        'item405': 'FUGAS DE ACEITE DE PISTÓN DE LEVANTE Y TANQUE HIDRÁULICO',
        'item500': 'ACCESORIOS DE LA PLUMA Y PLATAFORMA',
        'item501': 'ACCESORIOS DE IZAJE',
        'item600': 'TANQUE - CONTOMETRO Y PISTOLA SURTIDORA AUTOMÁTICA',
        'item601': 'BOMBA DE AGUA '
    }
    checklist_rows = []
    if daily_checklist:
        daily_dict = daily_checklist.to_dict()
        for key, desc in checklist_desc.items():
            value = daily_dict.get(key)
            if value in ['C', 'NC']:
                checklist_rows.append([desc, value if value is not None else ""])

    # --- Asegurar serializabilidad para JS en template ---
    if checklist_rows is None:
        checklist_rows = []
    _has_obs = False
    _obs = ''
    if daily_checklist:
        daily_dict = daily_checklist.to_dict()
        _has_obs = 'observaciones' in daily_dict and bool(daily_dict['observaciones'])
        _obs = daily_dict.get('observaciones', '')

    return render_template(
        'report.html',
        submission=submission,
        company=company,
        worker=worker,
        asset=asset,
        daily_checklist=daily_checklist,
        tools_check=tools_check,
        created_at=submission.created_at,
        pdf_mode=False,  # Siempre modo navegador
        app_root=os.path.abspath(os.path.dirname(__file__)),
        group_compliance=group_compliance,
        resumen=resumen,
        grupos_no_cumple=grupos_no_cumple,
        nc_daily=nc_daily,
        nc_tools=nc_tools,
        diario_no_cumple=diario_no_cumple,
        checklist_rows=checklist_rows,
        device_info=platform.platform(),
        _has_obs=_has_obs,
        _obs=_obs,
    )

@app.route('/all_reports', methods=['GET', 'POST'])
def all_reports():
    # Obtener filtros desde el formulario o query params
    selected_company = request.args.get('company_id', type=int)
    selected_asset = request.args.get('asset_id', type=int)
    selected_worker = request.args.get('worker_id', type=int)

    submissions_query = Submission.query
    if selected_company:
        submissions_query = submissions_query.filter_by(company_id=selected_company)
    if selected_asset:
        submissions_query = submissions_query.filter_by(asset_id=selected_asset)
    if selected_worker:
        submissions_query = submissions_query.filter_by(worker_id=selected_worker)
    submissions = submissions_query.all()

    # Leer checklist y tools_check desde las nuevas tablas relacionales para cada submission
    for s in submissions:
        s.daily_checklist = DailyChecklist.query.filter_by(submission_id=s.id).first()
        s.tools_check = ToolsCheck.query.filter_by(submission_id=s.id).first()

    companies = {c.id: c.name for c in Company.query.all()}
    workers = {w.id: w.name for w in Worker.query.all()}
    assets = {a.id: a for a in Asset.query.all()}
    for s in submissions:
        s.asset = assets.get(s.asset_id)
        # Obtener cumplimiento por grupo y resumen general
        group_compliance = GroupCompliance.query.filter_by(submission_id=s.id).all()
        s.group_compliance = group_compliance
        resumen = 'Cumple'
        for gc in group_compliance:
            if gc.compliance_status == 'No cumple':
                resumen = 'No cumple'
                break
        s.resumen = resumen
        s.grupos_no_cumple = [gc.group_name for gc in group_compliance if gc.compliance_status == 'No cumple']
    # Listas para los selects
    all_companies = Company.query.all()
    all_assets = Asset.query.all()
    all_workers = Worker.query.all()
    return render_template('all_reports.html', submissions=submissions, companies=companies, workers=workers, all_companies=all_companies, all_assets=all_assets, all_workers=all_workers, selected_company=selected_company, selected_asset=selected_asset, selected_worker=selected_worker)

@app.route('/admin/companies', methods=['GET', 'POST'])
def admin_companies():
    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('El nombre de la empresa es obligatorio.', 'error')
        else:
            existing = Company.query.filter_by(name=name).first()
            if existing:
                flash('Esta empresa ya se encuentra registrada.', 'error')
            else:
                company = Company(name=name)
                db.session.add(company)
                db.session.commit()
                flash('Empresa agregada exitosamente.', 'success')
        return redirect(url_for('admin_companies'))
    companies = Company.query.all()
    return render_template('admin_companies.html', companies=companies)

@app.route('/admin/workers', methods=['GET', 'POST'])
def admin_workers():
    companies = Company.query.all()
    selected_company = request.args.get('company_id', type=int)
    search_query = request.args.get('search', default='', type=str)
    if request.method == 'POST':
        name = request.form['name']
        company_id = request.form['company_id']
        if not name or not company_id:
            flash('Todos los campos son obligatorios.', 'error')
        else:
            existing = Worker.query.filter_by(name=name, company_id=company_id).first()
            if existing:
                flash('Este trabajador ya se encuentra registrado en esta empresa.', 'error')
            else:
                worker = Worker(name=name, company_id=company_id)
                db.session.add(worker)
                db.session.commit()
                flash('Trabajador agregado exitosamente.', 'success')
        return redirect(url_for('admin_workers'))
    workers_query = Worker.query
    if selected_company:
        workers_query = workers_query.filter_by(company_id=selected_company)
    if search_query:
        workers_query = workers_query.filter(Worker.name.ilike(f"%{search_query}%"))
    workers = workers_query.all()
    return render_template('admin_workers.html', workers=workers, companies=companies, selected_company=selected_company, search_query=search_query)

@app.route('/admin/assets', methods=['GET', 'POST'])
def admin_assets():
    companies = Company.query.all()
    selected_company = request.args.get('company_id', type=int)
    selected_type = request.args.get('type', default=None, type=str)
    if request.method == 'POST':
        type_ = request.form['type']
        code = request.form['code']
        company_id = request.form['company_id']
        if not type_ or not code or not company_id:
            flash('Todos los campos son obligatorios.', 'error')
        else:
            existing = Asset.query.filter_by(code=code).first()
            if existing:
                flash('Ya existe un equipo con esa placa/código.', 'error')
            else:
                asset = Asset(type=type_, code=code, company_id=company_id)
                db.session.add(asset)
                db.session.commit()
                flash('Equipo agregado exitosamente.', 'success')
        return redirect(url_for('admin_assets'))
    assets_query = Asset.query
    if selected_company:
        assets_query = assets_query.filter_by(company_id=selected_company)
    if selected_type:
        assets_query = assets_query.filter(Asset.type.ilike(f"%{selected_type}%"))
    assets = assets_query.all()
    # Obtener tipos únicos para el filtro, dependientes de la empresa seleccionada
    type_query = Asset.query
    if selected_company:
        type_query = type_query.filter_by(company_id=selected_company)
    all_types = sorted({a.type for a in type_query.distinct(Asset.type)})
    return render_template('admin_assets.html', assets=assets, companies=companies, selected_company=selected_company, selected_type=selected_type, all_types=all_types)

@app.route('/admin/companies/edit/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('El nombre de la empresa es obligatorio.', 'error')
        else:
            company.name = name
            db.session.commit()
            flash('Empresa editada exitosamente.', 'success')
            return redirect(url_for('admin_companies'))
    return render_template('admin_companies.html', companies=Company.query.all(), edit_company=company)

@app.route('/admin/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash('Empresa eliminada exitosamente.', 'success')
    return redirect(url_for('admin_companies'))

@app.route('/admin/workers/edit/<int:worker_id>', methods=['GET', 'POST'])
def edit_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    companies = Company.query.all()
    if request.method == 'POST':
        name = request.form['name']
        company_id = request.form['company_id']
        if not name or not company_id:
            flash('Todos los campos son obligatorios.', 'error')
        else:
            worker.name = name
            worker.company_id = company_id
            db.session.commit()
            flash('Trabajador editado exitosamente.', 'success')
            return redirect(url_for('admin_workers'))
    return render_template('admin_workers.html', workers=Worker.query.all(), companies=companies, edit_worker=worker)

@app.route('/admin/workers/delete/<int:worker_id>', methods=['POST'])
def delete_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    db.session.delete(worker)
    db.session.commit()
    flash('Trabajador eliminado exitosamente.', 'success')
    return redirect(url_for('admin_workers'))

@app.route('/admin/assets/edit/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    companies = Company.query.all()
    if request.method == 'POST':
        type_ = request.form['type']
        code = request.form['code']
        company_id = request.form['company_id']
        if not type_ or not code or not company_id:
            flash('Todos los campos son obligatorios.', 'error')
        else:
            asset.type = type_
            asset.code = code
            asset.company_id = company_id
            db.session.commit()
            flash('Equipo editado exitosamente.', 'success')
            return redirect(url_for('admin_assets'))
    return render_template('admin_assets.html', assets=Asset.query.all(), companies=companies, edit_asset=asset)

@app.route('/admin/assets/delete/<int:asset_id>', methods=['POST'])
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash('Equipo eliminado exitosamente.', 'success')
    return redirect(url_for('admin_assets'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search_workers', methods=['POST'])
def search_workers():
    data = request.json
    company_id = data.get('company_id')
    query = data.get('query', '')
    workers = Worker.query.filter(Worker.company_id == company_id, Worker.name.ilike(f"%{query}%")).all()
    worker_list = [{'id': w.id, 'name': w.name} for w in workers]
    return {"workers": worker_list}

# MIGRACIÓN DE DATOS DESDE CAMPOS JSON A TABLAS RELACIONALES
@app.cli.command('migrar_checklists')
def migrar_checklists():
    """
    Migrar datos de checklist_data y tools_check_data de Submission a las tablas DailyChecklist y ToolsCheck.
    """
    from sqlalchemy.exc import IntegrityError
    total = 0
    migrados = 0
    for sub in Submission.query.all():
        total += 1
        # Migrar checklist diario
        if sub.checklist_data:
            try:
                data = json.loads(sub.checklist_data)
                if not DailyChecklist.query.filter_by(submission_id=sub.id).first():
                    daily = DailyChecklist(submission_id=sub.id)
                    for col in DailyChecklist.__table__.columns.keys():
                        if col in data:
                            setattr(daily, col, data[col])
                    # Observaciones y foto
                    if 'observaciones' in data:
                        daily.observaciones = data['observaciones']
                    if 'foto' in data:
                        daily.foto = data['foto']
                    db.session.add(daily)
                    migrados += 1
            except Exception as e:
                print(f"Error migrando checklist diario para submission {sub.id}: {e}")
        # Migrar tools_check
        if sub.tools_check_data:
            try:
                data = json.loads(sub.tools_check_data)
                if not ToolsCheck.query.filter_by(submission_id=sub.id).first():
                    tools = ToolsCheck(submission_id=sub.id)
                    for col in ToolsCheck.__table__.columns.keys():
                        if col in data:
                            setattr(tools, col, data[col])
                    if 'observaciones' in data:
                        tools.observaciones = data['observaciones']
                    if 'foto' in data:
                        tools.foto = data['foto']
                    db.session.add(tools)
                    migrados += 1
            except Exception as e:
                print(f"Error migrando tools_check para submission {sub.id}: {e}")
    try:
        db.session.commit()
        print(f"Migración completada. {migrados} registros migrados de {total} submissions.")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error de integridad en la migración: {e}")

@app.route('/preview_report')
def preview_report():
    # Renderiza la plantilla de vista previa con datos de ejemplo
    return render_template('preview_report.html')

if __name__ == '__main__':
    try:
        test_mysql_connector()
        with app.app_context():
            db.create_all()
        app.run(debug=True, port=8080)
    except Exception as e:
        import traceback
        print('--- APP STARTUP ERROR ---')
        print(e)
        traceback.print_exc()
        raise
