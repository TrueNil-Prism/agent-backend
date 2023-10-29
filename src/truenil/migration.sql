/Users/kartikla/dev/truenil/agent-backend/venv/bin/python /Users/kartikla/dev/truenil/agent-backend/src/truenil/migration.py
CREATE TABLE IF NOT EXISTS "core"."organization" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "website" TEXT NOT NULL,
  "details" TEXT NOT NULL
)
;
CREATE TABLE IF NOT EXISTS "core"."organization_user" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "user_first_name" TEXT NOT NULL,
  "user_last_name" TEXT NOT NULL,
  "user_id" TEXT NOT NULL,
  "idp_provider" TEXT,
  "is_active" BOOLEAN NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."agent" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "uuid" UUID NOT NULL,
  "version" TEXT NOT NULL,
  "health_status" TEXT NOT NULL,
  "last_ping" TIMESTAMPTZ NOT NULL,
  "ip_address" TEXT NOT NULL,
  "host_name" TEXT NOT NULL,
  "running_as_user_name" TEXT,
  "environment_settings" TEXT,
  "metadata" JSON,
  "agent_state" TEXT NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."bucket" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "bucket_key" TEXT NOT NULL,
  "cloud" TEXT NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."file" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "bucket_id" BIGINT NOT NULL,
  "file_path" TEXT NOT NULL,
  "encryption_status" TEXT NOT NULL,
  "storage_type" TEXT NOT NULL,
  "file_type" TEXT NOT NULL,
  "compression_type" TEXT NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id"),
  FOREIGN KEY ("bucket_id") REFERENCES "agent"."bucket" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."agent_file" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "agent_id" BIGINT NOT NULL,
  "file_id" BIGINT NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id"),
  FOREIGN KEY ("agent_id") REFERENCES "agent"."agent" ("id"),
  FOREIGN KEY ("file_id") REFERENCES "agent"."file" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."agent_bucket" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "agent_id" BIGINT NOT NULL,
  "bucket_id" BIGINT NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id"),
  FOREIGN KEY ("agent_id") REFERENCES "agent"."agent" ("id"),
  FOREIGN KEY ("bucket_id") REFERENCES "agent"."bucket" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."agent_metrics" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "agent_id" BIGINT NOT NULL,
  "metric_name" TEXT NOT NULL,
  "metric_value" DOUBLE PRECISION NOT NULL,
  "process_name" TEXT,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id"),
  FOREIGN KEY ("agent_id") REFERENCES "agent"."agent" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."agent_token" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "token" TEXT NOT NULL,
  "is_active" BOOLEAN NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."agent_token_audit" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "agent_id" BIGINT NOT NULL,
  "token_id" BIGINT NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id"),
  FOREIGN KEY ("agent_id") REFERENCES "agent"."agent" ("id"),
  FOREIGN KEY ("token_id") REFERENCES "agent"."agent_token" ("id")
)
;
CREATE TABLE IF NOT EXISTS "agent"."user_file_permissions" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "file_id" BIGINT NOT NULL,
  "user" TEXT NOT NULL,
  "permissions" JSON NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id"),
  FOREIGN KEY ("file_id") REFERENCES "agent"."file" ("id")
)CREATE TABLE IF NOT EXISTS "agent"."user_file_permissions" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "created_at" TIMESTAMPTZ NOT NULL,
  "updated_at" TIMESTAMPTZ NOT NULL,
  "created_by" TEXT NOT NULL,
  "updated_by" TEXT NOT NULL,
  "organization_id" BIGINT NOT NULL,
  "file_id" BIGINT NOT NULL,
  "user" TEXT NOT NULL,
  "permissions" JSON NOT NULL,
  FOREIGN KEY ("organization_id") REFERENCES "core"."organization" ("id"),
  FOREIGN KEY ("file_id") REFERENCES "agent"."file" ("id")
);
create unique index on "agent"."agent_token"(token);
create unique index on agent.agent_file(agent_id,file_id);
create unique index on agent.agent_bucket(agent_id,bucket_id);
create index on core.organization_user(organization_id, user_id);