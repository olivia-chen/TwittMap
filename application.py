from flask import Flask,redirect
from flask import render_template
from pyes import *
from flask import request
import json
import requests
from wsgiref.simple_server import make_server
import flask_googlemaps
from flask import jsonify


# Address of the elasticsearch host
elasticsearchURL = 'https://search-twittmap-77ta2y45lfunfg4hhdxaezl524.us-west-2.es.amazonaws.com'
application = Flask(__name__)
application.config['GOOGLEMAPS_KEY']="AIzaSyC403JgsSdPSph8zoqbPs9DMzkLosIRD6o"
flask_googlemaps.GoogleMaps(application)

res_count = requests.get(elasticsearchURL + '/test-index/test-type/_count')
count_json = json.loads(res_count.text.replace("\\", r"\\"))

@application.route('/location')
def getlocation():
    a = request.args.get('lat',10,type=float)
    b = request.args.get('lng',10,type=float)
    results = getMessageByLocation((a,b))
    return results
def getMessageByLocation(location):
    conn = ES(['https://search-twittmap-77ta2y45lfunfg4hhdxaezl524.us-west-2.es.amazonaws.com'])
    latitute,longitute=location
    print("LAT!!!!!",latitute,"Long",longitute)
    if dd_select=='':
        print ("noo########################################")
        q=MatchAllQuery()
    else:
        q=TermQuery("message",dd_select)
    f=GeoDistanceFilter("location",{"lat":latitute,"lon":longitute},'100mi')
    #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",dd_select)
    s=FilteredQuery(q,f)

    results=conn.search(query=s)
    
    ret = {'res':[]}
    try:
        for result in results:
            ret['res'].append([result['location']['lat'], result['location']['lon']])
        
        #print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",ret)
        
        return jsonify(**ret)
    except:
        print ("No twitter Nearby")

@application.route('/',methods=['POST'])
def backend_query():
    global dd_select
    dd_select = request.form['keyword_drop_down']
    global selected
    selected = dd_select
    conn = ES(['https://search-twittmap-77ta2y45lfunfg4hhdxaezl524.us-west-2.es.amazonaws.com'])
    #latitute,longitute=location
    cLat = request.args.get('lat',10,type=float)
    cLon = request.args.get('lng',10,type=float)
    #f=GeoDistanceFilter("location",[cLat,cLon],"100km")
    q=TermQuery("message",dd_select)
    #s=FilteredQuery(q,f)
    #results=conn.search(query=s)
    results=conn.search(query=q)
    coord_list = []
    for i in results:
        if (i["location"]["lat"]) is not None:
            #print (i)
            coordinates = str(i["location"]["lat"])+","+str(i["location"]["lon"])
            coord_list.append(coordinates)

    return render_template('MapUI.html', count = count_json['count'], coord_list =  coord_list, selected = selected, keyword = dd_select)


@application.route('/', methods=['GET','POST'])

def home():
     return render_template('MapUI.html', count = count_json['count'], coord_list = [], keyword = "select")


if __name__ == '__main__':
     application.run(host='127.0.0.1')
     make_server("LowCost-env.zpivveuucj.us-west-2.elasticbeanstalk.com", application).serve_forever()
