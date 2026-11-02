-- Rollback WhatsApp-specific columns (safe if never applied).
DROP INDEX IF EXISTS idx_assistant_chat_message_whatsapp_ctx;

ALTER TABLE assistant_chat_message
  DROP COLUMN IF EXISTS wa_from,
  DROP COLUMN IF EXISTS customer_id;
