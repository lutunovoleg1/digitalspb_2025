pg_dump: warning: there are circular foreign-key constraints on this table:
pg_dump: detail: hypertable
pg_dump: hint: You might not be able to restore the dump without using --disable-triggers or temporarily dropping the constraints.
pg_dump: hint: Consider using a full dump instead of a --data-only dump to avoid this problem.
pg_dump: warning: there are circular foreign-key constraints on this table:
pg_dump: detail: chunk
pg_dump: hint: You might not be able to restore the dump without using --disable-triggers or temporarily dropping the constraints.
pg_dump: hint: Consider using a full dump instead of a --data-only dump to avoid this problem.
pg_dump: warning: there are circular foreign-key constraints on this table:
pg_dump: detail: continuous_agg
pg_dump: hint: You might not be able to restore the dump without using --disable-triggers or temporarily dropping the constraints.
pg_dump: hint: Consider using a full dump instead of a --data-only dump to avoid this problem.
--
-- PostgreSQL database dump
--

-- Dumped from database version 15.12 (Ubuntu 15.12-1.pgdg22.04+1)
-- Dumped by pg_dump version 15.12 (Ubuntu 15.12-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: timescaledb; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS timescaledb WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION timescaledb IS 'Enables scalable inserts and complex queries for time-series data (Community Edition)';


--
-- Name: timescaledb_toolkit; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS timescaledb_toolkit WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb_toolkit; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION timescaledb_toolkit IS 'Library of analytical hyperfunctions, time-series pipelining, and other SQL utilities';


--
-- Name: manage_device_stats_and_readings(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.manage_device_stats_and_readings() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- ╨Я╨╛╨┐╤Л╤В╨║╨░ ╤Г╨▓╨╡╨╗╨╕╤З╨╕╤В╤М record_count
    UPDATE device_stats
    SET record_count = record_count + 1
    WHERE device_id = NEW.device_id;

    -- ╨Х╤Б╨╗╨╕ ╨╜╨╡ ╨╜╨░╤И╨╗╨╕ тАФ ╨┤╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╨╜╨╛╨▓╤Г╤О ╨╖╨░╨┐╨╕╤Б╤М
    IF NOT FOUND THEN
        INSERT INTO device_stats (device_id, record_count)
        VALUES (NEW.device_id, 1);
    END IF;

    -- ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨╜╨░ 337 ╨╖╨░╨┐╨╕╤Б╤М
    PERFORM record_count
    FROM device_stats
    WHERE device_id = NEW.device_id
    AND record_count = 337;

    IF FOUND THEN
        -- ╨г╨╝╨╡╨╜╤М╤И╨░╨╡╨╝ ╨╛╨▒╤А╨░╤В╨╜╨╛
        UPDATE device_stats
        SET record_count = 336
        WHERE device_id = NEW.device_id;

        -- ╨г╨┤╨░╨╗╤П╨╡╨╝ ╤Б╨░╨╝╤Г╤О ╤Б╤В╨░╤А╤Г╤О ╨╖╨░╨┐╨╕╤Б╤М
        DELETE FROM readings
        WHERE time = (
            SELECT MIN(time)
            FROM readings
            WHERE device_id = NEW.device_id
        )
        AND device_id = NEW.device_id;
    END IF;

    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: readings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.readings (
    "time" timestamp without time zone NOT NULL,
    device_id text NOT NULL,
    a_plus numeric(6,3),
    a_minus numeric(6,3),
    r_plus numeric(6,3),
    r_minus numeric(6,3)
);


--
-- Name: _hyper_1_1_chunk; Type: TABLE; Schema: _timescaledb_internal; Owner: -
--

CREATE TABLE _timescaledb_internal._hyper_1_1_chunk (
    CONSTRAINT constraint_1 CHECK ((("time" >= '2025-04-24 00:00:00'::timestamp without time zone) AND ("time" < '2025-05-01 00:00:00'::timestamp without time zone)))
)
INHERITS (public.readings);


--
-- Name: device_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_stats (
    device_id text NOT NULL,
    record_count integer DEFAULT 0 NOT NULL
);


--
-- Name: _hyper_1_1_chunk 1_1_readings_pkey; Type: CONSTRAINT; Schema: _timescaledb_internal; Owner: -
--

ALTER TABLE ONLY _timescaledb_internal._hyper_1_1_chunk
    ADD CONSTRAINT "1_1_readings_pkey" PRIMARY KEY (device_id, "time");


--
-- Name: device_stats device_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_stats
    ADD CONSTRAINT device_stats_pkey PRIMARY KEY (device_id);


--
-- Name: readings readings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.readings
    ADD CONSTRAINT readings_pkey PRIMARY KEY (device_id, "time");


--
-- Name: _hyper_1_1_chunk_readings_device_id_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_1_chunk_readings_device_id_time_idx ON _timescaledb_internal._hyper_1_1_chunk USING btree (device_id, "time" DESC);


--
-- Name: _hyper_1_1_chunk_readings_time_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: -
--

CREATE INDEX _hyper_1_1_chunk_readings_time_idx ON _timescaledb_internal._hyper_1_1_chunk USING btree ("time" DESC);


--
-- Name: readings_device_id_time_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX readings_device_id_time_idx ON public.readings USING btree (device_id, "time" DESC);


--
-- Name: readings_time_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX readings_time_idx ON public.readings USING btree ("time" DESC);


--
-- Name: _hyper_1_1_chunk trg_manage_device_stats_and_readings; Type: TRIGGER; Schema: _timescaledb_internal; Owner: -
--

CREATE TRIGGER trg_manage_device_stats_and_readings AFTER INSERT ON _timescaledb_internal._hyper_1_1_chunk FOR EACH ROW EXECUTE FUNCTION public.manage_device_stats_and_readings();


--
-- Name: readings trg_manage_device_stats_and_readings; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_manage_device_stats_and_readings AFTER INSERT ON public.readings FOR EACH ROW EXECUTE FUNCTION public.manage_device_stats_and_readings();


--
-- Name: readings ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.readings FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();


--
-- PostgreSQL database dump complete
--

