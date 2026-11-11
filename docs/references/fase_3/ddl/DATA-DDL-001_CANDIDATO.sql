-- DATA-DDL-001 v0.1 (2026-11-10) | DISEÑO CANDIDATO — NO APLICAR SIN APROBACIÓN
-- Base: PostgreSQL 16+ sugerido; verificación sobre motor REAL pendiente.
-- Archivo de referencia para convertir a migraciones Alembic, NO migración ejecutada.
-- Requisitos de sesión: timezone UTC; usuario DB de permisos mínimos; sin datos reales.
BEGIN;

CREATE TABLE persons (
    id uuid PRIMARY KEY,
    display_name varchar(160) NOT NULL CHECK (btrim(display_name) <> ''),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE clients (
    id uuid PRIMARY KEY,
    client_code varchar(32) NOT NULL UNIQUE,
    name varchar(180) NOT NULL,
    status varchar(12) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','SUSPENDED')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (btrim(client_code) <> '' AND btrim(name) <> '')
);

CREATE TABLE accounts (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES persons(id) ON DELETE RESTRICT,
    username varchar(120) NOT NULL,
    password_hash text NOT NULL,
    account_kind varchar(10) NOT NULL CHECK (account_kind IN ('INTERNAL','EXTERNAL')),
    client_id uuid REFERENCES clients(id) ON DELETE RESTRICT,
    status varchar(10) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DISABLED')),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, person_id),
    UNIQUE (id, account_kind),
    UNIQUE (id, client_id, account_kind),
    CHECK (username = lower(btrim(username)) AND username <> ''),
    CHECK (length(password_hash) > 20),
    CHECK ((account_kind='EXTERNAL' AND client_id IS NOT NULL)
        OR (account_kind='INTERNAL' AND client_id IS NULL))
);
CREATE UNIQUE INDEX ux_accounts_username_lower ON accounts (lower(username));

CREATE TABLE account_roles (
    account_id uuid NOT NULL,
    account_kind varchar(10) NOT NULL,
    role_code varchar(24) NOT NULL,
    PRIMARY KEY (account_id, role_code),
    FOREIGN KEY (account_id, account_kind) REFERENCES accounts(id,account_kind) ON DELETE RESTRICT,
    CHECK ((account_kind='EXTERNAL' AND role_code='EXTERNAL_READER')
        OR (account_kind='INTERNAL' AND role_code IN ('ANALYST','LAWYER','PREPARER','COORDINATOR','ADMIN')))
);

CREATE TABLE auth_sessions (
    id uuid PRIMARY KEY,
    account_id uuid NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    token_digest bytea NOT NULL UNIQUE CHECK (octet_length(token_digest)=32),
    issued_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz,
    CHECK (expires_at > issued_at),
    CHECK (revoked_at IS NULL OR revoked_at >= issued_at)
);
CREATE INDEX ix_auth_sessions_account_expires ON auth_sessions(account_id,expires_at);

CREATE TABLE judicial_processes (
    id uuid PRIMARY KEY,
    radicado varchar(23) NOT NULL UNIQUE CHECK (radicado ~ '^[0-9]{23}$'),
    label varchar(180),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE acquisition_runs (
    id uuid PRIMARY KEY,
    process_id uuid NOT NULL REFERENCES judicial_processes(id) ON DELETE RESTRICT,
    source_code varchar(32) NOT NULL DEFAULT 'DEMO-FIXTURE' CHECK (source_code='DEMO-FIXTURE'),
    status varchar(12) NOT NULL CHECK (status IN ('PENDING','SUCCESS','INCOMPLETE','FAILED')),
    request_key varchar(100) NOT NULL UNIQUE,
    requested_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    error_code varchar(64),
    coverage_note text,
    UNIQUE (id,process_id),
    CHECK ((status='PENDING' AND finished_at IS NULL)
        OR (status<>'PENDING' AND finished_at IS NOT NULL)),
    CHECK (status<>'FAILED' OR error_code IS NOT NULL)
);
CREATE INDEX ix_acquisition_process_requested ON acquisition_runs(process_id,requested_at DESC);

CREATE TABLE observations (
    id uuid PRIMARY KEY,
    process_id uuid NOT NULL REFERENCES judicial_processes(id) ON DELETE RESTRICT,
    acquisition_run_id uuid NOT NULL UNIQUE,
    quality varchar(16) NOT NULL CHECK (quality IN ('COMPARABLE','INCOMPLETE','INDETERMINATE')),
    observed_at timestamptz NOT NULL,
    received_at timestamptz NOT NULL DEFAULT now(),
    sealed_at timestamptz,
    payload_sha256 varchar(64) NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    provenance varchar(80) NOT NULL DEFAULT 'DEMO-FIXTURE',
    coverage_note text,
    UNIQUE (id,process_id),
    FOREIGN KEY (acquisition_run_id,process_id) REFERENCES acquisition_runs(id,process_id) ON DELETE RESTRICT,
    CHECK (received_at >= observed_at),
    CHECK (sealed_at IS NULL OR sealed_at >= received_at)
);
CREATE INDEX ix_observations_process_observed ON observations(process_id,observed_at DESC);

CREATE TABLE observed_actions (
    observation_id uuid NOT NULL REFERENCES observations(id) ON DELETE RESTRICT,
    action_key varchar(64) NOT NULL,
    content_sha256 varchar(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    description text NOT NULL,
    occurred_on date,
    PRIMARY KEY (observation_id,action_key),
    CHECK (action_key ~ '^ACT-[0-9]{2,}$' AND btrim(description) <> '')
);

CREATE TABLE trackings (
    id uuid PRIMARY KEY,
    tracking_code varchar(40) NOT NULL UNIQUE,
    client_id uuid NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    process_id uuid NOT NULL REFERENCES judicial_processes(id) ON DELETE RESTRICT,
    status varchar(12) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','ACTIVE','FINISHED')),
    baseline_observation_id uuid,
    last_adopted_observation_id uuid,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id,client_id),
    UNIQUE (id,process_id),
    UNIQUE (id,client_id,process_id),
    FOREIGN KEY (baseline_observation_id,process_id) REFERENCES observations(id,process_id) ON DELETE RESTRICT,
    FOREIGN KEY (last_adopted_observation_id,process_id) REFERENCES observations(id,process_id) ON DELETE RESTRICT,
    CHECK ((baseline_observation_id IS NULL) = (last_adopted_observation_id IS NULL))
);
-- PR-F3: un único seguimiento no finalizado por cliente/proceso; finalizar permite abrir nuevo.
CREATE UNIQUE INDEX ux_trackings_open_per_client_process ON trackings(client_id,process_id)
    WHERE status IN ('PENDING','ACTIVE');
CREATE INDEX ix_trackings_client_status ON trackings(client_id,status);

CREATE TABLE external_tracking_scopes (
    account_id uuid NOT NULL,
    account_kind varchar(10) NOT NULL DEFAULT 'EXTERNAL' CHECK (account_kind='EXTERNAL'),
    client_id uuid NOT NULL,
    tracking_id uuid NOT NULL,
    permission_code varchar(32) NOT NULL DEFAULT 'READ_PUBLICATIONS' CHECK (permission_code='READ_PUBLICATIONS'),
    granted_at timestamptz NOT NULL DEFAULT now(),
    revoked_at timestamptz,
    PRIMARY KEY (account_id,tracking_id,permission_code),
    FOREIGN KEY (account_id,client_id,account_kind) REFERENCES accounts(id,client_id,account_kind) ON DELETE RESTRICT,
    FOREIGN KEY (tracking_id,client_id) REFERENCES trackings(id,client_id) ON DELETE RESTRICT,
    CHECK (revoked_at IS NULL OR revoked_at >= granted_at)
);
CREATE INDEX ix_scopes_active_tracking ON external_tracking_scopes(client_id,tracking_id)
    WHERE revoked_at IS NULL;

-- Asignación interna por seguimiento (control adicional al rol, sin alcance global).
CREATE TABLE internal_tracking_assignments (
    account_id uuid NOT NULL,
    account_kind varchar(10) NOT NULL DEFAULT 'INTERNAL' CHECK (account_kind='INTERNAL'),
    tracking_id uuid NOT NULL REFERENCES trackings(id) ON DELETE RESTRICT,
    assigned_at timestamptz NOT NULL DEFAULT now(),
    revoked_at timestamptz,
    PRIMARY KEY (account_id,tracking_id),
    FOREIGN KEY (account_id,account_kind) REFERENCES accounts(id,account_kind) ON DELETE RESTRICT,
    CHECK (revoked_at IS NULL OR revoked_at >= assigned_at)
);
CREATE INDEX ix_internal_assignments_tracking_active ON internal_tracking_assignments(tracking_id)
    WHERE revoked_at IS NULL;

CREATE TABLE comparisons (
    id uuid PRIMARY KEY,
    process_id uuid NOT NULL REFERENCES judicial_processes(id) ON DELETE RESTRICT,
    old_observation_id uuid NOT NULL,
    new_observation_id uuid NOT NULL,
    rule_version varchar(32) NOT NULL,
    result varchar(16) NOT NULL CHECK (result IN ('CHANGES_FOUND','NO_CHANGES','NOT_COMPARABLE')),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (old_observation_id,new_observation_id,rule_version),
    UNIQUE (id,process_id),
    UNIQUE (id,process_id,new_observation_id),
    FOREIGN KEY (old_observation_id,process_id) REFERENCES observations(id,process_id) ON DELETE RESTRICT,
    FOREIGN KEY (new_observation_id,process_id) REFERENCES observations(id,process_id) ON DELETE RESTRICT,
    CHECK (old_observation_id <> new_observation_id AND btrim(rule_version) <> '')
);

CREATE TABLE technical_changes (
    id uuid PRIMARY KEY,
    comparison_id uuid NOT NULL,
    process_id uuid NOT NULL,
    new_observation_id uuid NOT NULL,
    action_key varchar(64) NOT NULL,
    change_kind varchar(12) NOT NULL DEFAULT 'ADDED' CHECK (change_kind='ADDED'),
    evidence text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (comparison_id,action_key,change_kind),
    UNIQUE (id,process_id),
    UNIQUE (id,comparison_id,process_id),
    FOREIGN KEY (comparison_id,process_id,new_observation_id)
        REFERENCES comparisons(id,process_id,new_observation_id) ON DELETE RESTRICT,
    FOREIGN KEY (new_observation_id,action_key)
        REFERENCES observed_actions(observation_id,action_key) ON DELETE RESTRICT,
    CHECK (btrim(evidence) <> '')
);

CREATE TABLE tracking_evaluations (
    id uuid PRIMARY KEY,
    tracking_id uuid NOT NULL,
    process_id uuid NOT NULL,
    comparison_id uuid NOT NULL,
    decision varchar(12) NOT NULL CHECK (decision IN ('ELIGIBLE','SKIPPED')),
    reason text NOT NULL,
    evaluated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tracking_id,comparison_id),
    UNIQUE (id,tracking_id,comparison_id),
    UNIQUE (id,tracking_id,comparison_id,decision),
    FOREIGN KEY (tracking_id,process_id) REFERENCES trackings(id,process_id) ON DELETE RESTRICT,
    FOREIGN KEY (comparison_id,process_id) REFERENCES comparisons(id,process_id) ON DELETE RESTRICT,
    CHECK (btrim(reason) <> '')
);

CREATE TABLE novelties (
    id uuid PRIMARY KEY,
    novelty_code varchar(40) NOT NULL UNIQUE,
    tracking_id uuid NOT NULL,
    client_id uuid NOT NULL,
    process_id uuid NOT NULL,
    comparison_id uuid NOT NULL,
    change_id uuid NOT NULL,
    evaluation_id uuid NOT NULL,
    evaluation_decision varchar(12) NOT NULL DEFAULT 'ELIGIBLE' CHECK (evaluation_decision='ELIGIBLE'),
    status varchar(32) NOT NULL DEFAULT 'PENDING_OPERATIVE' CHECK (status IN
        ('PENDING_OPERATIVE','IN_OPERATIVE_REVIEW','PENDING_LEGAL','TREATMENT_DEFINED','IN_FOLLOWUP','DISCARDED')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tracking_id,change_id),
    UNIQUE (id,tracking_id),
    FOREIGN KEY (tracking_id,client_id,process_id)
        REFERENCES trackings(id,client_id,process_id) ON DELETE RESTRICT,
    FOREIGN KEY (change_id,comparison_id,process_id)
        REFERENCES technical_changes(id,comparison_id,process_id) ON DELETE RESTRICT,
    FOREIGN KEY (evaluation_id,tracking_id,comparison_id,evaluation_decision)
        REFERENCES tracking_evaluations(id,tracking_id,comparison_id,decision) ON DELETE RESTRICT
);
CREATE INDEX ix_novelties_tracking_status ON novelties(tracking_id,status,created_at DESC);

CREATE TABLE novelty_reviews (
    id uuid PRIMARY KEY,
    novelty_id uuid NOT NULL REFERENCES novelties(id) ON DELETE RESTRICT,
    review_kind varchar(16) NOT NULL CHECK (review_kind IN ('OPERATIVE','LEGAL')),
    review_sequence integer NOT NULL DEFAULT 1 CHECK (review_sequence > 0),
    actor_account_id uuid NOT NULL,
    actor_person_id uuid NOT NULL,
    decision text NOT NULL,
    evidence_note text NOT NULL,
    reviewed_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (novelty_id,review_kind,review_sequence),
    FOREIGN KEY (actor_account_id,actor_person_id) REFERENCES accounts(id,person_id) ON DELETE RESTRICT,
    CHECK (btrim(decision) <> '' AND btrim(evidence_note) <> '')
);

CREATE TABLE publications (
    id uuid PRIMARY KEY,
    tracking_id uuid NOT NULL,
    client_id uuid NOT NULL,
    current_version_id uuid,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id,tracking_id,client_id),
    FOREIGN KEY (tracking_id,client_id) REFERENCES trackings(id,client_id) ON DELETE RESTRICT
);
CREATE INDEX ix_publications_tracking ON publications(tracking_id);

