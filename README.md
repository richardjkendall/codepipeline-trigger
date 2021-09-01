# codepipeline-trigger
Lambda function which provides a webhook/API to trigger an AWS CodePipeline.

This code was designed to work with TypeForm webhook calls: https://developer.typeform.com/webhooks/secure-your-webhooks/ although it should work with any requestor that supports HMAC signatures.

There's a Terraform module available to deploy this here: https://github.com/richardjkendall/tf-modules/tree/master/modules/codepipeline-starter

Notes: 
* currently only sha256 signatures are supported
* Any POST to the API with a valid signature will trigger the codepipeline, the content of the request body is not used

## Config

The lambda function expects the following environment variables:

|Variable|Purpose|
|---|---|
|HMAC_HEADER_NAME|Name of HTTP header which contains the HMAC header|
|HMAC_TOKEN|Name of the SSM SecureString Parameter which contains the expected HMAC token|
|PIPELINE_NAME|Name of the codepipeline to be triggered|


