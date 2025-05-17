terraform {
  required_providers {
    mongodbatlas = {
      source = "mongodb/mongodbatlas"
      version = "~> 1.12"
    }
  }
  backend "remote" {
    organization = "your-org-name"
    workspaces {
      name = "gymhelper"
    }
  }
}

provider "mongodbatlas" {
  public_key  = var.atlas_public_key
  private_key = var.atlas_private_key
}

variable "atlas_public_key" {
  description = "MongoDB Atlas Public Key"
  type        = string
}

variable "atlas_private_key" {
  description = "MongoDB Atlas Private Key"
  type        = string
  sensitive   = true
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
  auto_scaling_disk_gb_enabled = true
}