CREATE TABLE publication_versions (
    id uuid PRIMARY KEY,
    publication_id uuid NOT NULL,
    version_number integer NOT NULL CHECK (version_number > 0),
    recipient_tracking_id uuid NOT NULL,
    recipient_client_id uuid NOT NULL,
    status varchar(24) NOT NULL DEFAULT 'DRAFT' CHECK (status IN
        ('DRAFT','PENDING_APPROVAL','APPROVED','REJECTED','PUBLISHED')),
    content_text text NOT NULL CHECK (btrim(content_text) <> ''),
    content_sha256 varchar(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT now(),
    frozen_at timestamptz,
    approved_at timestamptz,
    published_at timestamptz,
    UNIQUE (publication_id,version_number),
    UNIQUE (id,publication_id),
    UNIQUE (id,recipient_tracking_id),
    FOREIGN KEY (publication_id,recipient_tracking_id,recipient_client_id)
        REFERENCES publications(id,tracking_id,client_id) ON DELETE RESTRICT,
    CHECK (status='DRAFT' OR frozen_at IS NOT NULL),
    CHECK (status NOT IN ('APPROVED','PUBLISHED') OR approved_at IS NOT NULL),
    CHECK (status<>'PUBLISHED' OR published_at IS NOT NULL)
);
-- FK circular segura: puntero nullable insertado después de crear la versión.
ALTER TABLE publications ADD CONSTRAINT fk_publications_current_version
    FOREIGN KEY (current_version_id,id)
    REFERENCES publication_versions(id,publication_id) ON DELETE RESTRICT;

CREATE TABLE publication_preparers (
    version_id uuid NOT NULL REFERENCES publication_versions(id) ON DELETE RESTRICT,
    person_id uuid NOT NULL REFERENCES persons(id) ON DELETE RESTRICT,
    account_id uuid NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (version_id,person_id),
    FOREIGN KEY (account_id,person_id) REFERENCES accounts(id,person_id) ON DELETE RESTRICT
);

CREATE TABLE publication_version_novelties (
    version_id uuid NOT NULL,
    tracking_id uuid NOT NULL,
    novelty_id uuid NOT NULL,
    PRIMARY KEY (version_id,novelty_id),
    FOREIGN KEY (version_id,tracking_id) REFERENCES publication_versions(id,recipient_tracking_id) ON DELETE RESTRICT,
    FOREIGN KEY (novelty_id,tracking_id) REFERENCES novelties(id,tracking_id) ON DELETE RESTRICT
);

CREATE TABLE publication_approvals (
    id uuid PRIMARY KEY,
    version_id uuid NOT NULL UNIQUE REFERENCES publication_versions(id) ON DELETE RESTRICT,
    approver_account_id uuid NOT NULL,
    approver_person_id uuid NOT NULL,
    verdict varchar(8) NOT NULL CHECK (verdict IN ('APPROVE','REJECT')),
    snapshot_sha256 varchar(64) NOT NULL CHECK (snapshot_sha256 ~ '^[0-9a-f]{64}$'),
    justification text NOT NULL,
    decided_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (approver_account_id,approver_person_id)
        REFERENCES accounts(id,person_id) ON DELETE RESTRICT,
    CHECK (btrim(justification) <> '')
);

CREATE TABLE state_transitions (
    id uuid PRIMARY KEY,
    resource_type varchar(24) NOT NULL CHECK (resource_type IN ('CLIENT','TRACKING','NOVELTY','PUBLICATION_VERSION')),
    client_id uuid REFERENCES clients(id) ON DELETE RESTRICT,
    tracking_id uuid REFERENCES trackings(id) ON DELETE RESTRICT,
    novelty_id uuid REFERENCES novelties(id) ON DELETE RESTRICT,
    version_id uuid REFERENCES publication_versions(id) ON DELETE RESTRICT,
    from_state varchar(40),
    to_state varchar(40) NOT NULL,
    actor_account_id uuid,
    actor_person_id uuid,
    actor_kind varchar(8) NOT NULL CHECK (actor_kind IN ('USER','SYSTEM')),
    reason text NOT NULL,
    request_id uuid NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (actor_account_id,actor_person_id) REFERENCES accounts(id,person_id) ON DELETE RESTRICT,
    CHECK (((client_id IS NOT NULL)::int + (tracking_id IS NOT NULL)::int
        + (novelty_id IS NOT NULL)::int + (version_id IS NOT NULL)::int)=1),
    CHECK ((resource_type='CLIENT' AND client_id IS NOT NULL) OR
        (resource_type='TRACKING' AND tracking_id IS NOT NULL) OR
        (resource_type='NOVELTY' AND novelty_id IS NOT NULL) OR
        (resource_type='PUBLICATION_VERSION' AND version_id IS NOT NULL)),
    CHECK ((actor_kind='USER' AND actor_account_id IS NOT NULL AND actor_person_id IS NOT NULL)
        OR (actor_kind='SYSTEM' AND actor_account_id IS NULL AND actor_person_id IS NULL)),
    CHECK (btrim(reason) <> '')
);
CREATE INDEX ix_state_transition_tracking ON state_transitions(tracking_id,occurred_at DESC)
    WHERE tracking_id IS NOT NULL;
CREATE INDEX ix_state_transition_novelty ON state_transitions(novelty_id,occurred_at DESC)
    WHERE novelty_id IS NOT NULL;

CREATE TABLE audit_events (
    id uuid PRIMARY KEY,
    request_id uuid NOT NULL,
    event_code varchar(64) NOT NULL,
    result varchar(10) NOT NULL CHECK (result IN ('SUCCESS','DENIED','ERROR')),
    actor_account_id uuid REFERENCES accounts(id) ON DELETE RESTRICT,
    resource_kind varchar(32),
    resource_id uuid,
    sanitized_reason varchar(100),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (btrim(event_code) <> '')
);
CREATE INDEX ix_audit_events_request ON audit_events(request_id,created_at DESC);
CREATE INDEX ix_audit_events_created ON audit_events(created_at DESC);

-- Guardas físicas del esquema candidato; NO sustituyen autorización por caso de uso.
CREATE FUNCTION f3_guard_acquisition_run() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.status <> 'PENDING' THEN
        RAISE EXCEPTION 'terminal acquisition run is immutable' USING ERRCODE='23514';
    END IF;
    IF NEW.status='PENDING' OR NEW.process_id <> OLD.process_id
       OR NEW.request_key <> OLD.request_key OR NEW.source_code <> OLD.source_code THEN
        RAISE EXCEPTION 'acquisition may only be finalized once' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_acquisition_run_finalize BEFORE UPDATE ON acquisition_runs
    FOR EACH ROW EXECUTE FUNCTION f3_guard_acquisition_run();

CREATE FUNCTION f3_guard_observation_accept() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE v_status varchar(12);
BEGIN
    SELECT status INTO v_status FROM acquisition_runs WHERE id=NEW.acquisition_run_id FOR UPDATE;
    IF v_status IS NULL OR v_status IN ('PENDING','FAILED')
       OR (v_status='INCOMPLETE' AND NEW.quality='COMPARABLE') THEN
        RAISE EXCEPTION 'observation must reference a finalized compatible acquisition' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_observation_accept BEFORE INSERT ON observations
    FOR EACH ROW EXECUTE FUNCTION f3_guard_observation_accept();

CREATE FUNCTION f3_reject_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'append-only record; write a new immutable record instead' USING ERRCODE='23514';
END $$;
CREATE FUNCTION f3_guard_observation_seal() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP='DELETE' THEN
        RAISE EXCEPTION 'sealed snapshot cannot be deleted' USING ERRCODE='23514';
    END IF;
    IF OLD.sealed_at IS NOT NULL OR NEW.sealed_at IS NULL
       OR ROW(NEW.id,NEW.process_id,NEW.acquisition_run_id,NEW.quality,NEW.observed_at,
              NEW.received_at,NEW.payload_sha256,NEW.provenance,NEW.coverage_note)
       IS DISTINCT FROM
          ROW(OLD.id,OLD.process_id,OLD.acquisition_run_id,OLD.quality,OLD.observed_at,
              OLD.received_at,OLD.payload_sha256,OLD.provenance,OLD.coverage_note) THEN
        RAISE EXCEPTION 'observation can only transition from unsealed to sealed' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_observations_seal BEFORE UPDATE OR DELETE ON observations
    FOR EACH ROW EXECUTE FUNCTION f3_guard_observation_seal();

CREATE FUNCTION f3_guard_observed_action_insert() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE v_sealed_at timestamptz;
BEGIN
    SELECT sealed_at INTO v_sealed_at FROM observations WHERE id=NEW.observation_id FOR UPDATE;
    IF NOT FOUND OR v_sealed_at IS NOT NULL THEN
        RAISE EXCEPTION 'cannot insert action outside an unsealed snapshot' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_observed_action_insert BEFORE INSERT ON observed_actions
    FOR EACH ROW EXECUTE FUNCTION f3_guard_observed_action_insert();
CREATE TRIGGER tr_observed_actions_append_only BEFORE UPDATE OR DELETE ON observed_actions
    FOR EACH ROW EXECUTE FUNCTION f3_reject_mutation();
CREATE TRIGGER tr_comparisons_append_only BEFORE UPDATE OR DELETE ON comparisons
    FOR EACH ROW EXECUTE FUNCTION f3_reject_mutation();
CREATE TRIGGER tr_changes_append_only BEFORE UPDATE OR DELETE ON technical_changes
    FOR EACH ROW EXECUTE FUNCTION f3_reject_mutation();
CREATE TRIGGER tr_reviews_append_only BEFORE UPDATE OR DELETE ON novelty_reviews
    FOR EACH ROW EXECUTE FUNCTION f3_reject_mutation();
CREATE TRIGGER tr_approvals_append_only BEFORE UPDATE OR DELETE ON publication_approvals
    FOR EACH ROW EXECUTE FUNCTION f3_reject_mutation();
CREATE TRIGGER tr_state_transitions_append_only BEFORE UPDATE OR DELETE ON state_transitions
    FOR EACH ROW EXECUTE FUNCTION f3_reject_mutation();
CREATE TRIGGER tr_audit_events_append_only BEFORE UPDATE OR DELETE ON audit_events
    FOR EACH ROW EXECUTE FUNCTION f3_reject_mutation();

CREATE FUNCTION f3_guard_comparison() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_old_quality varchar(16);
    v_new_quality varchar(16);
    v_old_sealed timestamptz;
    v_new_sealed timestamptz;
    v_old_time timestamptz;
    v_new_time timestamptz;
BEGIN
    SELECT quality,sealed_at,observed_at INTO v_old_quality,v_old_sealed,v_old_time
    FROM observations WHERE id=NEW.old_observation_id;
    SELECT quality,sealed_at,observed_at INTO v_new_quality,v_new_sealed,v_new_time
    FROM observations WHERE id=NEW.new_observation_id;
    IF v_old_quality IS DISTINCT FROM 'COMPARABLE' OR v_new_quality IS DISTINCT FROM 'COMPARABLE'
       OR v_old_sealed IS NULL OR v_new_sealed IS NULL OR v_old_time >= v_new_time THEN
        RAISE EXCEPTION 'comparison requires two sealed ordered comparable observations' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_comparison_guard BEFORE INSERT ON comparisons
    FOR EACH ROW EXECUTE FUNCTION f3_guard_comparison();

CREATE FUNCTION f3_guard_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM comparisons WHERE id=NEW.comparison_id AND result='CHANGES_FOUND') THEN
        RAISE EXCEPTION 'technical change requires confirmed difference' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_technical_change_guard BEFORE INSERT ON technical_changes
    FOR EACH ROW EXECUTE FUNCTION f3_guard_change();

