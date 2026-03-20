-- Código de verificação: expiração + contador de tentativas

ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS verification_code_expires_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS verification_attempts SMALLINT NOT NULL DEFAULT 0;
