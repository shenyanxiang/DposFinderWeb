from flask import Flask, jsonify, request, current_app, send_from_directory, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from utils import *
from datetime import datetime
from threading import Thread
import time
import json
import psycopg2
import subprocess

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + \
    os.path.join(app.root_path, 'jobs.db') + '?check_same_thread=False'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

CORS(app, resources={r'/*': {'origins': '*'}})

class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), index=True, unique=True)
    task = db.Column(db.String(10))
    ip = db.Column(db.String(50))
    num_sequence = db.Column(db.Integer)
    status = db.Column(db.String(30))
    email = db.Column(db.String(30))
    submit_time = db.Column(db.DateTime())
    
    def __repr__(self) -> str:
        return "<Job %s>" % self.job_id
    
    @property
    def serialize(self):
        return {
            #  'id': self.id,
           'job_id': self.job_id,
           'ip': self.ip,
           'task': self.task,
           'num_sequence': self.num_sequence,
           'status': self.status,
           'email': self.email,
           'submit_time': dump_datetime(self.submit_time)
       }
    
def get_queue_status():
    filtered_jobs = Jobs.query.filter((Jobs.status == 'Waiting in a queue') | (Jobs.status == 'Running')).all()
    return len(filtered_jobs) <= 1

def run_protein_prediction(app, id, job_dir, pred_serotype, top_k, plot_attn):
    with app.app_context():
        try:
            Jobs.query.get(id).status = 'Waiting in a queue'
            db.session.commit()
            while not get_queue_status():
                time.sleep(10)
            Jobs.query.get(id).status = 'Running'
            db.session.commit()
            cmd = f"/public/yxshen/.conda/envs/DposFinder/bin/python DposFinder/protein_predict.py --fasta_path {job_dir} --no_cuda {'--serotype' if pred_serotype == 'true' else ''} --top_k {top_k} {'--attn' if plot_attn == 'true' else ''}"

            subprocess.run(cmd, shell=True, check=True)

            Jobs.query.get(id).status = 'Finished'
            db.session.commit()

        except subprocess.CalledProcessError as e:
            Jobs.query.get(id).status = 'Error'
            db.session.commit()
            with open(os.path.join(job_dir, 'error.log'), 'w') as f:
                f.write(str(e))

def run_genome_prediction(app, id, job_dir, file_type, pred_serotype, top_k, plot_attn):
    with app.app_context():
        try:
            Jobs.query.get(id).status = 'Waiting in a queue'
            db.session.commit()
            while not get_queue_status():
                time.sleep(10)
            Jobs.query.get(id).status = 'Running'
            db.session.commit()
            cmd = f"/public/yxshen/.conda/envs/DposFinder/bin/python DposFinder/genome_predict.py --fasta_path {job_dir} --file_type {file_type} --no_cuda {'--serotype' if pred_serotype == 'true' else ''} --top_k {top_k} {'--attn' if plot_attn == 'true' else ''}"

            subprocess.run(cmd, shell=True, check=True)

            Jobs.query.get(id).status = 'Finished'
            db.session.commit()

        except subprocess.CalledProcessError as e:
            Jobs.query.get(id).status = 'Error'
            db.session.commit()
            with open(os.path.join(job_dir, 'error.log'), 'w') as f:
                f.write(str(e))  

def connect_to_db():
    conn = psycopg2.connect(database="DposDB", user=os.environ.get('POSTGRESQL_USER'), password=os.environ.get('POSTGRESQL_PASSWD'), host="localhost", port="5432")
    return conn

@app.route('/test', methods=['GET'])
def test():
    return jsonify(message="test", status=200)

@app.route('/api/download/<path:filename>', methods=['GET'])
def download(filename):
    return send_from_directory(directory='./jobs', path=filename)

