-- Use Gemini-aligned role name for assistant replies (not legacy "assistant").
UPDATE assistant_chat_message
SET role = 'model'
WHERE role = 'assistant';

COMMENT ON COLUMN assistant_chat_message.role IS 'user | model (Gemini turn roles; legacy assistant migrated to model)';
