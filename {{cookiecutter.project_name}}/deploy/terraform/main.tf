locals {
    project                = "takinadaio"
    zone                   = "takinada.io"
    domain                 = local.zone
    bucket_name            = "uploads.takinada.io"
    bucket_iam_user        = "takinadaio"
    bucket_iam_user_policy = "takinadaio"
    server_ip              = "49.12.192.208"
}

terraform {
    required_providers {
        cloudflare = {
            source  = "cloudflare/cloudflare"
            version = "~> 3.26"
        }
    }
}

provider "aws" {
    region = "eu-central-1"
}

resource "cloudflare_zone" "primary" {
    zone = local.zone
}

data "cloudflare_zone" "primary" {
    name = local.domain
}

resource "cloudflare_record" "domain" {
    type    = "A"
    proxied = true
    name    = local.domain
    value   = local.server_ip
    zone_id = data.cloudflare_zone.primary.zone_id
}

resource "cloudflare_record" "wildcard_domain" {
    type    = "A"
    proxied = false
    name    = "*"
    value   = local.server_ip
    zone_id = data.cloudflare_zone.primary.zone_id
}

resource "cloudflare_record" "mg_cname" {
    type    = "CNAME"
    proxied = true
    name    = "email.mg"
    value   = "eu.mailgun.org"
    zone_id = data.cloudflare_zone.primary.zone_id
}

resource "cloudflare_record" "mg_mxa" {
    type     = "MX"
    name     = "mg"
    value    = "mxa.eu.mailgun.org"
    priority = 10
    zone_id  = data.cloudflare_zone.primary.zone_id
}

resource "cloudflare_record" "mg_mxb" {
    type     = "MX"
    name     = "mg"
    value    = "mxb.eu.mailgun.org"
    priority = 10
    zone_id  = data.cloudflare_zone.primary.zone_id
}

resource "cloudflare_record" "mg_txt" {
    type     = "TXT"
    name     = "mg"
    value    = "v=spf1 include:eu.mailgun.org ~all"
    priority = 10
    zone_id  = data.cloudflare_zone.primary.zone_id
}

resource "cloudflare_record" "google_verification" {
    type     = "TXT"
    name     = "takinada.io"
    value    = "google-site-verification=RQ-w_GiD-hwzi_JFAExLSRag0kcTORKiyAtuCdprStg"
    priority = 10
    zone_id  = data.cloudflare_zone.primary.zone_id
}

resource "aws_s3_bucket" "uploads" {
    bucket = local.bucket_name
}

resource "aws_s3_bucket_acl" "uploads_bucket_acl" {
    bucket = aws_s3_bucket.uploads.bucket
    acl    = "private"
}

resource "aws_iam_user" "uploads_bucket_iam" {
    name = local.bucket_iam_user
    tags = {
        terraform = "yes"
    }
}

resource "aws_iam_access_key" "uploads_bucket_access_key" {
    user = aws_iam_user.uploads_bucket_iam.name
}

resource "aws_iam_user_policy" "uploads_bucket_policy" {
    name   = local.bucket_iam_user_policy
    user   = aws_iam_user.uploads_bucket_iam.name
    policy = jsonencode({
        Version   = "2012-10-17"
        Statement = [
            {
                Resource = "${aws_s3_bucket.uploads.arn}/*"
                Effect   = "Allow"
                Action   = [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                ]
            },
            {
                Resource = aws_s3_bucket.uploads.arn
                Effect   = "Allow"
                Action   = [
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                ]
            }
        ]
    })
}
