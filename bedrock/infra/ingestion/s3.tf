resource "aws_s3_bucket" "my_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    "${var.s3_bucket_tag_name}" = var.s3_bucket_tag_value
  }
}
