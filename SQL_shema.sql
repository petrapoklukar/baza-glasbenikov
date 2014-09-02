-- Ali je treba pri REFERENCES zanr/obcina/.. dodati tudi CHECK ki bo preveril a je vnos pravilen?

CREATE TABLE glasbenik (
	uporabnisko_ime TEXT PRIMARY KEY,
	ime TEXT, 
	priimek TEXT,
	spol TEXT NOT NULL, 
	e_mail TEXT NOT NULL,
	leto_rojstva INTEGER NOT NULL
	geslo TEXT NOT NULL
);


-- Dodatna tabela, ki smo jo pozabili prej naredit
CREATE TABLE glasbenik_igra_zanr (
glasbenik TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
igra_zanr TEXT NOT NULL REFERENCES zanr(ime) ON UPDATE CASCADE,
PRIMARY KEY (glasbenik, igra_zanr)
);


-- Glasbenik mora imeti možnost izbiranja med večimi žanri, zato ne more imeti atributa isce_skupino_ki_igra_zanr ker bi potem lahko izbral samo enega. 
-- Če se izbriše glasbenika, potem on ne išče več skupine
CREATE TABLE glasbenik_isce_skupino (
	glasbenik TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
	zanr TEXT NOT NULL REFERENCES zanr(ime) ON UPDATE CASCADE,
	PRIMARY KEY (glasbenik, zanr)
);



-- Glasbenik lahko izbere več občin v katerih lahko deluje. 
CREATE TABLE glasbenik_deluje_v_okolici (
	glasbenik TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
	obcina TEXT NOT NULL REFERENCES obcina(ime) ON UPDATE CASCADE,
	PRIMARY KEY (glasbenik, obcina)
);


CREATE TABLE model ( --popravek šibka entiteta
	ime TEXT NOT NULL, -- del primarnega ključa 
	lastnik TEXT REFERENCES glasbenik(uporabnisko_ime)
		ON DELETE CASCADE -- če se uporabnik izbriše, tudi glasbilo ni več na voljo
		ON UPDATE CASCADE,
	vrsta_glasbila TEXT REFERENCES tip_glasbila_ali_vokal(ime)
		ON UPDATE CASCADE,	
	za_izposojo BOOLEAN,
	PRIMARY KEY(ime, lastnik)
);


CREATE TABLE igra_poje (
	glasbenik TEXT REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
	glasbilo TEXT REFERENCES tip_glasbila_ali_vokal(ime) ON UPDATE CASCADE,
	stopnja_znanja TEXT NOT NULL REFERENCES stopnja_znanja(stopnja), -- na voljo bodo samo tri moznosti: beginner, intermediate, advanced
	leto_zacetka INTEGER,
	PRIMARY KEY (glasbenik, glasbilo)
);



-- Glede stvarnika skupine: lahko dovolimo, da se naredi skupine brez članov in se kasneje doda njene člane (v neko novo tabelo). Tukej mormo mal pazit 
-- na zaporedje vnosov v bazo - da bo folk lahko sploh naredu skupino (nevem če se spomneta k je Bauer o tem govoru).
CREATE TABLE skupina(
	ime TEXT PRIMARY KEY,
	datum_ustanovitve DATE,
	e_mail TEXT NOT NULL,
	spletna_stran TEXT,
	fb TEXT,
	telefonska_stevilka INTEGER
);


-- Skupina lahko igra več žanrov, zato žanr ne more biti njen atribut. Če se kupino izbiše, potem ona ne igra več nobenga žanra.
CREATE TABLE skupina_igra_zanr (
	skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
	igra_zanr TEXT NOT NULL REFERENCES zanr(ime) ON UPDATE CASCADE,
	PRIMARY KEY (skupina, igra_zanr)
);


-- Glasbenik je lahko član večih skupin, zato tudi ne more imeti atributa je_clan. Če se izbriše glasbenika, ni več član skupine, Če se izbriše skupino, potem
-- ne more biti nihče njen član.
-- Člani skupine. Če se izbriše skupino, nima več članov. Če se izbriše glasbenika, ni več član skupine.
CREATE TABLE clani_skupine (
	skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
	clan TEXT NOT NULL REFERENCES glasbenik(uporabnisko_ime) ON DELETE CASCADE ON UPDATE CASCADE,
	glasbilo TEXT NOT NULL REFERENCES tip_glasbila_ali_vokal(ime) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY (skupina, clan, glasbilo)
);


-- Glede delovanja skupine se men zdi smiselno da lahko skupina deluje v večih občinah, ampak lahko tud popravmo to.
CREATE TABLE skupina_deluje_v_okolici (
	skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
	obcina TEXT NOT NULL REFERENCES obcina(ime) ON UPDATE CASCADE,
	PRIMARY KEY (skupina, obcina)
);

-- Če se izbriše skupino, potem ona ne išče več glasbil.
CREATE TABLE skupina_isce(
	skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
	glasbilo TEXT NOT NULL REFERENCES tip_glasbila_ali_vokal(ime) ON UPDATE CASCADE,
	spol TEXT REFERENCES spol(spol) ON UPDATE CASCADE DEFAULT 'vseeno', -- na voljo bo samo M, Z, vseeno
	stevilo INTEGER DEFAULT 1, -- atribut pove, koliko glasbenikov igrajoč dolocen instrument, isce skupina. 
	PRIMARY KEY (skupina, glasbilo,spol)
);

-- Občine ne moremo izbrisati, dokler obstaja vadnica, ki se nahaja v njej
CREATE TABLE vadnica (
	id SERIAL PRIMARY KEY , 
	e_mail TEXT NOT NULL, 
	telefonska_stevilka INTEGER, 
	ime TEXT,
	se_nahaja_v TEXT NOT NULL REFERENCES obcina(ime) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Občine ne moremo izbrisati, dokler obstaja koncertno prizorisce, ki se nahaja v njej
CREATE TABLE koncertno_prizorisce (
	id SERIAL PRIMARY KEY,
	e_mail TEXT NOT NULL, 
	telefonska_stevilka INTEGER, 
	ime TEXT, 
	se_nahaja_v TEXT NOT NULL REFERENCES obcina(ime) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Koncertnega prizorišča ne moremo izbrisati, če obstaja event, ki se je odvijal tam.
CREATE TABLE event (
	datum DATE NOT NULL, 
	ime TEXT NOT NULL, 
	prizorisce INTEGER REFERENCES koncertno_prizorisce(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	PRIMARY KEY (datum, ime)
);

-- Tukej nevem kaj bi blo najbl smiselno: če se skupino izbriše a se potem izbrišejo tudi vsi eventi na katerih je igrala?
CREATE TABLE skupina_je_igrala (
	skupina TEXT NOT NULL REFERENCES skupina(ime) ON DELETE CASCADE ON UPDATE CASCADE,
	event_datum DATE NOT NULL,
	event_ime TEXT NOT NULL,
	FOREIGN KEY (event_datum, event_ime) REFERENCES event(datum, ime) ON DELETE CASCADE ON UPDATE CASCADE, 
	-- če se izbriše event, se izbiše tudi vse skupine ki so igrale na tem eventu.
	PRIMARY KEY (skupina, event_datum, event_ime)
);

-- FIKSIRANE TABELE

-- Na voljo bodo tri možnosti: M, Z, vseeno.
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

-- Seznam vseh slovenskih občin. 
CREATE TABLE obcina (
	ime TEXT PRIMARY KEY
);