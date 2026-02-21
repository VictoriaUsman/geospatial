provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_sql_database_instance" "postgres" {
  name             = "urban-intel-db"
  database_version = "POSTGRES_15"
  region           = var.region
  settings {
    tier = "db-f1-micro"
  }
}
