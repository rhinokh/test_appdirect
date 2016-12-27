from flask import Flask, request

from oauth2 import Consumer
from oauth2 import Request as OauthRequest
from oauth2 import Server as OauthServer
from oauth2 import SignatureMethod_HMAC_SHA1

from lib.request import FlowRequest

request_oauth = ('oneflow-139996', 'LR7tqmp4bvKom3ZG')
request_oauth_signature_method = SignatureMethod_HMAC_SHA1()
oauth_server = OauthServer(
    signature_methods={
        request_oauth_signature_method.name: request_oauth_signature_method
    }
)

appdirect = FlowRequest()
appdirect.request_return_response_object = True
appdirect.request_oauth = request_oauth
appdirect.request_headers = {'accept': 'application/json', 'Content-Type': 'application/json'}


def validate(oauth_request):
    oauth_consumer = Consumer(key=request_oauth[0], secret=request_oauth[1])
    try:
        oauth_server.verify_request(
            request=oauth_request,
            consumer=oauth_consumer,
            token='')
        return True
    except Exception as e:
        print(e)
        pass

    return False

def validate_response(response):
    if not response:
        return False
    import pdb
    pdb.set_trace()
    oauth_request = OauthRequest.from_request(http_method=response.request.method,http_url=response.request.url,headers=response.headers)

    return validate(oauth_request=oauth_request)

def validate_request(request):
    if not request:
        return False

    oauth_request = OauthRequest.from_request(
        http_method=request.method,
        http_url=request.base_url,
        headers=request.headers,
        parameters=dict(request.form.copy()),
        query_string=request.query_string
    )

    oauth_request['oauth_consumer_key'] = request_oauth[0]  # very important

    return validate(oauth_request=oauth_request)

def get_event(url):
    response = appdirect.get(url=url)
    is_ok = validate_response(response=response)
    print(response.json())

    return '{"success":"%s"}' % is_ok


app = Flask(__name__)

@app.route('/create')
def create():
    is_ok = validate_request(request=request)
    if not is_ok:
        print "false"
        return "false" 

    url = request.args['url']
    result = get_event(url=url)

    return result

if __name__ == "__main__":
    app.run()