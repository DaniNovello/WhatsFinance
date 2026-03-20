-- WhatsFinance: schema + RPCs usados por db.py
-- Rode no Supabase: SQL Editor → New query → colar → Run
-- Ou: supabase db push (se usar Supabase CLI)

-- Extensões úteis (opcional)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Usuários (ID = Telegram chat/user id)
CREATE TABLE IF NOT EXISTS public.users (
  id BIGINT PRIMARY KEY,
  name TEXT NOT NULL,
  verification_code TEXT,
  password_hash TEXT,
  verification_code_expires_at TIMESTAMPTZ,
  verification_attempts SMALLINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS public.accounts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES public.users (id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  balance NUMERIC(14, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS public.credit_cards (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES public.users (id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  closing_day INTEGER NOT NULL DEFAULT 1,
  due_day INTEGER NOT NULL DEFAULT 10
);

CREATE TABLE IF NOT EXISTS public.transactions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES public.users (id) ON DELETE CASCADE,
  description TEXT NOT NULL,
  amount NUMERIC(14, 2) NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
  payment_method TEXT,
  category TEXT,
  card_id BIGINT REFERENCES public.credit_cards (id) ON DELETE SET NULL,
  account_id BIGINT REFERENCES public.accounts (id) ON DELETE SET NULL,
  transaction_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON public.accounts (user_id);
CREATE INDEX IF NOT EXISTS idx_credit_cards_user_id ON public.credit_cards (user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON public.transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON public.transactions (user_id, transaction_date DESC);

-- Insere transação; opcionalmente conta + saldo e data (mesma regra de negócio centralizada)
CREATE OR REPLACE FUNCTION public.handle_transaction_and_update_balance(
  p_user_id BIGINT,
  p_description TEXT,
  p_amount NUMERIC,
  p_type TEXT,
  p_payment_method TEXT,
  p_category TEXT,
  p_card_id BIGINT,
  p_account_id BIGINT DEFAULT NULL,
  p_transaction_date TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  ins_ts TIMESTAMPTZ;
BEGIN
  ins_ts := NOW();
  IF p_transaction_date IS NOT NULL AND TRIM(p_transaction_date) <> '' THEN
    ins_ts := p_transaction_date::TIMESTAMPTZ;
  END IF;

  INSERT INTO public.transactions (
    user_id,
    description,
    amount,
    type,
    payment_method,
    category,
    card_id,
    account_id,
    transaction_date
  )
  VALUES (
    p_user_id,
    p_description,
    p_amount,
    p_type,
    p_payment_method,
    p_category,
    p_card_id,
    p_account_id,
    ins_ts
  );

  IF p_account_id IS NOT NULL THEN
    IF NOT EXISTS (
      SELECT 1 FROM public.accounts a
      WHERE a.id = p_account_id AND a.user_id = p_user_id
    ) THEN
      RAISE EXCEPTION 'account not found or wrong user';
    END IF;
    IF p_type = 'income' THEN
      UPDATE public.accounts SET balance = balance + p_amount WHERE id = p_account_id;
    ELSE
      UPDATE public.accounts SET balance = balance - p_amount WHERE id = p_account_id;
    END IF;
  END IF;
END;
$$;

-- Remove transação e reverte saldo da conta (se houver)
CREATE OR REPLACE FUNCTION public.delete_transaction_and_revert_balance(
  p_transaction_id BIGINT,
  p_user_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  t public.transactions%ROWTYPE;
BEGIN
  SELECT * INTO t
  FROM public.transactions
  WHERE id = p_transaction_id AND user_id = p_user_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'transaction not found';
  END IF;

  IF t.account_id IS NOT NULL THEN
    IF t.type = 'income' THEN
      UPDATE public.accounts
      SET balance = balance - t.amount
      WHERE id = t.account_id;
    ELSE
      UPDATE public.accounts
      SET balance = balance + t.amount
      WHERE id = t.account_id;
    END IF;
  END IF;

  DELETE FROM public.transactions
  WHERE id = p_transaction_id AND user_id = p_user_id;
END;
$$;

-- Atualiza transação e ajusta saldos de conta
CREATE OR REPLACE FUNCTION public.update_transaction_and_balance(
  p_transaction_id BIGINT,
  p_user_id BIGINT,
  p_description TEXT,
  p_amount NUMERIC,
  p_type TEXT,
  p_payment_method TEXT,
  p_category TEXT,
  p_account_id BIGINT,
  p_card_id BIGINT,
  p_date TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  old_row public.transactions%ROWTYPE;
  new_ts TIMESTAMPTZ;
BEGIN
  SELECT * INTO old_row
  FROM public.transactions
  WHERE id = p_transaction_id AND user_id = p_user_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'transaction not found';
  END IF;

  new_ts := old_row.transaction_date;
  IF p_date IS NOT NULL AND TRIM(p_date) <> '' THEN
    new_ts := p_date::TIMESTAMPTZ;
  END IF;

  -- Reverte efeito na conta antiga
  IF old_row.account_id IS NOT NULL THEN
    IF old_row.type = 'income' THEN
      UPDATE public.accounts SET balance = balance - old_row.amount WHERE id = old_row.account_id;
    ELSE
      UPDATE public.accounts SET balance = balance + old_row.amount WHERE id = old_row.account_id;
    END IF;
  END IF;

  UPDATE public.transactions
  SET
    description = p_description,
    amount = p_amount,
    type = p_type,
    payment_method = p_payment_method,
    category = p_category,
    account_id = p_account_id,
    card_id = p_card_id,
    transaction_date = new_ts
  WHERE id = p_transaction_id AND user_id = p_user_id;

  -- Aplica efeito na conta nova
  IF p_account_id IS NOT NULL THEN
    IF p_type = 'income' THEN
      UPDATE public.accounts SET balance = balance + p_amount WHERE id = p_account_id;
    ELSE
      UPDATE public.accounts SET balance = balance - p_amount WHERE id = p_account_id;
    END IF;
  END IF;
END;
$$;

-- Permissões: service_role (recomendado no backend) + anon/authenticated (ex.: dev com chave anon)
GRANT USAGE ON SCHEMA public TO postgres, service_role, anon, authenticated;

GRANT ALL ON TABLE public.users, public.accounts, public.credit_cards, public.transactions TO service_role;
GRANT ALL ON TABLE public.users, public.accounts, public.credit_cards, public.transactions TO anon, authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.handle_transaction_and_update_balance(BIGINT, TEXT, NUMERIC, TEXT, TEXT, TEXT, BIGINT, BIGINT, TEXT) TO service_role, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.delete_transaction_and_revert_balance(BIGINT, BIGINT) TO service_role, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.update_transaction_and_balance(BIGINT, BIGINT, TEXT, NUMERIC, TEXT, TEXT, TEXT, BIGINT, BIGINT, TEXT) TO service_role, anon, authenticated;

-- RLS ligado com policies permissivas só para desenvolvimento (troque por policies reais antes de produção)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dev_allow_all_users" ON public.users FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY "dev_allow_all_accounts" ON public.accounts FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY "dev_allow_all_credit_cards" ON public.credit_cards FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY "dev_allow_all_transactions" ON public.transactions FOR ALL TO public USING (true) WITH CHECK (true);
