-- Unifica INSERT de transação com ajuste de saldo da conta (mesma regra que update/delete)
-- Substitui assinatura antiga (7 args) pela versão com p_account_id e p_transaction_date opcionais.

DROP FUNCTION IF EXISTS public.handle_transaction_and_update_balance(BIGINT, TEXT, NUMERIC, TEXT, TEXT, TEXT, BIGINT);

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

GRANT EXECUTE ON FUNCTION public.handle_transaction_and_update_balance(BIGINT, TEXT, NUMERIC, TEXT, TEXT, TEXT, BIGINT, BIGINT, TEXT) TO service_role, anon, authenticated;