CREATE FUNCTION f3_guard_tracking_baseline() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_baseline_quality varchar(16);
    v_last_quality varchar(16);
    v_baseline_sealed timestamptz;
    v_last_sealed timestamptz;
    v_baseline_time timestamptz;
    v_last_time timestamptz;
BEGIN
    IF TG_OP='UPDATE' AND OLD.baseline_observation_id IS NOT NULL AND
       NEW.baseline_observation_id IS DISTINCT FROM OLD.baseline_observation_id THEN
        RAISE EXCEPTION 'first baseline is immutable' USING ERRCODE='23514';
    END IF;
    IF NEW.baseline_observation_id IS NOT NULL THEN
        SELECT quality,sealed_at,observed_at INTO v_baseline_quality,v_baseline_sealed,v_baseline_time
        FROM observations WHERE id=NEW.baseline_observation_id;
        SELECT quality,sealed_at,observed_at INTO v_last_quality,v_last_sealed,v_last_time
        FROM observations WHERE id=NEW.last_adopted_observation_id;
        IF v_baseline_quality IS DISTINCT FROM 'COMPARABLE' OR v_last_quality IS DISTINCT FROM 'COMPARABLE'
           OR v_baseline_sealed IS NULL OR v_last_sealed IS NULL OR v_last_time < v_baseline_time THEN
            RAISE EXCEPTION 'tracking baseline and last observation must be comparable and ordered' USING ERRCODE='23514';
        END IF;
        IF TG_OP='UPDATE' AND OLD.last_adopted_observation_id IS NOT NULL AND
           NEW.last_adopted_observation_id IS DISTINCT FROM OLD.last_adopted_observation_id AND
           EXISTS (SELECT 1 FROM observations old_ob WHERE old_ob.id=OLD.last_adopted_observation_id
                   AND old_ob.observed_at >= v_last_time) THEN
            RAISE EXCEPTION 'tracking last adopted observation cannot move backwards' USING ERRCODE='23514';
        END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_tracking_baseline_guard BEFORE INSERT OR UPDATE ON trackings
    FOR EACH ROW EXECUTE FUNCTION f3_guard_tracking_baseline();

