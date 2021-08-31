import logging, os

from flask_lambda import FlaskLambda
from flask import jsonify, make_response

from error_handler import error_handler
from security import check_hmac
from codepipeline import trigger, get_pipeline_state

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s')
lambda_handler = FlaskLambda(__name__)
logger = logging.getLogger(__name__)

def success_json_response(payload):
  """
  Turns payload into a JSON HTTP200 response
  """
  response = make_response(jsonify(payload), 200)
  response.headers["Content-type"] = "application/json"
  return response

def check_and_trigger(pipeline):
  logger.info(f"check_and_trigger: for pipeline {pipeline}")
  state = get_pipeline_state(name = pipeline)
  flow_state = state["overall_state"]
  if flow_state == "InProgress":
    logger.info("Pipeline is running, so won't trigger again")
    return False
  else:
    logger.info(f"Pipeline state is {flow_state}, so will trigger again")
    response = trigger(
      pipeline = pipeline
    )
    return response

@lambda_handler.route("/trigger", methods=["POST"])
@error_handler
@check_hmac(http_header_name=os.environ["HMAC_HEADER_NAME"], token=os.environ["HMAC_TOKEN"])
def trigger_api():
  response = check_and_trigger(pipeline=os.environ["PIPELINE_NAME"])
  if response:
    return success_json_response({
      "triggered": "yes",
      "execId": response
    })
  else:
    return success_json_response({
      "triggered": "no"
    })

if __name__ == "__main__":
  lambda_handler.run(debug=True, port=5000, host="0.0.0.0", threaded=True)