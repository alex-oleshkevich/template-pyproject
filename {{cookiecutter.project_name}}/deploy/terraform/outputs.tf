output "uploads_bucket_arn" {
    value = aws_s3_bucket.uploads.arn
}

output "uploads_user_access_key" {
    value = aws_iam_access_key.uploads_bucket_access_key.id
}

output "uploads_user_secret_key" {
    value     = aws_iam_access_key.uploads_bucket_access_key.secret
    sensitive = true
}