CREATE FUNCTION f3_guard_publication_version() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_verdict varchar(8);
BEGIN
    IF OLD.status <> 'DRAFT' AND
       ROW(NEW.content_text,NEW.content_sha256,NEW.recipient_client_id,NEW.recipient_tracking_id,
           NEW.publication_id,NEW.version_number,NEW.frozen_at)
       IS DISTINCT FROM
       ROW(OLD.content_text,OLD.content_sha256,OLD.recipient_client_id,OLD.recipient_tracking_id,
           OLD.publication_id,OLD.version_number,OLD.frozen_at) THEN
        RAISE EXCEPTION 'submitted publication snapshot is immutable' USING ERRCODE='23514';
    END IF;
    IF OLD.status <> 'DRAFT' AND NEW.status=OLD.status AND NEW IS DISTINCT FROM OLD THEN
        RAISE EXCEPTION 'submitted version only changes through valid transition' USING ERRCODE='23514';
    END IF;
    IF OLD.status <> NEW.status THEN
        IF NOT ((OLD.status='DRAFT' AND NEW.status='PENDING_APPROVAL') OR
                (OLD.status='PENDING_APPROVAL' AND NEW.status IN ('APPROVED','REJECTED')) OR
                (OLD.status='APPROVED' AND NEW.status='PUBLISHED')) THEN
            RAISE EXCEPTION 'invalid publication status transition' USING ERRCODE='23514';
        END IF;
        IF NEW.status='PENDING_APPROVAL' AND
           (NOT EXISTS (SELECT 1 FROM publication_preparers WHERE version_id=NEW.id) OR
            NOT EXISTS (SELECT 1 FROM publication_version_novelties WHERE version_id=NEW.id)) THEN
            RAISE EXCEPTION 'publication requires preparer and linked novelty' USING ERRCODE='23514';
        END IF;
        IF NEW.status IN ('APPROVED','REJECTED') THEN
            SELECT verdict INTO v_verdict FROM publication_approvals WHERE version_id=NEW.id;
            IF v_verdict IS DISTINCT FROM CASE WHEN NEW.status='APPROVED' THEN 'APPROVE' ELSE 'REJECT' END THEN
                RAISE EXCEPTION 'status does not match authorized decision' USING ERRCODE='23514';
            END IF;
        END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_publication_version_guard BEFORE UPDATE ON publication_versions
    FOR EACH ROW EXECUTE FUNCTION f3_guard_publication_version();