@app.route('/api/analysis/protein', methods=['GET', 'POST'])
def analysis_protein():
    input_method = request.form.get('inputMethod')
    plot_attn = request.form.get('plotAttn')
    pred_serotype = request.form.get('predSerotype')
    top_k = request.form.get('topK')
    if not request.headers.getlist("X-Forwarded-For"):
        remote_ip = request.remote_addr
    else:
        remote_ip = request.headers.getlist("X-Forwarded-For")[0]
    
    job_id = request.form['job_id']
    job_dir = os.path.join('./jobs/', job_id)
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)
    sequence = os.path.join(job_dir, 'sequence.fasta')

    if input_method == 'file':
        with open(sequence, 'wb') as f:
            f.write(request.files['file'].read())
    elif input_method == 'text':
        with open(sequence, 'w') as f:
            f.write(request.form['inputprotein'])

    # check input file "sequence.fasta"
    if check_protein_fasta_file(sequence):
        num_sequence = len(
            [1 for line in open(sequence, 'r') if line.startswith(">")])
        job = Jobs(job_id=job_id, ip=remote_ip, task='protein-level depolymerase prediction', num_sequence=num_sequence, status='Preprocessing', email='', submit_time=datetime.now())
        db.session.add(job)
        db.session.commit()
        thread = Thread(target=run_protein_prediction, kwargs={'app': app, 'id': job.id, 'job_dir': job_dir, 'pred_serotype': pred_serotype, 'top_k': top_k, 'plot_attn': plot_attn})
        thread.start()
        return jsonify(message=f"Job {job.job_id} is successfully submitted", category="success", status=200)
    else:
        os.system(f'rm -r ./jobs/{job_id}')
        return jsonify(message=f"Invalid Input! Only FASTA Format of protein sequence is supported.", category="error", status=404)

    
    
@app.route('/api/analysis/genome', methods=['POST'])
def analysis_genome():
    input_method = request.form.get('inputMethod')
    plot_attn = request.form.get('plotAttn')
    pred_serotype = request.form.get('predSerotype')
    top_k = request.form.get('topK')
    if not request.headers.getlist("X-Forwarded-For"):
        remote_ip = request.remote_addr
    else:
        remote_ip = request.headers.getlist("X-Forwarded-For")[0]

    job_id = request.form['job_id']
    job_dir = os.path.join('./jobs/', job_id)
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)

    if input_method == 'file':
        file_content = request.files['file'].read()
        check_char = file_content.decode('utf-8')[0]
        if file_content.decode('utf-8')[0] != '>':
            file_type = 'gbk'
            with open(os.path.join(job_dir, 'sequence.gbk'), 'wb') as f:
                f.write(file_content)
            os.system(f"/public/yxshen/.conda/envs/DposFinder/bin/python ./gbk2faa.py {job_dir}/sequence.gbk")
        else:
            file_type = 'fasta'
            with open(os.path.join(job_dir, 'sequence.fasta'), 'wb') as f:
                f.write(file_content)
    elif input_method == 'text':
        with open(os.path.join(job_dir, 'sequence.fasta'), 'w') as f:
            file_content = request.form['inputgenome']
            f.write(file_content)
            file_type = 'fasta'
            check_char = file_content[0]

    sequence = os.path.join(job_dir, 'sequence.fasta')
            
    # check input file "sequence.fasta"
    if (check_char == '>' and check_genome_fasta_file(sequence)) or (check_char != '>' and check_protein_fasta_file(sequence)):
        num_sequence = len(
            [1 for line in open(sequence, 'r') if line.startswith(">")])
        job = Jobs(job_id=job_id, ip=remote_ip, task='genome-level depolymerase prediction', num_sequence=num_sequence, status='Preprocessing', email='', submit_time=datetime.now())
        db.session.add(job)
        db.session.commit()
        thread = Thread(target=run_genome_prediction, kwargs={'app': app, 'id': job.id, 'job_dir': job_dir, 'file_type': file_type, 'pred_serotype': pred_serotype, 'top_k': top_k, 'plot_attn': plot_attn})
        thread.start()
        return jsonify(message=f"Job {job.job_id} is successfully submitted", category="success", status=200)
    else:
        os.system(f'rm -r ./jobs/{job_id}')
        return jsonify(message=f"Invalid Input! Only FASTA or GenBank Format of genome sequence is supported.", category="error", status=404)
    
@app.route('/api/result/<job_id>', methods=['GET'])
def get_results(job_id):
    job = Jobs.query.filter_by(job_id=job_id).first()
    
    if job is not None:
        results = job.serialize
        current_time=datetime.now()
        results['current_time'] = dump_datetime(current_time)
        job_dir = os.path.join('./jobs', job_id)
        if job.status == 'Error':
            return jsonify(message=f"An error occured in Job: ID {job_id}. Please check the input once again", status=404)
            
        elif job.status == 'Finished': 
            if job.task == 'protein-level depolymerase prediction':
                data = parse_protein_prediction(job_dir)
                results['rows'] = json.loads(data)
            elif job.task == 'genome-level depolymerase prediction':
                data = parse_genome_prediction(job_dir)
                results['rows'] = json.loads(data)
                
            return jsonify(message=f"Job: ID {job_id} is Finished.",
                        category="success",
                        data=results,
                        status=200)
        else:
            return jsonify(message=f"Job: ID {job_id} is {job.status}.",
                        category="success",
                        data=results,
                        status=200)
    
    else:
        return jsonify(message=f"Job ID:{job_id} is not existed.",
                       status=404)
    
