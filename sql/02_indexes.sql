--Secondary indexes on foriegn keys.
CREATE INDEX idx_wallet_audit_logs_client_id ON wallet_audit_logs (client_id);
CREATE INDEX idx_contracts_client_id ON contracts (client_id);
CREATE INDEX idx_contracts_freelancer_id ON contracts (freelancer_id);

--Composite index for workflow 2 optimizations
CREATE INDEX idx_contracts_freelancer_id_created_at ON contracts (freelancer_id, created_at);

--Partial indexes
CREATE UNIQUE INDEX idx_active_gig ON contracts(freelancer_id) WHERE status = 'IN_PROGRESS';
CREATE INDEX idx_completed_gig ON contracts (freelancer_id) WHERE status = 'COMPLETED';