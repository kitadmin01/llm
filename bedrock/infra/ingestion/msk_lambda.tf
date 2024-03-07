resource "aws_lambda_function" "msk_lambda_fn" {
  function_name = "MyKafkaTriggeredFunction"
  handler       = "consumer.handler"
  role          = aws_iam_role.lambda_execution_role.arn
  runtime       = "python3.9" 


  filename      = "consumer.zip"
}
