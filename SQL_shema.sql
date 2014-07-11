create schema public;

CREATE TABLE glasbenik (
uporabnisko_ime TEXT PRIMARY KEY,
ime TEXT,
priimek TEXT,
spol TEXT NOT NULL REFERENCES spol(spol),
e_mail TEXT NOT NULL,
leto_rojstva INTEGER NOT NULL
);

-- Dodatna tabela, ki smo jo pozabili prej naredit
CREATE TABLE glasbenik_igra_zanr (
glasbenik TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
igra_zanr TEXT NOT NULL REFERENCES zanr(ime) ON UPDATE CASCADE,
PRIMARY KEY (glasbenik, igra_zanr)
);

-- Glasbenik mora imeti mo�nost izbiranja med ve�imi �anri, zato ne more imeti atributa isce_skupino_ki_igra_zanr ker bi potem lahko izbral samo enega.
-- �e se izbri�e glasbenika, potem on ne i��e ve� skupine
CREATE TABLE glasbenik_isce_skupino (
glasbenik TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
zanr TEXT NOT NULL REFERENCES zanr(ime) ON UPDATE CASCADE,
PRIMARY KEY (glasbenik, zanr)
);

-- Glasbenik lahko izbere ve� ob�in v katerih lahko deluje.
CREATE TABLE glasbenik_deluje_v_okolici (
glasbenik TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
obcina TEXT NOT NULL REFERENCES obcina(ime) ON UPDATE CASCADE,
PRIMARY KEY (glasbenik, obcina)
);



CREATE TABLE igra_poje (
glasbenik TEXT REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
glasbilo TEXT REFERENCES tip_glasbila_ali_vokal(ime) ON UPDATE CASCADE,
stopnja_znanja TEXT NOT NULL REFERENCES stopnja_znanja(stopnja), -- na voljo bodo samo tri moznosti: beginner, intermediate, advanced
leto_zacetka INTEGER,
PRIMARY KEY (glasbenik, glasbilo)
);

-- Glede stvarnika skupine: lahko dovolimo, da se naredi skupine brez �lanov in se kasneje doda njene �lane (v neko novo tabelo). Tukej mormo mal pazit
-- na zaporedje vnosov v bazo - da bo folk lahko sploh naredu skupino (nevem �e se spomneta k je Bauer o tem govoru).
CREATE TABLE skupina(
ime TEXT PRIMARY KEY,
datum_ustanovitve DATE,
e_mail TEXT NOT NULL,
spletna_stran TEXT,
fb TEXT,
telefonska_stevilka INTEGER
);

-- Skupina lahko igra ve� �anrov, zato �anr ne more biti njen atribut. �e se kupino izbi�e, potem ona ne igra ve� nobenga �anra.
CREATE TABLE skupina_igra_zanr (
skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
igra_zanr TEXT NOT NULL REFERENCES zanr(ime) ON UPDATE CASCADE,
PRIMARY KEY (skupina, igra_zanr)
);

-- �lani skupine. �e se izbri�e skupino, nima ve� �lanov. �e se izbri�e glasbenika, ni ve� �lan skupine.
CREATE TABLE clani_skupine (
skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
clan TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (skupina, clan)
);

-- Glede delovanja skupine se men zdi smiselno da lahko skupina deluje v ve�ih ob�inah, ampak lahko tud popravmo to.
CREATE TABLE skupina_deluje_v_okolici (
skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
obcina TEXT NOT NULL REFERENCES obcina(ime) ON UPDATE CASCADE,
PRIMARY KEY (skupina, obcina)
);

-- �e se izbri�e skupino, potem ona ne i��e ve� glasbil.
CREATE TABLE skupina_isce(
skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
glasbilo TEXT NOT NULL REFERENCES tip_glasbila_ali_vokal(ime) ON UPDATE CASCADE,
spol TEXT REFERENCES spol(spol) ON UPDATE CASCADE DEFAULT 'vseeno', -- na voljo bo samo M, Z, vseeno
stevilo INTEGER DEFAULT 1, -- atribut pove, koliko glasbenikov igrajo� dolocen instrument, isce skupina.
PRIMARY KEY (skupina, glasbilo, spol)
);

-- Ob�ine ne moremo izbrisati, dokler obstaja vadnica, ki se nahaja v njej
CREATE TABLE vadnica (
id SERIAL PRIMARY KEY ,
e_mail TEXT NOT NULL,
telefonska_stevilka INTEGER,
ime TEXT,
se_nahaja_v TEXT NOT NULL REFERENCES obcina(ime) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Ob�ine ne moremo izbrisati, dokler obstaja koncertno prizorisce, ki se nahaja v njej
CREATE TABLE koncertno_prizorisce (
id SERIAL PRIMARY KEY,
e_mail TEXT NOT NULL,
telefonska_stevilka INTEGER,
ime TEXT,
se_nahaja_v TEXT NOT NULL REFERENCES obcina(ime) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Koncertnega prizori��a ne moremo izbrisati, �e obstaja event, ki se je odvijal tam.
CREATE TABLE event (
datum DATE NOT NULL,
ime TEXT NOT NULL,
prizorisce INTEGER REFERENCES koncertno_prizorisce(id) ON DELETE RESTRICT ON UPDATE CASCADE,
PRIMARY KEY (datum, ime)
);

-- Tukej nevem kaj bi blo najbl smiselno: �e se skupino izbri�e a se potem izbri�ejo tudi vsi eventi na katerih je igrala?
CREATE TABLE skupina_je_igrala (
skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
event_datum DATE NOT NULL,
event_ime TEXT NOT NULL,
FOREIGN KEY (event_datum, event_ime) REFERENCES event(datum, ime) ON DELETE CASCADE ON UPDATE CASCADE,
-- �e se izbri�e event, se izbi�e tudi vse skupine ki so igrale na tem eventu.
PRIMARY KEY (skupina, event_datum, event_ime)
);

-- FIKSIRANE TABELE

-- Na voljo bodo tri mo�nosti: M, Z, vseeno.
CREATE TABLE spol (
spol TEXT PRIMARY KEY
);

-- Na voljo bodo tri stopnje: beginner, intermediate, advanced.
CREATE TABLE stopnja_znanja (
stopnja TEXT PRIMARY KEY
);

-- Uporabniki bodo lahko izbirali med obstojecimi tipi glasbil.
CREATE TABLE tip_glasbila_ali_vokal (
ime TEXT PRIMARY KEY
);

-- Uporabniki bodo lahko izbirali med obstojecimi zanri.
CREATE TABLE zanr (
ime TEXT PRIMARY KEY
);

-- Seznam vseh slovenskih ob�in.
CREATE TABLE obcina (
ime TEXT PRIMARY KEY
);