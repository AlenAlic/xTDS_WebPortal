{% import "organizer/_BAD_variables.sql" as var -%}
USE `BADdb`;

-- Define the event itself
INSERT INTO `event` SET `id` = 1, `name` = "ETDS 2018 Brno";

-- Define the different teams competing in tournament
-- Organization team
INSERT INTO `team` SET `id` = {{ var.team_organization }}, `name` = "ORGANIZATION";
-- Other teams
{%- for team in teams %}
INSERT INTO `team` SET `id` = {{ team.team_id }}, `name` = "{{ team.name }} ({{team.city}})";
{%- endfor %}

-- BAD team
-- Users
INSERT INTO `person` SET `id` = {{ var.id_root }}, `fname` = "Root", `name` = "Admin", `team` = {{ var.team_organization }};
INSERT INTO `person` SET `id` = {{ var.id_manager }}, `fname` = "BAD", `name` = "manager", `team` = {{ var.team_organization }};
INSERT INTO `person` SET `id` = {{ var.id_assistant }}, `fname` = "BAD", `name` = "assistant", `team` = {{ var.team_organization }};
INSERT INTO `person` SET `id` = {{ var.id_floor1 }}, `fname` = "Floor1", `name` = "Manager", `team` = {{ var.team_organization }};
INSERT INTO `person` SET `id` = {{ var.id_floor2 }}, `fname` = "Floor2", `name` = "Manager", `team` = {{ var.team_organization }};
INSERT INTO `person` SET `id` = {{ var.id_floor3 }}, `fname` = "Floor3", `name` = "Manager", `team` = {{ var.team_organization }};
-- User login codes
INSERT INTO `staff` SET `id` = {{ var.id_root }}, `tag` = "rt", `password` = SHA1("root");
INSERT INTO `staff` SET `id` = {{ var.id_manager }}, `tag` = "BADm", `password` = SHA1("etds");
INSERT INTO `staff` SET `id` = {{ var.id_assistant }}, `tag` = "BADa", `password` = SHA1("etds");
INSERT INTO `staff` SET `id` = {{ var.id_floor1 }}, `tag` = "F1", `password` = SHA1("floor");
INSERT INTO `staff` SET `id` = {{ var.id_floor2 }}, `tag` = "F2", `password` = SHA1("floor");
INSERT INTO `staff` SET `id` = {{ var.id_floor3 }}, `tag` = "F3", `password` = SHA1("floor");
-- User jobs
INSERT INTO `employ` SET `role` = "admin" , `who` = {{ var.id_root }};
INSERT INTO `employ` SET `role` = "admin" , `who` = {{ var.id_manager }};
INSERT INTO `employ` SET `role` = "admin" , `who` = {{ var.id_assistant }};
{%- for tourn in var.tournament_list %}
INSERT INTO `employ` SET `role` = "support" , `who` = {{ var.id_floor1 }}, `tourn` = {{ tourn }};
INSERT INTO `employ` SET `role` = "support" , `who` = {{ var.id_floor2 }}, `tourn` = {{ tourn }};
INSERT INTO `employ` SET `role` = "support" , `who` = {{ var.id_floor3 }}, `tourn` = {{ tourn }};
{%- endfor %}

-- Define the different disciplines
INSERT INTO `discipline` SET `id` = {{ var.discipline_Ballroom }}, `name` = "Ballroom";
INSERT INTO `discipline` SET `id` = {{ var.discipline_Latin }}, `name` = "Latin";
INSERT INTO `discipline` SET `id` = {{ var.discipline_Salsa }}, `name` = "Salsa";
INSERT INTO `discipline` SET `id` = {{ var.discipline_Polka }}, `name` = "Polka";

-- Define the different classes
INSERT INTO `class` SET `id` = {{ var.class_Breitensport_qualification }}, `name` = "Breitensport (Qualification)";
INSERT INTO `class` SET `id` = {{ var.class_Breitensport_Amateurs }}, `name` = "Amateurs";
INSERT INTO `class` SET `id` = {{ var.class_Breitensport_Professionals }}, `name` = "Profis";
INSERT INTO `class` SET `id` = {{ var.class_Breitensport_Masters }}, `name` = "Masters";
INSERT INTO `class` SET `id` = {{ var.class_Breitensport_Champions }}, `name` = "Champions";
INSERT INTO `class` SET `id` = {{ var.class_CloseD }}, `name` = "CloseD";
INSERT INTO `class` SET `id` = {{ var.class_Open_Class }}, `name` = "Open Class";
INSERT INTO `class` SET `id` = {{ var.class_Salsa }}, `name` = "Salsa";
INSERT INTO `class` SET `id` = {{ var.class_Polka }}, `name` = "Polka";
INSERT INTO `class` SET `id` = {{ var.class_TEST }}, `name` = "TEST";