@app.route('/api/result/<job_id>/<protein_id>', methods=['GET'])
def get_protein_information(job_id, protein_id):
    job = Jobs.query.filter_by(job_id=job_id).first()
    if job is not None:
        results = job.serialize
        protein_dir = os.path.join('./jobs', job_id, 'outputs', protein_id)
        information_file = os.path.join(protein_dir, 'information.tsv')
        df = pd.read_csv(information_file, sep='\t')
        results['rows'] = json.loads(df.to_json(orient='records'))
        attn_file = os.path.join(protein_dir, 'attn', 'img', f'{protein_id}_attn.png')
        results['show_attn'] = os.path.exists(attn_file)
        serotype_file = os.path.join(protein_dir, 'predicted_serotype.csv')
        results['show_serotype'] = os.path.exists(serotype_file)
        return jsonify(message=f"Get {protein_id} information",
                        category="success",
                        data=results,
                        status=200)
    else:
        return jsonify(message=f"Job ID:{job_id} is not existed.",
                       status=404)

@app.route('/api/result/<job_id>/<protein_id>/attn', methods=['GET'])
def get_attn_png(job_id, protein_id):
    job = Jobs.query.filter_by(job_id=job_id).first()
    if job is not None:
        protein_dir = os.path.join('./jobs', job_id, 'outputs', protein_id)
        attn_file = os.path.join(protein_dir, 'attn', 'img', f'{protein_id}_attn.png')
        return send_file(attn_file, mimetype='image/jpeg')
    else:
        return jsonify(message=f"Job ID:{job_id} is not existed.",
                       status=404)
    
@app.route('/api/result/<job_id>/<protein_id>/serotype', methods=['GET'])
def get_serotype_result(job_id, protein_id):
    job = Jobs.query.filter_by(job_id=job_id).first()
    if job is not None:
        protein_dir = os.path.join('./jobs', job_id, 'outputs', protein_id)
        serotype_result = parse_serotype_result(protein_dir)
        results = job.serialize
        results['rows'] = json.loads(serotype_result)
        return jsonify(message=f"Get {protein_id} serotype result",
                        category="success",
                        data=results,
                        status=200)
    else:
        return jsonify(message=f"Job ID:{job_id} is not existed.",
                       status=404)

@app.route('/api/result/<job_id>/<protein_id>/blast', methods=['GET'])
def get_blast_result(job_id, protein_id):
    job = Jobs.query.filter_by(job_id=job_id).first()
    if job is not None:
        protein_dir = os.path.join('./jobs', job_id, 'outputs', protein_id)
        blast_result = parse_blast_result(protein_dir)
        results = job.serialize
        results['rows'] = json.loads(blast_result)
        return jsonify(message=f"Get {protein_id} blast result",
                        category="success",
                        data=results,
                        status=200)
    else:
        return jsonify(message=f"Job ID:{job_id} is not existed.",
                       status=404)

@app.route('/api/ex_dpos/page/list/<int:pageSize>/<int:currentPage>', methods=['GET'])
def getDposList(pageSize, currentPage):
    name = request.args.get('name')
    sort = request.args.get('sort')
    order = request.args.get('order')
    experimental = request.args.get('experimental')

    conn = connect_to_db()
    cursor = conn.cursor()

    query = f"""SELECT * FROM "Dpos_info".published_dpos WHERE LOWER(dpos_accession) LIKE LOWER('%{name}%')"""
    if experimental:
        query += f""" AND experimental = '{experimental}'"""
    if sort and order:
        query += f""" ORDER BY {sort} {order}"""
    cursor.execute(query)
    rows = cursor.fetchall()
    keys = ['id', 'phage', 'dpos_accession', 'experimental', 'reference']
    filtered_data = [{key: row[i] for i, key in enumerate(keys)} for row in rows]

    start_index = (currentPage - 1) * pageSize
    end_index = start_index + pageSize
    paged_data = filtered_data[start_index:end_index]

    conn = connect_to_db()
    cursor = conn.cursor()

    return jsonify({
        'result': paged_data,
        'page': {
            'total': len(filtered_data)
        }
    })

