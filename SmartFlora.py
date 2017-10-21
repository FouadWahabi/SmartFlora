import json
import time

import collections
from boto3.session import Session

import requests
from flask import (
    render_template, Flask
)

global session
global machinelearning
global model
global prediction_endpoint
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

sched = BackgroundScheduler()

obs_fields = [
    u'datetime_utc',
    u't_conds',
    u't_dewptm',
    u't_fog',
    u't_hail',
    u't_heatindexm',
    u't_hum',
    u't_precipm',
    u't_pressurem',
    u't_rain',
    u't_snow',
    u't_tempm',
    u't_thunder',
    u't_tornado',
    u't_vism',
    u't_wdird',
    u't_wdire',
    u't_wgustm',
    u't_windchillm',
    u't_wspdm']

obs_fields_mapper = [
    u'local_epoch',
    u'weather',
    u'dewpoint_c',
    False,
    False,
    None,
    u'relative_humidity',  # convert percent to number
    None,
    u'pressure_mb',
    False,
    False,
    u'temp_c',
    False,
    False,
    u'visibility_km',
    u'wind_degrees',
    u'wind_dir',
    None,
    None,
    u'dewpoint_c'
]

predictions = collections.OrderedDict()


@sched.scheduled_job('interval', minutes=1)
def getCurrentWeather():
    res = requests.get('http://api.wunderground.com/api/daf89dfd5f4e63c6/conditions/q/Tunisia/Tunis.json')
    res_data = res.json()
    res_data = res_data['current_observation']
    data = {}
    for i in xrange(len(obs_fields)):
        if obs_fields[i] not in data:
            if i == 0:
                data[obs_fields[i]] = time.strftime('%Y%m%d-%H:%M',
                                                    time.localtime(int(res_data[obs_fields_mapper[i]])))
            elif obs_fields_mapper[i] is None:
                data[obs_fields[i]] = ''
            elif not obs_fields_mapper[i]:
                data[obs_fields[i]] = '0'
            else:
                data[obs_fields[i]] = str(res_data[obs_fields_mapper[i]]).strip('%')
    print data
    response = machinelearning.predict(MLModelId=model_id, Record=data, PredictEndpoint=prediction_endpoint)
    if data["datetime_utc"] not in predictions:
        predictions[data["datetime_utc"]] = ''

    if len(predictions) >= 10:
        predictions.pop(next(iter(predictions)))
    predictions[data["datetime_utc"]] = response["Prediction"]["predictedValue"]


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/api/water')
def water():
    return json.dumps(predictions)


if __name__ == '__main__':
    session = Session(aws_access_key_id="AKIAJ5RNU4IHID63UBXQ",
                      aws_secret_access_key="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")
    machinelearning = session.client('machinelearning', region_name='us-east-1')
    model_id = 'ml-wSihsNcr0sM'
    model = machinelearning.get_ml_model(MLModelId=model_id)
    prediction_endpoint = model.get('EndpointInfo').get('EndpointUrl')

    getCurrentWeather()
    sched.start()
    app.run(host='0.0.0.0', port=9000)
