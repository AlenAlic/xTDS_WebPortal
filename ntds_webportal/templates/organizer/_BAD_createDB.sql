-- create DB for BAD
-- DB format: 0300

-- start from zero
DROP   DATABASE IF EXISTS `BADdb`;
CREATE DATABASE `BADdb`;
use             `BADdb`;

-- a known dancing discipline (well, usually just "Latin" and "Ballroom"...)
CREATE TABLE `discipline` (
  `id`   INTEGER(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a known class (like "B Class" or "Amateurs" or "Open")
CREATE TABLE `class` (
  `id` INTEGER(11)   NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a known dance
CREATE TABLE `dance` (
  `id`   INTEGER(2)  NOT NULL AUTO_INCREMENT,  
  `name` VARCHAR(64) NOT NULL,
  `tag`  VARCHAR(4)  NOT NULL,
  `disc` INTEGER(11) NOT NULL,                  -- --> discipline
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- event (like ETDS 05/2016)
CREATE TABLE `event` (
  `id`   INTEGER(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- tournament (like Amateurs Ballroom) (may link to its qualification "tournament")
CREATE TABLE `tournament` (
  `id`        INTEGER(11) NOT NULL AUTO_INCREMENT,
  `class`     INTEGER(11) NOT NULL,                           -- --> class
  `disc`      INTEGER(11) NOT NULL,                           -- --> discipline
  `event`     INTEGER(11) NOT NULL,                           -- --> event
  `quali`     INTEGER(11) NULL DEFAULT NULL,                  -- --> tournament
  `when`      DATETIME    NOT NULL,
  `mode`      ENUM('SP','CP_R','CP_D','CP_T') NOT NULL DEFAULT 'SP', -- single partner, change per round/dance/tournament
  `iscpt`     SMALLINT(1) NOT NULL DEFAULT 0,                 -- 1 for CP_T tournaments (mode changes to SP *after* lottery!)   
  `floormin`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- only requried for multi-floor heats (1 means A, 0 means single-floor)
  `floormax`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- only requried for multi-floor heats (1 means A, 0 means single-floor)
  `numberls`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- number stack for leaders or !CP: set id (each number used at most once per set id)
  `numberl0`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- number stack for leaders or !CP: min number
  `numberl1`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- number stack for leaders or !CP: max number
  `numberfs`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- number stack for followers (CP): set id (each number used at most once per set id)
  `numberf0`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- number stack for followers (CP): min number
  `numberf1`  INTEGER(4)  NOT NULL DEFAULT 0,                 -- number stack for followers (CP): max number
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a round of a single tournament
CREATE TABLE `round` (
  `id`      INTEGER(11)                NOT NULL AUTO_INCREMENT,
  `tourn`   INTEGER(11)                NOT NULL,  -- --> tournament
  `type`    ENUM('FR','IR','RD','SF','FIN') NOT NULL,
  `no`      INTEGER(2)                 NOT NULL,
  `pmin`    INTEGER(4)                 NOT NULL,
  `pmax`    INTEGER(4)                 NOT NULL,
  `mmin`    INTEGER(4)                 NOT NULL,
  `mmax`    INTEGER(4)                 NOT NULL,
  `active`  INTEGER(11)                NOT NULL,  -- --> dance: bit mask of danceno's, bit 0 set iff MMI generally active
  `closed`  SMALLINT(1)                NOT NULL,  -- meaning that judging has finished for this round    
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- assign a dance to a tournament
CREATE TABLE `t_dance` (
  `id`      INTEGER(11)   NOT NULL AUTO_INCREMENT,
  `dance`   INTEGER(11)   NOT NULL,       -- --> dance
  `tourn`   INTEGER(11)   NOT NULL,       -- --> tournament
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- assign a dance to a round of a tournament
CREATE TABLE `r_dance` (
  `id`      INTEGER(11) NOT NULL AUTO_INCREMENT,
  `dance`   INTEGER(11) NOT NULL,         -- --> dance
  `round`   INTEGER(11) NOT NULL,         -- --> round
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a team may designate a club, university, or city
CREATE TABLE `team` (
  `id`      INTEGER(11)   NOT NULL AUTO_INCREMENT,
  `name`    VARCHAR(64)   NOT NULL,
  `joined`  INTEGER(11)   NOT NULL DEFAULT 0,  -- --> team (indicating joined team, 0 ^= id)
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a person who may be part of a couple, and/or a staff member
CREATE TABLE `person` (
  `id`       INTEGER(11)   NOT NULL AUTO_INCREMENT,
  `fname`    VARCHAR(64)   NOT NULL,
  `name`     VARCHAR(64)   NOT NULL,
  `team`     INTEGER(11)   NOT NULL,           -- --> team
  `email`    VARCHAR(64)   NULL DEFAULT NULL,
  `comment`  VARCHAR(255)  NULL DEFAULT NULL,
  `secret`   VARCHAR(64)   NULL DEFAULT NULL,
  -- from here: columns mainly for ETDS registration
  `fee`      DECIMAL(8,2)  NULL DEFAULT NULL,  -- participation fee, in EUR
  `student`  SMALLINT(1)   NULL DEFAULT NULL,  -- 1: is a student
  `newcomer` SMALLINT(1)   NULL DEFAULT NULL,  -- 1: is a newcomer (1st ETDS)
  `helper`   SMALLINT(1)   NULL DEFAULT NULL,  -- 1: offers to help during the event
  `etdsbs`   SMALLINT(1)   NULL DEFAULT NULL,  -- 1: has ever danced BS @ ETDS
  `lastbs`   INTEGER(4)    NULL DEFAULT NULL,  -- last year to have danced BS formerly 
  `monday`   SMALLINT(1)   NULL DEFAULT NULL,  -- 1: joins breakfast on Monday
  `nosleep`  SMALLINT(1)   NULL DEFAULT NULL,  -- 1: does NOT sleep in the ETDS location
  `veggie`   SMALLINT(1)   NULL DEFAULT NULL,  -- 1: vegetarian food
  `cups`     SMALLINT(1)   NULL DEFAULT NULL,  -- number of cups bought
  `towels`   SMALLINT(1)   NULL DEFAULT NULL,  -- number of towels bought
  `shirts`   SMALLINT(1)   NULL DEFAULT NULL,  -- number of shirts bought
  `stype`    VARCHAR(20)   NULL DEFAULT NULL,  -- type of shirts
  `class_b`  VARCHAR(20)   NULL DEFAULT NULL,  -- starting class ballroom
  `class_l`  VARCHAR(20)   NULL DEFAULT NULL,  -- starting class latin
  `want2a_b` SMALLINT(1)   NULL DEFAULT NULL,  -- 1: wants to adjudicate ballroom
  `want2a_l` SMALLINT(1)   NULL DEFAULT NULL,  -- 1: wants to adjudicate latin
  `adlic_b`  VARCHAR(20)   NULL DEFAULT NULL,  -- adjudicators' license for ballroom
  `adlic_l`  VARCHAR(20)   NULL DEFAULT NULL,  -- adjudicators' license for latin
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- team payments (ETDS registration only)
CREATE TABLE `payment` (
  `id`       INTEGER(11)   NOT NULL AUTO_INCREMENT,
  `team`     INTEGER(11)   NOT NULL,          -- --> team
  `euro`     DECIMAL(8,2)  NOT NULL,          -- amount of payment, in EUR
  `day`      DATE          NOT NULL,          -- date of transaction
  `text`     VARCHAR(255)  NULL DEFAULT NULL, -- transaction text
  PRIMARY KEY (`id`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- additional information for a person who belongs to "the team" (ATT: id shared with person!)
-- persons registered here may log in (provided they have a password)
CREATE TABLE `staff` (
  `id`       INTEGER(11)  NOT NULL AUTO_INCREMENT,
  `tag`      VARCHAR(64)   NOT NULL,
  `password` VARCHAR(64)  NOT NULL,           -- encoded with SHA1(<pw>)
  `comment`  VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag` (`tag`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- assign a staff member to a certain tournament (and possibly a certain floor)
CREATE TABLE `employ` (
  `role`  ENUM('adjudicator','captain','admin','chair','scrutineer','support') NOT NULL,
  `who`   INTEGER(11) NOT NULL,            -- --> person/staff 
  `tourn` INTEGER(11) NOT NULL DEFAULT 0,  -- --> tournament (relevant for all roles except admin; judicator(tourn=0) means w/o assignment
  `floor` INTEGER(2)  NOT NULL DEFAULT 0,  -- only relevant for role adjudicator; 0 for single-floor      
  `round` INTEGER(11) NOT NULL DEFAULT 0,  -- only relevant for role adjudicator; last round shown in MMI
  `dance` INTEGER(11) NOT NULL DEFAULT 0,  -- only relevant for role adjudicator; last dance shown in MMI
  PRIMARY KEY (`role`,`tourn`,`who`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a start may be EITHER a couple (in case of a tournament with single partner: SP) OR a single dancer (in case of a tournament with changing partners: CP)
-- INV 1: dancing                          => (lead != NULL,follow != NULL) matches tournament.mode
-- INV 2: dancing AND (tournament started) => startno != NULL
CREATE TABLE `start` (
  `id`      INTEGER(11) NOT NULL AUTO_INCREMENT,
  `tourn`   INTEGER(11) NOT NULL,           -- --> tournament
  `lead`    INTEGER(11) NULL DEFAULT NULL,  -- --> person (CP: lead XOR follow is NULL)
  `follow`  INTEGER(11) NULL DEFAULT NULL,  -- --> person (CP: lead XOR follow is NULL)
  `startno` INTEGER(4)  NULL DEFAULT NULL,  -- every start has a number -- except CP_T followers(!)
  `dancing` SMALLINT(1) NOT NULL DEFAULT 1, -- 0=missing/dropped/not yet present 1=starting
  PRIMARY KEY (`id`),
  UNIQUE KEY `leader`   (`tourn`,`lead`),
  UNIQUE KEY `follower` (`tourn`,`follow`),
  UNIQUE KEY `number`   (`tourn`,`startno`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- an exception rule from partner lottery (for known/same team/usual partners)
CREATE TABLE `exclude` (
  `lead`    INTEGER(11) NOT NULL,           -- --> start
  `follow`  INTEGER(11) NOT NULL,           -- --> start
  PRIMARY KEY (`lead`,`follow`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a single heat assignment for a certain starter in a certain round (also covers changing-partner assignment)
CREATE TABLE `heat` (
  `id`      INTEGER(11) NOT NULL AUTO_INCREMENT,
  `start`   INTEGER(11) NOT NULL,                           -- --> start 
  `other`   INTEGER(11) NOT NULL,                           -- --> start (!CP: == start)
  `role`    ENUM('lead','follow') NOT NULL DEFAULT 'lead',	-- !CP: using 'lead' only
  `dance`   INTEGER(11) NOT NULL,                           -- --> dance
  `round`   INTEGER(11) NOT NULL,                           -- --> round
  `no`      INTEGER(3)  NOT NULL,    
  `floor`   INTEGER(2)  NOT NULL DEFAULT 0, 
  `check`   INTEGER(1)  NOT NULL DEFAULT 0,                 -- for floor management & moderator (info only)
  PRIMARY KEY (`id`),
  UNIQUE KEY `all` (`round`, `dance`, `start`, `other`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a placing of a certain starter after a certain round (starts already dropped to be copied into later rounds!)
CREATE TABLE `placing` (
  `start`   INTEGER(11)  NOT NULL,   						            -- --> start
  `round`   INTEGER(11)  NOT NULL,   						            -- --> round
  `role`    ENUM('lead','follow') NOT NULL DEFAULT 'lead',	-- !CP: using 'lead'
  `min`     INTEGER(4)   NOT NULL,
  `max`     INTEGER(4)   NOT NULL,
  `val`     DECIMAL(4,1) NULL DEFAULT NULL,
  PRIMARY KEY (`round`,`start`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- a single final mark for a certain start in a certain dance from a certain judicator
-- used for both prior and final rounds, created together with round 
CREATE TABLE `mark` (
  `start`   INTEGER(11) NOT NULL,             -- --> start
  `judi`    INTEGER(11) NOT NULL,             -- --> staff/person  
  `dance`   INTEGER(11) NOT NULL,             -- --> dance 
  `round`   INTEGER(11) NOT NULL,             -- --> round
  `mark`    INTEGER(2)  NOT NULL DEFAULT 0,   -- only 0/1 in case of on elimination round! 
  PRIMARY KEY (`dance`,`round`,`judi`,`start`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- placing of a single final dance (only created during final adjudication)
CREATE TABLE `fin_dance` (
  `start`   INTEGER(11)  NOT NULL,   -- --> start
  `dance`   INTEGER(11)  NOT NULL,   -- --> dance 
  `round`   INTEGER(11)  NOT NULL,   -- --> round
  `val`     DECIMAL(4,1) NOT NULL,   -- placing for this final dance (mean value if shared) 
  PRIMARY KEY (`round`,`start`,`dance`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';

-- skating rule application log (for reporting only)
CREATE TABLE `skating` (
  `start`   INTEGER(11)  NOT NULL,   -- --> start
  `round`   INTEGER(11)  NOT NULL,   -- --> round
  `rule`    INTEGER(2)   NOT NULL,   -- 10 or 11
  `ptarget` INTEGER(4)   NOT NULL,   -- target place (pmin) of rule application
  `pref`    INTEGER(4)   NOT NULL,   -- reference (examined) place
  `num`     INTEGER(4)   NOT NULL,   -- number of hits
  `sum`     DECIMAL(6,1) NOT NULL,   -- sum of values
  PRIMARY KEY (`round`,`ptarget`,`rule`,`pref`,`start`)
) ENGINE=InnoDB
AUTO_INCREMENT=1 CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