-- Define the different dances with id, name, tag (short name) and disc (which discipline it belongs to, pointer)
INSERT INTO `dance` SET `id` = {{ var.dance_SW }}, `name` = "Slow Waltz",     `tag` = "SW", `disc` = {{ var.discipline_Ballroom }};
INSERT INTO `dance` SET `id` = {{ var.dance_TG }}, `name` = "Tango",          `tag` = "TG", `disc` = {{ var.discipline_Ballroom }};
INSERT INTO `dance` SET `id` = {{ var.dance_VW }}, `name` = "Viennese Waltz", `tag` = "VW", `disc` = {{ var.discipline_Ballroom }};
INSERT INTO `dance` SET `id` = {{ var.dance_SF }}, `name` = "Slow Foxtrot",   `tag` = "SF", `disc` = {{ var.discipline_Ballroom }};
INSERT INTO `dance` SET `id` = {{ var.dance_QS }}, `name` = "Quickstep",      `tag` = "QS", `disc` = {{ var.discipline_Ballroom }};
INSERT INTO `dance` SET `id` = {{ var.dance_SB }}, `name` = "Samba",          `tag` = "SB", `disc` = {{ var.discipline_Latin }};
INSERT INTO `dance` SET `id` = {{ var.dance_CC }}, `name` = "Cha Cha",        `tag` = "CC", `disc` = {{ var.discipline_Latin }};
INSERT INTO `dance` SET `id` = {{ var.dance_RB }}, `name` = "Rumba",          `tag` = "RB", `disc` = {{ var.discipline_Latin }};
INSERT INTO `dance` SET `id` = {{ var.dance_PD }}, `name` = "Paso Doble",     `tag` = "PD", `disc` = {{ var.discipline_Latin }};
INSERT INTO `dance` SET `id` = {{ var.dance_JV }}, `name` = "Jive",           `tag` = "JV", `disc` = {{ var.discipline_Latin }};
INSERT INTO `dance` SET `id` = {{ var.dance_SS }}, `name` = "Salsa",          `tag` = "SS", `disc` = {{ var.discipline_Salsa }};
-- INSERT INTO `dance` SET `id` = {{ var.dance_BC }}, `name` = "Bachata",        `tag` = "BC", `disc` = {{ var.discipline_Salsa }};
-- INSERT INTO `dance` SET `id` = {{ var.dance_MG }}, `name` = "Merengue",       `tag` = "MG", `disc` = {{ var.discipline_Salsa }};
INSERT INTO `dance` SET `id` = {{ var.dance_PK }}, `name` = "Polka",          `tag` = "PK", `disc` = {{ var.discipline_Polka }};

