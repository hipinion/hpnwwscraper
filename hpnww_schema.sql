--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: faction; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE faction AS ENUM (
    'werewolf',
    'vampire',
    'village',
    'neutral',
    'switchable',
    'moderator',
    'nonentity'
);


--
-- Name: vote_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE vote_type AS ENUM (
    'lynch',
    'no kill',
    'rescind',
    'mayor',
    'rescind mayor',
    'non standard'
);


SET default_with_oids = false;

--
-- Name: player; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE player (
    name text NOT NULL,
    role text,
    status text
);


--
-- Name: player_faction; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE player_faction (
    player text,
    faction faction,
    when_known timestamp without time zone
);


--
-- Name: post; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE post (
    player text,
    "time" timestamp with time zone,
    content text,
    thread_sequence integer NOT NULL
);


--
-- Name: role; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE role (
    name text NOT NULL,
    faction faction
);


--
-- Name: vote; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE vote (
    post integer NOT NULL,
    player_for text NOT NULL,
    type vote_type NOT NULL,
    context text
);


--
-- Name: player_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY player
    ADD CONSTRAINT player_pkey PRIMARY KEY (name);


--
-- Name: post_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY post
    ADD CONSTRAINT post_pkey PRIMARY KEY (thread_sequence);


--
-- Name: role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY role
    ADD CONSTRAINT role_pkey PRIMARY KEY (name);


--
-- Name: vote_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vote
    ADD CONSTRAINT vote_pkey PRIMARY KEY (post, type, player_for);


--
-- Name: pf_player_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY player_faction
    ADD CONSTRAINT pf_player_fk FOREIGN KEY (player) REFERENCES player(name);


--
-- Name: player_role_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY player
    ADD CONSTRAINT player_role_fk FOREIGN KEY (role) REFERENCES role(name);


--
-- Name: post_player_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY post
    ADD CONSTRAINT post_player_fk FOREIGN KEY (player) REFERENCES player(name);


--
-- Name: vote_player_for_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vote
    ADD CONSTRAINT vote_player_for_fk FOREIGN KEY (player_for) REFERENCES player(name);


--
-- Name: vote_post_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY vote
    ADD CONSTRAINT vote_post_fk FOREIGN KEY (post) REFERENCES post(thread_sequence);


--
-- PostgreSQL database dump complete
--