CREATE FUNCTION f3_guard_version_components() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_version_id uuid;
    v_status varchar(24);
BEGIN
    IF TG_OP='UPDATE' THEN
        RAISE EXCEPTION 'change draft components through delete and reinsert, not UPDATE' USING ERRCODE='23514';
    END IF;
    v_version_id := CASE WHEN TG_OP='DELETE' THEN OLD.version_id ELSE NEW.version_id END;
    SELECT status INTO v_status FROM publication_versions WHERE id=v_version_id FOR UPDATE;
    IF v_status IS DISTINCT FROM 'DRAFT' THEN
        RAISE EXCEPTION 'cannot change publication components after submission' USING ERRCODE='23514';
    END IF;
    IF TG_OP='DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_preparers_guard BEFORE INSERT OR UPDATE OR DELETE ON publication_preparers
    FOR EACH ROW EXECUTE FUNCTION f3_guard_version_components();
CREATE TRIGGER tr_version_novelties_guard BEFORE INSERT OR UPDATE OR DELETE ON publication_version_novelties
    FOR EACH ROW EXECUTE FUNCTION f3_guard_version_components();

CREATE FUNCTION f3_guard_publication_approval() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_status varchar(24);
    v_digest varchar(64);
BEGIN
    SELECT status,content_sha256 INTO v_status,v_digest
    FROM publication_versions WHERE id=NEW.version_id FOR UPDATE;
    IF v_status IS DISTINCT FROM 'PENDING_APPROVAL' OR v_digest IS DISTINCT FROM NEW.snapshot_sha256 THEN
        RAISE EXCEPTION 'approval must target a frozen pending version' USING ERRCODE='23514';
    END IF;
    IF EXISTS (SELECT 1 FROM publication_preparers
               WHERE version_id=NEW.version_id AND person_id=NEW.approver_person_id) THEN
        RAISE EXCEPTION 'preparer cannot approve or reject own version' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_approval_guard BEFORE INSERT ON publication_approvals
    FOR EACH ROW EXECUTE FUNCTION f3_guard_publication_approval();

CREATE FUNCTION f3_guard_current_publication() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.current_version_id IS NOT NULL AND
       NOT EXISTS (SELECT 1 FROM publication_versions
                   WHERE id=NEW.current_version_id AND publication_id=NEW.id AND status='PUBLISHED') THEN
        RAISE EXCEPTION 'current publication pointer requires a published version' USING ERRCODE='23514';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER tr_current_publication_guard BEFORE INSERT OR UPDATE ON publications
    FOR EACH ROW EXECUTE FUNCTION f3_guard_current_publication();

COMMIT;