-- Define the different tournaments, normally every discipline-class combination has its own tournament.
-- Mode SP: since our couples will remain fixed during each tournament
-- May link to its qualification tournament, in which case no new starting numbers are needed
-- Day 1
INSERT INTO `tournament` SET `id` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `event` = 1, `class` = {{ var.class_Breitensport_qualification }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-03 09:00", `mode` = "SP", `numberl0` = 1, `numberl1` = 199, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Ballroom_Breitensport_Amateurs }}, `event` = 1, `class` = {{ var.class_Breitensport_Amateurs }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-03 11:00", `mode` = "SP", `quali` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Ballroom_Breitensport_Professionals }}, `event` = 1, `class` = {{ var.class_Breitensport_Professionals }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-03 12:00", `mode` = "SP", `quali` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Ballroom_Breitensport_Masters }}, `event` = 1, `class` = {{ var.class_Breitensport_Masters }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-03 13:00", `mode` = "SP", `quali` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Ballroom_Breitensport_Champions }}, `event` = 1, `class` = {{ var.class_Breitensport_Champions }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-03 14:00", `mode` = "SP", `quali` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Latin_CloseD }}, `event` = 1, `class` = {{ var.class_CloseD }}, `disc` = {{ var.discipline_Latin }}, `when` = "2018-03-03 15:00", `mode` = "CP_D", `numberl0` = 200, `numberl1` = 299, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Latin_Open_Class }}, `event` = 1, `class` = {{ var.class_Open_Class }}, `disc` = {{ var.discipline_Latin }}, `when` = "2018-03-03 15:00", `mode` = "CP_D", `numberl0` = 300, `numberl1` = 399, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Polka }}, `event` = 1, `class` = {{ var.class_Polka }}, `disc` = {{ var.discipline_Polka }}, `when` = "2018-03-03 15:00", `mode` = "SP", `numberl0` = 400, `numberl1` = 599, `floormin` = 1, `floormax` = 2;
-- Day 2
INSERT INTO `tournament` SET `id` = {{ var.tournament_Latin_Breitensport_qualification }}, `event` = 1, `class` = {{ var.class_Breitensport_qualification }}, `disc` = {{ var.discipline_Latin }}, `when` = "2018-03-04 09:00", `mode` = "SP", `numberl0` = 1, `numberl1` = 199;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Latin_Breitensport_Amateurs }}, `event` = 1, `class` = {{ var.class_Breitensport_Amateurs }}, `disc` = {{ var.discipline_Latin }}, `when` = "2018-03-04 11:00", `mode` = "SP", `quali` = {{ var.tournament_Latin_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Latin_Breitensport_Professionals }}, `event` = 1, `class` = {{ var.class_Breitensport_Professionals }}, `disc` = {{ var.discipline_Latin }}, `when` = "2018-03-04 12:00", `mode` = "SP", `quali` = {{ var.tournament_Latin_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Latin_Breitensport_Masters }}, `event` = 1, `class` = {{ var.class_Breitensport_Masters }}, `disc` = {{ var.discipline_Latin }}, `when` = "2018-03-04 13:00", `mode` = "SP", `quali` = {{ var.tournament_Latin_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Latin_Breitensport_Champions }}, `event` = 1, `class` = {{ var.class_Breitensport_Champions }}, `disc` = {{ var.discipline_Latin }}, `when` = "2018-03-04 14:00", `mode` = "SP", `quali` = {{ var.tournament_Latin_Breitensport_qualification }}, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Ballroom_CloseD }}, `event` = 1, `class` = {{ var.class_CloseD }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-04 15:00", `mode` = "CP_D", `numberl0` = 200, `numberl1` = 299, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Ballroom_Open_Class }}, `event` = 1, `class` = {{ var.class_Open_Class }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-04 15:00", `mode` = "CP_D", `numberl0` = 300, `numberl1` = 399, `floormin` = 1, `floormax` = 2;
INSERT INTO `tournament` SET `id` = {{ var.tournament_Salsa }}, `event` = 1, `class` = {{ var.class_Salsa }}, `disc` = {{ var.discipline_Salsa }}, `when` = "2018-03-03 15:00", `mode` = "SP", `numberl0` = 400, `numberl1` = 599, `floormin` = 1, `floormax` = 2;
-- Test to educate judges
INSERT INTO `tournament` SET `id` = {{ var.tournament_TEST }}, `event` = 1, `class` = {{ var.class_TEST }}, `disc` = {{ var.discipline_Ballroom }}, `when` = "2018-03-03 08:00", `mode` = "SP", `numberl0` = 900, `numberl1` = 999, `floormin` = 1, `floormax` = 2;

-- The dances to be danced in tournament, altered in webUI prior to actual rounds
-- First day
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `dance` = {{ var.dance_SW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `dance` = {{ var.dance_TG }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_qualification }}, `dance` = {{ var.dance_QS }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Amateurs }}, `dance` = {{ var.dance_SW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Amateurs }}, `dance` = {{ var.dance_TG }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Amateurs }}, `dance` = {{ var.dance_QS }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Professionals }}, `dance` = {{ var.dance_SW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Professionals }}, `dance` = {{ var.dance_TG }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Professionals }}, `dance` = {{ var.dance_QS }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Masters }}, `dance` = {{ var.dance_SW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Masters }}, `dance` = {{ var.dance_TG }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Masters }}, `dance` = {{ var.dance_QS }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Champions }}, `dance` = {{ var.dance_SW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Champions }}, `dance` = {{ var.dance_TG }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Breitensport_Champions }}, `dance` = {{ var.dance_QS }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_CloseD }}, `dance` = {{ var.dance_CC }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_CloseD }}, `dance` = {{ var.dance_RB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_CloseD }}, `dance` = {{ var.dance_JV }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Open_Class }}, `dance` = {{ var.dance_SB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Open_Class }}, `dance` = {{ var.dance_CC }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Open_Class }}, `dance` = {{ var.dance_RB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Open_Class }}, `dance` = {{ var.dance_PD }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Open_Class }}, `dance` = {{ var.dance_JV }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Polka }}, `dance` = {{ var.dance_PK }};

