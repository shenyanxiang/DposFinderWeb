from flask import Flask, jsonify, request, current_app
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from utils import *
from datetime import datetime
from threading import Thread

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

def run_genome_prediction(app, id, job_dir, save_attn):
    with app.app_context():
        try:
        #     os.system(
        #         f'/public/software/miniconda3/envs/TXSEfinder/bin/macsyfinder --db-type ordered_replicon --sequence-db {fasta} --hmmer /public/software/miniconda3/envs/TXSEfinder/bin/hmmsearch --models-dir /public/Server/www/cgi-bin/TXSEDB/data/ --models TXSS T1SS T2SS T3SS T4SS_typeI T4SS_typeT T6SSi T6SSii T6SSiii -o {job_dir}/TXSS -w 8') # remove T4SS typeC, typeG
    
        #     systems = read_system_names(f'{job_dir}/TXSS/best_solution_summary.tsv')
            
        #     if len(systems) > 0:
        #         Jobs.query.get(id).status = 'Waiting for prediction'
        #         db.session.commit()
        #         while not get_queue_status():
        #             time.sleep(10)
        #         Jobs.query.get(id).status = 'Predicting secreted proteins'
        #         db.session.commit()
                
        #         if save_attn:
        #             cmd = f'/public/software/miniconda3/envs/TXSEfinder/bin/python /public/Server/www/cgi-bin/TXSEDB/predictv2.py --fasta_path {fasta} --model_location /public/Server/www/cgi-bin/TXSEDB/data/checkpoint.pt --secretion_systems {" ".join(systems)} --out_dir {job_dir} --save_attn'
        #         else:
        #             cmd = f'/public/software/miniconda3/envs/TXSEfinder/bin/python /public/Server/www/cgi-bin/TXSEDB/predictv2.py --fasta_path {fasta} --model_location /public/Server/www/cgi-bin/TXSEDB/data/checkpoint.pt --secretion_systems {" ".join(systems)} --out_dir {job_dir}'
                    
        #         print(cmd)
        #         os.system(cmd)
                
        #         # run blastp
        #         os.system(f'/public/software/miniconda3/envs/TXSEfinder/bin/python /public/Server/www/cgi-bin/TXSEDB/run_blastp.py {job_dir}')

        #         if save_attn:
        #             Jobs.query.get(id).status = 'Plotting sequence attention'
        #             db.session.commit()
        #             os.system(f'/public/software/miniconda3/envs/TXSEfinder/bin/python /public/Server/www/cgi-bin/TXSEDB/plot_attention.py {job_dir}')

            Jobs.query.get(id).status = 'Done'
            db.session.commit()

        
        except Exception as e:
            Jobs.query.get(id).status = 'Error'
            db.session.commit()
            with open(os.path.join(job_dir, 'error.log'), 'w') as f:
                f.write(str(e))  

@app.route('/open', methods=['GET'])
def open_door():
    return jsonify(u'Hello World!')

last_sequence = 'imhere'
@app.route('/api/analysis/protein', methods=['GET', 'POST'])
def analysis_protein():
    global last_sequence
    response_object = {'status': 'success'}
    if request.method == 'POST':
        input_method = request.form.get('inputMethod') or request.json.get('inputMethod')
        if input_method == 'file':
            file = request.files['file']
            return jsonify(response_object)
        else:
            post_data = request.get_json()
            last_sequence = post_data.get('job_id')
            return jsonify(response_object)
    else:
        response_object['sequence'] = last_sequence
        return jsonify(response_object)
    
@app.route('/api/analysis/genome', methods=['GET', 'POST'])
def analysis_genome():
    global last_sequence
    response_object = {'status': 'success'}
    if request.method == 'POST':
        input_method = request.form.get('inputMethod')
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
                f.write(request.form['inputGenome'])
                
        # check input file "sequence.fasta"
        if check_genome_fasta_file(sequence):
            num_sequence = len(
                [1 for line in open(sequence) if line.startswith(">")])
            job = Jobs(job_id=job_id, ip=remote_ip, task='genome-level depolymerase prediction', num_sequence=num_sequence, status='Preprocessing', email='', submit_time=datetime.utcnow())
            db.session.add(job)
            db.session.commit()
            thread = Thread(target=run_genome_prediction, kwargs={'app': app, 'id': job.id, 'job_dir': job_dir, 'save_attn': False})
            thread.start()
            return jsonify(message=f"Job {job.job_id} is successfully submitted", category="success", status=200)
        else:
            os.system(f'rm -r ./jobs/{job_id}')
            return jsonify(message=f"Invalid Input! Only FASTA Format of genome sequence is supported.")
    else:
        response_object['sequence'] = last_sequence
        return jsonify(response_object)
    
@app.route('/api/result/<job_id>', methods=['GET'])
def get_results(job_id):
    job = Jobs.query.filter_by(job_id=job_id).first()
    
    if job is not None:
        results = job.serialize
        current_time=datetime.utcnow()
        results['current_time'] = dump_datetime(current_time)
        job_dir = os.path.join('/public/Server/www/cgi-bin/TXSEDB/jobs', job_id)
        if job.status == 'Error':
            return jsonify(message=f"An error occured in Job: ID {job_id}. Please check the input once again", status=404)
            
        elif job.status == 'Done': 
            # if job.task == 'sequence':
            #     data = parse_predictions(job_dir)
            #     results['rows'] = json.loads(data)
            # elif job.task == 'genome':
            #     system_list = read_system_names(f'{job_dir}/TXSS/best_solution_summary.tsv')
            #     results['system_list'] = system_list
            #     if len(system_list) > 0:
            #         txcp, txss = read_txcp_results(f'{job_dir}/TXSS/best_solution.tsv', f'{job_dir}/sequence.fasta')
            #         with open(f'{job_dir}/sequence.fa.fai') as f:
            #             results['accession'] = f.read().split()[0]    
            #         results['txss'] = txss
            #         results['txcp'] = txcp
            #         results['rows'] = json.loads(parse_genome_predictions(job_dir, f'{job_dir}/sequence.fasta'))    
            # elif job.task == "blastp":
            #     data, counts = parse_blastp(job_dir)
            #     results['rows'] = json.loads(data)
            #     results['counts'] = counts
                
            # if os.path.exists(os.path.join(job_dir, 'attn')):
            #     results['attn'] = True
                
            return jsonify(message=f"Job: ID {job_id} is Done.",
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

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run()