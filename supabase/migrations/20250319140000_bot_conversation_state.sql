-- Estado conversacional do bot Telegram (sobrevive a restart do Flask)

CREATE TABLE IF NOT EXISTS public.bot_conversation_state (
  telegram_id BIGINT PRIMARY KEY REFERENCES public.users (id) ON DELETE CASCADE,
  current_state TEXT,
  pending_intent TEXT,
  payload_json JSONB,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION public.set_bot_conversation_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_bot_conversation_updated_at ON public.bot_conversation_state;
CREATE TRIGGER trg_bot_conversation_updated_at
  BEFORE UPDATE ON public.bot_conversation_state
  FOR EACH ROW
  EXECUTE PROCEDURE public.set_bot_conversation_updated_at();

ALTER TABLE public.bot_conversation_state ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "dev_allow_all_bot_conversation_state" ON public.bot_conversation_state;
CREATE POLICY "dev_allow_all_bot_conversation_state"
  ON public.bot_conversation_state FOR ALL TO public
  USING (true) WITH CHECK (true);

GRANT ALL ON TABLE public.bot_conversation_state TO service_role, anon, authenticated;