-- Second day
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_qualification }}, `dance` = {{ var.dance_CC }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_qualification }}, `dance` = {{ var.dance_RB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_qualification }}, `dance` = {{ var.dance_JV }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Amateurs }}, `dance` = {{ var.dance_CC }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Amateurs }}, `dance` = {{ var.dance_RB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Amateurs }}, `dance` = {{ var.dance_JV }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Professionals }}, `dance` = {{ var.dance_CC }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Professionals }}, `dance` = {{ var.dance_RB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Professionals }}, `dance` = {{ var.dance_JV }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Masters }}, `dance` = {{ var.dance_CC }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Masters }}, `dance` = {{ var.dance_RB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Masters }}, `dance` = {{ var.dance_JV }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Champions }}, `dance` = {{ var.dance_CC }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Champions }}, `dance` = {{ var.dance_RB }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Latin_Breitensport_Champions }}, `dance` = {{ var.dance_JV }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_CloseD }}, `dance` = {{ var.dance_SW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_CloseD }}, `dance` = {{ var.dance_TG }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_CloseD }}, `dance` = {{ var.dance_QS }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Open_Class }}, `dance` = {{ var.dance_SW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Open_Class }}, `dance` = {{ var.dance_TG }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Open_Class }}, `dance` = {{ var.dance_VW }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Open_Class }}, `dance` = {{ var.dance_SF }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Ballroom_Open_Class }}, `dance` = {{ var.dance_QS }};
INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Salsa }}, `dance` = {{ var.dance_SS }};
-- INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Salsa }}, `dance` = {{ var.dance_BC }};
-- INSERT INTO `t_dance` SET `tourn` = {{ var.tournament_Salsa }}, `dance` = {{ var.dance_MG }};

-- TEST Lead and Follows
{%- for i in range(50) %}
INSERT INTO `person` SET `id` = {{ 9001 + i }}, `fname` = "Leader{{ i+1 }}", `name` = "Test", `team` = {{ var.team_organization }};
INSERT INTO `person` SET `id` = {{ 9101 + i }}, `fname` = "Follower{{ i+1 }}", `name` = "Test", `team` = {{ var.team_organization }};
INSERT INTO `start` (`tourn`,`lead`,`follow`) VALUES ({{ var.tournament_TEST }}, {{ 9001 + i }}, {{ 9101 + i }});
{%- endfor %}

-- Dancers
-- Insert dancers into system:
{%- for dancer in dancers %}
INSERT INTO `person` SET `id` = "{{ dancer.contestant_id }}", `fname` = "{{ dancer.first_name }}", `name` = "{{ dancer.get_last_name() }}", `team` = (SELECT `id` FROM `team` WHERE `name` = "{{ dancer.contestant_info[0].team.name }} ({{ dancer.contestant_info[0].team.city }})");
{%- endfor %}

-- Jury
{%- for dancer in dancers %}
{%- if dancer.volunteer_info[0].jury_ballroom == "yes" or dancer.volunteer_info[0].jury_ballroom == "maybe"
or dancer.volunteer_info[0].jury_latin == "yes" or dancer.volunteer_info[0].jury_latin == "maybe"
or dancer.volunteer_info[0].jury_salsa == "yes" or dancer.volunteer_info[0].jury_salsa == "maybe"
or dancer.volunteer_info[0].jury_polka == "yes" or dancer.volunteer_info[0].jury_polka == "maybe" %}
INSERT INTO `staff`      SET `id` = {{ dancer.contestant_id }}, `tag` = "{{ dancer.contestant_info[0].number }}", `password` = SHA1("jury{{ dancer.contestant_info[0].number }}");
INSERT INTO `employ`     SET `role` = "adjudicator", `who` = {{ dancer.contestant_id }};
INSERT INTO `employ`     SET `role` = "adjudicator", `who` = {{ dancer.contestant_id }}, `tourn` = {{ var.tournament_TEST }};
{%- endif %}
{%- endfor %}

SHOW WARNINGS;