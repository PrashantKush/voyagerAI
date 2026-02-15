-- OPTION A (recommended): Use the service_role key in your backend env vars.
-- It bypasses RLS, so no policy is needed.
-- Supabase Dashboard → Settings → API → "service_role" (secret) → copy.
-- Set SUPABASE_KEY to that value in Render (and in .env locally). Do not use in frontend.

-- OPTION B: If you must use the anon key, run the following in SQL Editor:

-- Ensure RLS is on and we have an INSERT policy for anon
ALTER TABLE trip_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow anon insert trip_logs" ON trip_logs;
DROP POLICY IF EXISTS "Allow anon to insert trip_logs" ON trip_logs;

CREATE POLICY "Allow anon insert trip_logs"
ON public.trip_logs
FOR INSERT
TO anon
WITH CHECK (true);
