import boto3
from botocore.exceptions import ClientError
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
import sagemaker
from sagemaker.session import Session

class ModelDeploymentAndEndpointManager:
    def __init__(self, flan_t5_model_name, flan_t5_endpoint_name, minilm_model_name, minilm_endpoint_name, aws_role_arn):
        self.flan_t5_model_name = flan_t5_model_name
        self.flan_t5_endpoint_name = flan_t5_endpoint_name
        self.minilm_model_name = minilm_model_name
        self.minilm_endpoint_name = minilm_endpoint_name
        self.aws_role_arn = aws_role_arn

    def deploy_model(self, hub_config, llm_image, endpoint_name, model_name):
      sagemaker_client = boto3.client('sagemaker')

      # Check if the model already exists
      model_exists = self.check_model_exists(model_name)

      # Create the model if it doesn't exist
      if not model_exists:
            print(f"Creating model '{model_name}'.")
            huggingface_model = HuggingFaceModel(
                  env=hub_config,
                  role=self.aws_role_arn,
                  image_uri=llm_image,
                  name=model_name,
                  sagemaker_session=sagemaker.Session()
            )

            # Deploy the model
            huggingface_model.deploy(
                  initial_instance_count=1,
                  instance_type="ml.t2.medium",
                  endpoint_name=endpoint_name
            )
      else:
            print(f"Model '{model_name}' already exists.")

      # Check if the endpoint configuration already exists
      endpoint_config_name = endpoint_name + "-config"
      try:
            sagemaker_client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
            print(f"Endpoint configuration '{endpoint_config_name}' already exists.")
      except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                  print(f"Creating new endpoint configuration '{endpoint_config_name}'.")
                  sagemaker_client.create_endpoint_config(
                  EndpointConfigName=endpoint_config_name,
                  ProductionVariants=[
                        {
                              'VariantName': 'AllTraffic',
                              'ModelName': model_name,
                              'InitialInstanceCount': 1,
                              'InstanceType': 'ml.t2.medium',
                              'InitialVariantWeight': 1
                        }
                  ]
                  )
            else:
                  raise

      # Check if the endpoint already exists
      if not self.check_endpoint_exists(endpoint_name):
            print(f"Creating endpoint '{endpoint_name}'.")
            sagemaker_client.create_endpoint(
                  EndpointName=endpoint_name,
                  EndpointConfigName=endpoint_config_name
            )
            print(f"Endpoint '{endpoint_name}' creation initiated.")
      else:
            print(f"Endpoint '{endpoint_name}' already exists.")


    def check_model_exists(self, model_name):
            sagemaker_client = boto3.client('sagemaker')
            try:
                  sagemaker_client.describe_model(ModelName=model_name)
                  return True
            except ClientError as e:
                  if e.response['Error']['Code'] == 'ValidationException':
                        return False
                  else:
                        raise

    def check_endpoint_exists(self, endpoint_name):
        sagemaker_client = boto3.client('sagemaker')
        try:
            sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                return False
            else:
                raise