@app.route('/api/ex_dpos/all', methods=['GET'])
def getAllDpos():
    # 返回所有的 depolymerase 数据
    conn = connect_to_db()
    cursor = conn.cursor()

    query = f"""SELECT * FROM "Dpos_info".published_dpos"""

    cursor.execute(query)
    rows = cursor.fetchall()
    keys = ['id', 'phage', 'dpos_accession', 'experimental', 'reference']
    filtered_data = [{key: row[i] for i, key in enumerate(keys)} for row in rows]

    return jsonify(filtered_data)

@app.route('/api/pred_dpos/page/list/<int:pageSize>/<int:currentPage>', methods=['GET'])
def getPredDposList(pageSize, currentPage):
    name = request.args.get('name')
    sort = request.args.get('sort')
    order = request.args.get('order')
    lifestyle = request.args.get('life_style')

    conn = connect_to_db()
    cursor = conn.cursor()

    query = f"""SELECT * FROM "Dpos_info".predicted_dpos WHERE LOWER(host) LIKE LOWER('%{name}%')"""
    if lifestyle:
        query += f""" AND experimental = '{lifestyle}'"""
    if sort and order:
        query += f""" ORDER BY {sort} {order}"""
    cursor.execute(query)
    rows = cursor.fetchall()
    keys = ['id', 'phage_id', 'host', 'life_style', 'locus_tag', 'coordinates', 'prediction_score', 'length']
    filtered_data = [{key: row[i] for i, key in enumerate(keys)} for row in rows]

    start_index = (currentPage - 1) * pageSize
    end_index = start_index + pageSize
    paged_data = filtered_data[start_index:end_index]

    conn = connect_to_db()
    cursor = conn.cursor()

    return jsonify({
        'result': paged_data,
        'page': {
            'total': len(filtered_data)
        }
    })

@app.route('/api/pred_dpos/all', methods=['GET'])
def getAllPredDpos():
    # 返回所有的 depolymerase 数据
    conn = connect_to_db()
    cursor = conn.cursor()

    query = f"""SELECT * FROM "Dpos_info".predicted_dpos"""

    cursor.execute(query)
    rows = cursor.fetchall()
    keys = ['id', 'phage_id', 'host', 'life_style', 'locus_tag', 'coordinates', 'prediction_score', 'length']
    filtered_data = [{key: row[i] for i, key in enumerate(keys)} for row in rows]

    return jsonify(filtered_data)

@app.route('/api/protein/<protein_id>', methods=['GET'])
def get_protein_info(protein_id):
    protein_dir = os.path.join('./dpos_db/valid_dpos', protein_id)
    information_file = os.path.join(protein_dir, 'information.tsv')
    df = pd.read_csv(information_file, sep='\t')
    results = {}
    results['rows'] = json.loads(df.to_json(orient='records'))
    results['attn_url'] = f'/public/yxshen/DposFinderWeb/server/dpos_db/valid_dpos/{protein_id}/attn/img/{protein_id}.png'
    return jsonify(message=f"Get {protein_id} information",
                    category="success",
                    data=results,
                    status=200)
@app.route('/api/protein/<protein_id>/attn', methods=['GET'])
def get_attn(protein_id):
    protein_dir = os.path.join('./dpos_db/valid_dpos', protein_id)
    attn_file = os.path.join(protein_dir, 'attn', 'img', f'{protein_id}.png')
    return send_file(attn_file, mimetype='image/jpeg')
@app.route('/api/protein/<protein_id>/disorder', methods=['GET'])
def get_disorder(protein_id):
    disorder_file_path = os.path.join('./dpos_db/valid_dpos', protein_id, 'disorders.txt')
    results = read_disorder(disorder_file_path)
    return jsonify(message="",
                   category="success",
                   data=json.loads(results),
                   status=200)
@app.route('/api/protein/<protein_id>/context', methods=['GET'])
def get_context_png(protein_id):
    protein_dir = os.path.join('./dpos_db/valid_dpos', protein_id)
    context_file = os.path.join(protein_dir, 'context.png')
    return send_file(context_file, mimetype='image/jpeg')
@app.route('/api/protein/<protein_id>/context_table', methods=['GET'])
def get_context_table(protein_id):
    protein_dir = os.path.join('./dpos_db/valid_dpos', protein_id)
    context_table = parse_context_table(protein_dir)
    return jsonify(message="",
                   category="success",
                   data=json.loads(context_table),
                   status=200)

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run()