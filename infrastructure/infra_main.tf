terraform {
  required_providers {
    mongodbatlas = {
      source = "mongodb/mongodbatlas"
      version = "~> 1.12"
    }
  }
}

provider "mongodbatlas" {
  public_key  = "jwrguhnv"
  private_key = "002b9e17-7cf0-41b8-9f32-a449f819200d"
}

variable "atlas_org_id" {
  description = "MongoDB Atlas Organization ID"
  type        = string
}

resource "mongodbatlas_project" "project" {
  name   = "gymhelper-project"
  org_id = var.atlas_org_id
}

resource "mongodbatlas_cluster" "cluster" {
  project_id   = mongodbatlas_project.project.id
  name         = "gymhelper-cluster"
  cluster_type = "REPLICASET"
  provider_name = "AWS"
  provider_region_name = "US_EAST_1"
  provider_instance_size_name = "M10"
  mongo_db_major_version = "7.0"
}